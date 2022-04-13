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

from django.utils.translation import ugettext as _
from django.utils.timezone import now, timedelta
from reportes_app.actividad_agente_log import AgenteTiemposReporte
from reportes_app.models import ActividadAgenteLog, LlamadaLog
from ominicontacto_app.utiles import datetime_hora_maxima_dia, datetime_hora_minima_dia, fecha_local
from ominicontacto_app.models import Pausa


class TiemposAgente(object):
    """
    Calculo de los tiempos del agente, session, pausas, en llamada
    """

    def __init__(self):
        self.agentes_tiempo = []

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
                        fecha_local(time_actual), timedelta(0), resta, timedelta(0), 0, 0, 0, 0,
                        timedelta(0), 0)
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
            agente.id).exclude(campana_id=0)

        campanas_ids = set()
        for log in logs_time:
            campanas_ids.add(log.campana_id)
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
                    date_time_actual, timedelta(0), timedelta(0), duracion_llamada, 1, 0, 0, 0,
                    timedelta(0), 0)
                agente_fecha.append(agente_nuevo)

        for datos_fecha in agente_fecha:
            fecha = datos_fecha.agente
            fecha_inicial = datetime_hora_minima_dia(fecha)
            fecha_final = datetime_hora_maxima_dia(fecha)
            transferencias = LlamadaLog.objects.obtener_cantidades_de_transferencias_recibidas(
                fecha_inicial, fecha_final, [agente.id], campanas_ids)
            cant_transfers = 0
            transferencias_por_camp = transferencias.get(agente.id, {})
            for cant in transferencias_por_camp.values():
                cant_transfers += cant
            datos_fecha._cantidad_llamadas_procesadas -= cant_transfers
            datos_fecha._transferidas_a_agente = cant_transfers

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
            agente.id).exclude(campana_id=0)
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
                    0, int(log['cantidad']), 0, 0, timedelta(0), 0)
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
        agente_fecha = self.calcular_tiempo_hold_tipo_fecha(agente, fecha_inferior, fecha_superior,
                                                            agente_fecha)
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

        datos_de_pausa = self._obtener_datos_de_pausa(str(pausa_id))
        for item in tiempos_pausa:
            tiempo = str(timedelta(seconds=tiempos_pausa[item].seconds))
            tiempo_agente = {
                'fecha': item,
                'pausa': datos_de_pausa['nombre'],
                'tipo_de_pausa': datos_de_pausa['tipo'],
                'tiempo': tiempo,
            }
            agentes_tiempo.append(tiempo_agente)

        return agentes_tiempo

    def calcular_tiempo_hold_tipo_fecha(self, agente, fecha_inferior,
                                        fecha_superior, agente_fecha):
        evento_hold = ['HOLD']
        evento_unhold = ['UNHOLD']
        tiempo_hold = timedelta(0)
        hold_fecha = [hold for hold in LlamadaLog.objects.obtener_evento_hold_fecha(
            evento_hold,
            fecha_inferior,
            fecha_superior,
            agente.id)]

        primer_unhold = LlamadaLog.objects.obtener_evento_hold_fecha(evento_unhold, fecha_inferior,
                                                                     fecha_superior, agente.id
                                                                     ).first()
        if hold_fecha:
            primer_hold = hold_fecha[0]
            if primer_unhold and primer_unhold.time < primer_hold.time:
                tiempo_hold += primer_unhold.time - fecha_inferior

        for log in hold_fecha:
            fecha_actual = fecha_local(log.time)
            agente_en_lista = list(filter(lambda x: x.agente == fecha_actual,
                                          agente_fecha))
            inicio_hold = log.time
            callid = log.callid
            fecha_desde = datetime_hora_minima_dia(fecha_actual)
            fecha_hasta = datetime_hora_maxima_dia(fecha_actual)
            unhold_fecha = LlamadaLog.objects.using('replica')\
                .filter(agente_id=agente.id, callid=callid,
                        event='UNHOLD', time__range=(log.time, fecha_hasta))\
                .order_by('time').first()
            if unhold_fecha:
                # Si existen varios unhold dentro de una llamada se elige el primero
                fin_hold = unhold_fecha.time
            else:
                # Si se corta la llamada sin haber podido hacer unhold o por otro motivo
                log_llamada = LlamadaLog.objects.using('replica')\
                    .filter(agente_id=agente.id, callid=callid,
                            time__range=(fecha_desde, fecha_hasta)).last()
                if log_llamada and log_llamada.event != 'HOLD':
                    fin_hold = log_llamada.time
                else:
                    fin_hold = now() \
                        if datetime_hora_maxima_dia(fecha_superior) >= now() else fecha_superior

            tiempo_hold += fin_hold - inicio_hold

            if agente_en_lista:
                agente_nuevo = agente_en_lista[0]
                agente_nuevo._tiempo_hold = tiempo_hold
            else:

                agente_nuevo = AgenteTiemposReporte(fecha_local(fecha_inferior), timedelta(0),
                                                    timedelta(0), timedelta(0), 0, 0, 0, 0,
                                                    tiempo_hold, 0)
                agente_fecha.append(agente_nuevo)
        return agente_fecha

    def _computar_tiempo_session_fecha(self, tiempos_fechas, inicio, fin):
        """ Computa la duracion de la sesion en la lista de tiempos por fecha """
        fecha_inicio = fecha_local(inicio)
        fecha_fin = fecha_local(fin)

        if tiempos_fechas and tiempos_fechas[-1].agente == fecha_inicio:
            tiempos = tiempos_fechas[-1]
        else:
            tiempos = AgenteTiemposReporte(
                fecha_inicio, timedelta(0), timedelta(0), timedelta(0),
                0, 0, 0, 0, timedelta(0), 0)
            tiempos_fechas.append(tiempos)

        if fecha_fin == tiempos.agente:
            tiempos._tiempo_sesion += fin - inicio
        else:
            fin_dia = datetime_hora_maxima_dia(fecha_inicio)
            tiempos._tiempo_sesion += fin_dia - inicio
            inicio_dia = datetime_hora_minima_dia(fecha_fin)
            duracion = fin - inicio_dia
            tiempos = AgenteTiemposReporte(
                fecha_fin, duracion, timedelta(0), timedelta(0), 0, 0, 0, 0, timedelta(0), 0)
            tiempos_fechas.append(tiempos)

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
