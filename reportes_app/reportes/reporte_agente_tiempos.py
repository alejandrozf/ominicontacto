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
from collections import OrderedDict
import pygal

from django.utils.translation import ugettext as _
from django.utils.timezone import now, timedelta
from reportes_app.actividad_agente_log import AgenteTiemposReporte
from reportes_app.models import ActividadAgenteLog, LlamadaLog
from reportes_app.reportes.reporte_llamadas import LLAMADA_TRANSF_INTERNA
from ominicontacto_app.models import AgenteProfile, Pausa, Campana
from pygal.style import Style
from ominicontacto_app.utiles import (
    datetime_hora_minima_dia, datetime_hora_maxima_dia, fecha_local
)

from utiles_globales import adicionar_render_unicode


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
            datos['nombre'] = _(u'ACW')
            datos['tipo'] = Pausa.CHOICE_PRODUCTIVA
        elif id_pausa == '00':
            datos['nombre'] = _(u'Supervisión')
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

        # Establezco un limite hasta al cual calcular la ultima sesion abierta
        hora_limite = now()
        hora_maxima = datetime_hora_maxima_dia(fecha_superior)
        if hora_maxima < hora_limite:
            hora_limite = hora_maxima

        TIME = 1
        EVENT = 2
        for agente in agentes:

            tiempos_agente = list(filter(lambda x: x.agente == agente, self.agentes_tiempo))
            if tiempos_agente:
                agregar_tiempos = False
                tiempos_agente = tiempos_agente[0]
            else:
                agregar_tiempos = True
                tiempos_agente = AgenteTiemposReporte(
                    agente, timedelta(0), timedelta(0), timedelta(0), 0, 0, 0, 0)

            datos_ultima_sesion = {
                'inicio': None,
                'fin': None,
            }
            logs_agente = self._filter_query_por_agente(logs_time, agente.id)
            for log in reversed(logs_agente):

                if log[EVENT] == 'REMOVEMEMBER':
                    if datos_ultima_sesion['inicio'] is None:
                        # Si la ultima sesion no esta iniciada descarto el REMOVEMEMBER.
                        pass
                    elif datos_ultima_sesion['fin'] is None:
                        # Si no esta finalizada, contabilizo la sesion.
                        datos_ultima_sesion['fin'] = log[TIME]
                        duracion = datos_ultima_sesion['fin'] - datos_ultima_sesion['inicio']
                        tiempos_agente._tiempo_sesion += duracion
                    # Si la ultima sesion ya esta finalizada, descarto el REMOVEMEMBER

                if log[EVENT] == 'ADDMEMBER':
                    # Si la ultima sesion esta iniciada
                    if datos_ultima_sesion['inicio'] is not None:
                        #  Si no esta finalizada Contabilizo una sesion. y Arranco otra.
                        if datos_ultima_sesion['fin'] is None:
                            # ATENCION: Se podria estimar mejor poniendo un maximo.
                            duracion = log[TIME] - datos_ultima_sesion['inicio']
                            tiempos_agente._tiempo_sesion += duracion
                            datos_ultima_sesion['inicio'] = log[TIME]
                            datos_ultima_sesion['fin'] = None
                        # Si esta finalizada, solamente arranco otra
                        else:
                            datos_ultima_sesion['inicio'] = log[TIME]
                            datos_ultima_sesion['fin'] = None
                    else:
                        datos_ultima_sesion['inicio'] = log[TIME]

                    # Si el ultimo log es ADDMEMBER, se ignora esa sesion.

            # Caso en que la última sesión puede estar en curso:
            if datos_ultima_sesion['inicio'] is not None and datos_ultima_sesion['fin'] is None:
                # Contabilizo duracion de sesión hasta la hora actual o fecha limite del reporte
                duracion = hora_limite - datos_ultima_sesion['inicio']
                tiempos_agente._tiempo_sesion += duracion

            if agregar_tiempos and tiempos_agente._tiempo_sesion:
                self.agentes_tiempo.append(tiempos_agente)

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

        # Establezco un limite hasta al cual calcular la ultima pausa no finalizada
        hora_limite = now()
        hora_maxima = datetime_hora_maxima_dia(fecha_superior)
        if hora_maxima < hora_limite:
            hora_limite = hora_maxima

        TIME = 1
        EVENT = 2
        for agente in agentes:
            time_actual = hora_limite

            logs_agente = self._filter_query_por_agente(logs_time, agente.id)

            for log in logs_agente:
                # Asumo que si la pausa no esta finalizada, es porque el agente esta online
                if log[EVENT] == 'PAUSEALL':
                    resta = time_actual - log[TIME]
                    agente_en_lista = list(filter(lambda x: x.agente == agente,
                                                  self.agentes_tiempo))
                    if agente_en_lista:
                        agente_nuevo = agente_en_lista[0]
                        agente_nuevo._tiempo_pausa += resta
                    else:
                        agente_nuevo = AgenteTiemposReporte(
                            agente, timedelta(0), resta, timedelta(0), 0, 0, 0, 0)
                        self.agentes_tiempo.append(agente_nuevo)
                    time_actual = log[TIME]
                if log[EVENT] == 'UNPAUSEALL' or log[EVENT] == 'REMOVEMEMBER':
                    time_actual = log[TIME]

    def calcular_tiempo_llamada(self, agentes, fecha_inferior, fecha_superior):
        """ Calcula el tiempo de llamada teniendo en cuenta los eventos
        de finalizacion de conexion con Cliente"""

        eventos_llamadas = list(LlamadaLog.EVENTOS_FIN_CONEXION)
        agentes_id = [agente.id for agente in agentes]

        logs_time = LlamadaLog.objects.obtener_tiempo_llamadas_agente(
            eventos_llamadas,
            fecha_inferior,
            fecha_superior,
            agentes_id)

        for log in logs_time:

            tiempo_llamada = timedelta(seconds=int(log[1]))
            agente = AgenteProfile.objects.get(pk=int(log[0]))
            agente_en_lista = list(filter(lambda x: x.agente == agente,
                                          self.agentes_tiempo))
            if agente_en_lista:
                agente_nuevo = agente_en_lista[0]
                agente_nuevo._tiempo_llamada = tiempo_llamada
            else:
                agente_nuevo = AgenteTiemposReporte(
                    agente, timedelta(0), timedelta(0), tiempo_llamada, 0, 0, 0, 0)
                self.agentes_tiempo.append(agente_nuevo)

    def calcular_cantidad_llamadas(self, agentes, fecha_inferior, fecha_superior):
        """ Calcula la cantidad de llamadas procesads teniendo en cuenta los
        eventos de fin de conexión con un Cliente """

        eventos_llamadas = list(LlamadaLog.EVENTOS_FIN_CONEXION)
        agentes_id = [agente.id for agente in agentes]

        logs_time = LlamadaLog.objects.obtener_count_evento_agente(
            eventos_llamadas,
            fecha_inferior,
            fecha_superior,
            agentes_id)

        for log in logs_time:
            cantidad = int(log[1])
            agente = AgenteProfile.objects.get(pk=int(log[0]))
            agente_en_lista = list(filter(lambda x: x.agente == agente,
                                          self.agentes_tiempo))
            if agente_en_lista:
                agente_nuevo = agente_en_lista[0]
                agente_nuevo._cantidad_llamadas_procesadas = cantidad
            else:
                agente_nuevo = AgenteTiemposReporte(
                    agente, timedelta(0), timedelta(0), timedelta(0), cantidad, 0, 0, 0)
                self.agentes_tiempo.append(agente_nuevo)

    def calcular_intentos_fallidos(self, agentes, fecha_inferior, fecha_superior):
        """ Calcula la cantidad de intentos fallido para el tipo de llamada
        Manual NO CONNECT(NOANSWER, CANCEL, BUSY, CHANUNAVAIL, FAIL, OTHER,
        AMD, BLACKLIST, 'CONGESTION', 'NONDIALPLAN')"""

        eventos_llamadas = list(LlamadaLog.EVENTOS_NO_CONTACTACION)
        agentes_id = [agente.id for agente in agentes]

        logs_time = LlamadaLog.objects.obtener_count_evento_agente(
            eventos_llamadas,
            fecha_inferior,
            fecha_superior,
            agentes_id)

        for log in logs_time:

            cantidad = int(log[1])
            agente = AgenteProfile.objects.get(pk=int(log[0]))
            agente_en_lista = list(filter(lambda x: x.agente == agente,
                                          self.agentes_tiempo))
            if agente_en_lista:
                agente_nuevo = agente_en_lista[0]
                agente_nuevo._cantidad_intentos_fallidos = cantidad
            else:
                agente_nuevo = AgenteTiemposReporte(
                    agente, timedelta(0), timedelta(0), timedelta(0), 0, cantidad, 0, 0)
                self.agentes_tiempo.append(agente_nuevo)

    def calcular_tiempo_pausa_tipo(self, agentes, fecha_inferior, fecha_superior):
        """
        Calcula el tiempo por tipo de pausa de los agentes en el periodo evaluado
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

        # Establezco un limite hasta al cual calcular la ultima pausa no finalizada
        hora_limite = now()
        hora_maxima = datetime_hora_maxima_dia(fecha_superior)
        if hora_maxima < hora_limite:
            hora_limite = hora_maxima

        TIME = 1
        EVENT = 2
        ID_PAUSA = 3
        for agente in agentes:

            time_actual = hora_limite
            tiempos_pausa = {}
            logs_agente = self._filter_query_por_agente(logs_time, agente.id)
            # Iterar los logs (del último al primero) y contabiliza pausas cada vez que encuentra
            # un PAUSEALL seguido de otro evento PAUSEALL, UNPAUSEALL o REMOVEMEMBER

            for log in logs_agente:
                # Asumo que si la pausa no esta finalizada, es porque el agente esta online
                if log[EVENT] == 'PAUSEALL':
                    resta = time_actual - log[TIME]
                    id_pausa = log[ID_PAUSA]
                    if id_pausa in tiempos_pausa.keys():
                        tiempos_pausa[id_pausa] += resta
                    else:
                        tiempos_pausa.update({id_pausa: resta})
                    time_actual = log[TIME]
                if log[EVENT] == 'UNPAUSEALL' or log[EVENT] == 'REMOVEMEMBER':
                    time_actual = log[TIME]
            for id_pausa in tiempos_pausa:
                datos_de_pausa = self._obtener_datos_de_pausa(id_pausa)
                tiempo = str(timedelta(seconds=tiempos_pausa[id_pausa].seconds))
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
        eventos_llamadas = list(LlamadaLog.EVENTOS_FIN_CONEXION)

        campanas = Campana.objects.obtener_actuales()
        if not user.get_is_administrador():
            supervisor = user.get_supervisor_profile()
            campanas = supervisor.campanas_asignadas_actuales()

        agentes_tiempo = []
        agentes_id = [agente.id for agente in agentes]
        logs_time = LlamadaLog.objects.obtener_agentes_campanas_total(
            eventos_llamadas, fecha_inferior, fecha_superior, agentes_id,
            campanas)

        ID_CAMPANA = 1
        SUM_DURACION = 2
        CANTIDAD = 3
        for agente in agentes:
            logs_agente = self._filter_query_por_agente(logs_time, agente.id)
            for log in logs_agente:
                tiempo_agente = []
                tiempo_agente.append(agente.user.get_full_name())
                tiempo_agente.append(self._get_nombre_campana(campanas, log[ID_CAMPANA]))
                tiempo_agente.append(str(timedelta(seconds=log[SUM_DURACION])))
                tiempo_agente.append(log[CANTIDAD])
                agentes_tiempo.append(tiempo_agente)

        return agentes_tiempo

    def _obtener_llamadas_agente(self, agentes, fecha_inferior, fecha_superior):
        """
        Obtiene el totales de llamadas por agente
        :param fecha_inferior: fecha desde cual se contabilizaran las llamadas
        :param fecha_superior: fecha hasta el cual se contabilizaran las llamadas
        :return: queryset con las cantidades totales por agente
        """
        fecha_inferior = datetime_hora_minima_dia(fecha_inferior)
        fecha_superior = datetime_hora_maxima_dia(fecha_superior)
        agentes_id = [agente.id for agente in agentes]
        eventos_llamadas = list(LlamadaLog.EVENTOS_INICIO_CONEXION)
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
        return self._obtener_cantidad_por_tipo_de_llamada(dict_agentes,
                                                          agentes,
                                                          Campana.TYPE_PREVIEW)

    def _obtener_total_dialer_agente(self, dict_agentes, agentes):
        """
        Obtiene el total grabaciones DIALER por agente en una lista
        :return: lista con el total de llamadas DIALER por agente
        """
        return self._obtener_cantidad_por_tipo_de_llamada(dict_agentes,
                                                          agentes,
                                                          Campana.TYPE_DIALER)

    def _obtener_total_inbound_agente(self, dict_agentes, agentes):
        """
        Obtiene el total grabaciones INBOUND por agente en una lista
        :return: lista con el total de llamadas INBOUND por agente
        """
        return self._obtener_cantidad_por_tipo_de_llamada(dict_agentes,
                                                          agentes,
                                                          Campana.TYPE_ENTRANTE)

    def _obtener_total_manual_agente(self, dict_agentes, agentes):
        """
        Obtiene el total grabaciones MANUAL por agente en una lista
        :return: lista con el total de llamadas MANUAL por agente
        """
        return self._obtener_cantidad_por_tipo_de_llamada(dict_agentes,
                                                          agentes,
                                                          Campana.TYPE_MANUAL)

    def _obtener_total_transferidas_agente(self, dict_agentes, agentes):
        """
        Obtiene el total de llamadas TRANSFERIDAS por agente en una lista
        :return: lista con el total de llamadas TRANSFERIDAS recibidas por agente
        """
        return self._obtener_cantidad_por_tipo_de_llamada(dict_agentes,
                                                          agentes,
                                                          LLAMADA_TRANSF_INTERNA)

    def _obtener_cantidad_por_tipo_de_llamada(self, dict_agentes, agentes, tipo_llamada):
        total = OrderedDict(zip(agentes, [0] * len(agentes)))
        for log in dict_agentes.filter(tipo_llamada=tipo_llamada):
            id_agente = log['agente_id']
            if id_agente in agentes:
                total[id_agente] = log['cantidad']
        return total.values()

    def _obtener_total_agentes_tipos_llamadas(self, agentes, fecha_inferior,
                                              fecha_superior):
        dict_agentes, nombres_agentes, ids_agentes = self._obtener_llamadas_agente(
            agentes, fecha_inferior, fecha_superior)
        total_agentes = self._obtener_total_agente_llamadas(dict_agentes, ids_agentes)
        total_preview = self._obtener_total_preview_agente(dict_agentes, ids_agentes)
        total_dialer = self._obtener_total_dialer_agente(dict_agentes, ids_agentes)
        total_inbound = self._obtener_total_inbound_agente(dict_agentes, ids_agentes)
        total_manual = self._obtener_total_manual_agente(dict_agentes, ids_agentes)
        total_transferidas = self._obtener_total_transferidas_agente(dict_agentes, ids_agentes)
        dict_agentes_llamadas = {
            'total_agentes': total_agentes,
            'total_agente_dialer': total_dialer,
            'total_agente_inbound': total_inbound,
            'total_agente_manual': total_manual,
            'total_agente_preview': total_preview,
            'total_agente_transferidas': total_transferidas,
            'nombres_agentes': nombres_agentes
        }
        return dict_agentes_llamadas

    def _generar_grafico_agentes_llamadas(self, dict_agentes_llamadas):
        # Barra: Cantidad de llamadas de los agentes por tipo de llamadas.
        barra_agente_total = pygal.Bar(show_legend=True, style=ESTILO_AZUL_ROJO_AMARILLO)
        barra_agente_total.x_labels = dict_agentes_llamadas['nombres_agentes']
        barra_agente_total.add('PREVIEW', dict_agentes_llamadas['total_agente_preview'])
        barra_agente_total.add('DIALER', dict_agentes_llamadas['total_agente_dialer'])
        barra_agente_total.add('INBOUND', dict_agentes_llamadas['total_agente_inbound'])
        barra_agente_total.add('MANUAL', dict_agentes_llamadas['total_agente_manual'])
        barra_agente_total.add('TRANSFERIDAS', dict_agentes_llamadas['total_agente_transferidas'])

        return adicionar_render_unicode(barra_agente_total)

    def generar_reportes(self, agentes, fecha_inferior, fecha_superior, user):
        """Genera las estadisticas para generar todos los reportes de los agentes"""

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
            'dict_agente_counter': list(zip(dict_agentes_llamadas['nombres_agentes'],
                                            dict_agentes_llamadas['total_agentes'],
                                            dict_agentes_llamadas['total_agente_preview'],
                                            dict_agentes_llamadas['total_agente_dialer'],
                                            dict_agentes_llamadas['total_agente_inbound'],
                                            dict_agentes_llamadas['total_agente_manual'],
                                            dict_agentes_llamadas['total_agente_transferidas'])),
            'barra_agente_total': barra_agente_total,
        }

    def _computar_tiempo_session_fecha(self, tiempos_fechas, inicio, fin):
        """ Computa la duracion de la sesion en la lista de tiempos por fecha """
        fecha_inicio = fecha_local(inicio)
        fecha_fin = fecha_local(fin)

        if tiempos_fechas and tiempos_fechas[-1].agente == fecha_inicio:
            tiempos = tiempos_fechas[-1]
        else:
            tiempos = AgenteTiemposReporte(
                fecha_inicio, timedelta(0), timedelta(0), timedelta(0), 0, 0, 0, 0)
            tiempos_fechas.append(tiempos)

        if fecha_fin == tiempos.agente:
            tiempos._tiempo_sesion += fin - inicio
        else:
            fin_dia = datetime_hora_maxima_dia(fecha_inicio)
            tiempos._tiempo_sesion += fin_dia - inicio
            inicio_dia = datetime_hora_minima_dia(fecha_fin)
            duracion = fin - inicio_dia
            tiempos = AgenteTiemposReporte(
                fecha_fin, duracion, timedelta(0), timedelta(0), 0, 0, 0, 0)
            tiempos_fechas.append(tiempos)

    def calcular_tiempo_session_fecha_agente(self, agente, fecha_inferior,
                                             fecha_superior, tiempos_fechas):
        """ Calcula el tiempo de session teniendo en cuenta los eventos
        ADDMEMBER, REMOVEMEMBER por fecha dia a dia"""

        eventos_sesion = ['ADDMEMBER', 'REMOVEMEMBER']
        logs_erroneos = False
        logs_agente = ActividadAgenteLog.objects.obtener_tiempos_event_agentes(
            eventos_sesion, fecha_inferior, fecha_superior, [agente.id])
        datos_ultima_sesion = {
            'inicio': None,
            'fin': None,
        }

        TIME = 1
        EVENT = 2
        for log in reversed(logs_agente):
            if log[EVENT] == 'REMOVEMEMBER':
                if datos_ultima_sesion['inicio'] is None:
                    logs_erroneos = True
                    # Si la ultima sesion no esta iniciada descarto el REMOVEMEMBER.
                    pass
                elif datos_ultima_sesion['fin'] is None:
                    # Si no esta finalizada, contabilizo la sesion.
                    datos_ultima_sesion['fin'] = log[TIME]
                    self._computar_tiempo_session_fecha(tiempos_fechas,
                                                        datos_ultima_sesion['inicio'],
                                                        datos_ultima_sesion['fin'])
                # Si la ultima sesion ya esta finalizada, descarto el REMOVEMEMBER

            if log[EVENT] == 'ADDMEMBER':
                # Si la ultima sesion esta iniciada
                if datos_ultima_sesion['inicio'] is not None:
                    #  Si no esta finalizada Contabilizo una sesion. y Arranco otra.
                    if datos_ultima_sesion['fin'] is None:
                        logs_erroneos = True
                        # ATENCION: Se podria estimar mejor poniendo un maximo.
                        self._computar_tiempo_session_fecha(tiempos_fechas,
                                                            datos_ultima_sesion['inicio'],
                                                            log[TIME])
                        datos_ultima_sesion['inicio'] = log[TIME]
                        datos_ultima_sesion['fin'] = None
                    # Si esta finalizada, solamente arranco otra
                    else:
                        datos_ultima_sesion['inicio'] = log[TIME]
                        datos_ultima_sesion['fin'] = None
                else:
                    datos_ultima_sesion['inicio'] = log[TIME]

        # Si la ultima sesion esta incompleta, aviso de logs erroneos / sesiones incompletas.
        if datos_ultima_sesion['inicio'] is not None and datos_ultima_sesion['fin'] is None:
            logs_erroneos = True
            hora_reporte = now()
            # Contabilizo duracion de sesión hasta la hora actual
            self._computar_tiempo_session_fecha(tiempos_fechas,
                                                datos_ultima_sesion['inicio'],
                                                hora_reporte)
        return tiempos_fechas, logs_erroneos

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

        # Establezco un limite hasta al cual calcular la ultima pausa no finalizada
        hora_limite = now()
        hora_maxima = datetime_hora_maxima_dia(fecha_superior)
        if hora_maxima < hora_limite:
            hora_limite = hora_maxima

        TIME = 1
        EVENT = 2
        time_actual = hora_limite
        for log in logs_time:
            agente_nuevo = None

            # Descarto Pausas sin log de finalización
            if log[EVENT] == 'PAUSEALL':

                resta = time_actual - log[TIME]
                date_time_actual = fecha_local(time_actual)
                agente_en_lista = list(filter(lambda x: x.agente == date_time_actual,
                                              agente_fecha))
                if agente_en_lista:
                    agente_nuevo = agente_en_lista[0]
                    agente_nuevo._tiempo_pausa += resta
                else:
                    agente_nuevo = AgenteTiemposReporte(
                        fecha_local(time_actual), timedelta(0), resta, timedelta(0), 0, 0, 0, 0)
                    agente_fecha.append(agente_nuevo)
                time_actual = log[TIME]

            if log[EVENT] == 'UNPAUSEALL' or log[EVENT] == 'REMOVEMEMBER':
                time_actual = log[TIME]
        return agente_fecha

    def calcular_tiempo_llamada_agente_fecha(self, agente, fecha_inferior,
                                             fecha_superior, agente_fecha):
        """ Calcula el tiempo de llamada teniendo en cuenta los eventos
        COMPLETECALLER y COMPLETEOUTNUM, por fecha dia a dia para el agente"""

        eventos_llamadas = list(LlamadaLog.EVENTOS_FIN_CONEXION)

        logs_time = LlamadaLog.objects.obtener_tiempo_llamada_agente(
            eventos_llamadas,
            fecha_inferior,
            fecha_superior,
            agente.id)

        for log in logs_time:

            date_time_actual = fecha_local(log.time)
            agente_en_lista = list(filter(lambda x: x.agente == date_time_actual,
                                          agente_fecha))
            duracion_llamada = timedelta(seconds=log.duracion_llamada)
            if agente_en_lista:
                agente_nuevo = agente_en_lista[0]
                agente_nuevo._tiempo_llamada += duracion_llamada
                agente_nuevo._cantidad_llamadas_procesadas += 1
            else:
                agente_nuevo = AgenteTiemposReporte(
                    date_time_actual, timedelta(0), timedelta(0), duracion_llamada, 1, 0, 0, 0)
                agente_fecha.append(agente_nuevo)
        return agente_fecha

    def calcular_intentos_fallidos_fecha_agente(self, agente, fecha_inferior,
                                                fecha_superior, agente_fecha):
        """ Calcula la cantidad de intentos fallido para el tipo de llamada
        Manual NO CONNECT(NOANSWER, CANCEL, BUSY, CHANUNAVAIL, FAIL, OTHER,
        AMD, BLACKLIST, 'CONGESTION', 'NONDIALPLAN') por fecha dia a dia para el agente"""

        eventos_llamadas = list(LlamadaLog.EVENTOS_NO_CONTACTACION)

        logs_time = LlamadaLog.objects.obtener_count_evento_agente_agrupado_fecha(
            eventos_llamadas,
            fecha_inferior,
            fecha_superior,
            agente.id)
        for log in logs_time:
            date_time_actual = log['fecha']
            agente_en_lista = list(filter(lambda x: x.agente == date_time_actual,
                                          agente_fecha))
            if agente_en_lista:
                agente_nuevo = agente_en_lista[0]
                agente_nuevo._cantidad_intentos_fallidos = int(log['cantidad'])
            else:
                agente_nuevo = AgenteTiemposReporte(
                    date_time_actual, timedelta(0), timedelta(0), timedelta(0),
                    0, int(log['cantidad']), 0, 0)
                agente_fecha.append(agente_nuevo)
        return agente_fecha

    def generar_por_fecha_agente(self, agente, fecha_inferior, fecha_superior):
        """generar las estadisticas de los tiempos del agente"""
        agente_fecha = []
        agente_fecha, error = self.calcular_tiempo_session_fecha_agente(
            agente, fecha_inferior, fecha_superior, agente_fecha)
        agente_fecha = self.calcular_tiempo_pausa_fecha_agente(
            agente, fecha_inferior, fecha_superior, agente_fecha)
        agente_fecha = self.calcular_tiempo_llamada_agente_fecha(
            agente, fecha_inferior, fecha_superior, agente_fecha
        )
        agente_fecha = self.calcular_intentos_fallidos_fecha_agente(
            agente, fecha_inferior, fecha_superior, agente_fecha
        )
        return agente_fecha, error

    def calcular_tiempo_pausa_tipo_fecha(self, agente, fecha_inferior,
                                         fecha_superior, pausa_id):
        """
        Calcula el tiempo de pausa de los agentes en el periodo evaluado
        :return: un listado de agentes con el tiempo de pausa
        """
        agentes_tiempo = []
        # iterar por agente evaluando los eventos de pausa
        logs_time = ActividadAgenteLog.objects.obtener_pausas_por_agente_fechas_pausa(
            fecha_inferior,
            fecha_superior,
            agente.id)

        # Establezco un limite hasta al cual calcular la ultima pausa no finalizada
        hora_limite = now()
        hora_maxima = datetime_hora_maxima_dia(fecha_superior)
        if hora_maxima < hora_limite:
            hora_limite = hora_maxima

        time_actual = hora_limite
        tiempos_pausa = {}

        # iterar los log teniendo en cuenta que si encuentra un evento
        # UNPAUSEALL/REMOVEMEMBER y luego un PAUSEALL calcula el tiempo de session

        for log in logs_time:
            # Descarto otras Pausas, pero las tengo en cuenta para contabilizar finalizaciones
            if log.event == 'PAUSEALL' and log.pausa_id != pausa_id:
                time_actual = log.time
            # Descarto Pausas sin log de finalización
            elif log.event == 'PAUSEALL':
                resta = time_actual - log.time
                fecha_pausa = fecha_local(time_actual)
                if fecha_pausa in tiempos_pausa.keys():
                    tiempos_pausa[fecha_pausa] += resta
                else:
                    tiempos_pausa.update({fecha_pausa: resta})
                time_actual = log.time
            if log.event == 'UNPAUSEALL' or log.event == 'REMOVEMEMBER':
                time_actual = log.time
        for item in tiempos_pausa:
            datos_de_pausa = self._obtener_datos_de_pausa(str(pausa_id))
            tiempo = str(timedelta(seconds=tiempos_pausa[item].seconds))
            tiempo_agente = {
                'fecha': item,
                'pausa': datos_de_pausa['nombre'],
                'tipo_de_pausa': datos_de_pausa['tipo'],
                'tiempo': tiempo,
            }
            agentes_tiempo.append(tiempo_agente)

        return agentes_tiempo
