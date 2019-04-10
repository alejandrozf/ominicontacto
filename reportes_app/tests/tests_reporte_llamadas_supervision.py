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

from django.test import TestCase

from reportes_app.reportes.reporte_llamadas_supervision import (
    ReporteDeLLamadasEntrantesDeSupervision
)
from reportes_app.tests.utiles import GeneradorDeLlamadaLogs
from ominicontacto_app.tests.factories import (
    SupervisorProfileFactory, AgenteProfileFactory, CampanaFactory, OpcionCalificacionFactory,
    CalificacionClienteFactory
)
from ominicontacto_app.models import Campana, OpcionCalificacion


class ReporteDeLLamadasEntrantesDeSupervisionTest(TestCase):

    def setUp(self):
        super(ReporteDeLLamadasEntrantesDeSupervisionTest, self).setUp()
        self.generador = GeneradorDeLlamadaLogs()

        self.supervisor = SupervisorProfileFactory()
        self.agente1 = AgenteProfileFactory()

        self.entrante1 = CampanaFactory.create(type=Campana.TYPE_ENTRANTE, nombre='camp-entrante-1',
                                               estado=Campana.ESTADO_ACTIVA,
                                               supervisors=[self.supervisor.user])
        self.opcion_calificacion = OpcionCalificacionFactory(campana=self.entrante1,
                                                             tipo=OpcionCalificacion.GESTION)
        self.entrante2 = CampanaFactory.create(type=Campana.TYPE_ENTRANTE, nombre='camp-entrante-2',
                                               estado=Campana.ESTADO_ACTIVA)

    def test_reporte_vacio(self):
        reporte = ReporteDeLLamadasEntrantesDeSupervision(self.supervisor.user)
        self.assertIn(self.entrante1.id, reporte.estadisticas)
        self.assertEqual(reporte.estadisticas[self.entrante1.id]['recibidas'], 0)
        self.assertEqual(reporte.estadisticas[self.entrante1.id]['atendidas'], 0)
        self.assertEqual(reporte.estadisticas[self.entrante1.id]['expiradas'], 0)
        self.assertEqual(reporte.estadisticas[self.entrante1.id]['abandonadas'], 0)
        self.assertEqual(reporte.estadisticas[self.entrante1.id]['gestiones'], 0)
        self.assertNotIn(self.entrante2.id, reporte.estadisticas)

    def test_contabiliza_atendidas(self):
        self.generador.generar_log(self.entrante1, False, 'COMPLETEAGENT', '35100001111',
                                   agente=self.agente1, contacto=None, bridge_wait_time=-1,
                                   duracion_llamada=10, archivo_grabacion='', time=None)
        # No debe contar esta manual
        self.generador.generar_log(self.entrante1, True, 'COMPLETEAGENT', '35100001112',
                                   agente=self.agente1, contacto=None, bridge_wait_time=-1,
                                   duracion_llamada=10, archivo_grabacion='', time=None)
        reporte = ReporteDeLLamadasEntrantesDeSupervision(self.supervisor.user)
        self.assertEqual(reporte.estadisticas[self.entrante1.id]['recibidas'], 1)
        self.assertEqual(reporte.estadisticas[self.entrante1.id]['atendidas'], 1)
        self.assertEqual(reporte.estadisticas[self.entrante1.id]['expiradas'], 0)
        self.assertEqual(reporte.estadisticas[self.entrante1.id]['abandonadas'], 0)
        self.assertEqual(reporte.estadisticas[self.entrante1.id]['gestiones'], 0)

    def test_contabiliza_expiradas(self):
        self.generador.generar_log(self.entrante1, False, 'EXITWITHTIMEOUT', '35100001111',
                                   agente=self.agente1, contacto=None, bridge_wait_time=-1,
                                   duracion_llamada=-1, archivo_grabacion='', time=None)
        reporte = ReporteDeLLamadasEntrantesDeSupervision(self.supervisor.user)
        self.assertEqual(reporte.estadisticas[self.entrante1.id]['recibidas'], 1)
        self.assertEqual(reporte.estadisticas[self.entrante1.id]['atendidas'], 0)
        self.assertEqual(reporte.estadisticas[self.entrante1.id]['expiradas'], 1)
        self.assertEqual(reporte.estadisticas[self.entrante1.id]['abandonadas'], 0)
        self.assertEqual(reporte.estadisticas[self.entrante1.id]['gestiones'], 0)

    def test_contabiliza_gestiones(self):
        self.generador.generar_log(self.entrante1, False, 'COMPLETEAGENT', '35100001111',
                                   agente=self.agente1, contacto=None, bridge_wait_time=-1,
                                   duracion_llamada=10, archivo_grabacion='', time=None)
        CalificacionClienteFactory(opcion_calificacion=self.opcion_calificacion,
                                   agente=self.agente1)
        reporte = ReporteDeLLamadasEntrantesDeSupervision(self.supervisor.user)
        self.assertEqual(reporte.estadisticas[self.entrante1.id]['recibidas'], 1)
        self.assertEqual(reporte.estadisticas[self.entrante1.id]['atendidas'], 1)
        self.assertEqual(reporte.estadisticas[self.entrante1.id]['expiradas'], 0)
        self.assertEqual(reporte.estadisticas[self.entrante1.id]['abandonadas'], 0)
        self.assertEqual(reporte.estadisticas[self.entrante1.id]['gestiones'], 1)
