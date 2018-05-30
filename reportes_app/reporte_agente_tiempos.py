# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import pygal

from django.utils import timezone
from reportes_app.actividad_agente_log import AgenteTiemposReporte
from reportes_app.models import ActividadAgenteLog, LlamadaLog
from ominicontacto_app.models import AgenteProfile, Pausa, Campana
from pygal.style import Style
from ominicontacto_app.utiles import (
    datetime_hora_minima_dia, datetime_hora_maxima_dia, cast_datetime_part_date
)


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


class TiemposAgente(object):
    """
    Calculo de los tiempos del agente, session, pausas, en llamada
    """

    def __init__(self):
        self.agentes_tiempo = []

    def _filter_query_por_agente(self, query_agentes, agente_pk):
        resultado = []
        for item in query_agentes:
            if item[0] == agente_pk:
                resultado.append(item)
        return resultado

    def _get_nombre_campana(self, query_campanas, campana_pk):
        for item in query_campanas:
            if item.pk == campana_pk:
                return item.nombre
        return campana_pk

    def _obtener_datos_de_pausa(self, id_pausa):
        datos = {'nombre': 'n/d', 'tipo': 'n/d'}
        if id_pausa == '0':
            datos['nombre'] = 'ACW'
            datos['tipo'] = Pausa.CHOICE_PRODUCTIVA
        else:
            try:
                pausa = Pausa.objects.get(id=id_pausa)
            except ValueError:
                datos['nombre'] = '%s*' % (id_pausa, )
            except Pausa.DoesNotExist:
                datos['nombre'] = '%s*' % (id_pausa, )
            else:
                datos['nombre'] = pausa.nombre
                datos['tipo'] = pausa.get_tipo()

        return datos

    def calcular_tiempo_session(self, agentes, fecha_inferior, fecha_superior):
        """ Calcula el tiempo de session teniendo en cuenta los eventos
        ADDMEMBER, REMOVEMEMBER"""

        eventos_sesion = ['ADDMEMBER', 'REMOVEMEMBER']
        agentes_id = [agente.id for agente in agentes]

        logs_time = ActividadAgenteLog.objects.obtener_tiempos_event_agentes(
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
                                             self.agentes_tiempo)
                    if agente_en_lista:
                        agente_nuevo = agente_en_lista[0]
                        if agente_nuevo.tiempo_sesion:
                            agente_nuevo._tiempo_sesion += resta
                        else:
                            agente_nuevo._tiempo_sesion = resta
                    else:
                        agente_nuevo = AgenteTiemposReporte(
                            agente, resta, 0, 0, 0, 0)
                        self.agentes_tiempo.append(agente_nuevo)
                    agente_nuevo = None
                    is_remove = False
                    time_actual = None
                if logs[2] == 'REMOVEMEMBER':
                    time_actual = logs[1]
                    is_remove = True

    def calcular_tiempo_pausa(self, agentes, fecha_inferior, fecha_superior):
        """ Calcula el tiempo de pausa teniendo en cuenta los eventos PAUSEALL,
        UNPAUSEALL y REMOVEMEMBER"""

        eventos_pausa = ['PAUSEALL', 'UNPAUSEALL', 'REMOVEMEMBER']
        agentes_id = [agente.id for agente in agentes]

        logs_time = ActividadAgenteLog.objects.obtener_tiempos_event_agentes(
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
                                             self.agentes_tiempo)
                    if agente_en_lista:
                        agente_nuevo = agente_en_lista[0]
                        if agente_nuevo.tiempo_pausa:
                            agente_nuevo._tiempo_pausa += resta
                        else:
                            agente_nuevo._tiempo_pausa = resta
                    else:
                        agente_nuevo = AgenteTiemposReporte(
                            agente, None, resta, 0, 0, 0)
                        self.agentes_tiempo.append(agente_nuevo)
                    agente_nuevo = None
                    is_unpause = False
                    time_actual = None
                if logs[2] == 'UNPAUSEALL' or logs[2] == 'REMOVEMEMBER':
                    time_actual = logs[1]
                    is_unpause = True

    def calcular_tiempo_llamada(self, agentes, fecha_inferior, fecha_superior):
        """ Calcula el tiempo de llamada teniendo en cuenta los eventos
        COMPLETECALLER y COMPLETEAGENT"""

        eventos_llamadas = ['COMPLETECALLER', 'COMPLETEAGENT']
        agentes_id = [agente.id for agente in agentes]

        logs_time = LlamadaLog.objects.obtener_tiempo_llamadas_agente(
            eventos_llamadas,
            fecha_inferior,
            fecha_superior,
            agentes_id)

        for log in logs_time:

            agente = AgenteProfile.objects.get(pk=int(log[0]))
            agente_en_lista = filter(lambda x: x.agente == agente,
                                     self.agentes_tiempo)
            if agente_en_lista:
                agente_nuevo = agente_en_lista[0]
                agente_nuevo._tiempo_llamada = int(log[1])
            else:
                agente_nuevo = AgenteTiemposReporte(
                    agente, None, None, int(log[1]), 0, 0)
                self.agentes_tiempo.append(agente_nuevo)

    def calcular_cantidad_llamadas(self, agentes, fecha_inferior, fecha_superior):
        """ Calcula la cantidad de llamadas procesads teniendo en cuenta los
        eventos COMPLETECALLER y COMPLETEAGENT"""

        eventos_llamadas = ['COMPLETECALLER', 'COMPLETEAGENT']
        agentes_id = [agente.id for agente in agentes]

        logs_time = LlamadaLog.objects.obtener_count_evento_agente(
            eventos_llamadas,
            fecha_inferior,
            fecha_superior,
            agentes_id)

        for log in logs_time:

            agente = AgenteProfile.objects.get(pk=int(log[0]))
            agente_en_lista = filter(lambda x: x.agente == agente,
                                     self.agentes_tiempo)
            if agente_en_lista:
                agente_nuevo = agente_en_lista[0]
                agente_nuevo._cantidad_llamadas_procesadas = int(log[1])
            else:
                agente_nuevo = AgenteTiemposReporte(
                    agente, None, 0, 0, logs_time.count(), 0)
                self.agentes_tiempo.append(agente_nuevo)

    def calcular_intentos_fallidos(self, agentes, fecha_inferior, fecha_superior):
        """ Calcula la cantidad de intentos fallido para el tipo de llamada
        Manual NO CONNECT(NOANSWER, CANCEL, BUSY, CHANUNAVAIL, FAIL, OTHER,
        AMD, BLACKLIST)"""

        eventos_llamadas = ['NOANSWER', 'CANCEL', 'BUSY', 'CHANUNAVAIL',
                            'FAIL', 'OTHER', 'AMD', 'BLACKLIST']
        agentes_id = [agente.id for agente in agentes]

        logs_time = LlamadaLog.objects.obtener_count_evento_agente(
            eventos_llamadas,
            fecha_inferior,
            fecha_superior,
            agentes_id)

        for log in logs_time:

            agente = AgenteProfile.objects.get(pk=int(log[0]))
            agente_en_lista = filter(lambda x: x.agente == agente,
                                     self.agentes_tiempo)
            if agente_en_lista:
                agente_nuevo = agente_en_lista[0]
                agente_nuevo._cantidad_intentos_fallidos = int(log[1])
            else:
                agente_nuevo = AgenteTiemposReporte(
                    agente, None, 0, 0, 0, int(log[1]))
                self.agentes_tiempo.append(agente_nuevo)

    def calcular_tiempo_pausa_tipo(self, agentes, fecha_inferior, fecha_superior):
        """
        Calcula el tiempo de pausa de los agentes en el periodo evaluado
        :return: un listado de agentes con el tiempo de pausa
        """
        eventos_pausa = ['PAUSEALL', 'UNPAUSEALL', 'REMOVEMEMBER']

        agentes_tiempo = []
        # iterar por agente evaluando los eventos de pausa
        agentes_id = [agente.id for agente in agentes]
        logs_time = ActividadAgenteLog.objects.obtener_tiempos_event_agentes(
            eventos_pausa,
            fecha_inferior,
            fecha_superior,
            agentes_id)

        for agente in agentes:

            is_unpause = False
            time_actual = None
            tiempos_pausa = {}
            log_agente = self._filter_query_por_agente(logs_time, agente.id)
            # iterar los log teniendo en cuenta que si encuentra un evento
            # UNPAUSEALL/REMOVEMEMBER y luego un PAUSEALL calcula el tiempo de session

            for logs in log_agente:
                if is_unpause and logs[2] == 'PAUSEALL':
                    resta = time_actual - logs[1]
                    id_pausa = logs[3]
                    if id_pausa in tiempos_pausa.keys():
                        tiempos_pausa[id_pausa] += resta
                    else:
                        tiempos_pausa.update({id_pausa: resta})
                    is_unpause = False
                    time_actual = None
                if logs[2] == 'UNPAUSEALL' or logs[2] == 'REMOVEMEMBER':
                    time_actual = logs[1]
                    is_unpause = True
            for id_pausa in tiempos_pausa:
                datos_de_pausa = self._obtener_datos_de_pausa(id_pausa)
                tiempo = str(timezone.timedelta(seconds=tiempos_pausa[id_pausa].seconds))
                tiempo_agente = {
                    'id': agente.id,
                    'nombre_agente': agente.user.get_full_name(),
                    'pausa': datos_de_pausa['nombre'],
                    'tipo_de_pausa': datos_de_pausa['tipo'],
                    'tiempo': tiempo,
                    'pausa_id': id_pausa
                }
                agentes_tiempo.append(tiempo_agente)

        return agentes_tiempo

    def obtener_count_llamadas_campana(self, agentes, fecha_inferior,
                                       fecha_superior, user):
        eventos_llamadas = ['COMPLETECALLER', 'COMPLETEAGENT']

        campanas = Campana.objects.obtener_all_dialplan_asterisk()
        if not user.get_is_administrador():
            campanas = Campana.objects.obtener_campanas_vista_by_user(
                campanas, user)

        agentes_tiempo = []
        agentes_id = [agente.id for agente in agentes]
        logs_time = LlamadaLog.objects.obtener_agentes_campanas_total(
            eventos_llamadas, fecha_inferior, fecha_superior, agentes_id,
            campanas)

        for agente in agentes:
            logs_agente = self._filter_query_por_agente(logs_time, agente.id)
            for log in logs_agente:
                tiempo_agente = []
                tiempo_agente.append(agente.user.get_full_name())
                tiempo_agente.append(self._get_nombre_campana(campanas, log[1]))
                tiempo_agente.append(str(timezone.timedelta(0, log[2])))
                tiempo_agente.append(log[3])
                agentes_tiempo.append(tiempo_agente)

        return agentes_tiempo

    def _obtener_llamadas_agente(self, agentes, fecha_inferior, fecha_superior):
        """
        Obtiene el totales de llamadas por agente
        :param fecha_inferior: fecha desde cual se obtendran las grabaciones
        :param fecha_superior: fecha hasta el cual se obtendran las grabaciones
        :return: queryset con las cantidades totales por agente
        """
        fecha_inferior = datetime_hora_minima_dia(fecha_inferior)
        fecha_superior = datetime_hora_maxima_dia(fecha_superior)
        agentes_id = [agente.id for agente in agentes]
        eventos_llamadas = ['COMPLETECALLER', 'COMPLETEAGENT']
        dict_agentes = LlamadaLog.objects.obtener_count_agente().filter(
            time__range=(fecha_inferior, fecha_superior),
            agente_id__in=agentes_id,
            event__in=eventos_llamadas)

        agentes = []
        ids_agentes = []

        for agente_id in dict_agentes:
            ids_agentes.append(agente_id['agente_id'])
            try:
                agente = AgenteProfile.objects.get(
                    pk=agente_id['agente_id'])
                agentes.append(agente.user.get_full_name())
            except AgenteProfile.DoesNotExist:
                agentes.append(agente_id['agente_id'])

        return dict_agentes, agentes, ids_agentes

    def _obtener_total_agente_llamadas(self, dict_agentes, agentes):
        """
        Obtiene el total grabaciones  por agente en una lista
        :return: lista con el total de llamadas por agente
        """
        total_agentes = []

        for agente_unit, agente in zip(dict_agentes, agentes):
            if agente_unit['agente_id'] == agente:
                total_agentes.append(agente_unit['cantidad'])
            else:
                total_agentes.append(0)

        return total_agentes

    def _obtener_total_preview_agente(self, dict_agentes, agentes):
        """
        Obtiene el total grabaciones PREVIEW por agente en una lista
        :return: lista con el total de llamadas PREVIEW por agente
        """
        total_preview = []

        for agente in agentes:
            cantidad = 0
            result = dict_agentes.filter(tipo_llamada=4).\
                filter(agente_id=agente)
            if result:
                cantidad = result[0]['cantidad']

            total_preview.append(cantidad)

        return total_preview

    def _obtener_total_dialer_agente(self, dict_agentes, agentes):
        """
        Obtiene el total grabaciones DIALER por agente en una lista
        :return: lista con el total de llamadas DIALER por agente
        """
        total_dialer = []

        for agente in agentes:
            cantidad = 0
            result = dict_agentes.filter(tipo_llamada=2). \
                filter(agente_id=agente)
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
            result = dict_agentes.filter(tipo_llamada=3).\
                filter(agente_id=agente)
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
            result = dict_agentes.filter(tipo_llamada=1). \
                filter(agente_id=agente)
            if result:
                cantidad = result[0]['cantidad']

            total_manual.append(cantidad)

        return total_manual

    def _obtener_total_agentes_tipos_llamadas(self, agentes, fecha_inferior,
                                              fecha_superior):
        dict_agentes, nombres_agentes, ids_agentes = self._obtener_llamadas_agente(
            agentes, fecha_inferior, fecha_superior)
        total_agentes = self._obtener_total_agente_llamadas(dict_agentes, ids_agentes)
        total_preview = self._obtener_total_preview_agente(dict_agentes, ids_agentes)
        total_dialer = self._obtener_total_dialer_agente(dict_agentes, ids_agentes)
        total_inbound = self._obtener_total_inbound_agente(dict_agentes, ids_agentes)
        total_manual = self._obtener_total_manual_agente(dict_agentes, ids_agentes)
        dict_agentes_llamadas = {
            'total_agentes': total_agentes,
            'total_agente_dialer': total_dialer,
            'total_agente_inbound': total_inbound,
            'total_agente_manual': total_manual,
            'total_agente_preview': total_preview,
            'nombres_agentes': nombres_agentes
        }
        return dict_agentes_llamadas

    def _generar_grafico_agentes_llamadas(self, dict_agentes_llamadas):
        # Barra: Cantidad de llamadas de los agentes por tipo de llamadas.
        barra_agente_total = pygal.Bar(  # @UndefinedVariable
            show_legend=False,
            style=ESTILO_AZUL_ROJO_AMARILLO)
        barra_agente_total.title = 'Cantidad de llamadas de los agentes por ' \
                                   'tipo de llamadas'

        barra_agente_total.x_labels = dict_agentes_llamadas['nombres_agentes']
        barra_agente_total.add('PREVIEW', dict_agentes_llamadas['total_agente_preview'])
        barra_agente_total.add('DIALER', dict_agentes_llamadas['total_agente_dialer'])
        barra_agente_total.add('INBOUND', dict_agentes_llamadas['total_agente_inbound'])
        barra_agente_total.add('MANUAL', dict_agentes_llamadas['total_agente_manual'])

        return barra_agente_total

    def _obtener_agentes(self):
        return AgenteProfile.objects.obtener_activos()

    def generar_reportes(self, agentes, fecha_inferior, fecha_superior, user):
        """Genera las estadisticas para generar todos los reportes de los agentes"""

        if not agentes:
            agentes = self._obtener_agentes()

        # calculamos los tiempos de los agentes por cada agente
        self.calcular_tiempo_session(agentes, fecha_inferior, fecha_superior)
        self.calcular_tiempo_pausa(agentes, fecha_inferior, fecha_superior)
        self.calcular_tiempo_llamada(agentes, fecha_inferior, fecha_superior)
        self.calcular_cantidad_llamadas(agentes, fecha_inferior, fecha_superior)
        self.calcular_intentos_fallidos(agentes, fecha_inferior, fecha_superior)

        # calculamos el tiempo en pausa por tipo de pausa
        agente_pausa = self.calcular_tiempo_pausa_tipo(
            agentes, fecha_inferior, fecha_superior)
        # calculamos el tiempo de llamadas por agente en cada campana
        count_llamada_campana = self.obtener_count_llamadas_campana(
            agentes, fecha_inferior, fecha_superior, user)
        # calculamos el total de llamadas por tipo de llamadas de cada agente
        dict_agentes_llamadas = self._obtener_total_agentes_tipos_llamadas(
            agentes, fecha_inferior, fecha_superior)
        # creamos el grafico de agente por cada tipo de llamada
        barra_agente_total = self._generar_grafico_agentes_llamadas(
            dict_agentes_llamadas)
        return {
            'fecha_desde': fecha_inferior,
            'fecha_hasta': fecha_superior,
            'agentes_tiempos': self.agentes_tiempo,
            'agente_pausa': agente_pausa,
            'count_llamada_campana': count_llamada_campana,
            'dict_agente_counter': zip(dict_agentes_llamadas['nombres_agentes'],
                                       dict_agentes_llamadas['total_agentes'],
                                       dict_agentes_llamadas['total_agente_preview'],
                                       dict_agentes_llamadas['total_agente_dialer'],
                                       dict_agentes_llamadas['total_agente_inbound'],
                                       dict_agentes_llamadas['total_agente_manual']),
            'barra_agente_total': barra_agente_total,
        }

    def calcular_tiempo_session_fecha_agente(self, agente, fecha_inferior,
                                             fecha_superior, agente_fecha):
        """ Calcula el tiempo de session teniendo en cuenta los eventos
        ADDMEMBER, REMOVEMEMBER por fecha dia a dia"""

        eventos_sesion = ['ADDMEMBER', 'REMOVEMEMBER']

        logs_time = ActividadAgenteLog.objects.obtener_tiempos_event_agentes(
            eventos_sesion,
            fecha_inferior,
            fecha_superior,
            [agente.id])

        time_actual = None
        is_remove = False
        for logs in logs_time:
            agente_nuevo = None
            if is_remove and logs[2] == 'ADDMEMBER':
                if cast_datetime_part_date(time_actual) == cast_datetime_part_date(logs[1]):

                    resta = time_actual - logs[1]
                    date_time_actual = cast_datetime_part_date(time_actual)
                    agente_en_lista = filter(lambda x: x.agente == date_time_actual,
                                             agente_fecha)
                    if agente_en_lista:
                        agente_nuevo = agente_en_lista[0]
                        if agente_nuevo.tiempo_sesion:
                            agente_nuevo._tiempo_sesion += resta
                        else:
                            agente_nuevo._tiempo_sesion = resta
                    else:
                        agente_nuevo = AgenteTiemposReporte(
                            cast_datetime_part_date(
                                time_actual), resta, 0, 0, 0, 0)
                        agente_fecha.append(agente_nuevo)
                    agente_nuevo = None
                    is_remove = False
                    time_actual = None
                else:
                    agente_nuevo = None
                    is_remove = False
                    time_actual = None
            if logs[2] == 'REMOVEMEMBER':
                time_actual = logs[1]
                is_remove = True
        return agente_fecha

    def calcular_tiempo_pausa_fecha_agente(self, agente, fecha_inferior,
                                           fecha_superior, agente_fecha):
        """ Calcula el tiempo de pausa teniendo en cuenta los eventos PAUSEALL,
        UNPAUSEALL y REMOVEMEMBER por fecha dia a dia para el agente"""

        eventos_pausa = ['PAUSEALL', 'UNPAUSEALL', 'REMOVEMEMBER']

        logs_time = ActividadAgenteLog.objects.obtener_tiempos_event_agentes(
            eventos_pausa,
            fecha_inferior,
            fecha_superior,
            [agente.id])

        time_actual = None
        is_unpause = False
        for logs in logs_time:
            agente_nuevo = None

            if is_unpause and logs[2] == 'PAUSEALL':
                if cast_datetime_part_date(
                        time_actual) == cast_datetime_part_date(logs[1]):
                    resta = time_actual - logs[1]
                    date_time_actual = cast_datetime_part_date(time_actual)
                    agente_en_lista = filter(lambda x: x.agente == date_time_actual,
                                             agente_fecha)
                    if agente_en_lista:
                        agente_nuevo = agente_en_lista[0]
                        if agente_nuevo.tiempo_pausa:
                            agente_nuevo._tiempo_pausa += resta
                        else:
                            agente_nuevo._tiempo_pausa = resta
                    else:
                        agente_nuevo = AgenteTiemposReporte(
                            cast_datetime_part_date(
                                time_actual), None, resta, 0, 0, 0)
                        agente_fecha.append(agente_nuevo)
                is_unpause = False
                time_actual = None

            if logs[2] == 'UNPAUSEALL' or logs[2] == 'REMOVEMEMBER':
                time_actual = logs[1]
                is_unpause = True
        return agente_fecha

    def calcular_tiempo_llamada_agente_fecha(self, agente, fecha_inferior,
                                             fecha_superior, agente_fecha):
        """ Calcula el tiempo de llamada teniendo en cuenta los eventos
        COMPLETECALLER y COMPLETEAGENT, por fecha dia a dia para el agente"""

        eventos_llamadas = ['COMPLETECALLER', 'COMPLETEAGENT']

        logs_time = LlamadaLog.objects.obtener_tiempo_llamada_agente(
            eventos_llamadas,
            fecha_inferior,
            fecha_superior,
            agente.id)

        for log in logs_time:

            date_time_actual = cast_datetime_part_date(log.time)
            agente_en_lista = filter(lambda x: x.agente == date_time_actual,
                                     agente_fecha)
            if agente_en_lista:
                agente_nuevo = agente_en_lista[0]
                if agente_nuevo._tiempo_llamada:
                    agente_nuevo._tiempo_llamada += log.duracion_llamada
                    agente_nuevo._cantidad_llamadas_procesadas += 1
                else:
                    agente_nuevo._tiempo_llamada = log.duracion_llamada
                    agente_nuevo._cantidad_llamadas_procesadas = 1
            else:
                agente_nuevo = AgenteTiemposReporte(
                    date_time_actual, None, None, log.duracion_llamada, 1, 0)
                agente_fecha.append(agente_nuevo)
        return agente_fecha

    def calcular_intentos_fallidos_fecha_agente(self, agente, fecha_inferior,
                                                fecha_superior, agente_fecha):
        """ Calcula la cantidad de intentos fallido para el tipo de llamada
        Manual NO CONNECT(NOANSWER, CANCEL, BUSY, CHANUNAVAIL, FAIL, OTHER,
        AMD, BLACKLIST) por fecha dia a dia para el agente"""

        eventos_llamadas = ['NOANSWER', 'CANCEL', 'BUSY', 'CHANUNAVAIL',
                            'FAIL', 'OTHER', 'AMD', 'BLACKLIST']

        logs_time = LlamadaLog.objects.obtener_count_evento_agente_agrupado_fecha(
            eventos_llamadas,
            fecha_inferior,
            fecha_superior,
            agente.id)
        for log in logs_time:
            date_time_actual = log[0]
            agente_en_lista = filter(lambda x: x.agente == date_time_actual,
                                     agente_fecha)
            if agente_en_lista:
                agente_nuevo = agente_en_lista[0]
                agente_nuevo._cantidad_intentos_fallidos = int(log[1])
            else:
                agente_nuevo = AgenteTiemposReporte(
                    date_time_actual, None, 0, 0, 0, int(log[1]))
                agente_fecha.append(agente_nuevo)
        return agente_fecha

    def generar_por_fecha_agente(self, agente, fecha_inferior, fecha_superior):
        """generar las estadisticas de los tiempos del agente"""
        agente_fecha = []
        agente_fecha = self.calcular_tiempo_session_fecha_agente(
            agente, fecha_inferior, fecha_superior, agente_fecha)
        agente_fecha = self.calcular_tiempo_pausa_fecha_agente(
            agente, fecha_inferior, fecha_superior, agente_fecha)
        agente_fecha = self.calcular_tiempo_llamada_agente_fecha(
            agente, fecha_inferior, fecha_superior, agente_fecha
        )
        agente_fecha = self.calcular_intentos_fallidos_fecha_agente(
            agente, fecha_inferior, fecha_superior, agente_fecha
        )
        return agente_fecha

    def calcular_tiempo_pausa_tipo_fecha(self, agente, fecha_inferior, fecha_superior):
        """
        Calcula el tiempo de pausa de los agentes en el periodo evaluado
        :return: un listado de agentes con el tiempo de pausa
        """
        eventos_pausa = ['PAUSEALL', 'UNPAUSEALL', 'REMOVEMEMBER']

        agentes_tiempo = []
        # iterar por agente evaluando los eventos de pausa
        logs_time = ActividadAgenteLog.objects.obtener_tiempos_event_agentes(
            eventos_pausa,
            fecha_inferior,
            fecha_superior,
            [agente.id])

        is_unpause = False
        time_actual = None
        tiempos_pausa = {}

        # iterar los log teniendo en cuenta que si encuentra un evento
        # UNPAUSEALL/REMOVEMEMBER y luego un PAUSEALL calcula el tiempo de session

        for logs in logs_time:
            if is_unpause and logs[2] == 'PAUSEALL':
                if cast_datetime_part_date(time_actual) == cast_datetime_part_date(logs[1]):
                    resta = time_actual - logs[1]
                    id_pausa = logs[3]
                    time_actual = cast_datetime_part_date(time_actual)
                    if (id_pausa, time_actual) in tiempos_pausa.keys():
                        tiempos_pausa[id_pausa] += resta
                    else:
                        tiempos_pausa.update({(time_actual, id_pausa): resta})
                    is_unpause = False
                    time_actual = None
                else:
                    is_unpause = False
                    time_actual = None
            if logs[2] == 'UNPAUSEALL' or logs[2] == 'REMOVEMEMBER':
                time_actual = logs[1]
                is_unpause = True
        for item in tiempos_pausa:
            datos_de_pausa = self._obtener_datos_de_pausa(item[1])
            tiempo = str(timezone.timedelta(seconds=tiempos_pausa[item].seconds))
            tiempo_agente = {
                'fecha': item[0],
                'pausa': datos_de_pausa['nombre'],
                'tipo_de_pausa': datos_de_pausa['tipo'],
                'tiempo': tiempo,
                'pausa_id': item[1]
            }
            agentes_tiempo.append(tiempo_agente)

        return agentes_tiempo
