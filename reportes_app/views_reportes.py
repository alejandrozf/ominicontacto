# -*- coding: utf-8 -*-

"""Vistas genéricas de reportes de campañas"""

from __future__ import unicode_literals

import datetime

from django.shortcuts import redirect
from django.views.generic import FormView, ListView, View
from django.utils import timezone

from ominicontacto_app.forms import ReporteForm
from ominicontacto_app.models import Campana, AgenteProfile
from ominicontacto_app.services.estadisticas_campana import EstadisticasService
from ominicontacto_app.services.reporte_agente import EstadisticasAgenteService
from ominicontacto_app.services.reporte_campana_calificacion import ReporteCampanaService
from ominicontacto_app.services.reporte_campana_pdf import ReporteCampanaPDFService
from ominicontacto_app.services.reporte_llamados_contactados_csv import ReporteCampanaContactadosCSV
from ominicontacto_app.services.reporte_metadata_cliente import ReporteMetadataClienteService
from ominicontacto_app.utiles import convert_fecha_datetime


class CampanaReporteCalificacionListView(ListView):
    """
    Muestra un listado de contactos a los cuales se los calificaron en la campana
    """
    template_name = 'calificaciones_campana.html'
    context_object_name = 'campana'
    model = Campana

    def get_context_data(self, **kwargs):
        context = super(CampanaReporteCalificacionListView, self).get_context_data(
            **kwargs)

        service = ReporteCampanaService()
        service_formulario = ReporteMetadataClienteService()
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        service.crea_reporte_csv(campana)
        service_formulario.crea_reporte_csv(campana)
        context['campana'] = campana
        return context


class ExportaReporteCampanaView(View):
    """
    Esta vista invoca a generar un csv de reporte de la campana.
    """

    model = Campana
    context_object_name = 'campana'

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        service = ReporteCampanaService()
        url = service.obtener_url_reporte_csv_descargar(self.object)

        return redirect(url)


class ExportaReporteFormularioVentaView(View):
    """
    Esta vista invoca a generar un csv de reporte de la la venta.
    """

    model = Campana
    context_object_name = 'campana'

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        service = ReporteMetadataClienteService()
        url = service.obtener_url_reporte_csv_descargar(self.object)

        return redirect(url)


class CampanaReporteGraficoView(FormView):
    """Esta vista genera el reporte grafico de la campana"""

    context_object_name = 'campana'
    model = Campana
    form_class = ReporteForm
    template_name = 'reporte_grafico_campana.html'

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get(self, request, *args, **kwargs):
        service = EstadisticasService()
        hoy_ahora = timezone.now()
        hoy = hoy_ahora.date()
        # genera reporte de llamadas contactados
        calificados_csv = ReporteCampanaContactadosCSV()
        calificados_csv.crea_reporte_csv(self.get_object(), hoy, hoy_ahora)
        # genera los reportes grafico de la campana
        graficos_estadisticas = service.general_campana(self.get_object(), hoy, hoy_ahora)
        # generar el reporte pdf
        service_pdf = ReporteCampanaPDFService()
        service_pdf.crea_reporte_pdf(self.get_object(), graficos_estadisticas)
        return self.render_to_response(self.get_context_data(
            graficos_estadisticas=graficos_estadisticas,
            pk_campana=self.kwargs['pk_campana']))

    def get_context_data(self, **kwargs):
        context = super(CampanaReporteGraficoView, self).get_context_data(
            **kwargs)

        context['campana'] = self.get_object()
        return context

    def form_valid(self, form):
        fecha = form.cleaned_data.get('fecha')
        fecha_desde, fecha_hasta = fecha.split('-')
        fecha_desde = convert_fecha_datetime(fecha_desde)
        fecha_hasta = convert_fecha_datetime(fecha_hasta)
        # genera reporte de llamadas contactados
        calificados_csv = ReporteCampanaContactadosCSV()
        calificados_csv.crea_reporte_csv(self.get_object(), fecha_desde, fecha_hasta)
        # generar el reporte grafico de acuerdo al periodo de fecha seleccionado
        service = EstadisticasService()
        graficos_estadisticas = service.general_campana(self.get_object(), fecha_desde, fecha_hasta)
        # genera el reporte pdf de la campana
        service_pdf = ReporteCampanaPDFService()
        service_pdf.crea_reporte_pdf(self.get_object(), graficos_estadisticas)
        return self.render_to_response(self.get_context_data(
            graficos_estadisticas=graficos_estadisticas,
            pk_campana=self.kwargs['pk_campana']))


class ExportaCampanaReportePDFView(View):
    """
    Esta vista invoca a generar un pdf de reporte de la campana
    """

    model = Campana
    context_object_name = 'campana'

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        service = ReporteCampanaPDFService()
        url = service.obtener_url_reporte_pdf_descargar(self.object)
        return redirect(url)


class ExportaReporteContactadosView(View):
    """
    Esta vista invoca a generar un csv de reporte de la campana.
    """

    model = Campana
    context_object_name = 'campana'

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        service_csv = ReporteCampanaContactadosCSV()
        url = service_csv.obtener_url_reporte_csv_descargar(
            self.object, "contactados")

        return redirect(url)


class ExportaReporteNoAtendidosView(View):
    """
    Esta vista invoca a generar un csv de reporte de la campana.
    """

    model = Campana
    context_object_name = 'campana'

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        service_csv = ReporteCampanaContactadosCSV()
        url = service_csv.obtener_url_reporte_csv_descargar(
            self.object, "no_atendidos")

        return redirect(url)


class ExportaReporteCalificadosView(View):
    """
    Esta vista invoca a generar un csv de reporte de la campana.
    """

    model = Campana
    context_object_name = 'campana'

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        service_csv = ReporteCampanaContactadosCSV()
        url = service_csv.obtener_url_reporte_csv_descargar(
            self.object, "calificados")

        return redirect(url)


class AgenteCampanaReporteGrafico(FormView):
    """Esta vista genera el reporte grafico de la campana para un agente"""
    template_name = 'reporte_agente.html'
    form_class = ReporteForm

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get(self, request, *args, **kwargs):
        service = EstadisticasAgenteService()
        hoy_ahora = datetime.datetime.today()
        hoy = hoy_ahora.date()
        agente = AgenteProfile.objects.get(pk=self.kwargs['pk_agente'])
        # generar el reporte para el agente de la campana
        graficos_estadisticas = service.general_campana(agente,
                                                        self.get_object(), hoy,
                                                        hoy_ahora)
        return self.render_to_response(self.get_context_data(
            graficos_estadisticas=graficos_estadisticas))

    def get_context_data(self, **kwargs):
        context = super(AgenteCampanaReporteGrafico, self).get_context_data(
            **kwargs)

        agente = AgenteProfile.objects.get(pk=self.kwargs['pk_agente'])
        context['pk_campana'] = self.kwargs['pk_campana']

        context['agente'] = agente
        return context

    def form_valid(self, form):
        fecha = form.cleaned_data.get('fecha')
        fecha_desde, fecha_hasta = fecha.split('-')
        fecha_desde = convert_fecha_datetime(fecha_desde)
        fecha_hasta = convert_fecha_datetime(fecha_hasta)
        # genera el reporte para el agente de esta campana
        service = EstadisticasAgenteService()
        agente = AgenteProfile.objects.get(pk=self.kwargs['pk_agente'])
        graficos_estadisticas = service.general_campana(agente,
                                                        self.get_object(),
                                                        fecha_desde,
                                                        fecha_hasta)
        return self.render_to_response(self.get_context_data(
            graficos_estadisticas=graficos_estadisticas))
