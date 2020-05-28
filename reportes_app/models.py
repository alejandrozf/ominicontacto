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

from django.db import models, connection
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.core.exceptions import SuspiciousOperation
from django.utils.translation import ugettext as _

from ominicontacto_app.models import Campana
from ominicontacto_app.utiles import datetime_hora_minima_dia, datetime_hora_maxima_dia


class QueueLog(models.Model):
    """ Tabla queue_log para la insercion de Logs desde Asterisk """
    # time character varying(26) DEFAULT NULL::character varying,
    time = models.CharField(max_length=100, blank=True, null=True, default=None)
    # callid character varying(32) DEFAULT ''::character varying NOT NULL,
    callid = models.CharField(max_length=100, blank=True, null=False, default='')
    # queuename character varying(32) DEFAULT ''::character varying NOT NULL,
    queuename = models.CharField(max_length=100, blank=True, default='')
    # agent character varying(32) DEFAULT ''::character varying NOT NULL,
    agent = models.CharField(max_length=100, blank=True, default='')
    # event character varying(32) DEFAULT ''::character varying NOT NULL,
    event = models.CharField(max_length=100, blank=True, default='')
    # data1 character varying(100) DEFAULT ''::character varying NOT NULL,
    data1 = models.CharField(max_length=100, blank=True, default='')
    # data2 character varying(100) DEFAULT ''::character varying NOT NULL,
    data2 = models.CharField(max_length=100, blank=True, default='')
    # data3 character varying(100) DEFAULT ''::character varying NOT NULL,
    data3 = models.CharField(max_length=100, blank=True, default='')
    # data4 character varying(100) DEFAULT ''::character varying NOT NULL,
    data4 = models.CharField(max_length=100, blank=True, default='')
    # data5 character varying(100) DEFAULT ''::character varying NOT NULL
    data5 = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        db_table = 'queue_log'


