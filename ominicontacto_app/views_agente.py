# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
from django.views.generic import FormView, UpdateView, ListView
from django.shortcuts import redirect
from ominicontacto_app.models import AgenteProfile
from ominicontacto_app.forms import ReporteForm
from ominicontacto_app.services.reporte_agente_calificacion import \
    ReporteAgenteService
from ominicontacto_app.services.reporte_agente_venta import \
    ReporteFormularioVentaService
from ominicontacto_app.utiles import convert_fecha_datetime
from ominicontacto_app.services.reporte_llamadas import EstadisticasService
from django.http import JsonResponse
from django.contrib.auth import logout
from django.conf import settings
from ominicontacto_app.services.asterisk_ami_http import (
    AsteriskHttpClient, AsteriskHttpOriginateError
)
import logging as _logging


logger = _logging.getLogger(__name__)


class AgenteReporteCalificaciones(FormView):

    template_name = 'agente/reporte_agente_calificaciones.html'
    context_object_name = 'agente'
    model = AgenteProfile
    form_class = ReporteForm

    def get_object(self, queryset=None):
        return AgenteProfile.objects.get(pk=self.kwargs['pk_agente'])

    def get(self, request, *args, **kwargs):
        service = ReporteAgenteService()
        service_formulario = ReporteFormularioVentaService()
        hoy_ahora = datetime.datetime.today()
        hoy = hoy_ahora.date()
        agente = AgenteProfile.objects.get(pk=self.kwargs['pk_agente'])
        service.crea_reporte_csv(agente, hoy, hoy_ahora)
        service_formulario.crea_reporte_csv(agente, hoy, hoy_ahora)
        fecha_desde = datetime.datetime.combine(hoy, datetime.time.min)
        fecha_hasta = datetime.datetime.combine(hoy_ahora, datetime.time.max)
        listado_calificaciones = agente.calificaciones.filter(fecha__range=(
            fecha_desde, fecha_hasta))
        return self.render_to_response(self.get_context_data(
            listado_calificaciones=listado_calificaciones, agente=agente))

    def form_valid(self, form):
        fecha = form.cleaned_data.get('fecha')
        fecha_desde, fecha_hasta = fecha.split('-')
        fecha_desde = convert_fecha_datetime(fecha_desde)
        fecha_hasta = convert_fecha_datetime(fecha_hasta)
        service = ReporteAgenteService()
        service_formulario = ReporteFormularioVentaService()
        agente = AgenteProfile.objects.get(pk=self.kwargs['pk_agente'])
        service.crea_reporte_csv(agente, fecha_desde, fecha_hasta)
        service_formulario.crea_reporte_csv(agente, fecha_desde, fecha_hasta)
        fecha_desde = datetime.datetime.combine(fecha_desde, datetime.time.min)
        fecha_hasta = datetime.datetime.combine(fecha_hasta, datetime.time.max)
        listado_calificaciones = agente.calificaciones.filter(fecha__range=(
            fecha_desde, fecha_hasta))
        return self.render_to_response(self.get_context_data(
            listado_calificaciones=listado_calificaciones, agente=agente))


class ExportaReporteFormularioVentaView(UpdateView):
    """
    Esta vista invoca a generar un csv de reporte de la la venta.
    """

    model = AgenteProfile
    context_object_name = 'agente'

    def get_object(self, queryset=None):
        return AgenteProfile.objects.get(pk=self.kwargs['pk_agente'])

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        service = ReporteFormularioVentaService()
        agente = AgenteProfile.objects.get(pk=self.kwargs['pk_agente'])
        url = service.obtener_url_reporte_csv_descargar(self.object)

        return redirect(url)


class ExportaReporteCalificacionView(UpdateView):
    """
    Esta vista invoca a generar un csv de reporte de las calificaciones.
    """

    model = AgenteProfile
    context_object_name = 'agente'

    def get_object(self, queryset=None):
        return AgenteProfile.objects.get(pk=self.kwargs['pk_agente'])

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        service = ReporteAgenteService()
        agente = AgenteProfile.objects.get(pk=self.kwargs['pk_agente'])
        url = service.obtener_url_reporte_csv_descargar(self.object)

        return redirect(url)


class AgenteReporteListView(FormView):
    """
    Esta vista lista los tiempo de los agentes

    """

    template_name = 'agente/tiempos.html'
    context_object_name = 'agentes'
    model = AgenteProfile
    form_class = ReporteForm

    # def get_context_data(self, **kwargs):
    #     context = super(AgenteReporteListView, self).get_context_data(
    #        **kwargs)
    #     agente_service = EstadisticasService()
    #     context['estadisticas'] = agente_service._calcular_estadisticas()
    #     return context

    def get(self, request, *args, **kwargs):
        hoy_ahora = datetime.datetime.today()
        hoy = hoy_ahora.date()
        agente_service = EstadisticasService()
        estadisticas = agente_service.general_campana(hoy, hoy_ahora)
        return self.render_to_response(self.get_context_data(
            estadisticas=estadisticas))

    def form_valid(self, form):
        fecha = form.cleaned_data.get('fecha')
        fecha_desde, fecha_hasta = fecha.split('-')
        fecha_desde = convert_fecha_datetime(fecha_desde)
        fecha_hasta = convert_fecha_datetime(fecha_hasta)

        agente_service = EstadisticasService()
        estadisticas = agente_service.general_campana(fecha_desde, fecha_hasta)

        return self.render_to_response(self.get_context_data(
            estadisticas=estadisticas))


def cambiar_estado_agente_view(request):
    pk_agente = request.GET['pk_agente']
    estado = request.GET['estado']
    agente = AgenteProfile.objects.get(pk=int(pk_agente))
    agente.estado = int(estado)
    agente.save()
    response = JsonResponse({'status': 'OK'})
    return response


def logout_view(request):
    logout(request)
    if request.user.is_agente and request.user.get_agente_profile():
        agente = request.user.get_agente_profile()
        variables = {
            'AGENTE': str(agente.pk),
            'AGENTNAME': request.user.get_full_name()
        }
        try:
            client = AsteriskHttpClient()
            client.login()
            client.originate("Local/066LOGOUT@fts-pausas/n", "ftp-pausas", True,
                             variables, True, aplication='Hangup')

        except AsteriskHttpOriginateError:
            logger.exception("Originate failed - agente: %s ", agente)

        except:
            logger.exception("Originate failed - agente: %s ", agente)

    return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
