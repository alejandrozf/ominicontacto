# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

"""Vistas genéricas de reportes de campañas"""

from __future__ import unicode_literals

import datetime

from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView, View


from ominicontacto_app.forms import ReporteCampanaForm

from ominicontacto_app.models import AgenteProfile, Campana, RespuestaFormularioGestion

from ominicontacto_app.services.estadisticas_campana import EstadisticasService

from ominicontacto_app.services.reporte_agente import EstadisticasAgenteService
from ominicontacto_app.services.reporte_campana_calificacion import ReporteCampanaService
from ominicontacto_app.services.reporte_campana_pdf import ReporteCampanaPDFService

from ominicontacto_app.utiles import convert_fecha_datetime, fecha_hora_local

from reportes_app.reportes.reporte_llamados_contactados_csv import ExportacionCampanaCSV
from ominicontacto_app.services.reporte_campana_csv import ExportacionArchivoCampanaCSV


class CampanaReporteCalificacionListView(FormView):
    """
    Muestra un listado de contactos a los cuales se los calificaron en la campana
    """
    template_name = 'calificaciones_campana.html'
    context_object_name = 'campana'
    model = Campana
    form_class = ReporteCampanaForm
    campana = None

    def get_object(self, queryset=None):
        if self.campana is None:
            user = self.request.user
            asignadas = Campana.objects.all()
            if not user.get_is_administrador():
                supervisor = user.get_supervisor_profile()
                asignadas = supervisor.campanas_asignadas()
            self.campana = asignadas.get(pk=self.kwargs['pk_campana'])
        return self.campana

    def get(self, request, *args, **kwargs):
        user = request.user
        asignadas = Campana.objects.all()

        if not user.get_is_administrador():
            supervisor = user.get_supervisor_profile()
            asignadas = supervisor.campanas_asignadas_actuales()

        try:
            self.campana = asignadas.get(pk=self.kwargs['pk_campana'])
        except Campana.DoesNotExist:
            messages.warning(self.request, _(u"Usted no puede acceder a esta campaña."))
            return redirect('index')

        return super(CampanaReporteCalificacionListView, self).get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CampanaReporteCalificacionListView, self).get_context_data(
            **kwargs)
        context['campana'] = self.get_object()
        context['calificaciones_task_id'] = get_random_string(8)
        context['formulario_gestion_task_id'] = get_random_string(8)
        return context

    def _procesa_historico_calificaciones(self, historico_calificaciones_qs):
        res = {}
        for hc in list(historico_calificaciones_qs):
            if hc.id not in res:
                res[hc.id] = {}
                res[hc.id]['id'] = hc.id
                res[hc.id]['telefono'] = hc.contacto.telefono
                res[hc.id]['datos'] = hc.contacto.datos
                res[hc.id]['cals'] = {}
                res[hc.id]['calif_actual'] = {}
                res[hc.id]['tiene_historico'] = False

            res[hc.id]['cals'][hc.history_id] = {
                'nombre': hc.opcion_calificacion.nombre,
                'observaciones': hc.observaciones,
                'fecha_hora': timezone.localtime(hc.history_date).strftime("%Y/%m/%d %H:%M:%S"),
                'history_id': hc.history_id,
            }

            if res[hc.id]['calif_actual'] == {}:
                res[hc.id]['calif_actual'] = res[hc.id]['cals'][hc.history_id]
            else:
                res[hc.id]['tiene_historico'] = True

        historico_formulario_gestion = RespuestaFormularioGestion.history.filter(
            calificacion__in=res.keys())

        for gestion in historico_formulario_gestion:
            if gestion.metadata is not None:
                calificacion_historica_id = gestion.history_change_reason
                if calificacion_historica_id is not None and str(calificacion_historica_id).isdigit:
                    try:
                        gestiones_list = res[gestion.calificacion.id]['cals'][int(
                            calificacion_historica_id)]['gestiones']
                    except Exception:
                        gestiones_list = []
                    gestiones_list.append(gestion.metadata.replace('\r\n', ' '))
                    res[gestion.calificacion.id]['cals'][int(calificacion_historica_id)].update({
                        'gestiones': gestiones_list
                    })
                    res[gestion.calificacion.id]['tiene_historico'] = True
        return res

    def form_valid(self, form):
        fecha = form.cleaned_data.get('fecha')
        fecha_desde, fecha_hasta = fecha.split('-')
        fecha_desde = convert_fecha_datetime(fecha_desde)
        fecha_hasta = convert_fecha_datetime(fecha_hasta)
        service = ReporteCampanaService(self.get_object())
        service.calificaciones_por_fechas(fecha_desde, fecha_hasta)
        calificaciones_qs = service.calificaciones_qs
        historico_calificaciones_qs = service.historico_calificaciones_qs
        historico_calidficaciones = self._procesa_historico_calificaciones(
            historico_calificaciones_qs)
        return self.render_to_response(self.get_context_data(
            calificaciones=calificaciones_qs,
            historico_calificaciones=historico_calidficaciones.values(),
            reporte_fecha_desde_elegida=fecha_desde.strftime("%m/%d/%Y"),
            reporte_fecha_hasta_elegida=fecha_hasta.strftime("%m/%d/%Y"),
            pk_campana=self.kwargs['pk_campana']
        ))


