# -*- coding: utf-8 -*-

"""
Servicio para generar reporte de las grabaciones de las llamadas
"""

import pygal
import datetime
from pygal.style import Style

from django.db.models import Q

from ominicontacto_app.models import Grabacion, Queuelog, Campana
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
        """
        Obtiene el total de llamadas por tipo de origen de llamadas
        :param listado_grabaciones: listados de las grabaciones de las llamadas
        :return: dicionario con los totales por tipo de llamadas
        """
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

    def _obtener_campana_grabacion(self, fecha_inferior, fecha_superior, campanas):
        """
        Obtiene el totales de llamadas por campanas
        :param fecha_inferior: fecha desde cual se obtendran las grabaciones
        :param fecha_superior: fecha hasta el cual se obtendran las grabaciones
        :return: queryset con las cantidades totales por campana
        """
        # lista de dict con la cantidad por  cada campana
        fecha_inferior = datetime.datetime.combine(fecha_inferior,
                                                   datetime.time.min)
        fecha_superior = datetime.datetime.combine(fecha_superior,
                                                   datetime.time.max)
        campanas = [campana.id for campana in campanas]
        dict_campana = Grabacion.objects.obtener_count_campana().filter(
            fecha__range=(fecha_inferior, fecha_superior), campana_id__in=campanas)
        campana = []
        campana_nombre = []

        for campana_id in dict_campana:
            campana.append(campana_id['campana'])
            campana_nombre.append(campana_id['campana__nombre'])
        return dict_campana, campana, campana_nombre

    def _obtener_total_campana_grabacion(self, dict_campana, campana):
        """
        Obtiene el totales de grabaciones por campana en una lista
        """

        total_campana = []

        for campana_unit, campana in zip(dict_campana, campana):
            if campana_unit['campana'] == campana:
                total_campana.append(campana_unit['cantidad'])
            else:
                total_campana.append(0)

        return total_campana

    def _obtener_total_ics_grabacion(self, dict_campana, campana):
        """
        Obtiene el total grabaciones ICS por campana en una lista
        :return: lista con el total de llamadas ics por campana
        """
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
        """
        Obtiene el total grabaciones DIALER por campana en una lista
        :return: lista con el total de llamadas DIALER por campana
        """
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
        """
        Obtiene el total grabaciones INBOUND por campana en una lista
        :return: lista con el total de llamadas INBOUND por campana
        """
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
        """
        Obtiene el total grabaciones MANUAL por campana en una lista
        :return: lista con el total de llamadas MANUAL por campana
        """
        total_manual = []

        for campana_id in campana:
            cantidad = 0
            result = dict_campana.filter(tipo_llamada=Grabacion.TYPE_MANUAL).\
                filter(campana=campana_id)
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

    def _obtener_total_llamadas_agente_inbound(self, fecha_inferior, fecha_superior):
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

    def calcular_cantidad_llamadas(self, campanas, fecha_inferior, fecha_superior):
        """
        Calcula la cantidad de llamadas ingresadas, atendidas, abandondas, expiradas
        por campana
        :return: en un dicionaros los totales por campana y los totales para hacer el
        grafico
        """
        eventos_llamadas_ingresadas = ['ENTERQUEUE']
        eventos_llamadas_atendidas = ['CONNECT']
        eventos_llamadas_abandonadas = ['ABANDON']
        eventos_llamadas_expiradas = ['EXITWITHTIMEOUT']

        nombres_queues = []
        total_atendidas = []
        total_abandonadas = []
        total_expiradas = []

        queues_tiempo = []

        for campana in campanas:
            ingresadas = Queuelog.objects.obtener_log_campana_id_event_periodo(
                eventos_llamadas_ingresadas, fecha_inferior, fecha_superior,
                campana.id)
            atendidas = Queuelog.objects.obtener_log_campana_id_event_periodo(
                eventos_llamadas_atendidas, fecha_inferior, fecha_superior,
                campana.id)
            abandonadas = Queuelog.objects.obtener_log_campana_id_event_periodo(
                eventos_llamadas_abandonadas, fecha_inferior, fecha_superior,
                campana.id)
            expiradas = Queuelog.objects.obtener_log_campana_id_event_periodo(
                eventos_llamadas_expiradas, fecha_inferior, fecha_superior,
                campana.id)
            count_llamadas_ingresadas = ingresadas.count()
            count_llamadas_atendidas = atendidas.count()
            count_llamadas_abandonadas = abandonadas.count()
            count_llamadas_expiradas = expiradas.count()
            count_llamadas_manuales = ingresadas.filter(data4='saliente').count()
            count_manuales_atendidas = atendidas.filter(data4='saliente').count()
            count_manuales_abandonadas = abandonadas.filter(data4='saliente').count()
            cantidad_campana = []
            cantidad_campana.append(campana.nombre)
            cantidad_campana.append(count_llamadas_ingresadas)
            cantidad_campana.append(count_llamadas_atendidas)
            cantidad_campana.append(count_llamadas_expiradas)
            cantidad_campana.append(count_llamadas_abandonadas)
            cantidad_campana.append(count_llamadas_manuales)
            cantidad_campana.append(count_manuales_atendidas)
            cantidad_campana.append(count_manuales_abandonadas)

            queues_tiempo.append(cantidad_campana)

            # para reportes
            nombres_queues.append(campana.nombre)
            total_atendidas.append(count_llamadas_atendidas)
            total_abandonadas.append(count_llamadas_expiradas)
            total_expiradas.append(count_llamadas_abandonadas)

        totales_grafico = {
            'nombres_queues': nombres_queues,
            'total_atendidas': total_atendidas,
            'total_abandonadas': total_abandonadas,
            'total_expiradas': total_expiradas
        }

        return queues_tiempo, totales_grafico

    def obtener_total_llamadas(self, fecha_inferior, fecha_superior, campanas):
        """
        Calcula la cantidad de llamadas ingresadas, atendidas, abandondas, expiradas
        :return: los totales de llamadas por ingresadas, atendidas, abandonad y expiradas
        """

        eventos_llamadas_ingresadas = ['ENTERQUEUE']
        eventos_llamadas_atendidas = ['CONNECT']
        eventos_llamadas_abandonadas = ['ABANDON']
        eventos_llamadas_expiradas = ['EXITWITHTIMEOUT']
        campanas_entrantes = campanas.filter(
            type=Campana.TYPE_ENTRANTE).values_list('id', flat=True)
        campanas_dialer = campanas.filter(
            type=Campana.TYPE_DIALER).values_list('id', flat=True)

        ingresadas_dialer = Queuelog.objects.obtener_log_event_periodo(
            eventos_llamadas_ingresadas, fecha_inferior, fecha_superior).filter(
                Q(campana_id__in=campanas_dialer), ~Q(data4='saliente'))
        atendidas_dialer = Queuelog.objects.obtener_log_event_periodo(
            eventos_llamadas_atendidas, fecha_inferior, fecha_superior).filter(
                Q(campana_id__in=campanas_dialer), ~Q(data4='saliente'))
        abandonadas_dialer = Queuelog.objects.obtener_log_event_periodo(
            eventos_llamadas_abandonadas, fecha_inferior, fecha_superior).filter(
                Q(campana_id__in=campanas_dialer), ~Q(data4='saliente'))
        expiradas_dialer = Queuelog.objects.obtener_log_event_periodo(
            eventos_llamadas_expiradas, fecha_inferior, fecha_superior).filter(
                campana_id__in=campanas_dialer)

        ingresadas_entrantes = Queuelog.objects.obtener_log_event_periodo(
            eventos_llamadas_ingresadas, fecha_inferior, fecha_superior).filter(
                Q(campana_id__in=campanas_entrantes), ~Q(data4='saliente'))
        atendidas_entrantes = Queuelog.objects.obtener_log_event_periodo(
            eventos_llamadas_atendidas, fecha_inferior, fecha_superior).filter(
                Q(campana_id__in=campanas_entrantes), ~Q(data4='saliente'))
        abandonadas_entrantes = Queuelog.objects.obtener_log_event_periodo(
            eventos_llamadas_abandonadas, fecha_inferior, fecha_superior).filter(
                Q(campana_id__in=campanas_entrantes), ~Q(data4='saliente'))
        expiradas_entrantes = Queuelog.objects.obtener_log_event_periodo(
            eventos_llamadas_expiradas, fecha_inferior, fecha_superior).filter(
                Q(campana_id__in=campanas_entrantes), ~Q(data4='saliente'))

        llamadas_ingresadas_manuales = Queuelog.objects.obtener_log_event_periodo(
            eventos_llamadas_ingresadas, fecha_inferior, fecha_superior).filter(
            data4='saliente')
        llamadas_atendidas_manuales = Queuelog.objects.obtener_log_event_periodo(
            eventos_llamadas_atendidas, fecha_inferior, fecha_superior).filter(
            data4='saliente')
        llamadas_abandonadas_manuales = Queuelog.objects.obtener_log_event_periodo(
            eventos_llamadas_abandonadas, fecha_inferior, fecha_superior).filter(
            data4='saliente')

        count_llamadas_ingresadas_dialer = ingresadas_dialer.count()
        count_llamadas_gestionadas_dialer = atendidas_dialer.count()
        count_llamadas_abandonadas_dialer = abandonadas_dialer.count()
        count_llamadas_expiradas_dialer = expiradas_dialer.count()
        count_llamadas_perdidas_dialer = count_llamadas_abandonadas_dialer + \
            count_llamadas_expiradas_dialer

        count_llamadas_ingresadas_entrantes = ingresadas_entrantes.count()
        count_llamadas_atendidas_entrantes = atendidas_entrantes.count()
        count_llamadas_abandonadas_entrantes = abandonadas_entrantes.count()
        count_llamadas_expiradas_entrantes = expiradas_entrantes.count()

        count_llamadas_ingresadas_manuales = llamadas_ingresadas_manuales.count()
        count_llamadas_atendidas_manuales = llamadas_atendidas_manuales.count()
        count_llamadas_abandonadas_manuales = llamadas_abandonadas_manuales.count()

        total_llamadas_ingresadas = count_llamadas_ingresadas_entrantes + \
            count_llamadas_ingresadas_dialer + \
            count_llamadas_ingresadas_manuales

        cantidad_campana = []
        cantidad_campana.append(total_llamadas_ingresadas)

        cantidad_campana.append(count_llamadas_ingresadas_dialer)
        cantidad_campana.append(count_llamadas_gestionadas_dialer)
        cantidad_campana.append(count_llamadas_perdidas_dialer)

        cantidad_campana.append(count_llamadas_ingresadas_entrantes)
        cantidad_campana.append(count_llamadas_atendidas_entrantes)
        cantidad_campana.append(count_llamadas_expiradas_entrantes)
        cantidad_campana.append(count_llamadas_abandonadas_entrantes)

        cantidad_campana.append(count_llamadas_ingresadas_manuales)
        cantidad_campana.append(count_llamadas_atendidas_manuales)
        cantidad_campana.append(count_llamadas_abandonadas_manuales)

        return cantidad_campana

    def _calcular_estadisticas(self, fecha_inferior, fecha_superior, user, finalizadas):

        if finalizadas:
            campanas = Campana.objects.obtener_all_activas_finalizadas()
        else:
            campanas = Campana.objects.obtener_all_dialplan_asterisk()

        if not user.get_is_administrador():
            campanas = Campana.objects.obtener_campanas_vista_by_user(campanas, user)

        grabaciones = Grabacion.objects.grabacion_by_fecha_intervalo(
            fecha_inferior, fecha_superior).filter(campana__in=campanas)

        # obtiene el total de llamadas por tipo de llamadas
        counter_tipo_llamada = self._obtener_total_llamdas_tipo(grabaciones)

        total_grabaciones = len(grabaciones)
        # calculo el porcentaje de las llamadas por tipo de llamadas
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

        queues_llamadas, totales_grafico = self.calcular_cantidad_llamadas(
            campanas, fecha_inferior, fecha_superior)

        total_llamadas = self.obtener_total_llamadas(fecha_inferior, fecha_superior,
                                                     campanas)

        dict_campana, campana, campana_nombre = self._obtener_campana_grabacion(
            fecha_inferior, fecha_superior, campanas)
        total_campana = self._obtener_total_campana_grabacion(dict_campana, campana)
        total_grabacion_ics = self._obtener_total_ics_grabacion(dict_campana,
                                                                campana)
        total_grabacion_dialer = self._obtener_total_dialer_grabacion(dict_campana,
                                                                      campana)
        total_grabacion_inbound = self._obtener_total_inbound_grabacion(dict_campana,
                                                                        campana)
        total_grabacion_manual = self._obtener_total_manual_grabacion(dict_campana,
                                                                      campana)

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
            'queues_llamadas': queues_llamadas,
            'fecha_desde': fecha_inferior,
            'fecha_hasta': fecha_superior,
            'total_llamadas': total_llamadas,
            'totales_grafico': totales_grafico,

        }
        return dic_estadisticas

    def general_llamadas_hoy(self, fecha_inferior, fecha_superior, user, finalizadas):
        estadisticas = self._calcular_estadisticas(
            fecha_inferior, fecha_superior, user, finalizadas)

        if estadisticas:
            logger.info("Generando grafico para grabaciones de llamadas ")

        no_data_text = "No hay llamadas para ese periodo"
        torta_grabaciones = pygal.Pie(  # @UndefinedVariable
            style=ESTILO_AZUL_ROJO_AMARILLO,
            no_data_text=no_data_text,
            no_data_font_size=32,
            legend_font_size=25,
            truncate_legend=10,
            tooltip_font_size=50,
        )

        # torta_grabaciones.title = "Resultado de las llamadas"
        torta_grabaciones.add('Dialer', estadisticas['porcentaje_dialer'])
        torta_grabaciones.add('Inbound', estadisticas['porcentaje_ics'])
        torta_grabaciones.add('Ics', estadisticas['porcentaje_inbound'])
        torta_grabaciones.add('Manual', estadisticas['porcentaje_manual'])

        # Barra: Cantidad de llamadas de las campana por tipo de llamadas
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
            'torta_grabaciones': torta_grabaciones,
            'dict_campana_counter': zip(estadisticas['campana_nombre'],
                                        estadisticas['total_campana'],
                                        estadisticas['total_grabacion_ics'],
                                        estadisticas['total_grabacion_dialer'],
                                        estadisticas['total_grabacion_inbound'],
                                        estadisticas['total_grabacion_manual']),
            'barra_campana_total': barra_campana_total,
            'barra_campana_llamadas': barra_campana_llamadas,
        }
