# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from ominicontacto_app.models import (
    CampanaDialer
)
from django.views.generic import (
    ListView, DeleteView
)
from django.views.generic.base import RedirectView
from ominicontacto_app.services.campana_service import CampanaService

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
