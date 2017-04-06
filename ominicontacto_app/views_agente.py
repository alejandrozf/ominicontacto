# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
from django.views.generic import FormView, UpdateView
from django.shortcuts import redirect
from ominicontacto_app.models import AgenteProfile
from ominicontacto_app.forms import ReporteForm
from ominicontacto_app.services.reporte_agente_calificacion import \
    ReporteAgenteService
from ominicontacto_app.services.reporte_agente_venta import \
    ReporteFormularioVentaService
from ominicontacto_app.utiles import convert_fecha_datetime


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


def cambiar_estado_agente_view(request):
    pk_agente = request.GET['pk_agente']
    estado = request.GET['user']
    agente = AgenteProfile.objects.get(pk=int(pk_agente))
    agente.estado = int(estado)
    agente.save()
    response = JsonResponse({'status': 'OK', 'chat': chat.pk})
    return response
