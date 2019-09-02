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
from mock import patch

from django.core.urlresolvers import reverse
from django.test import TestCase

from reportes_app.reportes.reporte_llamadas_supervision import (
    ReporteDeLLamadasEntrantesDeSupervision, ReporteDeLLamadasSalientesDeSupervision
)
from reportes_app.tests.utiles import GeneradorDeLlamadaLogs
from ominicontacto_app.tests.factories import (
    SupervisorProfileFactory, AgenteProfileFactory, CampanaFactory, OpcionCalificacionFactory,
    CalificacionClienteFactory
)
from ominicontacto_app.models import Campana, OpcionCalificacion


class ReporteDeLLamadasEntrantesDeSupervisionTest(TestCase):

    PWD = u'admin123'

    def setUp(self):
        super(ReporteDeLLamadasEntrantesDeSupervisionTest, self).setUp()
        self.generador = GeneradorDeLlamadaLogs()

        self.supervisor = SupervisorProfileFactory()
        self.supervisor.user.set_password(self.PWD)
        self.supervisor.user.save()

        self.agente1 = AgenteProfileFactory()

        self.entrante1 = CampanaFactory.create(type=Campana.TYPE_ENTRANTE, nombre='camp-entrante-1',
                                               estado=Campana.ESTADO_ACTIVA,
                                               supervisors=[self.supervisor.user])
        self.opcion_calificacion = OpcionCalificacionFactory(campana=self.entrante1,
                                                             tipo=OpcionCalificacion.GESTION)
        # Campaña que no debe estar en los reportes por no ser del supervisor
        self.entrante2 = CampanaFactory.create(type=Campana.TYPE_ENTRANTE, nombre='camp-entrante-2',
                                               estado=Campana.ESTADO_ACTIVA)

    @patch.object(ReporteDeLLamadasEntrantesDeSupervision, '_obtener_llamadas_en_espera_raw')
    def test_reporte_vacio(self, _obtener_llamadas_en_espera_raw):
        reporte = ReporteDeLLamadasEntrantesDeSupervision(self.supervisor.user)
        self.assertNotIn(self.entrante1.id, reporte.estadisticas)
        self.assertNotIn(self.entrante2.id, reporte.estadisticas)

    @patch.object(ReporteDeLLamadasEntrantesDeSupervision, '_obtener_llamadas_en_espera_raw')
    def test_contabiliza_atendidas(self, _obtener_llamadas_en_espera_raw):
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

    @patch.object(ReporteDeLLamadasEntrantesDeSupervision, '_obtener_llamadas_en_espera_raw')
    def test_contabiliza_expiradas(self, _obtener_llamadas_en_espera_raw):
        self.generador.generar_log(self.entrante1, False, 'EXITWITHTIMEOUT', '35100001111',
                                   agente=self.agente1, contacto=None, bridge_wait_time=-1,
                                   duracion_llamada=-1, archivo_grabacion='', time=None)
        reporte = ReporteDeLLamadasEntrantesDeSupervision(self.supervisor.user)
        self.assertEqual(reporte.estadisticas[self.entrante1.id]['recibidas'], 1)
        self.assertEqual(reporte.estadisticas[self.entrante1.id]['atendidas'], 0)
        self.assertEqual(reporte.estadisticas[self.entrante1.id]['expiradas'], 1)
        self.assertEqual(reporte.estadisticas[self.entrante1.id]['abandonadas'], 0)
        self.assertEqual(reporte.estadisticas[self.entrante1.id]['gestiones'], 0)

    @patch.object(ReporteDeLLamadasEntrantesDeSupervision, '_obtener_llamadas_en_espera_raw')
    def test_contabiliza_gestiones(self, _obtener_llamadas_en_espera_raw):
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

    def _generar_ami_response_llamadas_espera(self, campana_entrante):
        return ('Event: QueueEntry\r\nQueue: {0}_{1}\r\nMax: 5\r\nStrategy: '
                'rrmemory\r\nCalls: 0\r\nHoldtime: 0\r\nTalkTime: 0\r\n'
                'Completed: 0\r\nAbandoned: 0\r\n'
                'ServiceLevel: 30\r\nServicelevelPerf: 0.0\r\nServicelevelPerf2: 0.0\r\n'
                'Weight: 0\r\n'
                'ActionID: d9555aefdc48-00000001\r\n\r\nEvent: QueueStatusComplete\r\nActionID: '
                'd9555aefdc48-00000001\r\n'
                'EventList: Complete\r\nListItems: 31\r\n').format(campana_entrante.id,
                                                                   campana_entrante.nombre)

    @patch.object(ReporteDeLLamadasEntrantesDeSupervision, '_obtener_llamadas_en_espera_raw')
    def test_contabilizar_llamadas_en_espera(self, _obtener_llamadas_en_espera_raw):
        self.generador.generar_log(self.entrante1, False, 'COMPLETEAGENT', '35100001111',
                                   agente=self.agente1, contacto=None, bridge_wait_time=-1,
                                   duracion_llamada=10, archivo_grabacion='', time=None)
        _obtener_llamadas_en_espera_raw.return_value = self._generar_ami_response_llamadas_espera(
            self.entrante1)
        self.client.login(username=self.supervisor.user.username, password=self.PWD)
        url = reverse('supervision_campanas_entrantes')
        response = self.client.get(url)
        estadisticas = response.context_data['estadisticas']
        self.assertEqual(estadisticas[self.entrante1.pk]['en_cola'], 1)

    @patch.object(ReporteDeLLamadasEntrantesDeSupervision, '_obtener_llamadas_en_espera_raw')
    def test_contabiliza_promedio_tiempo_espera(self, _obtener_llamadas_en_espera_raw):
        callid_call1 = 1
        callid_call2 = 2
        self.entrante2.supervisors.add(self.supervisor.user)
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
        self.client.login(username=self.supervisor.user.username, password=self.PWD)
        url = reverse('supervision_campanas_entrantes')
        response = self.client.get(url)
        estadisticas = response.context_data['estadisticas']
        self.assertEqual(estadisticas[self.entrante1.pk]['t_promedio_espera'], 5)
        self.assertEqual(estadisticas[self.entrante2.pk]['t_promedio_espera'], 6)


