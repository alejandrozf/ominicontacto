# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models, connection
from django.db.models import Count
from django.core.exceptions import SuspiciousOperation
from ominicontacto_app.utiles import datetime_hora_minima_dia, datetime_hora_maxima_dia


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
            raise (SuspiciousOperation("No se encontro llamadas "))

    def obtener_tiempo_llamada_agente(self, eventos, fecha_desde, fecha_hasta, agente_id):
        """devuelve la duracion de llamadas y fecha"""
        if fecha_desde and fecha_hasta:
            fecha_desde = datetime_hora_minima_dia(fecha_desde)
            fecha_hasta = datetime_hora_maxima_dia(fecha_hasta)

        try:
            return self.filter(agente_id=agente_id, event__in=eventos,
                               time__range=(fecha_desde, fecha_hasta))
        except LlamadaLog.DoesNotExist:
            raise (SuspiciousOperation("No se encontro llamadas "))


class LlamadaLog(models.Model):
    """
    Define la estructura de un evento de log de cola relacionado con una llamada
    """

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
    archivo_grabacion = models.CharField(max_length=50, blank=True, null=True)

    def __unicode__(self):
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


class ActividadAgenteLog(models.Model):
    """
    Define la estructura de un evento de log de cola relacionado con la actividad de un agente
    """

    objects = ActividadAgenteLogManager()

    time = models.DateTimeField(db_index=True)
    agente_id = models.IntegerField(db_index=True, blank=True, null=True)
    event = models.CharField(max_length=32, blank=True, null=True)
    pausa_id = models.CharField(max_length=128, blank=True, null=True)

    def __unicode__(self):
        return "Log de actividad agente con fecha {0} para agente de id {1} con el evento {2} " \
               "con data1 {3}".format(self.time, self.agente_id,
                                      self.event, self.pausa_id)