class ExportaCampanaReporteCalificacionView(View):
    """
    Esta vista invoca a generar un csv de reporte de la campana.
    """

    model = Campana
    context_object_name = 'campana'

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        service = ExportacionArchivoCampanaCSV(self.object, "calificados")
        url = service.obtener_url_reporte_csv_descargar()
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
        service = ExportacionArchivoCampanaCSV(self.object, "formulario_gestion")
        url = service.obtener_url_reporte_csv_descargar()
        return redirect(url)


class CampanaReporteGraficoView(FormView):
    """Esta vista genera el reporte grafico de la campana"""

    context_object_name = 'campana'
    model = Campana
    form_class = ReporteCampanaForm
    template_name = 'reporte_grafico_campana.html'

    campana = None

    def get_object(self, queryset=None):
        if self.campana is None:
            user = self.request.user
            asignadas = Campana.objects.all()

            if not user.get_is_administrador():
                supervisor = user.get_supervisor_profile()
                asignadas = supervisor.campanas_asignadas()
            self.campana = asignadas.filter(
                pk=self.kwargs['pk_campana']).select_related('bd_contacto').first()
        return self.campana

    def get(self, request, *args, **kwargs):
        campana = self.get_object()
        if not campana:
            messages.warning(self.request, _(u"Usted no puede acceder a esta campaña."))
            return redirect('index')
        hoy_ahora = fecha_hora_local(timezone.now())
        hoy = hoy_ahora.date()
        fecha_desde = fecha_hora_local(datetime.datetime.combine(hoy, datetime.time.min))
        fecha_hasta = fecha_hora_local(datetime.datetime.combine(hoy_ahora, datetime.time.max))
        service = EstadisticasService(campana, fecha_desde, fecha_hasta)
        # genera los reportes grafico de la campana
        graficos_estadisticas = service.general_campana()
        # generar el reporte pdf
        service_pdf = ReporteCampanaPDFService()
        service_pdf.crea_reporte_pdf(campana, graficos_estadisticas)
        return self.render_to_response(self.get_context_data(
            graficos_estadisticas=graficos_estadisticas,
            pk_campana=self.kwargs['pk_campana']))

    def get_context_data(self, **kwargs):
        context = super(CampanaReporteGraficoView, self).get_context_data(
            **kwargs)
        self.campana = self.get_object()
        context['campana'] = self.campana
        context['campana_entrante'] = (self.campana.type == Campana.TYPE_ENTRANTE)
        context['task_id'] = get_random_string(8)
        return context

    def form_valid(self, form):
        campana = self.get_object()
        fecha = form.cleaned_data.get('fecha')
        fecha_desde, fecha_hasta = fecha.split('-')
        fecha_desde = convert_fecha_datetime(fecha_desde)
        fecha_hasta = convert_fecha_datetime(fecha_hasta)
        fecha_desde = datetime.datetime.combine(fecha_desde, datetime.time.min)
        fecha_hasta = datetime.datetime.combine(fecha_hasta, datetime.time.max)
        # generar el reporte grafico de acuerdo al periodo de fecha seleccionado
        service = EstadisticasService(campana, fecha_desde, fecha_hasta)
        graficos_estadisticas = service.general_campana()
        # genera el reporte pdf de la campana
        service_pdf = ReporteCampanaPDFService()
        service_pdf.crea_reporte_pdf(campana, graficos_estadisticas)
        return self.render_to_response(self.get_context_data(
            graficos_estadisticas=graficos_estadisticas,
            reporte_fecha_desde_elegida=fecha_desde.strftime("%m/%d/%Y"),
            reporte_fecha_hasta_elegida=fecha_hasta.strftime("%m/%d/%Y"),
            pk_campana=self.kwargs['pk_campana']))


class ExportaCampanaReporteGraficoPDFView(View):
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


class ExportaReporteLlamadosContactadosView(View):
    """
    Esta vista invoca a generar un csv de reporte de la campana.
    """

    model = Campana
    context_object_name = 'campana'

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        service_csv = ExportacionCampanaCSV()
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
        service_csv = ExportacionCampanaCSV()
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
        service_csv = ExportacionCampanaCSV()
        url = service_csv.obtener_url_reporte_csv_descargar(
            self.object, "calificados")

        return redirect(url)


class AgenteCampanaReporteGrafico(FormView):
    """Esta vista genera el reporte grafico de la campana para un agente"""
    template_name = 'reporte_agente.html'
    form_class = ReporteCampanaForm

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
