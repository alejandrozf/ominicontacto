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

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from api_app.utils.routes.inbound import escribir_ruta_entrante_config

from ominicontacto_app.models import Campana, Queue, User, OpcionCalificacion, QueueMember
from ominicontacto_app.tests.factories import (GrupoFactory, AgenteProfileFactory,
                                               # ArchivoDeAudioFactory,
                                               FormularioFactory,
                                               FieldFormularioFactory, BaseDatosContactoFactory,
                                               ContactoFactory, CampanaFactory,
                                               NombreCalificacionFactory, PausaFactory,
                                               OpcionCalificacionFactory)
from configuracion_telefonia_app.tests.factories import (RutaSalienteFactory, TroncalSIPFactory,
                                                         PatronDeDiscadoFactory,
                                                         RutaEntranteFactory,
                                                         OrdenTroncalFactory)
from configuracion_telefonia_app.regeneracion_configuracion_telefonia import (
    SincronizadorDeConfiguracionTroncalSipEnAsterisk,
    SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk)

from configuracion_telefonia_app.models import DestinoEntrante

from ominicontacto_app.services.creacion_queue import ActivacionQueueService
from ominicontacto_app.services.asterisk_service import ActivacionAgenteService

from ominicontacto_app.views_queue_member import adicionar_agente_activo_cola, activar_cola