class LlamadaLogManager(models.Manager):

    def obtener_tiempo_llamadas_agente(self, eventos, fecha_desde, fecha_hasta, agentes):
        if fecha_desde and fecha_hasta:
            fecha_desde = datetime_hora_minima_dia(fecha_desde)
            fecha_hasta = datetime_hora_maxima_dia(fecha_hasta)

        cursor = connection.cursor()
        sql = """select agente_id, SUM(duracion_llamada::integer)
                 from reportes_app_llamadalog where time between %(fecha_desde)s and
                 %(fecha_hasta)s and event = ANY(%(eventos)s) and agente_id = ANY(%(agentes)s)
                 GROUP BY agente_id order by agente_id
        """
        params = {
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'eventos': eventos,
            'agentes': agentes,
        }

        cursor.execute(sql, params)
        values = cursor.fetchall()
        return values

    def obtener_count_evento_agente(self, eventos, fecha_desde, fecha_hasta, agentes):
        if fecha_desde and fecha_hasta:
            fecha_desde = datetime_hora_minima_dia(fecha_desde)
            fecha_hasta = datetime_hora_maxima_dia(fecha_hasta)

        cursor = connection.cursor()
        sql = """select agente_id, count(*)
                 from reportes_app_llamadalog where time between %(fecha_desde)s and
                 %(fecha_hasta)s and event = ANY(%(eventos)s) and agente_id = ANY(%(agentes)s)
                 GROUP BY agente_id order by agente_id
        """
        params = {
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'eventos': eventos,
            'agentes': agentes,
        }

        cursor.execute(sql, params)
        values = cursor.fetchall()
        return values

    def obtener_agentes_campanas_total(self, eventos, fecha_desde, fecha_hasta, agentes,
                                       campanas):

        if fecha_desde and fecha_hasta:
            fecha_desde = datetime_hora_minima_dia(fecha_desde)
            fecha_hasta = datetime_hora_maxima_dia(fecha_hasta)

        cursor = connection.cursor()
        sql = """select agente_id, campana_id, SUM(duracion_llamada::integer), Count(*)
                 from reportes_app_llamadalog where time between %(fecha_desde)s and
                 %(fecha_hasta)s and event = ANY(%(eventos)s) and agente_id = ANY(%(agentes)s)
                 and campana_id = ANY(%(campanas)s) GROUP BY agente_id, campana_id order by
                 agente_id, campana_id
        """
        params = {
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'eventos': eventos,
            'agentes': agentes,
            'campanas': [campana.id for campana in campanas],
        }

        cursor.execute(sql, params)
        values = cursor.fetchall()
        return values

    def obtener_count_agente(self):
        try:
            return self.values('agente_id').annotate(
                cantidad=Count('agente_id')).order_by('agente_id')
        except LlamadaLog.DoesNotExist:
            raise (SuspiciousOperation(_("No se encontraron llamadas ")))

    def obtener_tiempo_llamada_agente(self, eventos, fecha_desde, fecha_hasta, agente_id):
        """devuelve la duracion de llamadas y fecha"""
        if fecha_desde and fecha_hasta:
            fecha_desde = datetime_hora_minima_dia(fecha_desde)
            fecha_hasta = datetime_hora_maxima_dia(fecha_hasta)

        try:
            return self.filter(agente_id=agente_id, event__in=eventos,
                               time__range=(fecha_desde, fecha_hasta))
        except LlamadaLog.DoesNotExist:
            raise (SuspiciousOperation(_("No se encontraron llamadas ")))

    def obtener_count_evento_agente_agrupado_fecha(self, eventos, fecha_desde,
                                                   fecha_hasta, agente_id):
        if fecha_desde and fecha_hasta:
            fecha_desde = datetime_hora_minima_dia(fecha_desde)
            fecha_hasta = datetime_hora_maxima_dia(fecha_hasta)

        return LlamadaLog.objects.filter(event__in=eventos, agente_id=agente_id,
                                         time__range=(fecha_desde, fecha_hasta)).annotate(
            fecha=TruncDate('time')).values('fecha').annotate(cantidad=Count('fecha'))

    def obtener_llamadas_finalizadas_del_dia(self, agente_id, fecha):
        fecha_desde = datetime_hora_minima_dia(fecha)
        fecha_hasta = datetime_hora_maxima_dia(fecha)
        return self.filter(agente_id=agente_id,
                           time__gte=fecha_desde, time__lte=fecha_hasta,
                           event__in=LlamadaLog.EVENTOS_FIN_CONEXION)

    def entrantes_espera(self):
        campanas_eliminadas_ids = list(
            Campana.objects.obtener_borradas().values_list('pk', flat=True))
        ids_llamadas_entrantes = list(self.filter(
            tipo_campana=Campana.TYPE_ENTRANTE, event='ENTERQUEUE').values_list(
                'callid', flat=True).exclude(campana_id__in=campanas_eliminadas_ids))
        logs = self.filter(callid__in=ids_llamadas_entrantes, event='CONNECT')
        return logs

    def entrantes_abandono(self):
        campanas_eliminadas_ids = list(
            Campana.objects.obtener_borradas().values_list('pk', flat=True))
        return self.filter(
            tipo_campana=Campana.TYPE_ENTRANTE,
            tipo_llamada=LlamadaLog.LLAMADA_ENTRANTE,
            event__in=['ABANDON', 'ABANDONWEL']).exclude(
                campana_id__in=campanas_eliminadas_ids)


