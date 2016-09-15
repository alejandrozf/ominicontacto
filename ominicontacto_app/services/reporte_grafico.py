# -*- coding: utf-8 -*-

import pygal
from pygal.style import Style, RedBlueStyle

from ominicontacto_app.models import Grabacion
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


class GraficoService():

    def _obtener_total_llamdas_tipo(self, listado_grabaciones):
        counter_por_tipo = {
            Grabacion.TYPE_DIALER: 0,
            Grabacion.TYPE_ICS: 0,
            Grabacion.TYPE_INBOUND: 0,
            Grabacion.TYPE_MANUAL: 0,
        }

        tipos_llamadass = (Grabacion.TYPE_DIALER, Grabacion.TYPE_INBOUND,
                           Grabacion.TYPE_ICS, Grabacion.TYPE_MANUAL)

        for grabacion in listado_grabaciones:
            if grabacion.tipo_llamada in tipos_llamadass:
                counter_por_tipo[grabacion.tipo_llamada] += 1

        return counter_por_tipo

    def _calcular_estadisticas(self, grabaciones):
        counter_tipo_llamada = self._obtener_total_llamdas_tipo(grabaciones)

        total_grabaciones = len(grabaciones)

        porcentaje_dialer = 0.0
        porcentaje_ics = 0.0
        porcentaje_inbound = 0.0
        porcentaje_manual = 0.0
        if total_grabaciones > 0:
            porcentaje_dialer = (100.0 * float(counter_tipo_llamada[Grabacion.TYPE_DIALER]) /
                float(total_grabaciones))
            porcentaje_ics = (100.0 * float(counter_tipo_llamada[Grabacion.TYPE_ICS]) /
                float(total_grabaciones))
            porcentaje_inbound = (100.0 * float(counter_tipo_llamada[Grabacion.TYPE_INBOUND]) /
                float(total_grabaciones))
            porcentaje_manual = (100.0 * float(counter_tipo_llamada[Grabacion.TYPE_MANUAL]) /
                float(total_grabaciones))

        total_dialer = counter_tipo_llamada[Grabacion.TYPE_DIALER]
        total_ics = counter_tipo_llamada[Grabacion.TYPE_ICS]
        total_inbound = counter_tipo_llamada[Grabacion.TYPE_INBOUND]
        total_manual = counter_tipo_llamada[Grabacion.TYPE_MANUAL]
        dic_estadisticas = {
            'porcentaje_dialer': porcentaje_dialer,
            'porcentaje_ics': porcentaje_ics,
            'porcentaje_inbound': porcentaje_inbound,
            'porcentaje_manual': porcentaje_manual,
            'total_grabaciones': total_grabaciones,
            'total_dialer': total_dialer,
            'total_ics': total_ics,
            'total_inbound': total_inbound,
            'total_manual': total_manual,
        }
        return dic_estadisticas

    def general_llamadas_hoy(self, grabaciones):

        estadisticas = self._calcular_estadisticas(grabaciones)

        if estadisticas:
            logger.info("Generando grafico para grabaciones de llamadas ")

        no_data_text = "No hay llamadas para ese periodo"
        torta_grabaciones = pygal.Pie(# @UndefinedVariable
                style=ESTILO_AZUL_ROJO_AMARILLO,
                no_data_text=no_data_text,
                no_data_font_size=32,
                legend_font_size=25,
                truncate_legend=10,
                tooltip_font_size=50,
            )

        #torta_grabaciones.title = "Resultado de las llamadas"
        torta_grabaciones.add('Dialer', estadisticas['porcentaje_dialer'])
        torta_grabaciones.add('Inbound', estadisticas['porcentaje_ics'])
        torta_grabaciones.add('Ics', estadisticas['porcentaje_inbound'])
        torta_grabaciones.add('Manual', estadisticas['porcentaje_manual'])
        return {
            'estadisticas': estadisticas,
            'torta_grabaciones': torta_grabaciones,
        }
