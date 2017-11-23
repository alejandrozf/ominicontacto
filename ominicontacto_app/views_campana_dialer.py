# -*- coding: utf-8 -*-

"""
Vista para administrar el modelo Campana de tipo dialer
Observacion se copiaron varias vistas del modulo views_campana
"""

from __future__ import unicode_literals

import json

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from ominicontacto_app.models import Contacto, Campana, SupervisorProfile
from django.views.generic import (
    ListView, DeleteView, FormView, UpdateView
)
from django.views.generic.base import RedirectView
from ominicontacto_app.services.campana_service import CampanaService
from ominicontacto_app.forms import (
    UpdateBaseDatosForm, BusquedaContactoForm, FormularioCampanaContacto,
    FormularioNuevoContacto, CampanaSupervisorUpdateForm
)
from ominicontacto_app.utiles import convertir_ascii_string
from ominicontacto_app.views_campana import CampanaSupervisorUpdateView

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
        context['inactivas'] = campanas.filter(estado=Campana.ESTADO_INACTIVA)
        context['pausadas'] = campanas.filter(estado=Campana.ESTADO_PAUSADA)
        context['activas'] = campanas.filter(estado=Campana.ESTADO_ACTIVA)
        context['borradas'] = campanas.filter(estado=Campana.ESTADO_BORRADA,
                                              oculto=False)
        context['finalizadas'] = campanas.filter(estado=Campana.ESTADO_FINALIZADA)
        return context

    # def get(self, request, *args, **kwargs):
    #   return self.render_to_response(self.get_context_data())


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


class CampanaDialerDeleteView(DeleteView):
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
        self.object.remover()
        message = '<strong>Operación Exitosa!</strong>\
        Se llevó a cabo con éxito la eliminación de la campana.'

        messages.add_message(
            self.request,
            messages.SUCCESS,
            message,
        )
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


def mostrar_campanas_dialer_borradas_ocultas_view(request):
    """Vista para mostrar campanas dialer ocultas"""
    borradas = Campana.objects.obtener_borradas()
    if request.user.is_authenticated() and request.user and \
            not request.user.get_is_administrador():
        user = request.user
        borradas = Campana.objects.obtener_campanas_vista_by_user(borradas, user)
    data = {
        'borradas': borradas.filter(type=Campana.TYPE_DIALER),
    }
    return render(request, 'campana_dialer/campanas_borradas.html', data)


def detalle_campana_dialer_view(request):
    """Vista que muestrar el detalle de campana en wombat"""
    pk_campana = int(request.GET['pk_campana'])
    campana = Campana.objects.get(pk=pk_campana)
    campana_service = CampanaService()
    dato_campana = campana_service.obtener_dato_campana_run(campana)
    status = campana_service.obtener_status_campana_running(
        dato_campana['hoppercampId'])
    data = {
        'campana': campana,
        'efectuadas': dato_campana['n_calls_attempted'],
        'terminadas': dato_campana['n_calls_completed'],
        'estimadas': dato_campana['n_est_remaining_calls'],
        'status': status

    }
    return render(request, 'campana_dialer/detalle_campana.html', data)


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
        columnas = form.cleaned_data.get('columnas')
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


class CampanaDialerBusquedaContactoFormView(FormView):
    """Vista realiza la busqueda de contacto en una campana dialer
    Copiada del modulo views_campana actualmente se usa esta vista, revisar la otra
    vista si se usa
    """
    form_class = BusquedaContactoForm
    template_name = 'campana_dialer/busqueda_contacto.html'

    def get(self, request, *args, **kwargs):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        listado_de_contacto = Contacto.objects.contactos_by_bd_contacto(
            campana.bd_contacto)
        return self.render_to_response(self.get_context_data(
            listado_de_contacto=listado_de_contacto))

    def get_context_data(self, **kwargs):
        context = super(CampanaDialerBusquedaContactoFormView, self).get_context_data(
            **kwargs)
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        context['campana'] = campana
        return context

    def form_valid(self, form):
        filtro = form.cleaned_data.get('buscar')
        try:
            campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
            listado_de_contacto = Contacto.objects.\
                contactos_by_filtro_bd_contacto(campana.bd_contacto, filtro)
        except Contacto.DoesNotExist:
            listado_de_contacto = Contacto.objects.contactos_by_bd_contacto(
                campana.bd_contacto)
            return self.render_to_response(self.get_context_data(
                form=form, listado_de_contacto=listado_de_contacto))

        if listado_de_contacto:
            return self.render_to_response(self.get_context_data(
                form=form, listado_de_contacto=listado_de_contacto))
        else:
            listado_de_contacto = Contacto.objects.contactos_by_bd_contacto(
                campana.bd_contacto)
            return self.render_to_response(self.get_context_data(
                form=form, listado_de_contacto=listado_de_contacto))


