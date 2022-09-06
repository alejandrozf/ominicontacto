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
import os

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from constance import config as constance_config
from api_app.utils.routes.inbound import escribir_ruta_entrante_config

from ominicontacto_app.models import (Campana, Queue, User, OpcionCalificacion, QueueMember,
                                      SupervisorProfile, ClienteWebPhoneProfile)
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

PASSWORD = 'usuario0*'


class Command(BaseCommand):
    """
    Se crean en BD valores mínimos para tener un entorno de desarrollo listo
    """

    help = "Valores mínimos para tener un entorno de desarrollo listo"

    agent_1_username = 'ag1'
    agent_2_username = 'ag2'
    # agent_3_username = 'ag3'
    # agent_4_username = 'ag4'
    # agent_5_username = 'ag5'
    # agent_6_username = 'ag6'
    # agent_7_username = 'ag7'
    # agent_8_username = 'ag8'
    # agent_9_username = 'ag9'
    # agent_10_username = 'ag10'

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

    def _crear_campana_manual(self, nombre_campana):
        # crear campaña manual
        campana = CampanaFactory(
            nombre=nombre_campana, bd_contacto=self.bd_contacto,
            type=Campana.TYPE_MANUAL, reported_by=self.admin, estado=Campana.ESTADO_ACTIVA
        )
        # crear Queue para la campaña
        Queue.objects.create(
            campana=campana,
            name=campana.nombre,
            maxlen=25,
            wrapuptime=5,
            servicelevel=10,
            strategy='rrmemory',
            eventmemberstatus=True,
            eventwhencalled=True,
            ringinuse=True,
            setinterfacevar=True,
            weight=0,
            wait=25,
            auto_grabacion=True,
        )

        self._crear_opciones_calificacion(campana)

        return campana

    def _crear_campana_entrante(self, nombre_campana):
        # crear campaña entrante
        campana = CampanaFactory(
            nombre=nombre_campana, bd_contacto=self.bd_contacto,
            type=Campana.TYPE_ENTRANTE, reported_by=self.admin, estado=Campana.ESTADO_ACTIVA
        )
        # crear Queue para la campaña
        Queue.objects.create(
            campana=campana,
            name=campana.nombre,
            maxlen=25,
            timeout=12,
            retry=5,
            wrapuptime=5,
            servicelevel=10,
            strategy='rrmemory',
            eventmemberstatus=True,
            eventwhencalled=True,
            ringinuse=True,
            setinterfacevar=True,
            weight=0,
            wait=30,
            auto_grabacion=True,
        )

        self._crear_opciones_calificacion(campana)

        return campana

    def _crear_campana_dialer(self, nombre_campana):
        # crear campaña dialer
        campana = CampanaFactory(
            nombre=nombre_campana, bd_contacto=self.bd_contacto,
            type=Campana.TYPE_DIALER, reported_by=self.admin, estado=Campana.ESTADO_ACTIVA
        )
        # crear Queue para la campaña
        Queue.objects.create(
            campana=campana,
            name=campana.nombre,
            maxlen=1,
            timeout=12,
            retry=5,
            wrapuptime=5,
            servicelevel=5,
            strategy='rrmemory',
            eventmemberstatus=True,
            eventwhencalled=True,
            ringinuse=True,
            setinterfacevar=True,
            weight=0,
            wait=10,
            auto_grabacion=True,
        )

        self._crear_opciones_calificacion(campana)

        return campana

    def _crear_campana_preview(self, nombre_campana):
        # crear campaña dialer
        campana = CampanaFactory(
            nombre=nombre_campana, bd_contacto=self.bd_contacto,
            type=Campana.TYPE_PREVIEW, reported_by=self.admin, estado=Campana.ESTADO_ACTIVA
        )
        # crear Queue para la campaña
        Queue.objects.create(
            campana=campana,
            name=campana.nombre,
            maxlen=1,
            timeout=12,
            retry=5,
            wrapuptime=5,
            servicelevel=5,
            strategy='rrmemory',
            eventmemberstatus=True,
            eventwhencalled=True,
            ringinuse=True,
            setinterfacevar=True,
            weight=0,
            wait=10,
            auto_grabacion=True,
        )
        self._crear_opciones_calificacion(campana)

        campana.establecer_valores_iniciales_agente_contacto(False, False)

        return campana

    def _crear_ruta_entrante(self, campana_entrante, telefono):
        destino_campana_entrante = DestinoEntrante.crear_nodo_ruta_entrante(
            campana_entrante)
        ruta_entrante = RutaEntranteFactory(
            telefono=telefono, destino=destino_campana_entrante, prefijo_caller_id='')
        escribir_ruta_entrante_config(self, ruta_entrante)

    def _crear_agente(self, grupo, username, password):
        agente = AgenteProfileFactory(grupo=grupo, reported_by=self.admin)
        agente.user.username = username
        agente.user.set_password(password)
        agente.sip_extension = 1000 + agente.user.id
        agente.user.is_agente = True
        agente.user.save()
        agente.save()
        agente.user.groups.add(Group.objects.get(name='Agente'))
        asterisk_sip_service = ActivacionAgenteService()
        asterisk_sip_service.activar()
        return agente

    def _crear_supervisor_gerente(self, username):
        user = User.objects.create_user(
            username=username,
            email=username + '@example.com',
            password=PASSWORD,
            is_supervisor=True,
            first_name='Gerente',
            last_name=username
        )
        user.groups.set([Group.objects.get(name=User.GERENTE)])
        SupervisorProfile.objects.create(
            user=user,
            sip_extension=1000 + user.id,
            sip_password="sdsfhdfhfdhfd",
            is_administrador=False,
            is_customer=False,
        )
        return user

    def _crear_cliente_webphone(self, username):
        user = User.objects.create_user(
            username=username,
            email=username + '@example.com',
            password=PASSWORD,
            is_supervisor=False,
            first_name='Gerente',
            last_name=username
        )
        user.groups.set([Group.objects.get(name=User.CLIENTE_WEBPHONE)])
        cliente_webphone = ClienteWebPhoneProfile(user=user, sip_extension=1000 + user.id)
        cliente_webphone.save()
        return user

    def _crear_datos_entorno(self, qa_devops):

        self.admin = User.objects.filter(is_staff=True).first()
        self.gerente = self._crear_supervisor_gerente('gerente')
        self.cliente_webphone = self._crear_cliente_webphone('webphone')

        # crear grupo
        grupo = GrupoFactory()

        agentes_creados = []  # Esta lista almacenará los agentes que crees

        agent_usernames = [self.agent_1_username, self.agent_2_username]
        for username in agent_usernames:
            agente = self._crear_agente(grupo, username, PASSWORD)
            agente.user.groups.add(Group.objects.get(name='Agente'))
            agentes_creados.append(agente)

        if not os.getenv('WEBPHONE_CLIENT_VERSION', '') == '':
            constance_config.WEBPHONE_CLIENT_ENABLED = True

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

        # crear BD (100 contactos)
        self.bd_contacto = BaseDatosContactoFactory()
        ContactoFactory.create_batch(100, bd_contacto=self.bd_contacto)

        # Crear campañas
        campana_manual = self._crear_campana_manual('test_manual_01')
        campana_entrante = self._crear_campana_entrante('test_entrante_01')
        campana_entrante_2 = self._crear_campana_entrante('test_entrante_02')
        campana_entrante_2.videocall_habilitada = True
        campana_entrante_2.save()
        campana_dialer = self._crear_campana_dialer('test_dialer_01')
        campana_preview = self._crear_campana_preview('test_preview_01')

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

        # crear rutas entrantes
        self._crear_ruta_entrante(campana_entrante, '99999999' if qa_devops else '01177660010')
        self._crear_ruta_entrante(campana_entrante_2, '01177660011')

        # Asigno agentes a campañas (no entrantes)
        campanas = [campana_manual, campana_dialer, campana_preview]
        for agente in agentes_creados:
            for campana in campanas:
                self._asignar_agente_a_campana(agente, campana)
        # Asigno 1 Agente por campaña entrante
        self._asignar_agente_a_campana(agentes_creados[0], campana_entrante)
        self._asignar_agente_a_campana(agentes_creados[1], campana_entrante_2)

        # Asigno campañas a gerente
        campanas.extend([campana_entrante, campana_entrante_2])
        self.gerente.campanasupervisors.set(campanas)

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
