# -*- coding: utf-8 -*-

"""Servicio para generar reporte de supervision de los agentes """

import pygal
import datetime
import os

from pygal.style import Style, RedBlueStyle

from django.conf import settings
from django.db.models import Count
from ominicontacto_app.models import AgenteProfile, Queuelog, Campana, Grabacion
from ominicontacto_app.services.queue_log_service import AgenteTiemposReporte

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


class EstadisticasService():

    def _obtener_agentes(self):
        return AgenteProfile.objects.filter(is_inactive=False)

    def _filter_query_por_agente(self, query_agentes, agente_pk):
        resultado = []
        for item in query_agentes:
            if item[0] == agente_pk:
                resultado.append(item)
        return resultado

    def calcular_tiempo_sesion(self, agentes, fecha_inferior, fecha_superior):
        """
        Calcula el tiempo de session de los agentes en el periodo evaluado
        :return: un listado de agentes con el tiempo de session
        """
        eventos_sesion = ['ADDMEMBER', 'REMOVEMEMBER']

        if fecha_inferior and fecha_superior:
            fecha_desde = datetime.datetime.combine(fecha_inferior,
                                                    datetime.time.min)
            fecha_hasta = datetime.datetime.combine(fecha_superior,
                                                    datetime.time.max)

        logs_queue = Queuelog.objects.filter(
            queuename='ALL',
            event__in=eventos_sesion,
            time__range=(fecha_desde, fecha_hasta)).order_by('-time')

        agentes_tiempo = []

        # iterar por agente evaluando los eventos de session
        for agente in agentes:
            tiempo_agente = []
            logs_time = logs_queue.filter(agent=agente)
            is_remove = False
            time_actual = None
            # iterar los log teniendo en cuenta que si encuentra un evento REMOVEMEMBER
            # y luego un ADDMEMBER calcula el tiempo de session
            for logs in logs_time:
                if is_remove and logs.event == 'ADDMEMBER':
                    resta = time_actual - logs.time
                    tiempo_agente.append(agente)
                    tiempo_agente.append(logs.time.strftime('%Y-%m-%d'))
                    tiempo_string = str(resta) + "hs"
                    tiempo_agente.append(str(tiempo_string))
                    agentes_tiempo.append(tiempo_agente)
                    tiempo_agente = []
                    is_remove = False
                    time_actual = None
                if logs.event == 'REMOVEMEMBER':
                    time_actual = logs.time
                    is_remove = True
        return agentes_tiempo

    def calcular_tiempo_pausa(self, agentes, fecha_inferior, fecha_superior):
        """
        Calcula el tiempo de pausa de los agentes en el periodo evaluado
        :return: un listado de agentes con el tiempo de pausa
        """
        eventos_pausa = ['PAUSEALL', 'UNPAUSEALL']

        agentes_tiempo = []
        # iterar por agente evaluando los eventos de pausa
        agentes_id = [agente.id for agente in agentes]
        logs_time = Queuelog.objects.obtener_tiempos_event_agentes(
            eventos_pausa,
            fecha_inferior,
            fecha_superior,
            agentes_id)

        for agente in agentes:

            #logs_time = Queuelog.objects.obtener_log_agente_pk_event_periodo_all(
             #   eventos_pausa, fecha_inferior, fecha_superior, agente.id)
            is_unpause = False
            time_actual = None
            tiempos_pausa = {}
            log_agente = self._filter_query_por_agente(logs_time, agente.id)
            # iterar los log teniendo en cuenta que si encuentra un evento UNPAUSEALL
            # y luego un PAUSEALL calcula el tiempo de session
            for logs in log_agente:
                if is_unpause and logs[2] == 'PAUSEALL':
                    resta = time_actual - logs[1]
                    if logs[3] in tiempos_pausa.keys():
                        tiempos_pausa[logs[3]] += resta
                    else:
                        tiempos_pausa.update({logs[3]: resta})
                    is_unpause = False
                    time_actual = None
                if logs[2] == 'UNPAUSEALL':
                    time_actual = logs[1]
                    is_unpause = True
            for tiempo_pausa in tiempos_pausa:
                tiempo_agente = []

                tiempo_agente.append(agente.user.get_full_name())
                tiempo_agente.append(tiempo_pausa)
                tiempos_pausa[tiempo_pausa] = str(datetime.timedelta(
                    seconds=tiempos_pausa[tiempo_pausa].seconds))
                tiempo_agente.append(tiempos_pausa[tiempo_pausa])
                agentes_tiempo.append(tiempo_agente)

        return agentes_tiempo

    def calcular_tiempo_llamada(self, agentes, fecha_inferior, fecha_superior):
        """
        Calcula el tiempo de llamadas de los agentes en el periodo evaluado
        :return: un listado de agentes con el tiempo de llamadas
        """
        eventos_llamadas = ['COMPLETECALLER', 'COMPLETEAGENT']

        agentes_tiempo = []

        # iterar por agente evaluando los eventos de llamadas
        for agente in agentes:
            logs_time = Queuelog.objects.obtener_log_agente_event_periodo(
                eventos_llamadas, fecha_inferior, fecha_superior, agente)
            llamadas_cola = {}
            for logs in logs_time:
                tiempo_llamada = int(logs.data2)
                if logs.queuename in llamadas_cola.keys():
                    llamadas_cola[logs.queuename] += tiempo_llamada
                else:
                    llamadas_cola.update({logs.queuename: tiempo_llamada})
            for tiempo_cola in llamadas_cola:
                tiempo_agente = []
                tiempo_agente.append(agente)
                tiempo_agente.append(tiempo_cola)
                llamadas_cola[tiempo_cola] = str(datetime.timedelta(
                    0, llamadas_cola[tiempo_cola]))
                tiempo_agente.append(llamadas_cola[tiempo_cola])
                agentes_tiempo.append(tiempo_agente)

        return agentes_tiempo

    def calcular_tiempos_agentes(self, agentes, fecha_inferior, fecha_superior):
        eventos_pausa = ['PAUSEALL', 'UNPAUSEALL']
        agentes_tiempo = []
        agentes_id = [agente.id for agente in agentes]
        logs_time = Queuelog.objects.obtener_tiempos_event_agentes(
            eventos_pausa,
            fecha_inferior,
            fecha_superior,
            agentes_id)

        for agente in agentes:
            agente_nuevo = None
            is_unpause = False
            time_actual = None

            log_agente = self._filter_query_por_agente(logs_time, agente.id)

            for logs in log_agente:
                if is_unpause and logs[2] == 'PAUSEALL':
                    resta = time_actual - logs[1]
                    agente_en_lista = filter(lambda x: x.agente == agente,
                                             agentes_tiempo)
                    if agente_en_lista:
                        agente_nuevo = agente_en_lista[0]
                        if agente_nuevo.tiempo_pausa:
                            agente_nuevo._tiempo_pausa += resta
                        else:
                            agente_nuevo._tiempo_pausa = resta
                    else:
                        agente_nuevo = AgenteTiemposReporte(
                            agente, None, resta, None, 0, 0, 0, 0)
                        agentes_tiempo.append(agente_nuevo)
                    agente_nuevo = None
                    is_unpause = False
                    time_actual = None
                if logs[2] == 'UNPAUSEALL':
                    time_actual = logs[1]
                    is_unpause = True

        eventos_sesion = ['ADDMEMBER', 'REMOVEMEMBER']

        logs_time = Queuelog.objects.obtener_tiempos_event_agentes(
            eventos_sesion,
            fecha_inferior,
            fecha_superior,
            agentes_id)

        for agente in agentes:
            agente_nuevo = None
            is_remove = False
            time_actual = None
            log_agente = self._filter_query_por_agente(logs_time, agente.id)
            for logs in log_agente:
                if is_remove and logs[2] == 'ADDMEMBER':
                    resta = time_actual - logs[1]
                    agente_en_lista = filter(lambda x: x.agente == agente,
                                             agentes_tiempo)
                    if agente_en_lista:
                        agente_nuevo = agente_en_lista[0]
                        if agente_nuevo.tiempo_sesion:
                            agente_nuevo._tiempo_sesion += resta
                        else:
                            agente_nuevo._tiempo_sesion = resta
                    else:
                        agente_nuevo = AgenteTiemposReporte(
                            agente, resta, None, None, 0, 0, 0, 0)
                        agentes_tiempo.append(agente_nuevo)
                    agente_nuevo = None
                    is_remove = False
                    time_actual = None
                if logs[2] == 'REMOVEMEMBER':
                    time_actual = logs[1]
                    is_remove = True

        eventos_llamadas = ['COMPLETECALLER', 'COMPLETEAGENT']

        agentes_id = [agente.id for agente in agentes]
        logs_time = Queuelog.objects.obtener_tiempo_llamadas_agente(
            eventos_llamadas, fecha_inferior, fecha_superior, agentes_id)

        for log in logs_time:

            agente = AgenteProfile.objects.get(pk=int(log[0]))
            agente_en_lista = filter(lambda x: x.agente == agente,
                                     agentes_tiempo)
            if agente_en_lista:
                agente_nuevo = agente_en_lista[0]
                agente_nuevo._tiempo_llamada = int(log[1])
            else:
                agente_nuevo = AgenteTiemposReporte(
                    agente, None, None, int(log[1]), 0, 0, 0, 0)
                agentes_tiempo.append(agente_nuevo)

        logs_time = Queuelog.objects.obtener_count_evento_agente(
            eventos_llamadas, fecha_inferior, fecha_superior, agentes_id)

        for log in logs_time:

            agente = AgenteProfile.objects.get(pk=int(log[0]))
            agente_en_lista = filter(lambda x: x.agente == agente,
                                     agentes_tiempo)
            if agente_en_lista:
                agente_nuevo = agente_en_lista[0]
                agente_nuevo._cantidad_llamadas_procesadas = int(log[1])
            else:
                agente_nuevo = AgenteTiemposReporte(
                    agente, None, None, None, logs_time.count(),
                    0, 0, 0)
                agentes_tiempo.append(agente_nuevo)

        eventos_llamadas_perdidas = ['RINGNOANSWER']

        logs_time = Queuelog.objects.obtener_count_evento_agente(
            eventos_llamadas_perdidas, fecha_inferior, fecha_superior, agentes_id)

        for log in logs_time:

            agente = AgenteProfile.objects.get(pk=int(log[0]))
            agente_en_lista = filter(lambda x: x.agente == agente,
                                     agentes_tiempo)
            if agente_en_lista:
                agente_nuevo = agente_en_lista[0]
                agente_nuevo._cantidad_llamadas_perdidas= int(log[1])
            else:
                agente_nuevo = AgenteTiemposReporte(
                    agente, None, None, None, 0,
                    int(log[1]), 0, 0)
                agentes_tiempo.append(agente_nuevo)

        logs_time = Queuelog.objects.obtener_tiempo_llamadas_saliente_agente(
            eventos_llamadas, fecha_inferior, fecha_superior, agentes_id)

        for log in logs_time:

            agente = AgenteProfile.objects.get(pk=int(log[0]))
            agente_en_lista = filter(lambda x: x.agente == agente,
                                     agentes_tiempo)
            if agente_en_lista:
                agente_nuevo = agente_en_lista[0]
                agente_nuevo._tiempo_llamada_saliente = int(log[1])
            else:
                agente_nuevo = AgenteTiemposReporte(
                    agente, None, None, None, 0, 0, int(log[1]), 0)
                agentes_tiempo.append(agente_nuevo)

        logs_time = Queuelog.objects.obtener_count_saliente_evento_agente(
            eventos_llamadas, fecha_inferior, fecha_superior, agentes_id)

        for log in logs_time:

            agente = AgenteProfile.objects.get(pk=int(log[0]))
            agente_en_lista = filter(lambda x: x.agente == agente,
                                     agentes_tiempo)
            if agente_en_lista:
                agente_nuevo = agente_en_lista[0]
                agente_nuevo._cantidad_llamadas_saliente = int(log[1])
            else:
                agente_nuevo = AgenteTiemposReporte(
                    agente, None, None, None, 0,
                    0, 0, int(log[1]))
                agentes_tiempo.append(agente_nuevo)

        return agentes_tiempo

    def obtener_count_llamadas_campana(self, agentes, fecha_inferior, fecha_superior,
                                       user):
        eventos_llamadas = ['COMPLETECALLER', 'COMPLETEAGENT']

        campanas = Campana.objects.obtener_all_dialplan_asterisk()
        if not user.get_is_administrador():
            campanas = Campana.objects.obtener_campanas_vista_by_user(campanas, user)

        agentes_tiempo = []
        agentes = [agente.id for agente in agentes]
        logs_time = Queuelog.objects.obtener_agentes_campanas_total(
            eventos_llamadas, fecha_inferior, fecha_superior, agentes, campanas)

        for log in logs_time:
            campana = log[1].split('_')
            try:
                campana_nombre = campana[1]
            except ValueError:
                campana_nombre = log[1]
            agente = log[0].split('_')
            try:
                agente_nombre = agente[1]
            except ValueError:
                agente_nombre = log[0]
            tiempo_agente = []
            tiempo_agente.append(agente_nombre)
            tiempo_agente.append(campana_nombre)
            tiempo_agente.append(str(datetime.timedelta(0, log[2])))
            tiempo_agente.append(log[3])
            agentes_tiempo.append(tiempo_agente)

        return agentes_tiempo

    ########################################################################
    #           ATENCION COPIADO de reporte_grafico.py

    def _obtener_agente_grabacion(self, agentes, fecha_inferior, fecha_superior):
        """
        Obtiene el totales de llamadas por agente
        :param fecha_inferior: fecha desde cual se obtendran las grabaciones
        :param fecha_superior: fecha hasta el cual se obtendran las grabaciones
        :return: queryset con las cantidades totales por agente
        """
        fecha_inferior = datetime.datetime.combine(fecha_inferior,
                                                   datetime.time.min)
        fecha_superior = datetime.datetime.combine(fecha_superior,
                                                   datetime.time.max)
        agentes = [agente.sip_extension for agente in agentes]
        dict_agentes = Grabacion.objects.obtener_count_agente().filter(
            fecha__range=(fecha_inferior, fecha_superior), sip_agente__in=agentes)
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
        """
        Obtiene el total grabaciones  por agente en una lista
        :return: lista con el total de llamadas por agente
        """
        total_agentes = []

        for agente_unit, agente in zip(dict_agentes, agentes):
            if agente_unit['sip_agente'] == agente:
                total_agentes.append(agente_unit['cantidad'])
            else:
                total_agentes.append(0)

        return total_agentes

    def _obtener_total_ics_agente(self, dict_agentes, agentes):
        """
        Obtiene el total grabaciones ICS por agente en una lista
        :return: lista con el total de llamadas ICS por agente
        """
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
        """
        Obtiene el total grabaciones DIALER por agente en una lista
        :return: lista con el total de llamadas DIALER por agente
        """
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
        """
        Obtiene el total grabaciones INBOUND por agente en una lista
        :return: lista con el total de llamadas INBOUND por agente
        """
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
        """
        Obtiene el total grabaciones MANUAL por agente en una lista
        :return: lista con el total de llamadas MANUAL por agente
        """
        total_manual = []

        for agente in agentes:
            cantidad = 0
            result = dict_agentes.filter(tipo_llamada=Grabacion.TYPE_MANUAL). \
                filter(sip_agente=agente)
            if result:
                cantidad = result[0]['cantidad']

            total_manual.append(cantidad)

        return total_manual

    ############################################################################

    def _calcular_estadisticas(self, fecha_inferior, fecha_superior, agentes, user):
        if not agentes:
            agentes = self._obtener_agentes()
        #agentes_tiempo = self.calcular_tiempo_sesion(agentes, fecha_inferior,
         #                                            fecha_superior)
        agentes_pausa = self.calcular_tiempo_pausa(agentes, fecha_inferior,
                                                   fecha_superior)
        #agentes_llamadas = self.calcular_tiempo_llamada(agentes,
         #                                               fecha_inferior, fecha_superior)
        agentes_tiempos = self.calcular_tiempos_agentes(agentes, fecha_inferior,
                                                        fecha_superior)
        count_llamada_campana = self.obtener_count_llamadas_campana(
            agentes, fecha_inferior, fecha_superior, user)

        # Copiado del modulo reporte_grafico
        dict_agentes, agentes_nombre, agentes = self._obtener_agente_grabacion(agentes,
            fecha_inferior, fecha_superior)

        total_agentes = self._obtener_total_agente_grabacion(dict_agentes, agentes)
        total_agente_ics = self._obtener_total_ics_agente(dict_agentes, agentes)
        total_agente_dialer = self._obtener_total_dialer_agente(dict_agentes, agentes)
        total_agente_inbound = self._obtener_total_inbound_agente(dict_agentes, agentes)
        total_agente_manual = self._obtener_total_manual_agente(dict_agentes, agentes)

        dic_estadisticas = {
            'agentes_tiempos': agentes_tiempos,
            'fecha_desde': fecha_inferior,
            'fecha_hasta': fecha_superior,
            'agentes_pausa': agentes_pausa,
            #'agentes_llamadas': agentes_llamadas,
            'count_llamada_campana': count_llamada_campana,
            'agentes': agentes,
            'agentes_nombre': agentes_nombre,
            'total_agentes': total_agentes,
            'total_agente_ics': total_agente_ics,
            'total_agente_dialer': total_agente_dialer,
            'total_agente_inbound': total_agente_inbound,
            'total_agente_manual': total_agente_manual,

        }
        return dic_estadisticas

    def general_campana(self, fecha_inferior, fecha_superior, agentes, user):
        estadisticas = self._calcular_estadisticas(fecha_inferior,
                                                   fecha_superior, agentes, user)

        if estadisticas:
            logger.info("Generando grafico calificaciones de campana por cliente ")

        # copiado de reporte_grafico
        # Barra: Cantidad de llamadas de los agentes por tipo de llamadas.
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
            'dict_agente_counter': zip(estadisticas['agentes_nombre'],
                                       estadisticas['total_agentes'],
                                       estadisticas['total_agente_ics'],
                                       estadisticas['total_agente_dialer'],
                                       estadisticas['total_agente_inbound'],
                                       estadisticas['total_agente_manual']),
            'barra_agente_total': barra_agente_total,
        }
