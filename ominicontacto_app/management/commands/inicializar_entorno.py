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
import logging

from django.core.management.base import BaseCommand, CommandError

from ominicontacto_app.models import Campana, Queue, User, OpcionCalificacion
from ominicontacto_app.tests.factories import (GrupoFactory, ModuloFactory, AgenteProfileFactory,
                                               ArchivoDeAudioFactory, FormularioFactory,
                                               FieldFormularioFactory, BaseDatosContactoFactory,
                                               ContactoFactory, CampanaFactory,
                                               NombreCalificacionFactory, PausaFactory,
                                               OpcionCalificacionFactory)
from configuracion_telefonia_app.tests.factories import (RutaSalienteFactory, TroncalSIPFactory,
                                                         PatronDeDiscadoFactory,
                                                         OrdenTroncalFactory)
from configuracion_telefonia_app.regeneracion_configuracion_telefonia import (
    SincronizadorDeConfiguracionTroncalSipEnAsterisk,
    SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk)

from ominicontacto_app.services.creacion_queue import ActivacionQueueService
from ominicontacto_app.services.asterisk_service import ActivacionAgenteService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Se crean en BD valores mínimos para tener un entorno de desarrollo listo
    """

    help = "Valores mínimos para tener un entorno de desarrollo listo"

    agent_username = 'agent'
    agent_password = 'agent1*'

    def _crear_datos_entorno(self):

        admin = User.objects.filter(is_staff=True).first()

        # crear grupo
        grupo = GrupoFactory()

        # crear modulo
        modulo = ModuloFactory()

        # crear agente
        agente = AgenteProfileFactory(grupo=grupo, reported_by=admin)
        agente.modulos.add(modulo)
        agente.user.username = self.agent_username
        agente.user.set_password(self.agent_password)
        agente.sip_extension = 1000 + agente.id
        agente.user.is_agente = True
        agente.user.save()
        agente.save()

        asterisk_sip_service = ActivacionAgenteService()
        asterisk_sip_service.activar()

        # crear audio
        ArchivoDeAudioFactory()

        # crear pausa
        PausaFactory()

        # crear formulario (2 campos)
        form = FormularioFactory()
        FieldFormularioFactory.create_batch(2, formulario=form)

        # crear califs.(1 gestion y 1 normal)
        success = NombreCalificacionFactory(nombre='Success')
        angry = NombreCalificacionFactory(nombre='Hangs up angry')

        # crear BD (3 contactos)
        bd_contacto = BaseDatosContactoFactory()

        ContactoFactory.create_batch(3, bd_contacto=bd_contacto)

        # crear campaña manual
        campana_manual = CampanaFactory(
            nombre='test_manual_campaign', bd_contacto=bd_contacto, type=Campana.TYPE_MANUAL,
            reported_by=admin, es_manual=True, estado=Campana.ESTADO_ACTIVA
        )
        # crear Queue para la campaña
        Queue.objects.create(
            campana=campana_manual,
            name=campana_manual.nombre,
            maxlen=5,
            wrapuptime=5,
            servicelevel=30,
            strategy='rrmemory',
            eventmemberstatus=True,
            eventwhencalled=True,
            ringinuse=True,
            setinterfacevar=True,
            weight=0,
            wait=120
        )

        # opciones de calificacion
        OpcionCalificacionFactory(
            nombre=success.nombre, campana=campana_manual, tipo=OpcionCalificacion.GESTION)
        OpcionCalificacionFactory(
            nombre=angry.nombre, campana=campana_manual, tipo=OpcionCalificacion.NO_ACCION)

        activacion_queue_service = ActivacionQueueService()
        activacion_queue_service.activar()

        # crea un troncal y con este una ruta entrante hacia el pbx-emulator
        text_config = ("type=friend\n"
                       "host=pbx-emulator\n"
                       "defaultuser=01177660010\n"
                       "secret=OMLtraining72\n"
                       "qualify=yes\n"
                       "insecure=invite\n"
                       "context=from-pstn\n"
                       "disallow=all\n"
                       "allow=alaw\n")
        register_string = "01177660010:OMLtraining72@pbx-emulator"
        troncal_pbx_emulator = TroncalSIPFactory(
            text_config=text_config, register_string=register_string, canales_maximos=1000,
            caller_id='')
        sincronizador_troncal = SincronizadorDeConfiguracionTroncalSipEnAsterisk()
        sincronizador_troncal.regenerar_troncales(troncal_pbx_emulator)
        ruta_saliente = RutaSalienteFactory(ring_time=25, dial_options="Tt")
        PatronDeDiscadoFactory(ruta_saliente=ruta_saliente, match_pattern="X.")
        OrdenTroncalFactory(ruta_saliente=ruta_saliente, orden=0, troncal=troncal_pbx_emulator)
        sincronizador_ruta_saliente = SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk()
        sincronizador_ruta_saliente.regenerar_rutas_salientes(ruta_saliente)

    def handle(self, *args, **options):
        try:
            self._crear_datos_entorno()
        except Exception as e:
            logging.error('Fallo del comando: {0}'.format(e.message))
            raise CommandError('Fallo del comando: {0}'.format(e.message))
