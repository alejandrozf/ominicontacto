# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.views.generic import FormView
from ominicontacto_app.models import AgenteProfile, Grupo
from reportes_app.forms import ReporteAgentesForm
from ominicontacto_app.utiles import convert_fecha_datetime
from reportes_app.reporte_agente_tiempos import TiemposAgente


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
        return self.render_to_response(self.get_context_data(
            graficos_estadisticas=graficos_estadisticas))
