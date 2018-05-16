# -*- coding: utf-8 -*-

"""
Tests del modoulo 'reportes_app.reporte_agente_tiempos.py'
"""

from __future__ import unicode_literals

from django.utils import timezone
from ominicontacto_app.tests.utiles import OMLBaseTest
from reportes_app.tests.utiles import GeneradorDeLlamadaLogs
from ominicontacto_app.models import Campana, AgenteProfile
from ominicontacto_app.tests.factories import (
    CampanaFactory, ContactoFactory, ActividadAgenteLogFactory, PausaFactory

)
from reportes_app.models import LlamadaLog, ActividadAgenteLog
from reportes_app.reporte_agente_tiempos import TiemposAgente


class ReportesAgenteTiemposTest(OMLBaseTest):

    def setUp(self):
        super(ReportesAgenteTiemposTest, self).setUp()
        user_agente = self.crear_user_agente()
        self.agente = self.crear_agente_profile(user_agente)
        self.inicio_sesion = ActividadAgenteLogFactory.create(
            event='ADDMEMBER', agente_id=self.agente.id)
        hora_fin_sesion = self.inicio_sesion.time + timezone.timedelta(hours=8)
        self.fin_sesion = ActividadAgenteLogFactory.create(
            time=hora_fin_sesion, event='REMOVEMEMBER', agente_id=self.agente.id)

    def test_genera_correctamente_tiempo_inicio_sesion(self):
        """test que controla que los tiempo de sesion de los agentes
         se generen correcamente"""
        inicio_sesion_agente = self.inicio_sesion.time - timezone.timedelta(
            minutes=17) - timezone.timedelta(days=1)
        ActividadAgenteLogFactory.create(
            event='ADDMEMBER', agente_id=self.agente.id, time=inicio_sesion_agente)
        fin_sesion_agente = self.fin_sesion.time + timezone.timedelta(
            minutes=79) - timezone.timedelta(days=1)
        ActividadAgenteLogFactory.create(
            time=fin_sesion_agente, event='REMOVEMEMBER', agente_id=self.agente.id)
        user_agente = self.crear_user_agente()
        agente1 = self.crear_agente_profile(user_agente)
        inicio_sesion_agente1 = self.inicio_sesion.time - timezone.timedelta(minutes=13)
        ActividadAgenteLogFactory.create(
            event='ADDMEMBER', agente_id=agente1.id, time=inicio_sesion_agente1)
        fin_sesion_agente1 = self.fin_sesion.time + timezone.timedelta(minutes=37)
        ActividadAgenteLogFactory.create(
            time=fin_sesion_agente1, event='REMOVEMEMBER', agente_id=agente1.id)

        # calculo el tiempo de sesion del agente
        tiempo_sesion_agente = self.fin_sesion.time - self.inicio_sesion.time
        tiempo_sesion_agente += fin_sesion_agente - inicio_sesion_agente
        # calculo el tiempo de sesion agente1
        tiempo_sesion_agente1 = fin_sesion_agente1 - inicio_sesion_agente1

        # realizamos calculo con el modulo
        reportes_estadisticas = TiemposAgente()
        agentes = AgenteProfile.objects.obtener_activos()
        fecha_hoy = timezone.now() + timezone.timedelta(days=1)
        fecha_ayer = fecha_hoy - timezone.timedelta(days=2)
        reportes_estadisticas.calcular_tiempo_session(agentes, fecha_ayer, fecha_hoy)
        agentes_tiempo = reportes_estadisticas.agentes_tiempo

        for agente in agentes_tiempo:
            print agente.agente
            if agente.agente.id is self.agente.id:
                self.assertEqual(tiempo_sesion_agente, agente.tiempo_sesion)
            elif agente.agente.id is agente1.id:
                self.assertEqual(tiempo_sesion_agente1, agente.tiempo_sesion)
            else:
                self.assertEqual(-1, agente.tiempo_sesion, "Agente no calculado"
                                                           " revisar test")

    def test_genera_correctamente_tiempo_pausa(self):
        """test que controla que los tiempos de pausas de los agentes
         se generen correcamente"""
        pausa = PausaFactory.create()
        inicio_pausa = self.inicio_sesion.time + timezone.timedelta(
            hours=1)
        ActividadAgenteLogFactory.create(
            event='PAUSEALL', agente_id=self.agente.id, time=inicio_pausa,
            pausa_id=pausa.id)
        fin_pausa = inicio_pausa + timezone.timedelta(minutes=19)
        ActividadAgenteLogFactory.create(
            event='UNPAUSEALL', agente_id=self.agente.id, time=fin_pausa,
            pausa_id=pausa.id)
