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

import copy
import datetime
import json

from django.utils.timezone import now, localtime, timedelta
from django.utils.translation import ugettext as _

from reportes_app.models import LlamadaLog
from reportes_app.reportes.reporte_agentes import ReporteAgentes

from ominicontacto_app.utiles import datetime_hora_maxima_dia, datetime_hora_minima_dia
from ominicontacto_app.models import (CalificacionCliente, AgenteProfile, Campana, User,
                                      Pausa)

from ominicontacto_app.services.asterisk.redis_database import AbstractRedisChanelPublisher

import logging as _logging

logger = _logging.getLogger(__name__)


class ReporteActividadAgente:

    def __init__(self):
        self.pausa = timedelta()
        self.sesion = timedelta()
        self.pausa_recreativa = timedelta()

    def _to_dict(self):
        seconds_pausa = self.pausa.total_seconds()
        seconds_sesion = self.sesion.total_seconds()

        result = {
            'pausa': seconds_pausa,
            'sesion': seconds_sesion,
        }
        result['tiempo_pausa'] = _("{0} hs".format(
            str(self.pausa_recreativa - datetime.timedelta(
                microseconds=self.pausa_recreativa.microseconds))))
        return result


class ReporteEstadisticasDiariaAgente(object):

    EVENTOS_REPORTE = ['ENTERQUEUE', 'ENTERQUEUE-TRANSFER', 'CONNECT', 'DIAL', 'ANSWER']

    CANTIDAD_LOGS = 10

    def _obtener_logs_de_llamadas(self):
        return LlamadaLog.objects.filter(time__gte=self.desde,
                                         time__lte=self.hasta,
                                         event__in=self.EVENTOS_REPORTE).order_by('-time')

    def _obtener_estadisticas_calificacion(self):
        return CalificacionCliente.objects.filter(
            fecha__gte=self.desde, fecha__lte=self.hasta).select_related(
                'auditoriacalificacion', 'agente', 'opcion_calificacion')

    def __init__(self):
        self.calificaciones_dict = {}
        self.estadisticas_dict_base = {
            'conectadas': {
                'total': 0,
                'salientes': 0,
                'entrantes': 0
            },
            'venta': {
                'total': 0,
                'observadas': 0
            },
            'logs': [],
        }
        self.estadisticas = {}
        self.callids_entrantes = set()
        self.callids_salientes = set()
        hoy = localtime(now())
        self.desde = datetime_hora_minima_dia(hoy)
        self.hasta = datetime_hora_maxima_dia(hoy)
        self.inicializar_estadisticas()
        self.logs_llamadas = list(self._obtener_logs_de_llamadas())
        self.calificaciones = list(self._obtener_estadisticas_calificacion())
        self.calcular_estadisticas()

    def inicializar_estadisticas(self):
        for agente in AgenteProfile.objects.obtener_activos():
            self.estadisticas[agente.pk] = copy.deepcopy(self.estadisticas_dict_base.copy())
            self.estadisticas[agente.pk]['tiempos'] = ReporteActividadAgente()
            self.estadisticas[agente.pk]['pausas'] = []

    def _calcular_pausas(self, info_agente):
        tipo_pausa = info_agente['tipo_de_pausa']
        self.estadisticas[info_agente['id']]['pausas'].append(
            {'nombre': info_agente['pausa'].nombre,
             'valor': info_agente['tiempo']})

        if tipo_pausa == Pausa.CHOICE_RECREATIVA:
            tiempo_datetime = datetime.datetime.strptime(info_agente['tiempo'], "%H:%M:%S")
            tiempo_pausa = timedelta(
                hours=tiempo_datetime.hour, minutes=tiempo_datetime.minute,
                seconds=tiempo_datetime.second)
            self.estadisticas[info_agente['id']]['tiempos'].pausa_recreativa += tiempo_pausa

    def contabilizar_estadisticas_actividad(self):
        hoy_ahora = datetime.datetime.today()
        hoy = hoy_ahora.date()
        agentes = AgenteProfile.objects.obtener_activos().prefetch_related('user')
        admin = User.objects.filter(is_staff=True).first()
        reporte_agentes = ReporteAgentes(user=admin).devuelve_reporte_agentes(agentes, hoy, hoy)
        for reporte_agente in reporte_agentes['agentes_tiempos']:
            self.estadisticas[reporte_agente.agente.pk]['tiempos'].sesion += \
                reporte_agente.tiempo_sesion
            self.estadisticas[reporte_agente.agente.pk]['tiempos'].pausa += \
                reporte_agente.tiempo_pausa
        for reporte_pausas_agente in reporte_agentes['agente_pausa']:
            self._calcular_pausas(reporte_pausas_agente)

    def adicionar_log(
            self, numero_marcado, callid, agente_id, campana_id, tipo_campana, contacto_id):
        numero_marcado = numero_marcado
        datos = ''
        es_gestion = ''
        calificacion_nombre = ''
        observaciones = ''
        auditoria_status = ''
        actions = ''
        calificacion = self.calificaciones_dict.get(callid, False)
        if calificacion:
            actions = {
                'calificacionId': calificacion.pk,
                'contactoId': calificacion.contacto_id,
                'campanaId': campana_id
            }
            datos = calificacion.contacto.datos
            es_gestion = calificacion.opcion_calificacion.es_gestion()
            calificacion_nombre = calificacion.opcion_calificacion.nombre
            auditoria = calificacion.obtener_auditoria()
            if auditoria:
                auditoria_status = auditoria.get_resultado_display()
            if es_gestion and calificacion.respuesta_formulario_gestion.exists():
                respuesta_formulario_gestion = calificacion.respuesta_formulario_gestion.first()
                actions['gestionId'] = respuesta_formulario_gestion.pk
            observaciones = calificacion.observaciones
        linea_log = {'phone': numero_marcado,
                     'data': datos,
                     'engaged': es_gestion,
                     'callDisposition': calificacion_nombre,
                     'comments': observaciones,
                     'audit': auditoria_status,
                     'actions': actions,
                     'campana_id': campana_id,
                     'contacto_id': contacto_id,
                     'tipo_campana': tipo_campana
                     }
        self.estadisticas[agente_id]['logs'].append(linea_log)

    def contabilizar_estadisticas_conectadas(
            self, tipo_campana, tipo_llamada, numero_marcado, callid, evento, agente_id,
            campana_id, contacto_id):
        # Si el log no corresponde a un agente activo lo ignoro.
        if agente_id not in self.estadisticas:
            return
        if evento == 'ANSWER' and tipo_campana != Campana.TYPE_DIALER:
            if len(self.estadisticas[agente_id]['logs']) < self.CANTIDAD_LOGS:
                self.adicionar_log(numero_marcado, callid, agente_id, campana_id, tipo_campana,
                                   contacto_id)
            self.estadisticas[agente_id]['conectadas']['total'] += 1
            self.estadisticas[agente_id]['conectadas']['salientes'] += 1
        if evento == 'CONNECT':
            if len(self.estadisticas[agente_id]['logs']) < self.CANTIDAD_LOGS:
                self.adicionar_log(numero_marcado, callid, agente_id, campana_id, tipo_campana,
                                   contacto_id)
            self.estadisticas[agente_id]['conectadas']['total'] += 1
            if tipo_llamada == LlamadaLog.LLAMADA_ENTRANTE:
                self.estadisticas[agente_id]['conectadas']['entrantes'] += 1
            elif tipo_llamada in LlamadaLog.TIPOS_LLAMADAS_SALIENTES:
                self.estadisticas[agente_id]['conectadas']['salientes'] += 1

    def contabilizar_estadisticas_calificaciones(self, calificacion):
        self.calificaciones_dict[calificacion.callid] = calificacion
        agente_id = calificacion.agente.pk
        if calificacion.opcion_calificacion.es_gestion():
            if agente_id not in self.estadisticas:
                return
            self.estadisticas[agente_id]['venta']['total'] += 1
        if calificacion.obtener_auditoria() and calificacion.tiene_auditoria_observada():
            if agente_id not in self.estadisticas:
                return
            self.estadisticas[agente_id]['venta']['observadas'] += 1

    def calcular_estadisticas(self):
        self.contabilizar_estadisticas_actividad()
        for calificacion in self.calificaciones:
            self.contabilizar_estadisticas_calificaciones(calificacion)

        for log_llamada in self.logs_llamadas:
            callid = log_llamada.callid
            evento = log_llamada.event
            agente_id = log_llamada.agente_id
            tipo_campana = log_llamada.tipo_campana
            tipo_llamada = log_llamada.tipo_llamada
            numero_marcado = log_llamada.numero_marcado
            contacto_id = log_llamada.contacto_id
            campana_id = log_llamada.campana_id
            self.contabilizar_estadisticas_conectadas(
                tipo_campana, tipo_llamada, numero_marcado, callid, evento, agente_id,
                campana_id, contacto_id)


class ReporteDiarioAgentesFamily(AbstractRedisChanelPublisher):

    def _create_dict(self, family_member):
        return family_member[1]

    def _obtener_todos(self):
        reporte = ReporteEstadisticasDiariaAgente()
        reporte_resultados = []
        for agente_id, datos in reporte.estadisticas.items():
            datos['tiempos'] = json.dumps(datos['tiempos']._to_dict())
            datos['conectadas'] = json.dumps(datos['conectadas'])
            datos['logs'] = json.dumps(datos['logs'])
            datos['venta'] = json.dumps(datos['venta'])
            datos['pausas'] = json.dumps(datos['pausas'])
            reporte_resultados.append((agente_id, datos))
        return reporte_resultados

    def _get_nombre_family(self, family_member):
        task_id = 'dashboard1'
        channel = "{0}:{1}:{2}".format(self.get_nombre_families(), family_member[0], task_id)
        return channel

    def get_nombre_families(self):
        return "OML:AGENT_REPORT:CURRENT_DAY_STATS"

    def regenerar_families(self):
        """regenera la family"""
        self._delete_tree_family()
        self._create_families()

    def regenerar_family(self, family_member):
        """regenera una family"""
        self.delete_family(family_member)
        self._create_family(family_member)