class LlamadaLog(models.Model):
    """
    Define la estructura de un evento de log de cola relacionado con una llamada
    """

    # Tipos de llamada
    LLAMADA_MANUAL = 1
    LLAMADA_DIALER = 2
    LLAMADA_ENTRANTE = 3
    LLAMADA_PREVIEW = 4
    LLAMADA_CLICK2CALL = 6
    LLAMADA_TRANSFER_INTERNA = 8
    LLAMADA_TRANSFER_EXTERNA = 9

    TIPOS_LLAMADAS_SALIENTES = (LLAMADA_MANUAL, LLAMADA_PREVIEW, LLAMADA_CLICK2CALL)

    EVENTOS_NO_CONTACTACION = ('NOANSWER', 'CANCEL', 'BUSY', 'CHANUNAVAIL', 'FAIL', 'OTHER',
                               'BLACKLIST', 'CONGESTION', 'NONDIALPLAN')

    EVENTOS_NO_DIALOGO = ('ABANDON', 'EXITWITHTIMEOUT', 'AMD', 'ABANDONWEL')

    EVENTOS_NO_CONEXION = EVENTOS_NO_CONTACTACION + EVENTOS_NO_DIALOGO

    # Eventos que indican que no se pudo completar una transferencia
    EVENTOS_NO_CONEXION_TRANSFER = [
        'BT-BUSY', 'BT-CANCEL', 'BT-CHANUNAVAIL', 'BT-CONGESTION', 'BT-NOANSWER', 'BT-ABANDON',
        'CT-DISCARD', 'CT-BUSY', 'CT-CANCEL', 'CT-CHANUNAVAIL', 'CT-CONGESTION',
        'BTOUT-BUSY', 'BTOUT-CANCEL', 'BTOUT-CONGESTION', 'BTOUT-CHANUNAVAIL', 'BTOUT-ABANDON',
        'CTOUT-DISCARD', 'CTOUT-BUSY', 'CTOUT-CANCEL', 'CTOUT-CHANUNAVAIL', 'CTOUT-CONGESTION'
    ]

    # Eventos que marcan el fin de la conexion con un agente. (Puede ser por conectar con otro)
    EVENTOS_FIN_CONEXION = ['COMPLETEAGENT', 'COMPLETEOUTNUM',
                            'BT-TRY', 'COMPLETE-BT',
                            'CAMPT-COMPLETE', 'CAMPT-FAIL', 'COMPLETE-CAMPT',
                            'CT-COMPLETE', 'COMPLETE-CT',
                            'BTOUT-TRY',
                            'CTOUT-COMPLETE', ]

    # Marcan el fin de la conexion por una transferencia para el agente original
    EVENTOS_FIN_CONEXION_POR_TRANSFER = ['BT-TRY', 'BTOUT-TRY',
                                         'CAMPT-COMPLETE', 'CAMPT-FAIL',
                                         'CT_COMPLETE', 'CTOUT-COMPLETE']

    EVENTOS_INICIO_CONEXION = ['CONNECT', 'ANSWER', 'BT-ANSWER', 'CT-ACCEPT']  # Con id_agente

    # EVENTOS_TRANSFER_TRY_IN = ['BT-TRY', 'ENTERQUEUE-TRANSFER', 'CT-TRY']
    # EVENTOS_TRANSFER_TRY_OUT = ['BTOUT-TRY', 'CTOUT-TRY']
    # EVENTOS_TRANSFER_TRY = EVENTOS_TRANSFER_TRY_IN + EVENTOS_TRANSFER_TRY_OUT
    # EVENTOS_TRANSFER_OK = ['BT-ANSWER', 'CONNECT', 'CT-ACCEPT', 'BTOUT-ANSWER', 'CTOUT-ACCEPT']
    # EVENTOS_BT_NO_CONNECT = ['BT-BUSY', 'BT-CANCEL', 'BT-CHANUNAVAIL', 'BT-CONGESTION',
    #                          'BT-ABANDON', 'BT-NOANSWER']
    # EVENTOS_CT_NO_CONNECT = ['CT-DISCARD', 'CT-BUSY', 'CT-CANCEL', 'CT-CHANUNAVAIL',
    #                          'CT-CONGESTION']
    # EVENTOS_BTOUT_NO_CONNECT = ['BTOUT-BUSY', 'BTOUT-CANCEL', 'BTOUT-CONGESTION',
    #                             'BTOUT-CHANUNAVAIL', 'BTOUT-ABANDON']
    # EVENTOS_CTOUT_NO_CONNECT = ['CTOUT-DISCARD', 'CTOUT-BUSY', 'CTOUT-CANCEL',
    #                             'CTOUT-CHANUNAVAIL', 'CTOUT-CONGESTION']
    # EVENTOS_TRANSFER_FAIL = EVENTOS_BT_NO_CONNECT + ['CAMPT-FAIL'] + EVENTOS_CT_NO_CONNECT + \
    #     EVENTOS_BTOUT_NO_CONNECT

    objects = LlamadaLogManager()

    time = models.DateTimeField(db_index=True)
    callid = models.CharField(max_length=32, blank=True, null=True)
    campana_id = models.IntegerField(db_index=True, blank=True, null=True)
    tipo_campana = models.IntegerField(blank=True, null=True)
    tipo_llamada = models.IntegerField(blank=True, null=True)
    agente_id = models.IntegerField(db_index=True, blank=True, null=True)
    event = models.CharField(max_length=32, blank=True, null=True)
    numero_marcado = models.CharField(max_length=128, blank=True, null=True)
    contacto_id = models.IntegerField(blank=True, null=True)
    bridge_wait_time = models.IntegerField(blank=True, null=True)
    duracion_llamada = models.IntegerField(blank=True, null=True)
    archivo_grabacion = models.CharField(max_length=100, blank=True, null=True)

    # campos sólo para algunos logs transferencias
    agente_extra_id = models.IntegerField(db_index=True, blank=True, null=True)
    campana_extra_id = models.IntegerField(db_index=True, blank=True, null=True)
    numero_extra = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return "Log de llamada con fecha {0} con id de campaña {1} con id de agente {2} " \
               "con el evento {3} ".format(self.time, self.campana_id,
                                           self.agente_id, self.event)


