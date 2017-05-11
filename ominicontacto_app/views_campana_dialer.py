# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from ominicontacto_app.models import (
    CampanaDialer
)
from django.views.generic import (
    ListView, DeleteView, FormView
)
from django.views.generic.base import RedirectView
from ominicontacto_app.services.campana_service import CampanaService
from ominicontacto_app.forms import UpdateBaseDatosDialerForm

import logging as logging_

logger = logging_.getLogger(__name__)


class CampanaDialerListView(ListView):
    """
    Esta vista lista los objetos CampanaDialer
    """

    template_name = 'campana_dialer/campana_list.html'
    context_object_name = 'campanas'
    model = CampanaDialer

    def get_context_data(self, **kwargs):
        context = super(CampanaDialerListView, self).get_context_data(
           **kwargs)
        context['inactivas'] = CampanaDialer.objects.obtener_inactivas()
        context['pausadas'] = CampanaDialer.objects.obtener_pausadas()
        context['activas'] = CampanaDialer.objects.obtener_activas()
        context['borradas'] = CampanaDialer.objects.obtener_borradas().filter(
            oculto=False)
        return context




class PlayCampanaDialerView(RedirectView):
    """
    Esta vista actualiza la campañana activándola.
    """

    pattern_name = 'campana_dialer_list'

    def post(self, request, *args, **kwargs):
        campana = CampanaDialer.objects.get(pk=request.POST['campana_id'])
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
    Esta vista actualiza la campañana activándola.
    """

    pattern_name = 'campana_dialer_list'

    def post(self, request, *args, **kwargs):
        campana = CampanaDialer.objects.get(pk=request.POST['campana_id'])
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
        campana = CampanaDialer.objects.get(pk=request.POST['campana_id'])
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
    model = CampanaDialer
    template_name = 'campana_dialer/delete_campana.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()

        service = CampanaService()
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
        return CampanaDialer.objects.get(pk=self.kwargs['pk_campana'])

    def get_success_url(self):
        return reverse('campana_dialer_list')


class OcultarCampanaDialerView(RedirectView):
    """
    Esta vista actualiza la campañana ocultandola.
    """

    pattern_name = 'campana_dialer_list'

    def get(self, request, *args, **kwargs):
        campana = CampanaDialer.objects.get(pk=self.kwargs['pk_campana'])
        campana.ocultar()
        return HttpResponseRedirect(reverse('campana_dialer_list'))


class DesOcultarCampanaDialerView(RedirectView):
    """
    Esta vista actualiza la campañana haciendola visible.
    """

    pattern_name = 'campana_dialer_list'

    def get(self, request, *args, **kwargs):
        campana = CampanaDialer.objects.get(pk=self.kwargs['pk_campana'])
        campana.desocultar()
        return HttpResponseRedirect(reverse('campana_dialer_list'))


def mostrar_campanas_dialer_borradas_ocultas_view(request):
    borradas = CampanaDialer.objects.obtener_borradas()
    data = {
        'borradas': borradas,
    }
    return render(request, 'campana_dialer/campanas_borradas.html', data)


def detalle_campana_dialer_view(request):
    pk_campana = int(request.GET['pk_campana'])
    campana = CampanaDialer.objects.get(pk=pk_campana)
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
    Esta vista sincroniza base datos con discador
    """

    model = CampanaDialer
    context_object_name = 'campana'
    form_class = UpdateBaseDatosDialerForm
    template_name = 'base_create_update_form.html'

    def get_object(self, queryset=None):
        return CampanaDialer.objects.get(pk=self.kwargs['pk_campana'])

    def get_form(self, form_class):
        self.object = self.get_object()
        metadata = self.object.bd_contacto.get_metadata()
        columnas_telefono = metadata.columnas_con_telefono
        nombres_de_columnas = metadata.nombres_de_columnas
        tts_choices = [(columna, nombres_de_columnas[columna]) for columna in
                       columnas_telefono if columna > 6]
        return form_class(tts_choices=tts_choices, **self.get_form_kwargs())

    def form_valid(self, form):
        usa_contestador = form.cleaned_data.get('usa_contestador')
        evitar_duplicados = form.cleaned_data.get('evitar_duplicados')
        evitar_sin_telefono = form.cleaned_data.get('evitar_sin_telefono')
        prefijo_discador = form.cleaned_data.get('prefijo_discador')
        telefonos = form.cleaned_data.get('telefonos')
        bd_contacto = form.cleaned_data.get('bd_contacto')
        self.object = self.get_object()
        campana_service = CampanaService()
        error = campana_service.validar_modificacion_bd_contacto(
            self.get_object(), bd_contacto)
        if error:
            return self.form_invalid(form, error=error)
        self.object.bd_contacto = bd_contacto
        self.object.save()

        campana_service.cambiar_base(self.get_object(), telefonos,
                                     usa_contestador, evitar_duplicados,
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
