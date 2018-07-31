# -*- coding: utf-8 -*-

"""
Vista para administrar el modelo Campana de tipo dialer
Observacion se copiaron varias vistas del modulo views_campana
"""

from __future__ import unicode_literals

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.views.generic import ListView, DeleteView, FormView
from django.views.generic.base import RedirectView

from ominicontacto_app.models import Campana
from ominicontacto_app.services.campana_service import CampanaService
from ominicontacto_app.forms import UpdateBaseDatosForm
from ominicontacto_app.views_campana import CampanaSupervisorUpdateView, CampanasDeleteMixin

import logging as logging_

logger = logging_.getLogger(__name__)


class CampanaDialerListView(ListView):
    """
    Esta vista lista los objetos Campana de type dialer
    Vista copiada
    """

    template_name = 'campana_dialer/campana_list.html'
    context_object_name = 'campanas'
    model = Campana

    def get_context_data(self, **kwargs):
        context = super(CampanaDialerListView, self).get_context_data(
            **kwargs)
        campanas = Campana.objects.obtener_campanas_dialer()
        # Filtra las campanas de acuerdo al usuario logeado si tiene permiso sobre
        # las mismas
        if self.request.user.is_authenticated() and self.request.user and \
                not self.request.user.get_is_administrador():
            user = self.request.user
            campanas = Campana.objects.obtener_campanas_vista_by_user(campanas, user)

        campana_service = CampanaService()
        campana_service.chequear_campanas_finalizada_eliminarlas(
            campanas.filter(estado=Campana.ESTADO_ACTIVA))
        context['campanas'] = campanas
        context['inactivas'] = campanas.filter(estado=Campana.ESTADO_INACTIVA)
        context['pausadas'] = campanas.filter(estado=Campana.ESTADO_PAUSADA)
        context['activas'] = campanas.filter(estado=Campana.ESTADO_ACTIVA)
        context['borradas'] = campanas.filter(estado=Campana.ESTADO_BORRADA,
                                              oculto=False)
        context['finalizadas'] = campanas.filter(estado=Campana.ESTADO_FINALIZADA)

        context['canales_en_uso'] = Campana.objects.obtener_canales_dialer_en_uso()
        return context


class PlayCampanaDialerView(RedirectView):
    """
    Esta vista actualiza la campañana activándola.
    """

    pattern_name = 'campana_dialer_list'

    def post(self, request, *args, **kwargs):
        campana = Campana.objects.get(pk=request.POST['campana_id'])
        campana_service = CampanaService()
        resultado = campana_service.start_campana_wombat(campana)
        campana.play()
        if resultado:
            message = '<strong>Operación Exitosa!</strong>\
            Se llevó a cabo con éxito la activación de\
            la Campaña.'

            messages.add_message(
                self.request,
                messages.SUCCESS,
                message,
            )
        else:
            message = '<strong>ERROR!</strong>\
                        No se pudo llevar  cabo con éxito la activación de\
                        la Campaña.'

            messages.add_message(
                self.request,
                messages.SUCCESS,
                message,
            )
        return super(PlayCampanaDialerView, self).post(request, *args, **kwargs)


class PausarCampanaDialerView(RedirectView):
    """
    Esta vista actualiza la campañana pausandola.
    """

    pattern_name = 'campana_dialer_list'

    def post(self, request, *args, **kwargs):
        campana = Campana.objects.get(pk=request.POST['campana_id'])
        campana_service = CampanaService()
        resultado = campana_service.pausar_campana_wombat(campana)
        campana.pausar()

        if resultado:
            message = '<strong>Operación Exitosa!</strong>\
            Se llevó a cabo con éxito la pausa de\
            la Campaña.'

            messages.add_message(
                self.request,
                messages.SUCCESS,
                message,
            )
        else:
            message = '<strong>ERROR!</strong>\
                        No se pudo llevar  cabo con éxito el pausado de\
                        la Campaña.'

            messages.add_message(
                self.request,
                messages.SUCCESS,
                message,
            )
        return super(PausarCampanaDialerView, self).post(request, *args, **kwargs)


class ActivarCampanaDialerView(RedirectView):
    """
    Esta vista actualiza la campañana activándola.
    """

    pattern_name = 'campana_dialer_list'

    def post(self, request, *args, **kwargs):
        campana = Campana.objects.get(pk=request.POST['campana_id'])
        campana_service = CampanaService()
        resultado = campana_service.despausar_campana_wombat(campana)
        campana.activar()

        if resultado:
            message = '<strong>Operación Exitosa!</strong>\
            Se llevó a cabo con éxito la activación de\
            la Campaña.'

            messages.add_message(
                self.request,
                messages.SUCCESS,
                message,
            )
        else:
            message = '<strong>ERROR!</strong>\
                        No se pudo llevar  cabo con éxito la activación de\
                        la Campaña.'

            messages.add_message(
                self.request,
                messages.SUCCESS,
                message,
            )
        return super(ActivarCampanaDialerView, self).post(request, *args, **kwargs)


