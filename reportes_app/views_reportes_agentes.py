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

from __future__ import unicode_literals

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template import loader
from django.utils.timezone import now
from django.views.generic import FormView, TemplateView

from ominicontacto_app.models import AgenteProfile, Grupo
from ominicontacto_app.utiles import convert_fecha_datetime, fecha_local

from reportes_app.forms import ReporteAgentesForm
from reportes_app.models import LlamadaLog
from reportes_app.reportes.reporte_agente_tiempos import TiemposAgente
from reportes_app.reportes.reporte_agente_tiempos_csv import ReporteAgenteCSVService
from reportes_app.reportes.reporte_agentes import ReporteAgentes


class ReportesTiemposAgente(FormView):
    """
    Esta vista lista los tiempos de los agentes

    """

    template_name = 'reportes_agentes_tiempos.html'
    context_object_name = 'agentes'
    model = AgenteProfile
    form_class = ReporteAgentesForm

    def get_form_kwargs(self):
        kwargs = super(ReportesTiemposAgente, self).get_form_kwargs()
        supervisor = self.request.user.get_supervisor_profile()
        if supervisor:
            agentes_asociados = AgenteProfile.objects.obtener_agentes_supervisor(
                supervisor).select_related('user')
            kwargs['agentes_asociados'] = agentes_asociados
            id_grupos = agentes_asociados.values_list('grupo_id', flat=True)
            kwargs['grupos_asociados'] = Grupo.objects.filter(id__in=id_grupos)
        else:
            kwargs['agentes_asociados'] = AgenteProfile.objects.filter(
                is_inactive=False).select_related('user')
            kwargs['grupos_asociados'] = Grupo.objects.all()

        return kwargs

    def form_valid(self, form):
        fecha = form.cleaned_data.get('fecha')
        fecha_desde, fecha_hasta = fecha.split('-')
        fecha_desde = convert_fecha_datetime(fecha_desde)
        fecha_hasta = convert_fecha_datetime(fecha_hasta)
        grupo_id = form.cleaned_data.get('grupo_agente')
        agentes_pk = form.cleaned_data.get('agente')
        todos_agentes = form.cleaned_data.get('todos_agentes')

        agentes = []
        if agentes_pk:
            agentes = AgenteProfile.objects.filter(pk__in=agentes_pk)
        if grupo_id:
            grupo = Grupo.objects.get(pk=int(grupo_id))
            agentes = grupo.agentes.filter(is_inactive=False)

        if todos_agentes or (agentes == [] and not grupo_id):
            supervisor = self.request.user.get_supervisor_profile()
            if supervisor:
                agentes = AgenteProfile.objects.obtener_agentes_supervisor(
                    supervisor)
            else:
                # Asumo es Administrador
                agentes = AgenteProfile.objects.obtener_activos()

        agentes = agentes.select_related('user')

        # generamos los reportes graficos
        reporte_tiempos = ReporteAgentes(self.request.user)
        graficos_estadisticas = reporte_tiempos.devuelve_reporte_agentes(
            agentes, fecha_desde, fecha_hasta)
        # generar reporte csv
        reporte_csv = ReporteAgenteCSVService()
        reporte_csv.crea_reporte_csv(graficos_estadisticas)

        return self.render_to_response(self.get_context_data(
            graficos_estadisticas=graficos_estadisticas))


def exporta_reporte_agente_llamada_view(request, tipo_reporte):
    """
    Esta vista invoca a generar un csv de reporte de los tiempos del agente
    """
    service = ReporteAgenteCSVService()
    url = service.obtener_url_reporte_csv_descargar(tipo_reporte)
    return redirect(url)


def reporte_por_fecha_modal_agente_view(request):
    """esta vista es invocada por una ajax para mostrar los datos por fechas
    de los agentes en una ventana modal"""
    if request.method == 'POST':
        if request.is_ajax():
            id_agente = request.POST['id_agente']
            fecha_desde = request.POST['fecha_desde']
            fecha_hasta = request.POST['fecha_hasta']
            fecha_desde = convert_fecha_datetime(fecha_desde)
            fecha_hasta = convert_fecha_datetime(fecha_hasta)

            tiempos_agentes = TiemposAgente()
            agente = AgenteProfile.objects.get(pk=int(id_agente))
            agentes, error = tiempos_agentes.generar_por_fecha_agente(
                agente, fecha_desde, fecha_hasta)
            ctx = {'agentes': agentes}
            t = loader.get_template('tbody_fechas_agentes.html')
            html = t.render(ctx)
            data = {
                'nombre_agente': agente.user.get_full_name(),
                'tbody': html,
                'error': error
            }
            return JsonResponse(data, safe=True)

    return render(request)


def reporte_por_fecha_pausa_modal_agente_view(request):
    """esta vista es invocada por una ajax para mostrar las pausas por fechas
    de los agentes en una ventana modal"""
    if request.method == 'POST':
        if request.is_ajax():

            id_agente = request.POST['id_agente']
            fecha_desde = request.POST['fecha_desde']
            fecha_hasta = request.POST['fecha_hasta']
            fecha_desde = convert_fecha_datetime(fecha_desde)
            fecha_hasta = convert_fecha_datetime(fecha_hasta)
            pausa_id = request.POST['pausa_id']
            tiempos_agentes = TiemposAgente()
            pausa = tiempos_agentes._obtener_datos_de_pausa(pausa_id)
            agente = AgenteProfile.objects.get(pk=int(id_agente))
            agentes = tiempos_agentes.calcular_tiempo_pausa_tipo_fecha(
                agente, fecha_desde, fecha_hasta, pausa_id)
            ctx = {'agentes': agentes}
            t = loader.get_template('tbody_pausa_fechas_agentes.html')
            html = t.render(ctx)
            data = {
                'nombre_agente': agente.user.get_full_name(),
                'tbody': html,
                'pausa': pausa['nombre']}
            return JsonResponse(data, safe=True)

    return render(request)


class HistoricoDeLlamadasView(TemplateView):
    """
    Devuelve el html del las llamadas del día para el agente
    """
    template_name = 'agente/historico_llamadas_del_dia.html'

    def get_context_data(self, *args, **kwargs):
        context = super(HistoricoDeLlamadasView, self).get_context_data(*args, **kwargs)
        agente_profile = self.request.user.get_agente_profile()
        hoy = fecha_local(now())
        logs = LlamadaLog.objects.obtener_llamadas_finalizadas_del_dia(agente_profile.id, hoy)
        context['registros'] = logs
        context['tipos_salientes'] = LlamadaLog.TIPOS_LLAMADAS_SALIENTES
        return context
