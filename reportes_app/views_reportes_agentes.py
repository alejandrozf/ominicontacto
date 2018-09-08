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

from django.template import loader
from django.http import JsonResponse
from django.views.generic import FormView
from django.shortcuts import redirect, render
from ominicontacto_app.models import AgenteProfile, Grupo
from reportes_app.forms import ReporteAgentesForm
from ominicontacto_app.utiles import convert_fecha_datetime
from reportes_app.reporte_agente_tiempos import TiemposAgente
from reportes_app.reporte_agente_tiempos_csv import ReporteAgenteCSVService


class ReportesTiemposAgente(FormView):
    """
    Esta vista lista los tiempos de los agentes

    """

    template_name = 'reportes_agentes_tiempos.html'
    context_object_name = 'agentes'
    model = AgenteProfile
    form_class = ReporteAgentesForm

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
            for agente_pk in agentes_pk:
                agente = AgenteProfile.objects.get(pk=agente_pk)
                agentes.append(agente)
        if grupo_id:
            grupo = Grupo.objects.get(pk=int(grupo_id))
            agentes = grupo.agentes.filter(is_inactive=False)

        if todos_agentes:
            agentes = []

        # generamos los reportes graficos
        tiempos_agentes = TiemposAgente()
        graficos_estadisticas = tiempos_agentes.generar_reportes(
            agentes, fecha_desde, fecha_hasta, self.request.user)
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
            pausa_id = int(request.POST['pausa_id'])
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
                'pausa': pausa['nombre']
                  }
            return JsonResponse(data, safe=True)

    return render(request)
