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

import logging as _logging

from collections import defaultdict
from datetime import datetime

from asterisk.manager import Manager, ManagerSocketException, ManagerAuthException, ManagerException

from django.conf import settings
from django.db.models import Avg, Count
from django.utils.encoding import force_text

from ominicontacto_app.models import Campana, OpcionCalificacion, CalificacionCliente
from reportes_app.models import LlamadaLog
from ominicontacto_app.utiles import datetime_hora_maxima_dia, datetime_hora_minima_dia

logger = _logging.getLogger(__name__)


class ReporteDeLlamadasDeSupervision(object):
    def __init__(self, user_supervisor):
        query_campanas = self._obtener_campanas(user_supervisor)
        self.campanas = {}
        for campana in query_campanas:
            self.campanas[campana.id] = campana

        hoy = datetime.now()
        self.desde = datetime_hora_minima_dia(hoy)
        self.hasta = datetime_hora_maxima_dia(hoy)

        self.estadisticas = {}
        self._contabilizar_estadisticas_de_llamadas()
        self._contabilizar_gestiones()

    def _inicializar_conteo_de_campana(self, campana):
        datos_campana = self.INICIALES.copy()
        datos_campana['nombre'] = force_text(campana.nombre)
        self.estadisticas[campana.id] = datos_campana

    def _contabilizar_gestiones(self):
        # Contabilizo las gestiones
        calificaciones = CalificacionCliente.objects.filter(
            fecha__gte=self.desde,
            fecha__lte=self.hasta,
            opcion_calificacion__campana_id__in=self.campanas.keys(),
            opcion_calificacion__tipo=OpcionCalificacion.GESTION
        ).values('opcion_calificacion__campana_id').annotate(
            cantidad=Count('opcion_calificacion__campana_id'))

        for cantidad in calificaciones:
            campana_id = cantidad['opcion_calificacion__campana_id']
            if campana_id not in self.estadisticas:
                self._inicializar_conteo_de_campana(self.campanas[campana_id])
            self.estadisticas[campana_id]['gestiones'] = cantidad['cantidad']

    def _contabilizar_estadisticas_de_llamadas(self):
        logs = self._obtener_logs_de_llamadas()
        for log in logs:
            if log.campana_id not in self.estadisticas:
                self._inicializar_conteo_de_campana(self.campanas[log.campana_id])
            estadisticas_campana = self.estadisticas[log.campana_id]
            self._contabilizar_tipos_de_llamada_por_campana(estadisticas_campana, log)

    @property
    def INICIALES(self):
        raise NotImplementedError

    def _obtener_campanas(user_supervisor):
        raise NotImplementedError

    def _obtener_logs_de_llamadas(self):
        raise NotImplementedError

    def _contabilizar_tipos_de_llamada_por_campana(self, datos_campana, log):
        raise NotImplementedError


