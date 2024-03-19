# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3, as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

import logging
from django.db import transaction
from django.utils.translation import gettext as _
from ominicontacto_app.models import QueueMember
from ominicontacto_app.services.asterisk.asterisk_ami import (
    AMIManagerConnectorError, AmiManagerClient)
from ominicontacto_app.services.creacion_queue import ActivacionQueueService
from ominicontacto_app.services.asterisk.supervisor_activity import SupervisorActivityAmiManager

logger = logging.getLogger(__name__)


def obtener_sip_agentes_sesiones_activas():
    # TODO: Controlar cantidad de conexiones a Asterisk con AMIManagerConnector
    agentes_activos_service = SupervisorActivityAmiManager()
    agentes = list(agentes_activos_service.obtener_agentes_activos())
    sips_agentes = []
    for agente in agentes:
        if agente['status'] != 'OFFLINE':
            sips_agentes.append(int(agente['sip']))
    return sips_agentes


class QueueMemberService(object):
    """ Se encarga de manejar las asignaciones de Agentes a Campañas y mantener los datos
    en base de datos, Asterisk via AMI, y Redis
    """

    def __init__(self, ami_client=None, conectar_ami=True):
        if ami_client:
            self.ami_client = ami_client
        elif conectar_ami:
            self.ami_client = AmiManagerClient()
            self.ami_client.connect()

    def disconnect(self):
        self.ami_client.disconnect()

    def activar_cola(self):
        activacion_queue_service = ActivacionQueueService()
        activacion_queue_service.activar()

    def eliminar_agente_de_colas_asignadas(self, agente):
        # ahora vamos a remover el agente de la cola de asterisk
        sip_agentes_logueados = obtener_sip_agentes_sesiones_activas()
        if agente.sip_extension in sip_agentes_logueados:
            queues_member_agente = agente.campana_member.all()
            for queue_member in queues_member_agente:
                campana = queue_member.queue_name.campana
                self._remover_agente_cola_asterisk(campana, agente)
        # TODO: Revisar si efectivamente hace falta activar_cola al borrar agente de las colas
        self.activar_cola()
        QueueMember.objects.borrar_member_queue(agente)

    def eliminar_agentes_de_cola(self, campana, agentes):
        QueueMember.objects.filter(
            member__in=agentes,
            queue_name=campana.queue_campana).delete()
        sip_agentes_logueados = obtener_sip_agentes_sesiones_activas()
        for agente in agentes:
            if agente.sip_extension in sip_agentes_logueados:
                self._remover_agente_cola_asterisk(campana, agente)

    def _remover_agente_cola_asterisk(self, campana, agente):
        queue = campana.get_queue_id_name()
        interface = 'PJSIP/{0}'.format(agente.sip_extension)
        try:
            self.ami_client.queue_remove(queue, interface)
        except AMIManagerConnectorError:
            logger.exception(
                _('QueueRemove failed - agente: {0} de la campana: {1}'.format(
                    agente, campana)))

    def _generar_penalties_default(self, agentes):
        return {agente.id: 0 for agente in agentes}

    def agregar_agentes_en_cola(self, campana, agentes, penalties=None):
        """ PRE: si penalties != None debera tener el valor definido para cada id de agente
            en agentes """
        if penalties is None:
            penalties = self._generar_penalties_default(agentes)
        sip_agentes_logueados = obtener_sip_agentes_sesiones_activas()
        for agente in agentes:
            penalty = penalties.get(agente.id, 0)
            with transaction.atomic():
                queue_member, created = QueueMember.objects.get_or_create(
                    member=agente,
                    queue_name=campana.queue_campana,
                    defaults=QueueMember.get_defaults(agente, campana))
                queue_member.penalty = penalty
                queue_member.save()
                if agente.sip_extension in sip_agentes_logueados:
                    self._adicionar_agente_cola_asterisk(
                        agente, queue_member, campana)

    def _adicionar_agente_cola_asterisk(self, agente, queue_member, campana):
        """Adiciona agente a la cola de su respectiva campaña"""
        queue = campana.get_queue_id_name()
        interface = "PJSIP/{0}".format(agente.sip_extension)
        penalty = queue_member.penalty
        paused = queue_member.paused
        member_name = agente.get_asterisk_caller_id()
        try:
            self.ami_client.queue_add(queue, interface, penalty, paused, member_name)
        except AMIManagerConnectorError:
            logger.exception(_("QueueAdd failed - agente: {0} de la campana: {1} ".format(
                agente, campana)))

    def agregar_agente_a_campanas(self, agente, campanas, verificar_sesion_activa=False):
        """ Agrega el agente a multiples campañas """
        agregar_en_asterisk = False
        if verificar_sesion_activa:
            sip_agentes_logueados = obtener_sip_agentes_sesiones_activas()
            agregar_en_asterisk = agente.sip_extension in sip_agentes_logueados
        try:
            campanas_ids = []
            for campana in campanas:
                campanas_ids.append(campana.id)
                queue_member, created = QueueMember.objects.get_or_create(
                    member=agente,
                    penalty=0,
                    queue_name=campana.queue_campana,
                    defaults=QueueMember.get_defaults(agente, campana))
                if agregar_en_asterisk:
                    self._adicionar_agente_cola_asterisk(
                        agente, queue_member, campana)
        except Exception as e:
            logger.exception(f'Error al adicionar agente a la cola de la campaña {e.__str__()}')