from utiles_globales import obtener_sip_agentes_sesiones_activas
from ominicontacto_app.services.asterisk.asterisk_ami import AmiManagerClient

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Se crean en BD valores mínimos para tener un entorno de desarrollo listo
    """

    help = "Valores mínimos para tener un entorno de desarrollo listo"

    agent_username = 'agent'
    agent_password = 'agent1*'

    def _crear_opciones_calificacion(self, campana):
        # opciones de calificacion
        OpcionCalificacionFactory(
            nombre=self.success.nombre, campana=campana, tipo=OpcionCalificacion.GESTION)
        OpcionCalificacionFactory(
            nombre=self.angry.nombre, campana=campana, tipo=OpcionCalificacion.NO_ACCION)

    def _asignar_agente_a_campana(self, agente, campana, penalty=0):
        try:
            client = AmiManagerClient()
            client.connect()
            with transaction.atomic():
                queue_member = QueueMember(penalty=penalty)
                queue_member_defaults = QueueMember.get_defaults(agente, campana)
                queue_member.member = agente
                queue_member.queue_name = campana.queue_campana
                queue_member.id_campana = queue_member_defaults['id_campana']
                queue_member.membername = queue_member_defaults['membername']
                queue_member.interface = queue_member_defaults['interface']
                # por ahora no definimos 'paused'
                queue_member.paused = queue_member_defaults['paused']
                queue_member.save()
                # adicionamos el agente a la cola actual que esta corriendo
                sip_agentes_logueados = obtener_sip_agentes_sesiones_activas()
                adicionar_agente_activo_cola(queue_member, campana, sip_agentes_logueados, client)
                activar_cola()
            client.disconnect()
        except Exception as e:
            print("Can't assign agent to campaign due to {0}".error(e))
            raise e

    def _crear_campana_manual(self):
        # crear campaña manual
        campana = CampanaFactory(
            nombre='test_manual_campaign', bd_contacto=self.bd_contacto,
            type=Campana.TYPE_MANUAL, reported_by=self.admin, estado=Campana.ESTADO_ACTIVA
        )
        # crear Queue para la campaña
        Queue.objects.create(
            campana=campana,
            name=campana.nombre,
            maxlen=5,
            wrapuptime=5,
            servicelevel=30,
            strategy='rrmemory',
            eventmemberstatus=True,
            eventwhencalled=True,
            ringinuse=True,
            setinterfacevar=True,
            weight=0,
            wait=120,
            auto_grabacion=True,
        )

        self._crear_opciones_calificacion(campana)

        return campana

    def _crear_campana_entrante(self):
        # crear campaña entrante
        campana = CampanaFactory(
            nombre='test_entrante_campaign', bd_contacto=self.bd_contacto,
            type=Campana.TYPE_ENTRANTE, reported_by=self.admin, estado=Campana.ESTADO_ACTIVA
        )
        # crear Queue para la campaña
        Queue.objects.create(
            campana=campana,
            name=campana.nombre,
            maxlen=5,
            timeout=3,
            retry=3,
            wrapuptime=5,
            servicelevel=30,
            strategy='rrmemory',
            eventmemberstatus=True,
            eventwhencalled=True,
            ringinuse=True,
            setinterfacevar=True,
            weight=0,
            wait=60,
            auto_grabacion=True,
        )

        self._crear_opciones_calificacion(campana)

        return campana

    def _crear_ruta_entrante(self, campana_entrante, qa_devops):
        telefono = '01177660010'
        if qa_devops:
            telefono = '99999999'
        destino_campana_entrante = DestinoEntrante.crear_nodo_ruta_entrante(
            campana_entrante)
        ruta_entrante = RutaEntranteFactory(
            telefono=telefono, destino=destino_campana_entrante, prefijo_caller_id='')
        escribir_ruta_entrante_config(self, ruta_entrante)

    def _crear_datos_entorno(self, qa_devops):

        self.admin = User.objects.filter(is_staff=True).first()

        # crear grupo
        grupo = GrupoFactory()

        # crear agente
        agente = AgenteProfileFactory(grupo=grupo, reported_by=self.admin)
        agente.user.username = self.agent_username
        agente.user.set_password(self.agent_password)
        agente.sip_extension = 1000 + agente.user.id
        agente.user.is_agente = True
        agente.user.save()
        agente.save()

        agente.user.groups.add(Group.objects.get(name='Agente'))

        asterisk_sip_service = ActivacionAgenteService()
        asterisk_sip_service.activar()

        # crear audio
        # ArchivoDeAudioFactory()

        # crear pausa
        PausaFactory()

        # crear formulario (2 campos)
        form = FormularioFactory()
        FieldFormularioFactory.create_batch(2, formulario=form)

        # crear califs.(1 gestion y 1 normal)
        self.success = NombreCalificacionFactory(nombre='Success')
        self.angry = NombreCalificacionFactory(nombre='Hangs up angry')

        # crear BD (3 contactos)
        self.bd_contacto = BaseDatosContactoFactory()

        ContactoFactory.create_batch(3, bd_contacto=self.bd_contacto)

        campana_manual = self._crear_campana_manual()
        campana_entrante = self._crear_campana_entrante()

        activacion_queue_service = ActivacionQueueService()
        activacion_queue_service.activar()

        caller_id = '01177660010'
        remote_host = 'pbxemulator:5060'
        if qa_devops:
            caller_id = '99999999'
            remote_host = '190.19.150.8:6066'

        # crea un troncal y con este una ruta entrante hacia el pbx-emulator
        text_config = ("type=wizard\n"
                       "transport=trunk-transport\n"
                       "accepts_registrations=no\n"
                       "accepts_auth=no\n"
                       "sends_registrations=yes\n"
                       "sends_auth=yes\n"
                       "endpoint/rtp_symmetric=no\n"
                       "endpoint/force_rport=no\n"
                       "endpoint/rewrite_contact=yes\n"
                       "endpoint/timers=yes\n"
                       "aor/qualify_frequency=60\n"
                       "endpoint/allow=alaw,ulaw\n"
                       "endpoint/dtmf_mode=rfc4733\n"
                       "endpoint/context=from-pstn\n"
                       "remote_hosts=" + remote_host + "\n"
                       "outbound_auth/username=" + caller_id + "\n"
                       "outbound_auth/password=omnileads\n")
        troncal_pbx_emulator = TroncalSIPFactory(
            text_config=text_config, canales_maximos=1000, tecnologia=1,
            caller_id=caller_id)
        sincronizador_troncal = SincronizadorDeConfiguracionTroncalSipEnAsterisk()
        sincronizador_troncal.regenerar_troncales(troncal_pbx_emulator)
        ruta_saliente = RutaSalienteFactory(ring_time=25, dial_options="Tt")
        PatronDeDiscadoFactory(ruta_saliente=ruta_saliente, match_pattern="X.")
        OrdenTroncalFactory(ruta_saliente=ruta_saliente, orden=0, troncal=troncal_pbx_emulator)
        sincronizador_ruta_saliente = SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk()
        sincronizador_ruta_saliente.regenerar_asterisk(ruta_saliente)

        # crear ruta entrante
        self._crear_ruta_entrante(campana_entrante, qa_devops)
        self._asignar_agente_a_campana(agente, campana_manual)
        self._asignar_agente_a_campana(agente, campana_entrante)

    def add_arguments(self, parser):
        parser.add_argument(
            '--qa-devops',
            action='store_true',
            help='Initializes with QA DEVOPS configuration',
        )

    def handle(self, *args, **options):
        qa_devops = options['qa_devops']
        if qa_devops:
            print('Initializing with QA DEVOPS configuration')
        try:
            self._crear_datos_entorno(qa_devops)
            print("Some initial data created for the OML fresh installation")
        except Exception as e:
            logging.error('Fallo del comando: {0}'.format(e))
            raise CommandError('Fallo del comando: {0}'.format(e))