class ActividadAgenteLogManager(models.Manager):
    """
    Manager de actividadAgenteLog
    """

    def obtener_tiempos_event_agentes(self, eventos, fecha_desde, fecha_hasta,
                                      agentes):

        if fecha_desde and fecha_hasta:
            fecha_desde = datetime_hora_minima_dia(fecha_desde)
            fecha_hasta = datetime_hora_maxima_dia(fecha_hasta)

        cursor = connection.cursor()
        sql = """select agente_id, time, event, pausa_id
                 from reportes_app_actividadagentelog where
                 time between %(fecha_desde)s and %(fecha_hasta)s and
                 event = ANY(%(eventos)s) and agente_id = ANY(%(agentes)s)
                 order by agente_id, time desc
        """
        params = {
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'eventos': eventos,
            'agentes': agentes,

        }

        cursor.execute(sql, params)
        values = cursor.fetchall()
        return values

    def obtener_pausas_por_agente_fechas_pausa(self, fecha_desde,
                                               fecha_hasta, agente_id, pausa_id):
        """Devuelve todas las pausas del agente por una pausa en particular"""
        if fecha_desde and fecha_hasta:
            fecha_desde = datetime_hora_minima_dia(fecha_desde)
            fecha_hasta = datetime_hora_maxima_dia(fecha_hasta)
        try:
            es_evento_pausa = Q(event__in=['PAUSEALL', 'UNPAUSEALL'], pausa_id=pausa_id)
            es_evento_sesion = Q(event='REMOVEMEMBER')
            return self.filter(agente_id=agente_id, time__range=(fecha_desde, fecha_hasta)).filter(
                es_evento_pausa | es_evento_sesion).order_by('-time')

        except ActividadAgenteLog.DoesNotExist:
            raise (SuspiciousOperation(_("No se encontraron pausas ")))


class ActividadAgenteLog(models.Model):
    """
    Define la estructura de un evento de log de cola relacionado con la actividad de un agente
    """

    objects = ActividadAgenteLogManager()

    time = models.DateTimeField(db_index=True)
    agente_id = models.IntegerField(db_index=True, blank=True, null=True)
    event = models.CharField(max_length=32, blank=True, null=True)
    pausa_id = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return "Log de actividad agente con fecha {0} para agente de id {1} con el evento {2} " \
               "con id de pausa {3}".format(self.time, self.agente_id,
                                            self.event, self.pausa_id)