class CampanaDialerDeleteView(CampanasDeleteMixin, DeleteView):
    """
    Esta vista se encarga de la eliminación de una campana
    """
    model = Campana
    template_name = 'campana_dialer/delete_campana.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        service = CampanaService()
        # remueve campana de wombat
        remover = service.remove_campana_wombat(self.object)
        if not remover:
            message = ("<strong>Operación Errónea!</strong> "
                       "No se pudo eliminar la campana {0} del discador".
                       format(self.object.nombre))
            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
        super(CampanaDialerDeleteView, self).delete(request, *args, **kwargs)
        self.object.remover()
        return HttpResponseRedirect(success_url)

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get_success_url(self):
        return reverse('campana_dialer_list')


class OcultarCampanaDialerView(RedirectView):
    """
    Esta vista actualiza la campañana ocultandola.
    """

    pattern_name = 'campana_dialer_list'

    def get(self, request, *args, **kwargs):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        campana.ocultar()
        return HttpResponseRedirect(reverse('campana_dialer_list'))


class DesOcultarCampanaDialerView(RedirectView):
    """
    Esta vista actualiza la campañana haciendola visible.
    """

    pattern_name = 'campana_dialer_list'

    def get(self, request, *args, **kwargs):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        campana.desocultar()
        return HttpResponseRedirect(reverse('campana_dialer_list'))


class UpdateBaseDatosDialerView(FormView):
    """
    Esta vista actualiza la base de datos de una campana y sincroniza la base de datos
    /lista en wombat
    """

    model = Campana
    context_object_name = 'campana'
    form_class = UpdateBaseDatosForm
    template_name = 'base_create_update_form.html'

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get_form(self):
        self.form_class = self.get_form_class()
        self.object = self.get_object()
        metadata = self.object.bd_contacto.get_metadata()
        nombres_de_columnas = metadata.nombres_de_columnas
        nombres_de_columnas.remove('telefono')
        tts_choices = [(columna, columna) for columna in
                       nombres_de_columnas]
        return self.form_class(tts_choices=tts_choices, **self.get_form_kwargs())

    def form_valid(self, form):
        evitar_duplicados = form.cleaned_data.get('evitar_duplicados')
        evitar_sin_telefono = form.cleaned_data.get('evitar_sin_telefono')
        prefijo_discador = form.cleaned_data.get('prefijo_discador')
        columnas = form.cleaned_data.get('telefonos')
        bd_contacto = form.cleaned_data.get('bd_contacto')
        self.object = self.get_object()
        campana_service = CampanaService()
        # valida de que se pueda cambiar la base de datos que tenga las misma columnas
        # que la actualmente poseee
        error = campana_service.validar_modificacion_bd_contacto(
            self.get_object(), bd_contacto)
        if error:
            return self.form_invalid(form, error=error)
        self.object.bd_contacto = bd_contacto
        self.object.save()
        # realiza el cambio de la base de datos en wombat
        campana_service.cambiar_base(self.get_object(), columnas, evitar_duplicados,
                                     evitar_sin_telefono, prefijo_discador)
        message = 'Operación Exitosa!\
                Se llevó a cabo con éxito el cambio de base de datos.'

        messages.add_message(
            self.request,
            messages.SUCCESS,
            message,
        )

        return redirect(self.get_success_url())

    def form_invalid(self, form, error=None):

        message = '<strong>Operación Errónea!</strong> \
                  La base de datos es erronea. {0}'.format(error)

        messages.add_message(
            self.request,
            messages.WARNING,
            message,
        )
        return self.render_to_response(self.get_context_data())

    def get_success_url(self):
        return reverse('campana_dialer_list')


class CampanaDialerSupervisorUpdateView(CampanaSupervisorUpdateView):
    """
    Esta vista agrega supervisores a una campana dialer
    logica copiado para campana_preview
    """

    def get_success_url(self):
        return reverse('campana_dialer_list')


class CampanaDialerBorradasListView(CampanaDialerListView):
    """
    Vista que lista las campañas dialer pero de incluyendo las borradas ocultas
    """

    template_name = 'campana_dialer/campanas_borradas.html'

    def get_context_data(self, **kwargs):
        context = super(CampanaDialerBorradasListView, self).get_context_data(**kwargs)
        context['borradas'] = context['campanas'].filter(estado=Campana.ESTADO_BORRADA)
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return super(CampanaDialerBorradasListView, self).get(request, *args, **kwargs)
        else:
            return JsonResponse({'result': 'desconectado'})
