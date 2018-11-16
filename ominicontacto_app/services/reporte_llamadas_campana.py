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

"""Servicio para generar reportes de las llamadas por campañas"""

import pygal

from pygal.style import Style
from ominicontacto_app.models import Campana


import logging as _logging

logger = _logging.getLogger(__name__)


ESTILO_AZUL_ROJO_AMARILLO = Style(
    background='transparent',
    plot_background='transparent',
    foreground='#555',
    foreground_light='#555',
    foreground_dark='#555',
    opacity='1',
    opacity_hover='.6',
    transition='400ms ease-in',
    colors=('#428bca', '#5cb85c', '#5bc0de', '#f0ad4e', '#d9534f',
            '#a95cb8', '#5cb8b5', '#caca43', '#96ac43', '#ca43ca')
)


class EstadisticasCampanaLlamadasService():

    def _calcular_estadisticas(self, fecha_inferior, fecha_superior, user):

        campanas = Campana.objects.obtener_all_dialplan_asterisk()
        if not user.get_is_administrador():
            campanas = Campana.objects.obtener_campanas_vista_by_user(campanas, user)

        queues_llamadas, totales_grafico = self.calcular_cantidad_llamadas(
            campanas, fecha_inferior, fecha_superior)

        total_llamadas = self.obtener_total_llamadas(fecha_inferior, fecha_superior)

        dic_estadisticas = {
            'queues_llamadas': queues_llamadas,
            'fecha_desde': fecha_inferior,
            'fecha_hasta': fecha_superior,
            'total_llamadas': total_llamadas,
            'totales_grafico': totales_grafico,

        }
        return dic_estadisticas

    def general_campana(self, fecha_inferior, fecha_superior, user):
        estadisticas = self._calcular_estadisticas(fecha_inferior,
                                                   fecha_superior, user)

        if estadisticas:
            logger.info("Generando grafico calificaciones de campana por cliente ")

        # Barra: Cantidad de llamadas por campana
        barra_campana_llamadas = pygal.Bar(  # @UndefinedVariable
            show_legend=False,
            style=ESTILO_AZUL_ROJO_AMARILLO)
        # barra_campana_llamadas.title = 'Distribucion por campana'

        barra_campana_llamadas.x_labels = \
            estadisticas['totales_grafico']['nombres_queues']
        barra_campana_llamadas.add('atendidas',
                                   estadisticas['totales_grafico']['total_atendidas'])
        barra_campana_llamadas.add('abandonadas ',
                                   estadisticas['totales_grafico']['total_abandonadas'])
        barra_campana_llamadas.add('expiradas',
                                   estadisticas['totales_grafico']['total_expiradas'])

        return {
            'estadisticas': estadisticas,
            'barra_campana_llamadas': barra_campana_llamadas,

        }
