# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime

from django.shortcuts import redirect
from ominicontacto_app.models import Campana, AgenteProfile
from ominicontacto_app.forms import ReporteForm
from django.views.generic import ListView, FormView, UpdateView
from ominicontacto_app.services.reporte_metadata_cliente import \
    ReporteMetadataClienteService
from ominicontacto_app.services.reporte_campana_calificacion import \
    ReporteCampanaService
from ominicontacto_app.services.reporte_campana_pdf import \
    ReporteCampanaPDFService
from ominicontacto_app.services.estadisticas_campana import EstadisticasService
from ominicontacto_app.services.reporte_agente import EstadisticasAgenteService
from ominicontacto_app.utiles import convert_fecha_datetime


class CampanaDialerReporteCalificacionListView(ListView):
    """
    Muestra un listado de contactos a los cuales se los calificaron
    """
    template_name = 'reporte/reporte_campana_formulario.html'
    context_object_name = 'campana'
    model = Campana

    def get_context_data(self, **kwargs):
        context = super(CampanaDialerReporteCalificacionListView, self).get_context_data(
            **kwargs)

        service = ReporteCampanaService()
        service_formulario = ReporteMetadataClienteService()
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        service.crea_reporte_csv(campana)
        service_formulario.crea_reporte_csv(campana)
        context['campana'] = campana
        return context


class CampanaDialerReporteGrafico(FormView):

    template_name = 'campana_dialer/reporte_campana_grafico.html'
    context_object_name = 'campana'
    model = Campana
    form_class = ReporteForm

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get(self, request, *args, **kwargs):
        # obtener_estadisticas_render_graficos_supervision()
        service = EstadisticasService()
        hoy_ahora = datetime.datetime.today()
        hoy = hoy_ahora.date()
        graficos_estadisticas = service.general_campana(self.get_object(), hoy,
                                                        hoy_ahora)
        service_pdf = ReporteCampanaPDFService()
        service_pdf.crea_reporte_pdf(self.get_object(), graficos_estadisticas)
        return self.render_to_response(self.get_context_data(
            graficos_estadisticas=graficos_estadisticas,
            pk_campana=self.kwargs['pk_campana']))

    def get_context_data(self, **kwargs):
        context = super(CampanaDialerReporteGrafico, self).get_context_data(
            **kwargs)

        context['campana'] = self.get_object()
        return context

    def form_valid(self, form):
        fecha = form.cleaned_data.get('fecha')
        fecha_desde, fecha_hasta = fecha.split('-')
        fecha_desde = convert_fecha_datetime(fecha_desde)
        fecha_hasta = convert_fecha_datetime(fecha_hasta)
        # obtener_estadisticas_render_graficos_supervision()
        service = EstadisticasService()
        graficos_estadisticas = service.general_campana(
            self.get_object(), fecha_desde, fecha_hasta)
        service_pdf = ReporteCampanaPDFService()
        service_pdf.crea_reporte_pdf(self.get_object(), graficos_estadisticas)
        return self.render_to_response(self.get_context_data(
            graficos_estadisticas=graficos_estadisticas,
            pk_campana=self.kwargs['pk_campana']))


class ExportaCampanaDialerReportePDFView(UpdateView):
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


class AgenteCampanaDialerReporteGrafico(FormView):

    template_name = 'campana/reporte_agente.html'
    context_object_name = 'campana'
    model = Campana
    form_class = ReporteForm

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get(self, request, *args, **kwargs):
        # obtener_estadisticas_render_graficos_supervision()
        service = EstadisticasAgenteService()
        hoy_ahora = datetime.datetime.today()
        hoy = hoy_ahora.date()
        agente = AgenteProfile.objects.get(pk=self.kwargs['pk_agente'])
        graficos_estadisticas = service.general_campana(agente,
                                                        self.get_object(), hoy,
                                                        hoy_ahora)
        return self.render_to_response(self.get_context_data(
            graficos_estadisticas=graficos_estadisticas))

    def get_context_data(self, **kwargs):
        context = super(AgenteCampanaDialerReporteGrafico, self).get_context_data(
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
        # obtener_estadisticas_render_graficos_supervision()
        service = EstadisticasAgenteService()
        agente = AgenteProfile.objects.get(pk=self.kwargs['pk_agente'])
        graficos_estadisticas = service.general_campana(agente,
                                                        self.get_object(),
                                                        fecha_desde,
                                                        fecha_hasta)
        return self.render_to_response(self.get_context_data(
            graficos_estadisticas=graficos_estadisticas))
