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
from ominicontacto_app.services.asterisk.supervisor_activity import SupervisorActivityAmiManager
from ominicontacto_app.models import Campana, OpcionCalificacion
from mock import patch

from django.urls import reverse
from django.test import TestCase

from reportes_app.models import LlamadaLog
from reportes_app.reportes.reporte_llamadas_supervision import (
    ReporteDeLLamadasEntrantesDeSupervision, ReporteDeLLamadasSalientesDeSupervision
)
from reportes_app.tests.utiles import GeneradorDeLlamadaLogs
from ominicontacto_app.tests.factories import AgenteProfileFactory, CalificacionClienteFactory, \
    CampanaFactory, LlamadaLogFactory, OpcionCalificacionFactory, QueueFactory, \
    QueueMemberFactory, SupervisorProfileFactory


class ReporteDeLLamadasEntrantesDeSupervisionTest(TestCase):

    PWD = u'admin123'

    def setUp(self):
        super(ReporteDeLLamadasEntrantesDeSupervisionTest, self).setUp()
        self.generador = GeneradorDeLlamadaLogs()

        self.supervisor = SupervisorProfileFactory()
        self.supervisor.user.set_password(self.PWD)
        self.supervisor.user.save()

        self.agente1 = AgenteProfileFactory()
        self.agente2 = AgenteProfileFactory()

        self.entrante1 = CampanaFactory.create(type=Campana.TYPE_ENTRANTE, nombre='camp-entrante-1',
                                               estado=Campana.ESTADO_ACTIVA,
                                               supervisors=[self.supervisor.user])
        self.opcion_calificacion = OpcionCalificacionFactory(campana=self.entrante1,
                                                             tipo=OpcionCalificacion.GESTION)
        # Campaña que no debe estar en los reportes por no ser del supervisor
        self.entrante2 = CampanaFactory.create(type=Campana.TYPE_ENTRANTE, nombre='camp-entrante-2',
                                               estado=Campana.ESTADO_ACTIVA)
        self.queue = QueueFactory.create(campana=self.entrante1)

    def test_reporte_vacio(self):
        reporte = ReporteDeLLamadasEntrantesDeSupervision(self.supervisor.user)
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
        reporte = ReporteDeLLamadasEntrantesDeSupervision(self.supervisor.user)
        self.assertEqual(
            reporte.estadisticas[self.entrante1.id]['atendidas'], 1)
        self.assertEqual(
            reporte.estadisticas[self.entrante1.id]['expiradas'], 0)
        self.assertEqual(
            reporte.estadisticas[self.entrante1.id]['abandonadas'], 0)
        self.assertEqual(
            reporte.estadisticas[self.entrante1.id]['gestiones'], 0)

    def test_contabiliza_expiradas(self):
        self.generador.generar_log(self.entrante1, False, 'EXITWITHTIMEOUT', '35100001111',
                                   agente=self.agente1, contacto=None, bridge_wait_time=-1,
                                   duracion_llamada=-1, archivo_grabacion='', time=None)
        reporte = ReporteDeLLamadasEntrantesDeSupervision(self.supervisor.user)
        self.assertEqual(
            reporte.estadisticas[self.entrante1.id]['atendidas'], 0)
        self.assertEqual(
            reporte.estadisticas[self.entrante1.id]['expiradas'], 1)
        self.assertEqual(
            reporte.estadisticas[self.entrante1.id]['abandonadas'], 0)
        self.assertEqual(
            reporte.estadisticas[self.entrante1.id]['gestiones'], 0)

    def test_contabiliza_gestiones(self):
        self.generador.generar_log(self.entrante1, False, 'COMPLETEAGENT', '35100001111',
                                   agente=self.agente1, contacto=None, bridge_wait_time=-1,
                                   duracion_llamada=10, archivo_grabacion='', time=None)
        CalificacionClienteFactory(opcion_calificacion=self.opcion_calificacion,
                                   agente=self.agente1)
        reporte = ReporteDeLLamadasEntrantesDeSupervision(self.supervisor.user)
        self.assertEqual(
            reporte.estadisticas[self.entrante1.id]['atendidas'], 1)
        self.assertEqual(
            reporte.estadisticas[self.entrante1.id]['expiradas'], 0)
        self.assertEqual(
            reporte.estadisticas[self.entrante1.id]['abandonadas'], 0)
        self.assertEqual(
            reporte.estadisticas[self.entrante1.id]['gestiones'], 1)

    def test_contabiliza_promedio_tiempo_espera(self):
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
        self.client.login(
            username=self.supervisor.user.username, password=self.PWD)
        url = reverse('supervision_campanas_entrantes')
        response = self.client.get(url)
        estadisticas = response.context_data['estadisticas']
        self.assertEqual(
            estadisticas[self.entrante1.pk]['t_promedio_espera'], 5)
        self.assertEqual(
            estadisticas[self.entrante2.pk]['t_promedio_espera'], 6)

    def test_contabilizar_promedio_llamadas_abandonadas(self):
        self.generador.generar_log(self.entrante1, False, 'ABANDON', '35100001111',
                                   agente=self.agente1, contacto=None, bridge_wait_time=5,
                                   duracion_llamada=10, archivo_grabacion='', time=None)
        LlamadaLogFactory(tipo_campana=Campana.TYPE_ENTRANTE,
                          tipo_llamada=LlamadaLog.LLAMADA_ENTRANTE,
                          campana_id=self.entrante1.pk,
                          event='ABANDONWEL', bridge_wait_time=2)
        self.client.login(
            username=self.supervisor.user.username, password=self.PWD)
        url = reverse('supervision_campanas_entrantes')
        response = self.client.get(url)
        estadisticas = response.context_data['estadisticas']
        self.assertEqual(
            estadisticas[self.entrante1.pk]['t_promedio_abandono'], 3.5)

    def _obtener_agentes_activos(self):
        return [{
            'id': self.agente1.id,
            'status': 'PAUSE-ACW'
        },
            {
            'id': self.agente2.id,
            'status': 'ONCALL-IN01'
        }
        ]

    @patch.object(SupervisorActivityAmiManager, 'obtener_agentes_activos')
    def test_contabilizar_agentes_activos_reporte_vacio(self, obtener_agentes_activos):
        obtener_agentes_activos.return_value = []
        reporte = ReporteDeLLamadasEntrantesDeSupervision(self.supervisor.user)
        self.assertNotIn(self.entrante1.id, reporte.estadisticas)
        self.assertNotIn(self.entrante2.id, reporte.estadisticas)

    @patch.object(SupervisorActivityAmiManager, 'obtener_agentes_activos')
    def test_contabilizar_agentes_pausa(self, obtener_agentes_activos):
        obtener_agentes_activos.return_value = self._obtener_agentes_activos()
        QueueMemberFactory.create(member=self.agente1, queue_name=self.queue)

        reporte = ReporteDeLLamadasEntrantesDeSupervision(self.supervisor.user)
        self.assertEqual(
            reporte.estadisticas[self.entrante1.id]['agentes_pausa'], 1)

    @patch.object(SupervisorActivityAmiManager, 'obtener_agentes_activos')
    def test_contabilizar_agentes_llamada(self, obtener_agentes_activos):
        obtener_agentes_activos.return_value = self._obtener_agentes_activos()
        QueueMemberFactory.create(member=self.agente2, queue_name=self.queue)

        reporte = ReporteDeLLamadasEntrantesDeSupervision(self.supervisor.user)
        self.assertEqual(
            reporte.estadisticas[self.entrante1.id]['agentes_llamada'], 1)

    @patch.object(SupervisorActivityAmiManager, 'obtener_agentes_activos')
    def test_contabilizar_agentes_llamada_pausa_activos(self, obtener_agentes_activos):
        obtener_agentes_activos.return_value = self._obtener_agentes_activos()
        QueueMemberFactory.create(member=self.agente1, queue_name=self.queue)
        QueueMemberFactory.create(member=self.agente2, queue_name=self.queue)

        reporte = ReporteDeLLamadasEntrantesDeSupervision(self.supervisor.user)
        self.assertEqual(
            reporte.estadisticas[self.entrante1.id]['agentes_pausa'], 1)
        self.assertEqual(
            reporte.estadisticas[self.entrante1.id]['agentes_llamada'], 1)
        self.assertEqual(
            reporte.estadisticas[self.entrante1.id]['agentes_online'], 2)


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
        self.assertEqual(
            reporte.estadisticas[self.manual.id]['no_conectadas'], 0)
        self.assertEqual(reporte.estadisticas[self.manual.id]['gestiones'], 0)
        self.assertEqual(
            reporte.estadisticas[self.preview.id]['efectuadas'], 1)
        self.assertEqual(
            reporte.estadisticas[self.preview.id]['conectadas'], 1)
        self.assertEqual(
            reporte.estadisticas[self.preview.id]['no_conectadas'], 0)
        self.assertEqual(reporte.estadisticas[self.preview.id]['gestiones'], 0)
        self.assertEqual(reporte.estadisticas[self.dialer.id]['efectuadas'], 2)
        self.assertEqual(reporte.estadisticas[self.dialer.id]['conectadas'], 2)
        self.assertEqual(
            reporte.estadisticas[self.dialer.id]['no_conectadas'], 0)
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
        self.assertEqual(
            reporte.estadisticas[self.manual.id]['no_conectadas'], 1)
        self.assertEqual(reporte.estadisticas[self.manual.id]['gestiones'], 0)
        self.assertEqual(
            reporte.estadisticas[self.preview.id]['efectuadas'], 1)
        self.assertEqual(
            reporte.estadisticas[self.preview.id]['conectadas'], 0)
        self.assertEqual(
            reporte.estadisticas[self.preview.id]['no_conectadas'], 1)
        self.assertEqual(reporte.estadisticas[self.preview.id]['gestiones'], 0)
        self.assertEqual(reporte.estadisticas[self.dialer.id]['efectuadas'], 2)
        self.assertEqual(reporte.estadisticas[self.dialer.id]['conectadas'], 0)
        self.assertEqual(
            reporte.estadisticas[self.dialer.id]['no_conectadas'], 2)
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
            self.assertEqual(
                reporte.estadisticas[id_campana]['no_conectadas'], 0)