class ReporteDeLLamadasSalientesDeSupervisionTest(TestCase):

    def setUp(self):
        super(ReporteDeLLamadasSalientesDeSupervisionTest, self).setUp()
        self.generador = GeneradorDeLlamadaLogs()

        self.supervisor = SupervisorProfileFactory()
        self.agente1 = AgenteProfileFactory()

        self.manual = CampanaFactory.create(type=Campana.TYPE_MANUAL, nombre='camp-manual-1',
                                            estado=Campana.ESTADO_ACTIVA,
                                            supervisors=[self.supervisor.user])
        self.opcion_calificacion_m1 = OpcionCalificacionFactory(campana=self.manual,
                                                                tipo=OpcionCalificacion.GESTION)
        self.dialer = CampanaFactory.create(type=Campana.TYPE_DIALER, nombre='camp-dialer-1',
                                            estado=Campana.ESTADO_ACTIVA,
                                            supervisors=[self.supervisor.user])
        self.opcion_calificacion_d1 = OpcionCalificacionFactory(campana=self.dialer,
                                                                tipo=OpcionCalificacion.GESTION)
        self.preview = CampanaFactory.create(type=Campana.TYPE_PREVIEW, nombre='camp-preview-1',
                                             estado=Campana.ESTADO_ACTIVA,
                                             supervisors=[self.supervisor.user])
        self.opcion_calificacion_p1 = OpcionCalificacionFactory(campana=self.preview,
                                                                tipo=OpcionCalificacion.GESTION)

        # Campañas que no deben estar en los reportes por no ser del supervisor
        self.manual2 = CampanaFactory.create(type=Campana.TYPE_MANUAL, nombre='camp-manual-2',
                                             estado=Campana.ESTADO_ACTIVA)
        self.dialer2 = CampanaFactory.create(type=Campana.TYPE_DIALER, nombre='camp-dialer-2',
                                             estado=Campana.ESTADO_ACTIVA)
        self.preview2 = CampanaFactory.create(type=Campana.TYPE_PREVIEW, nombre='camp-preview-2',
                                              estado=Campana.ESTADO_ACTIVA)

    def test_reporte_vacio(self):
        reporte = ReporteDeLLamadasSalientesDeSupervision(self.supervisor.user)
        for id_campana in [self.manual.id, self.dialer.id, self.preview.id]:
            self.assertNotIn(id_campana, reporte.estadisticas)
        self.assertNotIn(self.manual2.id, reporte.estadisticas)
        self.assertNotIn(self.dialer2.id, reporte.estadisticas)
        self.assertNotIn(self.preview2.id, reporte.estadisticas)

    def test_contabiliza_efectuadas_conectadas(self):
        self.generador.generar_log(self.manual, False, 'COMPLETEAGENT', '35100001111',
                                   agente=self.agente1, contacto=None, bridge_wait_time=-1,
                                   duracion_llamada=10, archivo_grabacion='', time=None)
        self.generador.generar_log(self.preview, False, 'COMPLETEAGENT', '35100001112',
                                   agente=self.agente1, contacto=None, bridge_wait_time=-1,
                                   duracion_llamada=10, archivo_grabacion='', time=None)
        self.generador.generar_log(self.dialer, False, 'COMPLETEAGENT', '35100001113',
                                   agente=self.agente1, contacto=None, bridge_wait_time=-1,
                                   duracion_llamada=10, archivo_grabacion='', time=None)
        self.generador.generar_log(self.dialer, True, 'COMPLETEAGENT', '35100001113',
                                   agente=self.agente1, contacto=None, bridge_wait_time=-1,
                                   duracion_llamada=10, archivo_grabacion='', time=None)
        reporte = ReporteDeLLamadasSalientesDeSupervision(self.supervisor.user)
        self.assertEqual(reporte.estadisticas[self.manual.id]['efectuadas'], 1)
        self.assertEqual(reporte.estadisticas[self.manual.id]['conectadas'], 1)
        self.assertEqual(reporte.estadisticas[self.manual.id]['no_conectadas'], 0)
        self.assertEqual(reporte.estadisticas[self.manual.id]['gestiones'], 0)
        self.assertEqual(reporte.estadisticas[self.preview.id]['efectuadas'], 1)
        self.assertEqual(reporte.estadisticas[self.preview.id]['conectadas'], 1)
        self.assertEqual(reporte.estadisticas[self.preview.id]['no_conectadas'], 0)
        self.assertEqual(reporte.estadisticas[self.preview.id]['gestiones'], 0)
        self.assertEqual(reporte.estadisticas[self.dialer.id]['efectuadas'], 2)
        self.assertEqual(reporte.estadisticas[self.dialer.id]['conectadas'], 2)
        self.assertEqual(reporte.estadisticas[self.dialer.id]['no_conectadas'], 0)
        self.assertEqual(reporte.estadisticas[self.dialer.id]['gestiones'], 0)

    def test_contabiliza_efectuadas_no_conectadas(self):
        self.generador.generar_log(self.manual, False, 'BUSY', '35100001111',
                                   agente=self.agente1, contacto=None, bridge_wait_time=-1,
                                   duracion_llamada=10, archivo_grabacion='', time=None)
        self.generador.generar_log(self.preview, False, 'NOANSWER', '35100001112',
                                   agente=self.agente1, contacto=None, bridge_wait_time=-1,
                                   duracion_llamada=10, archivo_grabacion='', time=None)
        self.generador.generar_log(self.dialer, False, 'BLACKLIST', '35100001113',
                                   agente=self.agente1, contacto=None, bridge_wait_time=-1,
                                   duracion_llamada=10, archivo_grabacion='', time=None)
        self.generador.generar_log(self.dialer, True, 'CONGESTION', '35100001113',
                                   agente=self.agente1, contacto=None, bridge_wait_time=-1,
                                   duracion_llamada=10, archivo_grabacion='', time=None)
        reporte = ReporteDeLLamadasSalientesDeSupervision(self.supervisor.user)
        self.assertEqual(reporte.estadisticas[self.manual.id]['efectuadas'], 1)
        self.assertEqual(reporte.estadisticas[self.manual.id]['conectadas'], 0)
        self.assertEqual(reporte.estadisticas[self.manual.id]['no_conectadas'], 1)
        self.assertEqual(reporte.estadisticas[self.manual.id]['gestiones'], 0)
        self.assertEqual(reporte.estadisticas[self.preview.id]['efectuadas'], 1)
        self.assertEqual(reporte.estadisticas[self.preview.id]['conectadas'], 0)
        self.assertEqual(reporte.estadisticas[self.preview.id]['no_conectadas'], 1)
        self.assertEqual(reporte.estadisticas[self.preview.id]['gestiones'], 0)
        self.assertEqual(reporte.estadisticas[self.dialer.id]['efectuadas'], 2)
        self.assertEqual(reporte.estadisticas[self.dialer.id]['conectadas'], 0)
        self.assertEqual(reporte.estadisticas[self.dialer.id]['no_conectadas'], 2)
        self.assertEqual(reporte.estadisticas[self.dialer.id]['gestiones'], 0)

    def test_contabiliza_gestiones(self):
        CalificacionClienteFactory(opcion_calificacion=self.opcion_calificacion_m1,
                                   agente=self.agente1)
        CalificacionClienteFactory(opcion_calificacion=self.opcion_calificacion_d1,
                                   agente=self.agente1)
        CalificacionClienteFactory(opcion_calificacion=self.opcion_calificacion_p1,
                                   agente=self.agente1)
        reporte = ReporteDeLLamadasSalientesDeSupervision(self.supervisor.user)
        for id_campana in [self.manual.id, self.dialer.id, self.preview.id]:
            self.assertIn(id_campana, reporte.estadisticas)
            self.assertEqual(reporte.estadisticas[id_campana]['efectuadas'], 0)
            self.assertEqual(reporte.estadisticas[id_campana]['conectadas'], 0)
            self.assertEqual(reporte.estadisticas[id_campana]['no_conectadas'], 0)
