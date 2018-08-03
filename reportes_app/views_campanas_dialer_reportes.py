# -*- coding: utf-8 -*-

"""Vista para reportes de campana dialer"""

from __future__ import unicode_literals

from django.utils.translation import ugettext as _

from django.shortcuts import render
from ominicontacto_app.models import Campana, OpcionCalificacion
from django.views.generic.detail import DetailView
from ominicontacto_app.services.campana_service import CampanaService


class CampanaDialerDetailView(DetailView):
    """Detalle de una campana dialer"""
    template_name = 'campana_dialer/detalle.html'
    model = Campana
    context_object_name = 'campana'

    def get_context_data(self, **kwargs):
        context = super(
            CampanaDialerDetailView, self).get_context_data(**kwargs)
        campana = self.get_object()
        campana_service = CampanaService()
        estados_running_wombat = [Campana.ESTADO_ACTIVA, Campana.ESTADO_PAUSADA,
                                  Campana.ESTADO_FINALIZADA]
        opciones_calificacion = campana.opciones_calificacion.all()
        context['opciones_calificacion'] = opciones_calificacion.values('nombre')
        context['opciones_calificacion_gestion'] = opciones_calificacion.filter(
            tipo=OpcionCalificacion.GESTION).values('nombre')
        if campana.estado in estados_running_wombat:
            dato_campana = campana_service.obtener_dato_campana_run(campana)
            if dato_campana:
                status = campana_service.obtener_status_campana_running(
                    dato_campana['hoppercampId'])
                context['efectuadas'] = dato_campana['n_calls_attempted']
                context['terminadas'] = dato_campana['n_calls_completed']
                context['estimadas'] = dato_campana['n_est_remaining_calls']
                context['status'] = status
                context['resultado'] = True
            else:
                context['resultado'] = False
        return context

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])


def detalle_campana_dialer_view(request):
    """Vista que muestrar el detalle de campana en wombat"""
    pk_campana = int(request.GET['pk_campana'])
    campana = Campana.objects.get(pk=pk_campana)
    campana_service = CampanaService()
    dato_campana = campana_service.obtener_dato_campana_run(campana)
    if dato_campana:
        status = campana_service.obtener_status_campana_running(
            dato_campana['hoppercampId'])
        data = {
            'error_consulta': False,
            'campana': campana,
            'efectuadas': dato_campana['n_calls_attempted'],
            'terminadas': dato_campana['n_calls_completed'],
            'estimadas': dato_campana['n_est_remaining_calls'],
            'status': status

        }
    else:
        data = {
            'campana': campana,
            'error_consulta': _(u"No se pudo consultar el estado actual de la campaña. "
                                "Consulte con su administrador.")
        }
    return render(request, 'campana_dialer/detalle_campana.html', data)
