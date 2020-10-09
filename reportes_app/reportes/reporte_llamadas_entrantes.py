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
from collections import defaultdict
from django.conf import settings
from django.utils.encoding import force_text
from django.utils.timezone import now, localtime
from django.db.models import Count
from asterisk.manager import Manager, ManagerSocketException, ManagerAuthException, ManagerException

from reportes_app.models import LlamadaLog
from ominicontacto_app.utiles import datetime_hora_maxima_dia, datetime_hora_minima_dia
from ominicontacto_app.models import CalificacionCliente, Campana, OpcionCalificacion
from ominicontacto_app.services.asterisk.redis_database import AbstractRedisFamily

import logging as _logging

logger = _logging.getLogger(__name__)


class ReporteDeLLamadasEntrantesDeSupervision(object):
    INICIALES = {
        'llamadas_atendidas': 0,
        'llamadas_abandonadas': 0,
        'llamadas_expiradas': 0,
        'tiempo_acumulado_abandonadas': 0,
        'tiempo_acumulado_espera': 0,
        'gestiones': 0,
        'llamadas_en_espera': 0,
    }
    EVENTOS_LLAMADA = ['ENTERQUEUE', 'ENTERQUEUE-TRANSFER', 'CONNECT', 'EXITWITHTIMEOUT', 'ABANDON',
                       'ABANDONWEL']

    def __init__(self):
        query_campanas = Campana.objects.obtener_actuales().filter(type=Campana.TYPE_ENTRANTE)
        self.campanas = {}
        for campana in query_campanas:
            self.campanas[campana.id] = campana

        hoy = localtime(now())
        self.desde = datetime_hora_minima_dia(hoy)
        self.hasta = datetime_hora_maxima_dia(hoy)
        self.estadisticas = {}
        self._contabilizar_estadisticas_de_llamadas()
        self._contabilizar_gestiones()
        self._contabilizar_llamadas_en_espera_por_campana()

    def _contabilizar_estadisticas_de_llamadas(self):
        logs = self._obtener_logs_de_llamadas()
        for log in logs:
            if log.campana_id not in self.estadisticas:
                self._inicializar_conteo_de_campana(self.campanas[log.campana_id])
            estadisticas_campana = self.estadisticas[log.campana_id]
            self._contabilizar_tipos_de_llamada_por_campana(estadisticas_campana, log)

    def _obtener_logs_de_llamadas(self):
        return LlamadaLog.objects.filter(time__gte=self.desde,
                                         time__lte=self.hasta,
                                         campana_id__in=self.campanas.keys(),
                                         event__in=self.EVENTOS_LLAMADA,
                                         tipo_llamada=LlamadaLog.LLAMADA_ENTRANTE)

    def _inicializar_conteo_de_campana(self, campana):
        datos_campana = self.INICIALES.copy()
        datos_campana['nombre'] = force_text(campana.nombre)
        self.estadisticas[campana.id] = datos_campana

    def _contabilizar_tipos_de_llamada_por_campana(self, datos_campana, log):
        if log.event == 'CONNECT':
            datos_campana['llamadas_atendidas'] += 1
            datos_campana['tiempo_acumulado_espera'] += log.bridge_wait_time
        elif log.event == 'EXITWITHTIMEOUT':
            datos_campana['llamadas_expiradas'] += 1
        elif log.event == 'ABANDON':
            datos_campana['llamadas_abandonadas'] += 1
            datos_campana['tiempo_acumulado_abandonadas'] += log.bridge_wait_time
        elif log.event == 'ABANDONWEL':
            datos_campana['llamadas_abandonadas'] += 1
            datos_campana['tiempo_acumulado_abandonadas'] += log.bridge_wait_time

    def _contabilizar_gestiones(self):
        # Contabilizo las gestiones
        calificaciones = CalificacionCliente.objects.filter(
            fecha__gte=self.desde,
            fecha__lte=self.hasta,
            opcion_calificacion__campana_id__in=self.campanas.keys(),
            opcion_calificacion__tipo=OpcionCalificacion.GESTION
        ).values('opcion_calificacion__campana_id').annotate(
            cantidad=Count('opcion_calificacion__campana_id')).order_by()

        for cantidad in calificaciones:
            campana_id = cantidad['opcion_calificacion__campana_id']
            if campana_id not in self.estadisticas:
                self._inicializar_conteo_de_campana(self.campanas[campana_id])
            self.estadisticas[campana_id]['gestiones'] = cantidad['cantidad']

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
                if campana_id in self.campanas.keys():
                    # por si es de una dialer, en ese caso se excluye
                    llamadas_en_cola_por_campana[campana_id] += 1
        return llamadas_en_cola_por_campana

    def _obtener_llamadas_en_espera_raw(self):
        manager = Manager()
        ami_manager_user = settings.ASTERISK['AMI_USERNAME']
        ami_manager_pass = settings.ASTERISK['AMI_PASSWORD']
        ami_manager_host = str(settings.ASTERISK_HOSTNAME)
        queue_status_raw = {}
        try:
            manager.connect(ami_manager_host)
            manager.login(ami_manager_user, ami_manager_pass)
            queue_status_raw = manager.send_action({"Action": "QueueStatus"}).data

        except ManagerSocketException as e:
            logger.exception("Error connecting to the manager: {0}".format(e))
        except ManagerAuthException as e:
            logger.exception("Error logging in to the manager: {0}".format(e))
        except ManagerException as e:
            logger.exception("Error {0}".format(e))
        finally:
            manager.close()
            return queue_status_raw

    def _obtener_llamadas_en_espera(self):
        queue_status_raw = self._obtener_llamadas_en_espera_raw()
        try:
            self.llamadas_en_cola = self._parsear_queue_status_pasada_2(
                self._parsear_queue_status_pasada_1(queue_status_raw))
        except Exception as e:
            logger.exception("Error {0}".format(e))
            self.llamadas_en_cola = defaultdict(int)

    def _contabilizar_llamadas_en_espera_por_campana(self):
        self._obtener_llamadas_en_espera()
        for campana_id, llamadas_en_cola_campana in self.llamadas_en_cola.items():
            if campana_id not in self.estadisticas:
                self._inicializar_conteo_de_campana(self.campanas[campana_id])
            self.estadisticas[campana_id]['llamadas_en_espera'] = llamadas_en_cola_campana


class ReporteLlamadasEntranteFamily(AbstractRedisFamily):

    def _create_dict(self, family_member):
        return family_member[1]

    def _obtener_todos(self):
        reporte = ReporteDeLLamadasEntrantesDeSupervision()
        return [(campana_id, datos) for campana_id, datos in reporte.estadisticas.items()]

    def _get_nombre_family(self, family_member):
        return "{0}:{1}".format(self.get_nombre_families(), family_member[0])

    def get_nombre_families(self):
        return "OML:SUPERVISION_CAMPAIGN"

    def regenerar_families(self):
        """regenera la family"""
        self._delete_tree_family()
        self._create_families()

    def regenerar_family(self, family_member):
        """regenera una family"""
        self.delete_family(family_member)
        self._create_family(family_member)
