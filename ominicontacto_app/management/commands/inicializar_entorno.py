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
from django.conf import settings
from constance import config as constance_config
from api_app.utils.routes.inbound import escribir_ruta_entrante_config
from ominicontacto_app.services.queue_member_service import QueueMemberService

from ominicontacto_app.models import (Campana, Queue, User, OpcionCalificacion,
                                      SupervisorProfile, ClienteWebPhoneProfile)
from ominicontacto_app.tests.factories import (GrupoFactory, AgenteProfileFactory,
                                               # ArchivoDeAudioFactory,
                                               ActuacionVigenteFactory,
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

logger = logging.getLogger(__name__)

PASSWORD = '098098ZZZ'


class Command(BaseCommand):
    """
    Se crean en BD valores mínimos para tener un entorno de desarrollo listo
    """

    help = "Valores mínimos para tener un entorno de desarrollo listo"

    def _crear_opciones_calificacion(self, campana):
        # opciones de calificacion
        OpcionCalificacionFactory(
            nombre=self.success.nombre, campana=campana, tipo=OpcionCalificacion.GESTION)
        OpcionCalificacionFactory(
            nombre=self.angry.nombre, campana=campana, tipo=OpcionCalificacion.NO_ACCION)
        OpcionCalificacionFactory(
            nombre=settings.CALIFICACION_REAGENDA, campana=campana, tipo=OpcionCalificacion.AGENDA)

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
            type=Campana.TYPE_DIALER, reported_by=self.admin, estado=Campana.ESTADO_ACTIVA,
            tiempo_desconexion=10
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
        ActuacionVigenteFactory(campana=campana, domingo=True, sabado=True,
                                hora_desde='00:00', hora_hasta='23:59:59')

        return campana

    def _crear_campana_preview(self, nombre_campana, bd_contacto, es_template=False):
        # crear campaña preview
        estado = Campana.ESTADO_ACTIVA
        if es_template:
            estado = Campana.ESTADO_TEMPLATE_ACTIVO
        campana = CampanaFactory(
            nombre=nombre_campana, bd_contacto=bd_contacto,
            type=Campana.TYPE_PREVIEW, reported_by=self.admin, estado=estado
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

        if not es_template:
            campana.establecer_valores_iniciales_agente_contacto(False, False)

        return campana

    def _crear_ruta_entrante(self, campana_entrante, telefono):
        destino_campana_entrante = DestinoEntrante.crear_nodo_ruta_entrante(
            campana_entrante)
        ruta_entrante = RutaEntranteFactory(
            telefono=telefono, destino=destino_campana_entrante, prefijo_caller_id='')
        escribir_ruta_entrante_config(self, ruta_entrante)

    def _crear_agentes(self, cantidad, grupo):
        # Crea un minimo de 2 agentes
        cantidad = max(2, cantidad)
        agentes_creados = []
        for i in range(0, cantidad):
            username = f'ag{i+1}'
            agente = self._crear_agente(grupo, username, PASSWORD)
            agentes_creados.append(agente)
        asterisk_sip_service = ActivacionAgenteService()
        asterisk_sip_service.activar()

        return agentes_creados

    def _crear_agente(self, grupo, username, password):
        agente = AgenteProfileFactory(grupo=grupo, reported_by=self.admin)
        agente.user.username = username
        agente.user.set_password(password)
        agente.sip_extension = 1000 + agente.user.id
        agente.user.is_agente = True
        agente.user.save()
        agente.save()
        agente.user.groups.add(Group.objects.get(name='Agente'))
        return agente

    def _crear_gerente(self, username):
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

    def _crear_supervisores(self, cantidad):
        for i in range(0, cantidad):
            username = f'ftsup{i+1}'
            self._crear_supervisor(username)

    def _crear_supervisor(self, username):
        user = User.objects.create_user(
            username=username,
            email=username + '@example.com',
            password=PASSWORD,
            is_supervisor=True,
            first_name=username,
            last_name=username
        )
        user.groups.set([Group.objects.get(name=User.SUPERVISOR)])
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
            first_name='WebphoneClient',
            last_name=username,
            is_cliente_webphone=True
        )
        user.groups.set([Group.objects.get(name=User.CLIENTE_WEBPHONE)])
        cliente_webphone = ClienteWebPhoneProfile(user=user, sip_extension=1000 + user.id)
        cliente_webphone.save()
        return user

    def _crear_dbs_contactos(self):
        # crear BD default (100 contactos)
        self.bd_contacto = BaseDatosContactoFactory()
        ContactoFactory.create_batch(100, bd_contacto=self.bd_contacto)

        # Crear DBs Preview
        metadata = '{"cant_col": 4, "cols_telefono": [0], ' + \
            '"nombres_de_columnas": ["telefono", "nombre", "direccion", "localidad"]}'
        self.bd_contacto_prw1 = BaseDatosContactoFactory(
            nombre='PRW1', nombre_archivo_importacion='',
            metadata=metadata, cantidad_contactos=7
        )
        ContactoFactory(bd_contacto=self.bd_contacto_prw1, telefono='123456721',
                        datos='["Jorge Success", "CORD", "SANLUIS"]')
        ContactoFactory(bd_contacto=self.bd_contacto_prw1, telefono='88887777',
                        datos='["Luis Blacklist","CATAMARCASUR178","SANJUAN"]')
        ContactoFactory(bd_contacto=self.bd_contacto_prw1, telefono='9999',
                        datos='["Graciela No Route","NAVARROSUR1132S","SANJUAN"]')
        ContactoFactory(bd_contacto=self.bd_contacto_prw1, telefono='123456729',
                        datos='["Alfredo Congestion","ABERASTAINSUR655","SANJUAN"]')
        ContactoFactory(bd_contacto=self.bd_contacto_prw1, telefono='123456725',
                        datos='["Oscar No Answer","CATAMARCASUR178","SANJUAN"]')
        ContactoFactory(bd_contacto=self.bd_contacto_prw1, telefono='123456720',
                        datos='["Cecilia Busy","CATAMARCASUR178","SANJUAN"]')
        ContactoFactory(bd_contacto=self.bd_contacto_prw1, telefono='123456725',
                        datos='["Ricardo Cancel","ABERASTAINSUR655","SANJUAN"]')

        self.bd_contacto_prw_success = BaseDatosContactoFactory(
            nombre='PRW1-SUCCESS', nombre_archivo_importacion='',
            metadata=metadata, cantidad_contactos=7
        )
        ContactoFactory(bd_contacto=self.bd_contacto_prw_success, telefono='123456721',
                        datos='["Jorge Success", "CORD", "SANLUIS"]')
        ContactoFactory(bd_contacto=self.bd_contacto_prw_success, telefono='123456731',
                        datos='["Luis Blacklist","CATAMARCASUR178","SANJUAN"]')
        ContactoFactory(bd_contacto=self.bd_contacto_prw_success, telefono='123456741',
                        datos='["Graciela No Route","NAVARROSUR1132S","SANJUAN"]')
        ContactoFactory(bd_contacto=self.bd_contacto_prw_success, telefono='123456751',
                        datos='["Alfredo Congestion","ABERASTAINSUR655","SANJUAN"]')
        ContactoFactory(bd_contacto=self.bd_contacto_prw_success, telefono='123456761',
                        datos='["Oscar No Answer","CATAMARCASUR178","SANJUAN"]')
        ContactoFactory(bd_contacto=self.bd_contacto_prw_success, telefono='123456771',
                        datos='["Cecilia Busy","CATAMARCASUR178","SANJUAN"]')
        ContactoFactory(bd_contacto=self.bd_contacto_prw_success, telefono='123456781',
                        datos='["Ricardo Cancel","ABERASTAINSUR655","SANJUAN"]')

    def _crear_datos_entorno(self, qa_devops, qa_agents, qa_supervisors):

        self.admin = User.objects.filter(is_staff=True).first()
        self.gerente = self._crear_gerente('gerente')
        self.cliente_webphone = self._crear_cliente_webphone('webphone_user')
        self._crear_supervisores(max(0, qa_supervisors))

        # crear grupo
        grupo = GrupoFactory(auto_unpause=0)

        agentes_creados = self._crear_agentes(qa_agents, grupo)
        agentes_base = [agentes_creados[0], agentes_creados[1]]

        if not os.getenv('WEBPHONE_CLIENT_VERSION', '') == '':
            constance_config.WEBPHONE_CLIENT_ENABLED = True

        asterisk_sip_service = ActivacionAgenteService()
        asterisk_sip_service.activar()

        # crear audio
        # ArchivoDeAudioFactory()

        # crear pausa
        PausaFactory(nombre="break", tipo='R')
        PausaFactory(nombre="gestion", tipo='P')
        PausaFactory(nombre="Pausa_0", tipo='P')

        # crear formulario (2 campos)
        form = FormularioFactory()
        FieldFormularioFactory.create_batch(2, formulario=form)

        # crear califs.(1 gestion y 1 normal)
        self.success = NombreCalificacionFactory(nombre='Success')
        self.success = NombreCalificacionFactory(nombre='ventas_Lee PLC')
        self.angry = NombreCalificacionFactory(nombre='hangup')

        self._crear_dbs_contactos()

        # Crear campañas
        campana_manual = self._crear_campana_manual('test_manual_01')
        campana_entrante = self._crear_campana_entrante('test_entrante_01')
        campana_entrante_2 = self._crear_campana_entrante('test_entrante_02')
        campana_entrante_2.videocall_habilitada = True
        campana_entrante_2.save()
        campana_dialer = self._crear_campana_dialer('test_dialer_01')
        campana_preview = self._crear_campana_preview('test_preview_01', self.bd_contacto)
        self._crear_campana_preview('PRW_TEMPLATE', self.bd_contacto_prw1, True)
        self._crear_campana_preview('PRW_SUCCESS_TEMPLATE', self.bd_contacto_prw_success, True)

        activacion_queue_service = ActivacionQueueService()
        activacion_queue_service.activar()

        caller_id = '01177660010'
        remote_host = 'pbxemulator:5070'
        if qa_devops:
            caller_id = '99999999'
            remote_host = '190.19.150.8:6066'

        # crea un troncal y con este una ruta entrante hacia el pbx-emulator
        text_config = (
            "type=wizard\n"
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
            ";external_media_address=****Container engine Host IP -> OML****\n"
            ";external_signaling_address=****Container engine Host IP -> OML****\n"
            ";external_signaling_port=****Container engine Host port forward -> OML****\n"
            "endpoint/context=from-pstn\n"
            "remote_hosts=" + remote_host + "\n"
            "outbound_auth/username=" + caller_id + "\n"
            "endpoint/from_user=" + caller_id + "\n"
            "outbound_auth/password=omnileads\n")
        troncal_pbx_emulator = TroncalSIPFactory(
            text_config=text_config, canales_maximos=1000, tecnologia=1,
            caller_id=caller_id)
        sincronizador_troncal = SincronizadorDeConfiguracionTroncalSipEnAsterisk()
        sincronizador_troncal.regenerar_troncales(troncal_pbx_emulator)
        ruta_saliente = RutaSalienteFactory(ring_time=25, dial_options="Tt")
        PatronDeDiscadoFactory(ruta_saliente=ruta_saliente, match_pattern="1234567[0-9][0-9]")
        PatronDeDiscadoFactory(ruta_saliente=ruta_saliente, match_pattern="88887777")
        OrdenTroncalFactory(ruta_saliente=ruta_saliente, orden=0, troncal=troncal_pbx_emulator)
        sincronizador_ruta_saliente = SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk()
        sincronizador_ruta_saliente.regenerar_asterisk(ruta_saliente)

        # crear rutas entrantes
        self._crear_ruta_entrante(campana_entrante, '99999999' if qa_devops else '01177660010')
        self._crear_ruta_entrante(campana_entrante_2, '01177660011')

        # Asigno agentes a campañas (no entrantes)
        queue_service = QueueMemberService()
        campanas = [campana_manual, campana_dialer, campana_preview]

        for campana in campanas:
            queue_service.agregar_agentes_en_cola(campana, agentes_base)
        # Asigno 1 Agente por campaña entrante
        queue_service.agregar_agentes_en_cola(campana_entrante, (agentes_base[0], ))
        queue_service.agregar_agentes_en_cola(campana_entrante, (agentes_base[1], ))

        # Luego de agregar los agentes refresco datos en asterisk
        queue_service.activar_cola()

        # Asigno campañas a gerente
        campanas.extend([campana_entrante, campana_entrante_2])
        self.gerente.campanasupervisors.set(campanas)

    def add_arguments(self, parser):
        parser.add_argument(
            '--qa-devops',
            action='store_true',
            help='Initializes with QA DEVOPS configuration',
        )
        parser.add_argument(
            '--qa-agents',
            type=int,
            default=2,
            required=False,
            action='store',
            help='Initializes with many Agents and Supervisors',
        )
        parser.add_argument(
            '--qa-supervisors',
            type=int,
            default=0,
            required=False,
            action='store',
            help='Initializes with many Agents and Supervisors',
        )

    def handle(self, *args, **options):
        qa_devops = options['qa_devops']
        qa_agents = options['qa_agents']
        qa_supervisors = options['qa_supervisors']
        if qa_devops:
            print('Initializing with QA DEVOPS configuration')
        try:
            self._crear_datos_entorno(qa_devops, qa_agents, qa_supervisors)
            print("Some initial data created for the OML fresh installation")
        except Exception as e:
            logging.error('Fallo del comando: {0}'.format(e))
            raise CommandError('Fallo del comando: {0}'.format(e))
