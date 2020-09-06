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
from ominicontacto_app.models import Campana, OpcionCalificacion
from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.tests.factories import (
    CampanaFactory, OpcionCalificacionFactory, QueueFactory, CalificacionClienteFactory,
    LlamadaLogFactory)

from reportes_app.reportes.reporte_llamadas_entrantes import ReporteDeLLamadasEntrantesDeSupervision
from reportes_app.tests.utiles import GeneradorDeLlamadaLogs
from reportes_app.models import LlamadaLog


class ReporteDeLLamadasEntrantesDeSupervisionTest(OMLBaseTest):

    PWD = u'admin123'

    def setUp(self):
        super(ReporteDeLLamadasEntrantesDeSupervisionTest, self).setUp()
        self.generador = GeneradorDeLlamadaLogs()

        self.agente1 = self.crear_agente_profile()
        self.agente2 = self.crear_agente_profile()

        self.entrante1 = CampanaFactory.create(type=Campana.TYPE_ENTRANTE, nombre='camp-entrante-1',
                                               estado=Campana.ESTADO_ACTIVA)
        self.opcion_calificacion = OpcionCalificacionFactory(campana=self.entrante1,
                                                             tipo=OpcionCalificacion.GESTION)
        # Campaña que no debe estar en los reportes por no ser del supervisor
        self.entrante2 = CampanaFactory.create(type=Campana.TYPE_ENTRANTE, nombre='camp-entrante-2',
                                               estado=Campana.ESTADO_ACTIVA)
        self.queue = QueueFactory.create(campana=self.entrante1)

    def test_contabiliza_expiradas(self):
        self.generador.generar_log(self.entrante1, False, 'EXITWITHTIMEOUT', '35100001111',
                                   agente=self.agente1, contacto=None, bridge_wait_time=-1,
                                   duracion_llamada=-1, archivo_grabacion='', time=None)
        reporte = ReporteDeLLamadasEntrantesDeSupervision()
        self.assertEqual(
            reporte.estadisticas[self.entrante1.id]['llamadas_atendidas'], 0)
        self.assertEqual(
            reporte.estadisticas[self.entrante1.id]['llamadas_expiradas'], 1)
        self.assertEqual(
            reporte.estadisticas[self.entrante1.id]['llamadas_abandonadas'], 0)
        self.assertEqual(
            reporte.estadisticas[self.entrante1.id]['gestiones'], 0)

    def test_contabiliza_gestiones(self):
        self.generador.generar_log(self.entrante1, False, 'COMPLETEAGENT', '35100001111',
                                   agente=self.agente1, contacto=None, bridge_wait_time=-1,
                                   duracion_llamada=10, archivo_grabacion='', time=None)
        CalificacionClienteFactory(opcion_calificacion=self.opcion_calificacion,
                                   agente=self.agente1)
        reporte = ReporteDeLLamadasEntrantesDeSupervision()
        self.assertEqual(
            reporte.estadisticas[self.entrante1.id]['llamadas_atendidas'], 1)
        self.assertEqual(
            reporte.estadisticas[self.entrante1.id]['llamadas_expiradas'], 0)
        self.assertEqual(
            reporte.estadisticas[self.entrante1.id]['llamadas_abandonadas'], 0)
        self.assertEqual(
            reporte.estadisticas[self.entrante1.id]['gestiones'], 1)

    def test_contabiliza_promedio_tiempo_espera(self):
        callid_call1 = 1
        callid_call2 = 2
        self.generador.generar_log(self.entrante1, False, 'COMPLETEAGENT', '35100001111',
                                   agente=self.agente1, contacto=None, bridge_wait_time=3,
                                   duracion_llamada=10, archivo_grabacion='', time=None,
                                   callid=callid_call1)
        self.generador.generar_log(self.entrante1, False, 'COMPLETEOUTNUM', '35100001112',
                                   agente=self.agente1, contacto=None, bridge_wait_time=7,
                                   duracion_llamada=10, archivo_grabacion='', time=None,
                                   callid=callid_call1)
        self.generador.generar_log(self.entrante2, False, 'COMPLETEAGENT', '3510000117',
                                   agente=self.agente1, contacto=None, bridge_wait_time=4,
                                   duracion_llamada=10, archivo_grabacion='', time=None,
                                   callid=callid_call2)
        self.generador.generar_log(self.entrante2, False, 'COMPLETEAGENT', '35100001110',
                                   agente=self.agente1, contacto=None, bridge_wait_time=8,
                                   duracion_llamada=10, archivo_grabacion='', time=None,
                                   callid=callid_call2)

        reporte = ReporteDeLLamadasEntrantesDeSupervision()
        estadisticas = reporte.estadisticas
        self.assertEqual(
            estadisticas[self.entrante1.pk]['tiempo_acumulado_espera'], 10)
        self.assertEqual(
            estadisticas[self.entrante2.pk]['tiempo_acumulado_espera'], 12)

    def test_contabilizar_promedio_llamadas_abandonadas(self):
        self.generador.generar_log(self.entrante1, False, 'ABANDON', '35100001111',
                                   agente=self.agente1, contacto=None, bridge_wait_time=5,
                                   duracion_llamada=10, archivo_grabacion='', time=None)
        LlamadaLogFactory(tipo_campana=Campana.TYPE_ENTRANTE,
                          tipo_llamada=LlamadaLog.LLAMADA_ENTRANTE,
                          campana_id=self.entrante1.pk,
                          event='ABANDONWEL', bridge_wait_time=2)
        reporte = ReporteDeLLamadasEntrantesDeSupervision()
        estadisticas = reporte.estadisticas
        self.assertEqual(
            estadisticas[self.entrante1.pk]['tiempo_acumulado_abandonadas'], 7)

    def test_reporte_vacio(self):
        reporte = ReporteDeLLamadasEntrantesDeSupervision()
        self.assertNotIn(self.entrante1.id, reporte.estadisticas)
        self.assertNotIn(self.entrante2.id, reporte.estadisticas)

    def test_contabiliza_atendidas(self):
        self.generador.generar_log(self.entrante1, False, 'COMPLETEAGENT', '35100001111',
                                   agente=self.agente1, contacto=None, bridge_wait_time=-1,
                                   duracion_llamada=10, archivo_grabacion='', time=None)
        # No debe contar esta manual
        self.generador.generar_log(self.entrante1, True, 'COMPLETEAGENT', '35100001112',
                                   agente=self.agente1, contacto=None, bridge_wait_time=-1,
                                   duracion_llamada=10, archivo_grabacion='', time=None)
        reporte = ReporteDeLLamadasEntrantesDeSupervision()
        self.assertEqual(
            reporte.estadisticas[self.entrante1.id]['llamadas_atendidas'], 1)
        self.assertEqual(
            reporte.estadisticas[self.entrante1.id]['llamadas_expiradas'], 0)
        self.assertEqual(
            reporte.estadisticas[self.entrante1.id]['llamadas_abandonadas'], 0)
        self.assertEqual(
            reporte.estadisticas[self.entrante1.id]['gestiones'], 0)
