# -*- coding: utf-8 -*-

import pygal
import datetime
from pygal.style import Style, RedBlueStyle

from ominicontacto_app.models import Grabacion, AgenteProfile
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

    def _obtener_campana_grabacion(self, fecha_inferior, fecha_superior):
        # lista de dict con la cantidad de cada campana
        fecha_inferior = datetime.datetime.combine(fecha_inferior,
                                                   datetime.time.min)
        fecha_superior = datetime.datetime.combine(fecha_superior,
                                                   datetime.time.max)
        dict_campana = Grabacion.objects.obtener_count_campana().filter(
            fecha__range=(fecha_inferior, fecha_superior))
        campana = []
        campana_nombre = []

        for campana_id in dict_campana:
            campana.append(campana_id['campana'])
            campana_nombre.append(campana_id['campana__nombre'])
        return dict_campana, campana, campana_nombre

    def _obtener_total_campana_grabacion(self, dict_campana, campana):

        total_campana = []

        for campana_unit, campana in zip(dict_campana, campana):
            if campana_unit['campana'] == campana:
                total_campana.append(campana_unit['cantidad'])
            else:
                total_campana.append(0)

        return total_campana

    def _obtener_total_ics_grabacion(self, dict_campana, campana):

        total_ics = []

        for campana_id in campana:
            cantidad = 0
            result = dict_campana.filter(tipo_llamada=Grabacion.TYPE_ICS).\
                filter(campana=campana_id)
            if result:
                cantidad = result[0]['cantidad']

            total_ics.append(cantidad)

        return total_ics

    def _obtener_total_dialer_grabacion(self, dict_campana, campana):

        total_dialer = []

        for campana_id in campana:
            cantidad = 0
            result = dict_campana.filter(tipo_llamada=Grabacion.TYPE_DIALER).\
                filter(campana=campana_id)
            if result:
                cantidad = result[0]['cantidad']

            total_dialer.append(cantidad)

        return total_dialer

    def _obtener_total_inbound_grabacion(self, dict_campana, campana):

        total_inbound = []
        for campana_id in campana:
            cantidad = 0
            result = dict_campana.filter(tipo_llamada=Grabacion.TYPE_INBOUND).\
                filter(campana=campana_id)
            if result:
                cantidad = result[0]['cantidad']

            total_inbound.append(cantidad)
        return total_inbound

    def _obtener_total_manual_grabacion(self, dict_campana, campana):

        total_manual = []

        for campana_id in campana:
            cantidad = 0
            result = dict_campana.filter(tipo_llamada=Grabacion.TYPE_MANUAL).\
                filter(campana=campana_id)
            if result:
                cantidad = result[0]['cantidad']

            total_manual.append(cantidad)

        return total_manual

    def _obtener_agente_grabacion(self, fecha_inferior, fecha_superior):
        # lista de dict con la cantidad de cada campana
        dict_agentes = Grabacion.objects.obtener_count_agente().filter(
            fecha__range=(fecha_inferior, fecha_superior))
        agentes = []
        sip_agentes = []

        for sip_agente in dict_agentes:
            sip_agentes.append(sip_agente['sip_agente'])
            try:
                agente = AgenteProfile.objects.get(sip_extension=sip_agente['sip_agente'])
                agentes.append(agente.user.get_full_name())
            except AgenteProfile.DoesNotExist:
                agentes.append(sip_agente['sip_agente'])

        return dict_agentes, agentes, sip_agentes

    def _obtener_total_agente_grabacion(self, dict_agentes, agentes):

        total_agentes = []

        for agente_unit, agente in zip(dict_agentes, agentes):
            if agente_unit['sip_agente'] == agente:
                total_agentes.append(agente_unit['cantidad'])
            else:
                total_agentes.append(0)

        return total_agentes

    def _obtener_total_ics_agente(self, dict_agentes, agentes):

        total_ics = []

        for agente in agentes:
            cantidad = 0
            result = dict_agentes.filter(tipo_llamada=Grabacion.TYPE_ICS).\
                filter(sip_agente=agente)
            if result:
                cantidad = result[0]['cantidad']

            total_ics.append(cantidad)

        return total_ics

    def _obtener_total_dialer_agente(self, dict_agentes, agentes):

        total_dialer = []

        for agente in agentes:
            cantidad = 0
            result = dict_agentes.filter(tipo_llamada=Grabacion.TYPE_DIALER). \
                filter(sip_agente=agente)
            if result:
                cantidad = result[0]['cantidad']

            total_dialer.append(cantidad)

        return total_dialer

    def _obtener_total_inbound_agente(self, dict_agentes, agentes):

        total_inbound = []
        for agente in agentes:
            cantidad = 0
            result = dict_agentes.filter(tipo_llamada=Grabacion.TYPE_INBOUND). \
                filter(sip_agente=agente)
            if result:
                cantidad = result[0]['cantidad']

            total_inbound.append(cantidad)
        return total_inbound

    def _obtener_total_manual_agente(self, dict_agentes, agentes):

        total_manual = []

        for agente in agentes:
            cantidad = 0
            result = dict_agentes.filter(tipo_llamada=Grabacion.TYPE_MANUAL). \
                filter(sip_agente=agente)
            if result:
                cantidad = result[0]['cantidad']

            total_manual.append(cantidad)

        return total_manual

    def _obtener_total_llamadas_campana_inbound(self, fecha_inferior,
                                                fecha_superior):
        # lista de dict con la cantidad de cada campana
        dict_campana = Grabacion.objects.obtener_count_campana().filter(
            fecha__range=(fecha_inferior, fecha_superior)).filter(
            tipo_llamada=3)
        list_campana = []
        list_cantidad = []
        for campana_counter in dict_campana:
             list_campana.append(campana_counter['campana__nombre'])
             list_cantidad.append(campana_counter['cantidad'])
        return list_campana, list_cantidad

    def _obtener_total_llamadas_agente_inbound(self, fecha_inferior,
                                                fecha_superior):
        # lista de dict con la cantidad de cada agente
        dict_agentes = Grabacion.objects.obtener_count_agente().filter(
            fecha__range=(fecha_inferior, fecha_superior)).filter(
            tipo_llamada=3)
        list_agente = []
        list_cantidad = []
        for agente_counter in dict_agentes:
            list_agente.append(agente_counter['sip_agente'])
            list_cantidad.append(agente_counter['cantidad'])
        return list_agente, list_cantidad

    def _calcular_estadisticas(self, fecha_inferior, fecha_superior):
        grabaciones = Grabacion.objects.grabacion_by_fecha_intervalo(fecha_inferior,
                                                                     fecha_superior)
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

        dict_campana, campana, campana_nombre = self._obtener_campana_grabacion(fecha_inferior, fecha_superior)
        total_campana = self._obtener_total_campana_grabacion(dict_campana, campana)
        total_grabacion_ics = self._obtener_total_ics_grabacion(dict_campana,
                                                              campana)
        total_grabacion_dialer = self._obtener_total_dialer_grabacion(dict_campana,
                                                              campana)
        total_grabacion_inbound = self._obtener_total_inbound_grabacion(dict_campana,
                                                              campana)
        total_grabacion_manual = self._obtener_total_manual_grabacion(dict_campana,
                                                              campana)
        dict_agentes, agentes_nombre, agentes = self._obtener_agente_grabacion(fecha_inferior, fecha_superior)

        total_agentes = self._obtener_total_agente_grabacion(dict_agentes, agentes)
        total_agente_ics = self._obtener_total_ics_agente(dict_agentes, agentes)
        total_agente_dialer = self._obtener_total_dialer_agente(dict_agentes, agentes)
        total_agente_inbound = self._obtener_total_inbound_agente(dict_agentes, agentes)
        total_agente_manual = self._obtener_total_manual_agente(dict_agentes, agentes)

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
            'campana_nombre': campana_nombre,
            'campana': campana,
            'total_campana': total_campana,
            'total_grabacion_ics': total_grabacion_ics,
            'total_grabacion_dialer': total_grabacion_dialer,
            'total_grabacion_inbound': total_grabacion_inbound,
            'total_grabacion_manual': total_grabacion_manual,
            'agentes': agentes,
            'agentes_nombre': agentes_nombre,
            'total_agentes': total_agentes,
            'total_agente_ics': total_agente_ics,
            'total_agente_dialer': total_agente_dialer,
            'total_agente_inbound': total_agente_inbound,
            'total_agente_manual': total_agente_manual,
        }
        return dic_estadisticas

    def general_llamadas_hoy(self, fecha_inferior, fecha_superior):
        estadisticas = self._calcular_estadisticas(fecha_inferior,
                                                   fecha_superior)

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

        # Barra: Total de llamados atendidos en cada intento por campana.
        barra_campana_total = pygal.Bar(  # @UndefinedVariable
            show_legend=False,
            style=ESTILO_AZUL_ROJO_AMARILLO)
        barra_campana_total.title = 'Cantidad de llamadas de las campana por tipo de llamadas'

        barra_campana_total.x_labels = estadisticas['campana_nombre']
        barra_campana_total.add('ICS',
                                estadisticas['total_grabacion_ics'])
        barra_campana_total.add('DIALER',
                                estadisticas['total_grabacion_dialer'])
        barra_campana_total.add('INBOUND',
                                estadisticas['total_grabacion_inbound'])
        barra_campana_total.add('MANUAL',
                                estadisticas['total_grabacion_manual'])

        # Barra: Total de llamados atendidos en cada intento por agente.
        barra_agente_total = pygal.Bar(  # @UndefinedVariable
            show_legend=False,
            style=ESTILO_AZUL_ROJO_AMARILLO)
        barra_agente_total.title = 'Cantidad de llamadas de los agentes por tipo de llamadas'

        barra_agente_total.x_labels = estadisticas['agentes_nombre']
        barra_agente_total.add('ICS',
                                estadisticas['total_agente_ics'])
        barra_agente_total.add('DIALER',
                                estadisticas['total_agente_dialer'])
        barra_agente_total.add('INBOUND',
                                estadisticas['total_agente_inbound'])
        barra_agente_total.add('MANUAL',
                                estadisticas['total_agente_manual'])

        return {
            'estadisticas': estadisticas,
            'torta_grabaciones': torta_grabaciones,
            'dict_campana_counter': zip(estadisticas['campana_nombre'],
                                        estadisticas['total_campana'],
                                        estadisticas['total_grabacion_ics'],
                                        estadisticas['total_grabacion_dialer'],
                                        estadisticas['total_grabacion_inbound'],
                                        estadisticas['total_grabacion_manual']),
            'barra_campana_total': barra_campana_total,
            'dict_agente_counter': zip(estadisticas['agentes_nombre'],
                                        estadisticas['total_agentes'],
                                        estadisticas['total_agente_ics'],
                                        estadisticas['total_agente_dialer'],
                                        estadisticas['total_agente_inbound'],
                                        estadisticas['total_agente_manual']),
            'barra_agente_total': barra_agente_total,
        }