class ReporteDeLLamadasEntrantesDeSupervision(ReporteDeLlamadasDeSupervision):
    INICIALES = {
        'recibidas': 0,
        'atendidas': 0,
        'expiradas': 0,
        'abandonadas': 0,
        'abandonadas_anuncio': 0,
        't_promedio_espera': 0,
        'en_cola': 0,
        'gestiones': 0,
    }
    EVENTOS_LLAMADA = ['ENTERQUEUE', 'ENTERQUEUE-TRANSFER', 'CONNECT', 'EXITWITHTIMEOUT', 'ABANDON',
                       'ABANDONWEL']

    def __init__(self, user_supervisor):
        super(ReporteDeLLamadasEntrantesDeSupervision, self).__init__(user_supervisor)
        self._contabilizar_llamadas_en_espera_por_campana()
        self._contabilizar_llamadas_promedio_espera()

    def _obtener_campanas(self, user_supervisor):
        campanas = Campana.objects.obtener_all_activas_finalizadas()
        campanas = campanas.filter(type=Campana.TYPE_ENTRANTE)
        if not user_supervisor.get_is_administrador():
            return Campana.objects.obtener_campanas_vista_by_user(campanas, user_supervisor)
        else:
            return campanas

    def _obtener_logs_de_llamadas(self):
        return LlamadaLog.objects.filter(time__gte=self.desde,
                                         time__lte=self.hasta,
                                         campana_id__in=self.campanas.keys(),
                                         event__in=self.EVENTOS_LLAMADA,
                                         tipo_llamada=LlamadaLog.LLAMADA_ENTRANTE)

    def _contabilizar_tipos_de_llamada_por_campana(self, datos_campana, log):
        if log.event == 'ENTERQUEUE':
            datos_campana['recibidas'] += 1
        elif log.event == 'ENTERQUEUE-TRANSFER':
            datos_campana['recibidas'] += 1
        elif log.event == 'CONNECT':
            datos_campana['atendidas'] += 1
        elif log.event == 'EXITWITHTIMEOUT':
            datos_campana['expiradas'] += 1
        elif log.event == 'ABANDON':
            datos_campana['abandonadas'] += 1
        elif log.event == 'ABANDONWEL':
            datos_campana['abandonadas_anuncio'] += 1
            datos_campana['recibidas'] += 1

    def _parsear_queue_status_pasada_1(self, queue_status_raw):
        # almacenamos una lista de pares con la información del tipo de evento
        # y la cola relacionada
        events_info = []
        event_queue = []
        for line in queue_status_raw.split('\n'):
            if line.startswith('Event'):
                event_queue.append(line)
            elif line.startswith('Queue'):
                event_queue.append(line)
                events_info.append(event_queue)
                event_queue = []
        return events_info

    def _parsear_queue_status_pasada_2(self, lista_queue_status):
        llamadas_en_cola_por_campana = defaultdict(int)
        for event in lista_queue_status:
            if event[0].find('QueueEntry') > -1:
                # obtenemos el id de la campana desde entradas como:
                # u'Queue: 29_Dialer-3\r'
                campana_id = int(event[1].split(' ')[1].split('_')[0])
                llamadas_en_cola_por_campana[campana_id] += 1
        return llamadas_en_cola_por_campana

    def _obtener_llamadas_en_espera_raw(self):
        manager = Manager()
        ami_manager_user = settings.ASTERISK['AMI_USERNAME']
        ami_manager_pass = settings.ASTERISK['AMI_PASSWORD']
        ami_manager_host = str(settings.OML_ASTERISK_HOSTNAME.replace('root@', ''))
        queue_status_raw = {}
        try:
            manager.connect(ami_manager_host)
            manager.login(ami_manager_user, ami_manager_pass)
            queue_status_raw = manager.send_action({"Action": "QueueStatus"}).data

        except ManagerSocketException as e:
            logger.exception("Error connecting to the manager: {0}".format(e.message))
        except ManagerAuthException as e:
            logger.exception("Error logging in to the manager: {0}".format(e.message))
        except ManagerException as e:
            logger.exception("Error {0}".format(e.message))
        finally:
            manager.close()
            return queue_status_raw

    def _obtener_llamadas_en_espera(self):
        queue_status_raw = self._obtener_llamadas_en_espera_raw()
        try:
            self.llamadas_en_cola = self._parsear_queue_status_pasada_2(
                self._parsear_queue_status_pasada_1(queue_status_raw))
        except Exception as e:
            logger.exception("Error {0}".format(e.message))
            self.llamadas_en_cola = defaultdict(int)

    def _contabilizar_llamadas_en_espera_por_campana(self):
        self._obtener_llamadas_en_espera()
        for campana, llamadas_en_cola_campana in self.llamadas_en_cola.items():
            self.estadisticas[campana]['en_cola'] = llamadas_en_cola_campana

    def _contabilizar_llamadas_promedio_espera(self):
        logs_llamadas_espera = LlamadaLog.objects.entrantes_espera()
        logs_llamadas_espera_hoy = logs_llamadas_espera.filter(time__gte=self.desde,
                                                               time__lte=self.hasta)
        logs_agrupados_espera = logs_llamadas_espera_hoy.values('campana_id').annotate(
            tiempo_espera=Avg('bridge_wait_time'))
        for log_llamada in logs_agrupados_espera:
            campana_id = log_llamada['campana_id']
            promedio_espera = log_llamada['tiempo_espera']
            self.estadisticas[campana_id]['t_promedio_espera'] = promedio_espera


class ReporteDeLLamadasSalientesDeSupervision(ReporteDeLlamadasDeSupervision):
    INICIALES = {
        'efectuadas': 0,
        'conectadas': 0,
        'no_conectadas': 0,
        'gestiones': 0,
    }
    EVENTOS_LLAMADA = ('DIAL', 'CONNECT', 'ANSWER') + LlamadaLog.EVENTOS_NO_CONEXION

    def _obtener_campanas(self, user_supervisor):
        campanas = Campana.objects.obtener_all_activas_finalizadas()
        campanas = campanas.filter(type__in=[Campana.TYPE_DIALER,
                                             Campana.TYPE_PREVIEW,
                                             Campana.TYPE_MANUAL])
        if not user_supervisor.get_is_administrador():
            return Campana.objects.obtener_campanas_vista_by_user(campanas, user_supervisor)
        else:
            return campanas

    def _obtener_logs_de_llamadas(self):
        return LlamadaLog.objects.filter(time__gte=self.desde,
                                         time__lte=self.hasta,
                                         campana_id__in=self.campanas.keys(),
                                         event__in=self.EVENTOS_LLAMADA)

    def _contabilizar_tipos_de_llamada_por_campana(self, datos_campana, log):
        if log.event == 'DIAL':
            datos_campana['efectuadas'] += 1
        elif log.event in LlamadaLog.EVENTOS_NO_CONEXION:
            datos_campana['no_conectadas'] += 1
        # Si es DIALER:
        elif log.tipo_campana == Campana.TYPE_DIALER:
            # Si es CONNECT en DIALER
            if log.event == 'CONNECT':
                datos_campana['conectadas'] += 1
            elif log.event == 'ANSWER' and log.tipo_llamada == Campana.TYPE_MANUAL:
                datos_campana['conectadas'] += 1
        # Si es MANUAL o PREVIEW
        elif log.event == 'ANSWER':
            datos_campana['conectadas'] += 1
