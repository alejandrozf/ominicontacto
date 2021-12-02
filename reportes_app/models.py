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

from django.utils.timezone import now
from ominicontacto_app.utiles import crear_segmento_grabaciones_url, datetime_hora_maxima_dia, \
    datetime_hora_minima_dia, fecha_local
import urllib.parse
from django.db import models, connection
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate
from django.core.exceptions import SuspiciousOperation
from django.utils.translation import ugettext as _
from django.conf import settings

from ominicontacto_app.models import AgenteProfile, CalificacionCliente, Campana, Contacto, \
    GrabacionMarca


class QueueLog(models.Model):
    """ Tabla queue_log para la insercion de Logs desde Asterisk """
    # time character varying(26) DEFAULT NULL::character varying,
    time = models.CharField(max_length=100, blank=True,
                            null=True, default=None)
    # callid character varying(32) DEFAULT ''::character varying NOT NULL,
    callid = models.CharField(
        max_length=100, blank=True, null=False, default='')
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

        result = LlamadaLog.objects.values_list('agente_id') \
                                   .annotate(sum=Sum('duracion_llamada')) \
                                   .filter(time__gte=fecha_desde, time__lte=fecha_hasta) \
                                   .filter(event__in=eventos) \
                                   .filter(agente_id__in=agentes) \
                                   .exclude(campana_id=0) \
                                   .order_by('agente_id')

        return result

    def obtener_count_evento_agente(self, eventos, fecha_desde, fecha_hasta, agentes):
        if fecha_desde and fecha_hasta:
            fecha_desde = datetime_hora_minima_dia(fecha_desde)
            fecha_hasta = datetime_hora_maxima_dia(fecha_hasta)

        cursor = connection.cursor()
        sql = """select agente_id, count(*)
                 from reportes_app_llamadalog where time between %(fecha_desde)s and
                 %(fecha_hasta)s and event = ANY(%(eventos)s) and agente_id = ANY(%(agentes)s)
                 AND NOT campana_id = '0'
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
        """
        Query que sumariza por agente y campaña la cantidad y duración de
        llamadas para los eventos indicados.
        """

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
                                         time__range=(fecha_desde, fecha_hasta)).exclude(
            campana_id=0).annotate(
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

    def obtener_grabaciones_by_fecha_intervalo_campanas(self, fecha_inicio, fecha_fin, campanas):
        fecha_inicio = datetime_hora_minima_dia(fecha_inicio)
        fecha_fin = datetime_hora_maxima_dia(fecha_fin)
        INCLUDED_EVENTS = ['COMPLETEAGENT', 'COMPLETEOUTNUM', 'BT-COMPLETE',
                           'COMPLETE-BT', 'CT-COMPLETE', 'COMPLETE-CT', 'CAMPT-COMPLETE',
                           'COMPLETE-CAMPT', 'BTOUT-COMPLETE', 'COMPLETE-BTOUT', 'CTOUT-COMPLETE',
                           'COMPLETE-CTOUT', 'CAMPT-FAIL', 'BT-BUSY', 'BTOUT-TRY', 'CT-ABANDON',
                           'CTOUT-TRY', 'BT-TRY']

        return self.filter(time__range=(fecha_inicio, fecha_fin),
                           campana_id__in=campanas, duracion_llamada__gt=0,
                           event__in=INCLUDED_EVENTS,
                           archivo_grabacion__isnull=False).order_by('-time').\
            exclude(archivo_grabacion='-1').exclude(event='ENTERQUEUE-TRANSFER')

    def obtener_grabaciones_by_filtro(self, fecha_desde, fecha_hasta, tipo_llamada, tel_cliente,
                                      callid, id_contacto_externo, agente, campana, campanas,
                                      marcadas, duracion, gestion):
        INCLUDED_EVENTS = ['COMPLETEAGENT', 'COMPLETEOUTNUM', 'BT-COMPLETE',
                           'COMPLETE-BT', 'CT-COMPLETE', 'COMPLETE-CT', 'CAMPT-COMPLETE',
                           'COMPLETE-CAMPT', 'BTOUT-COMPLETE', 'COMPLETE-BTOUT', 'CTOUT-COMPLETE',
                           'COMPLETE-CTOUT', 'CAMPT-FAIL', 'BT-BUSY', 'BTOUT-TRY', 'CT-ABANDON',
                           'CTOUT-TRY', 'BT-TRY']
        campanas_id = [campana.id for campana in campanas]
        grabaciones = self.filter(campana_id__in=campanas_id,
                                  archivo_grabacion__isnull=False,
                                  duracion_llamada__gt=0,
                                  event__in=INCLUDED_EVENTS)

        grabaciones = grabaciones.exclude(
            archivo_grabacion='-1').exclude(event='ENTERQUEUE-TRANSFER')

        if fecha_desde and fecha_hasta:
            fecha_desde = datetime_hora_minima_dia(fecha_desde)
            fecha_hasta = datetime_hora_maxima_dia(fecha_hasta)
            grabaciones = grabaciones.filter(time__range=(fecha_desde,
                                                          fecha_hasta))
        if tipo_llamada:
            grabaciones = grabaciones.filter(tipo_llamada=tipo_llamada)
        if tel_cliente:
            grabaciones = grabaciones.filter(
                numero_marcado__contains=tel_cliente)
        if callid:
            grabaciones = grabaciones.filter(callid=callid)
        if agente:
            grabaciones = grabaciones.filter(agente_id=agente.id)
        if campana:
            if campana != 'activas' and campana != 'borradas':
                grabaciones = grabaciones.filter(campana_id=campana)

            else:
                campanas_excluidas_id = []
                for camp in campanas:
                    if (camp.estado == Campana.ESTADO_BORRADA and campana == 'activas') or \
                            (camp.estado != Campana.ESTADO_BORRADA and campana == 'borradas'):
                        campanas_excluidas_id.append(camp.pk)

                grabaciones = grabaciones.exclude(
                    campana_id__in=campanas_excluidas_id)

        if duracion and duracion > 0:
            grabaciones = grabaciones.filter(duracion_llamada__gte=duracion)
        if id_contacto_externo:
            telefonos_contacto = Contacto.objects.values('telefono')
            telefono_id_externo = telefonos_contacto.filter(
                id_externo=id_contacto_externo)
            grabaciones = grabaciones.filter(
                numero_marcado__in=[t['telefono'] for t in telefono_id_externo])
        if marcadas:
            total_grabaciones_marcadas = self.obtener_grabaciones_marcadas()
            grabaciones = grabaciones & total_grabaciones_marcadas
        if gestion:
            calificaciones_gestion_campanas = CalificacionCliente.obtener_califs_gestion_campanas(
                campanas)
            callids_calificaciones_gestion = list(calificaciones_gestion_campanas.values_list(
                'callid', flat=True))
            grabaciones = grabaciones.filter(
                callid__in=callids_calificaciones_gestion)

        return grabaciones.order_by('-time')

    def obtener_grabaciones_marcadas(self):
        marcaciones = list(GrabacionMarca.objects.values_list('callid', flat=True))
        return self.filter(callid__in=marcaciones, archivo_grabacion__isnull=False,
                           duracion_llamada__gt=0).exclude(archivo_grabacion='-1') \
            .exclude(event='ENTERQUEUE-TRANSFER')

    def obtener_evento_hold_fecha(self, eventos, fecha_desde, fecha_hasta, agente_id):
        """devuelve el hold"""
        if fecha_desde and fecha_hasta:
            fecha_desde = datetime_hora_minima_dia(fecha_desde)
            fecha_hasta = datetime_hora_maxima_dia(fecha_hasta)

        try:
            return self.filter(agente_id=agente_id, event__in=eventos,
                               time__range=(fecha_desde, fecha_hasta))
        except LlamadaLog.DoesNotExist:
            raise (SuspiciousOperation(_("No se encontraron holds ")))

    def obtener_cantidades_de_transferencias_recibidas(
            self, fecha_inicial, fecha_final, agentes, campanas_ids):
        """
            Contabiliza Transferencias directas A AGENTE. Agrupa por agente y por campaña
        """
        resultados = self.filter(
            time__range=(fecha_inicial, fecha_final),
            agente_id__in=agentes, campana_id__in=campanas_ids,
            event__in=['BT-ANSWER', 'CT-ACCEPT']).values('agente_id', 'campana_id').annotate(
                cant=Count('id')).order_by('agente_id', 'campana_id')
        cantidades = {agente_id: {} for agente_id in agentes}
        for resultado in resultados:
            cantidades[resultado['agente_id']][resultado['campana_id']] = resultado['cant']
        return cantidades

    def cantidad_contactos_llamados(self, campana):
        return self.filter(
            campana_id=campana.id,
            contacto_id__in=Contacto.objects.filter(
                bd_contacto=campana.bd_contacto,
                es_originario=True,
            ),
        ).only("id").distinct("contacto_id").count()


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

    TIPOS_LLAMADAS_SALIENTES = (
        LLAMADA_MANUAL, LLAMADA_PREVIEW, LLAMADA_CLICK2CALL)

    TYPE_LLAMADA_CHOICES = (
        (LLAMADA_DIALER, 'DIALER'),
        (LLAMADA_ENTRANTE, 'INBOUND'),
        (LLAMADA_MANUAL, 'MANUAL'),
        (LLAMADA_PREVIEW, 'PREVIEW'),
    )

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
                            'CT-COMPLETE', 'COMPLETE-CT', 'ABANDON-CT',
                            'BTOUT-TRY',
                            'CTOUT-COMPLETE', ]

    # Marcan el fin de la conexion por una transferencia para el agente original
    EVENTOS_FIN_CONEXION_POR_TRANSFER = ['BT-TRY', 'BTOUT-TRY',
                                         'CAMPT-COMPLETE', 'CAMPT-FAIL',
                                         'CT_COMPLETE', 'CTOUT-COMPLETE']

    EVENTOS_INICIO_CONEXION = ['CONNECT', 'ANSWER',
                               'BT-ANSWER', 'CT-ACCEPT']  # Con id_agente

    # eventos inicio conexion de una llamada
    # (No incluye valores de eventos de transferencias si ocurren luego)
    EVENTOS_INICIO_CONEXION_AGENTE = ['CONNECT', 'ANSWER']  # Con id_agente

    # eventos fin conexion de una llamada
    # (No incluye valores de eventos de transferencias si ocurren luego)
    EVENTOS_FIN_CONEXION_AGENTE = ['COMPLETEAGENT', 'COMPLETEOUTNUM']  # Con id_agente

    # eventos de hold en una llamada
    EVENTOS_HOLD = ['HOLD', 'UNHOLD']

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
    callid = models.CharField(db_index=True, max_length=32, blank=True, null=True)
    campana_id = models.IntegerField(db_index=True, blank=True, null=True)
    tipo_campana = models.IntegerField(blank=True, null=True)
    tipo_llamada = models.IntegerField(blank=True, null=True)
    agente_id = models.IntegerField(db_index=True, blank=True, null=True)
    event = models.CharField(max_length=32, blank=True, null=True)
    numero_marcado = models.CharField(max_length=128, blank=True, null=True)
    contacto_id = models.IntegerField(db_index=True, blank=True, null=True)
    bridge_wait_time = models.IntegerField(blank=True, null=True)
    duracion_llamada = models.IntegerField(blank=True, null=True)
    archivo_grabacion = models.CharField(max_length=100, blank=True, null=True)

    # campos sólo para algunos logs transferencias
    agente_extra_id = models.IntegerField(db_index=True, blank=True, null=True)
    campana_extra_id = models.IntegerField(
        db_index=True, blank=True, null=True)
    numero_extra = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return "Log de llamada con fecha {0} con id de campaña {1} con id de agente {2} " \
               "con el evento {3} duración {4}".format(self.time, self.campana_id,
                                                       self.agente_id, self.event,
                                                       self.duracion_llamada)

    @property
    def url_archivo_grabacion(self):
        hoy = fecha_local(now())
        dia_grabacion = fecha_local(self.time)
        filename = "/".join([crear_segmento_grabaciones_url(),
                             dia_grabacion.strftime("%Y-%m-%d"),
                             self.archivo_grabacion])
        if dia_grabacion < hoy:
            return filename + '.' + settings.MONITORFORMAT
        else:
            return filename + '.wav'

    @property
    def url_archivo_grabacion_url_encoded(self):
        # TODO: Refactorizar junto con url_archivo_grabacion para eliminar duplicidad de código
        hoy = fecha_local(now())
        dia_grabacion = fecha_local(self.time)
        filename = "/".join([crear_segmento_grabaciones_url(),
                             dia_grabacion.strftime("%Y-%m-%d"),
                             urllib.parse.quote(self.archivo_grabacion)])
        if dia_grabacion < hoy:
            return filename + '.' + settings.MONITORFORMAT
        else:
            return filename + '.wav'

    @property
    def campana(self):
        return Campana.objects.get(id=self.campana_id)

    @property
    def tipo_llamada_show(self):
        switcher = {
            1: _('Llamada manual'),
            2: _('Llamada dialer'),
            3: _('Llamada entrante'),
            4: _('Llamada preview'),
            6: _('Llamada click2call'),
            8: _('Llamada transferencia interna'),
            9: _('Llamada transferencia externa')
        }
        return switcher.get(self.tipo_llamada, None)

    @property
    def agente(self):
        return AgenteProfile.objects.get(id=self.agente_id)


class ActividadAgenteLogManager(models.Manager):
    """
    Manager de actividadAgenteLog
    """

    def obtener_tiempos_event_agentes(self, eventos, fecha_desde, fecha_hasta,
                                      agentes):

        if fecha_desde and fecha_hasta:
            fecha_desde = datetime_hora_minima_dia(fecha_desde)
            fecha_hasta = datetime_hora_maxima_dia(fecha_hasta)

        result = ActividadAgenteLog.objects.values_list('agente_id', 'time', 'event', 'pausa_id') \
                                           .filter(time__gte=fecha_desde, time__lte=fecha_hasta) \
                                           .filter(event__in=eventos) \
                                           .filter(agente_id__in=agentes) \
                                           .order_by('agente_id', '-time')

        return result

    def obtener_pausas_por_agente_fechas_pausa(self, fecha_desde,
                                               fecha_hasta, agente_id):
        """Devuelve todas las pausas del agente por una pausa en particular"""
        if fecha_desde and fecha_hasta:
            fecha_desde = datetime_hora_minima_dia(fecha_desde)
            fecha_hasta = datetime_hora_maxima_dia(fecha_hasta)
        try:
            es_evento_pausa = Q(event__in=['PAUSEALL', 'UNPAUSEALL'])
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
