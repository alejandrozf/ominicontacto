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

"""
Tests del metodo 'ominicontacto_app.models'
"""

from __future__ import unicode_literals

import random

from mock import patch

from django.db.models import Count
from django.db import connections
from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.models import CalificacionCliente, Campana
from ominicontacto_app.services.audio_conversor import ConversorDeAudioService
from reciclado_app.resultado_contactacion import (
    EstadisticasContactacion, RecicladorContactosCampanaDIALER
)
from ominicontacto_app.tests.factories import QueueFactory, QueueMemberFactory
from reportes_app.models import LlamadaLog
from reportes_app.tests.utiles import GeneradorDeLlamadaLogs


class RecicladoTest(OMLBaseTest):

    @patch.object(ConversorDeAudioService, '_convertir_audio')
    def setUp(self, _convertir_audio):
        base_datos = self.crear_base_datos_contacto(cant_contactos=100)
        user_agente = self.crear_user_agente()
        self.agente = self.crear_agente_profile(user_agente)
        self.campana = self.crear_campana(type=Campana.TYPE_PREVIEW, bd_contactos=base_datos)
        self.queue_campana = QueueFactory(campana=self.campana)
        self.queue_member = QueueMemberFactory(member=self.agente, queue_name=self.queue_campana)
        self.estados = LlamadaLog.EVENTOS_NO_CONTACTACION
        connections['replica']._orig_cursor = connections['replica'].cursor
        connections['replica'].cursor = connections['default'].cursor

    def test_devuelve_correctamente_no_contactacion(self):

        """
        este test testea todos los resultados las cantidad de los no
        contactdos chequeando que devuelva correctamente
        """
        contactos = self.campana.bd_contacto.contactos.all()
        generador = GeneradorDeLlamadaLogs()
        cant_llamados = 100
        for _ in range(0, cant_llamados):
            contacto = random.choice(contactos)
            estado = random.choice(self.estados)
            generador.generar_log(self.campana, False, estado, contacto.telefono,
                                  self.agente, contacto)

        cantidades = {}
        for estado in self.estados:
            cantidades[EstadisticasContactacion.MAP_ESTADO_ID[estado]] = 0

        no_llamados = cant_llamados
        for contacto in contactos:
            logs = LlamadaLog.objects.filter(contacto_id=contacto.id).order_by('-id')
            if logs:
                log = logs[0]
                self.assertIn(log.event, self.estados)
                cantidades[EstadisticasContactacion.MAP_ESTADO_ID[log.event]] += 1
                no_llamados -= 1

        estadisticas = EstadisticasContactacion()
        no_contactados = estadisticas.obtener_cantidad_no_contactados(self.campana)
        for key, value in no_contactados.items():
            self.assertEqual(cantidades[key], value.cantidad)

    def test_devuelve_correctamente_calificados(self):
        """
        este test testea todos los resultados las cantidad de los
        contactdos chequeando que devuelva correctamente
        """

        contactos = self.campana.bd_contacto.contactos.all()
        opciones_calificacion = self.campana.opciones_calificacion.all()

        for contacto in contactos:
            opcion_calificacion = random.choice(opciones_calificacion)
            self.crear_calificacion_cliente(self.agente, contacto, opcion_calificacion)

        estadisticas = EstadisticasContactacion()
        calificados = estadisticas.obtener_cantidad_calificacion(self.campana)

        calificaciones_query = self.campana.obtener_calificaciones().values(
            'opcion_calificacion__nombre', 'opcion_calificacion__id').annotate(
            Count('opcion_calificacion')).filter(
            opcion_calificacion__count__gt=0).order_by()

        contactados_dict = {}
        for contactado in calificados:
            contactados_dict.update({contactado.id: contactado.cantidad})
        for contactacion in calificaciones_query:
            self.assertEquals(contactacion['opcion_calificacion__count'],
                              contactados_dict[contactacion['opcion_calificacion__id']])

    def test_obtiene_contactos_reciclados_no_contactados(self):
        reciclador = RecicladorContactosCampanaDIALER()

        # ahora vamos a chequear para los no contactados
        for estado in self.estados:
            id_estado = EstadisticasContactacion.MAP_ESTADO_ID[estado]
            no_contactados_reciclados = reciclador._obtener_contactos_no_contactados(
                self.campana, [id_estado, ])
            for contacto in no_contactados_reciclados:
                self.assertEqual(CalificacionCliente.objects.filter(
                    contacto_id=contacto.id).count(), 0)
                logs = LlamadaLog.objects.filter(contacto_id=contacto.id).order_by('-id')
                self.assertTrue(logs.count() > 0)
                self.assertEqual(logs[0].event, estado)