class FormularioSeleccionCampanaDialerFormView(FormView):
    """Vista para seleccionar una campana a la cual se le agregar un nuevo contacto
    Copiada del modulo views_campana actualmente se usa esta vista, revisar la otra
    vista si se usa
    """
    form_class = FormularioCampanaContacto
    template_name = 'campana_dialer/seleccion_campana_form.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated()\
                and self.request.user.get_agente_profile():
            agente = self.request.user.get_agente_profile()
        if not agente.campana_member.all():
            message = ("Este agente no esta asignado a ninguna campaña ")
            messages.warning(self.request, message)
        return super(FormularioSeleccionCampanaDialerFormView,
                     self).dispatch(request, *args, **kwargs)

    def get_form(self):
        self.form_class = self.get_form_class()
        if self.request.user.is_authenticated()\
                and self.request.user.get_agente_profile():
            agente = self.request.user.get_agente_profile()
            campanas = [queue.queue_name.campana
                        for queue in agente.get_campanas_activas_miembro()]

        campana_choice = [(campana.id, campana.nombre) for campana in
                          campanas if campana.type is Campana.TYPE_DIALER]
        return self.form_class(campana_choice=campana_choice, **self.get_form_kwargs())

    def form_valid(self, form):
        campana = form.cleaned_data.get('campana')
        return HttpResponseRedirect(
            reverse('nuevo_contacto_campana_dialer',
                    kwargs={"pk_campana": campana}))

    def get_success_url(self):
        reverse('view_blanco')


class FormularioNuevoContactoFormView(FormView):
    """Esta vista agrega un nuevo contacto para la campana seleccionada
    Copiada del modulo views_campana actualmente se usa esta vista, revisar la otra
    vista si se usa
    """
    form_class = FormularioNuevoContacto
    template_name = 'campana_dialer/nuevo_contacto_campana.html'

    def get_form(self):
        self.form_class = self.get_form_class()
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        base_datos = campana.bd_contacto
        metadata = base_datos.get_metadata()
        campos = metadata.nombres_de_columnas
        return self.form_class(campos=campos, **self.get_form_kwargs())

    def form_valid(self, form):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        base_datos = campana.bd_contacto
        metadata = base_datos.get_metadata()
        nombres = metadata.nombres_de_columnas
        telefono = form.cleaned_data.get('telefono')

        datos = []
        nombres.remove('telefono')

        for nombre in nombres:
            campo = form.cleaned_data.get(convertir_ascii_string(nombre))
            datos.append(campo)
        contacto = Contacto.objects.create(
            telefono=telefono, datos=json.dumps(datos),
            bd_contacto=base_datos)
        agente = self.request.user.get_agente_profile()

        if campana.type == Campana.TYPE_PREVIEW:
            # inicializamos una nueva entrada en la tabla que relaciona agentes
            # con contactos en campañas preview
            campana.agregar_agente_contacto(contacto)

        return HttpResponseRedirect(
            reverse('calificacion_formulario_update',
                    kwargs={"pk_campana": self.kwargs['pk_campana'],
                            "pk_contacto": contacto.pk,
                            "id_agente": agente.pk,
                            "wombat_id": 0}))

    def get_success_url(self):
        reverse('view_blanco')


class CampanaDialerSupervisorUpdateView(CampanaSupervisorUpdateView):
    """
    Esta vista agrega supervisores a una campana dialer
    logica copiado para campana_preview
    """

    def get_success_url(self):
        return reverse('campana_dialer_list')
