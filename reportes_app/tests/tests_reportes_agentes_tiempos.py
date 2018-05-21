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
        self.inicio_sesion_agente = ActividadAgenteLogFactory.create(
            event='ADDMEMBER', agente_id=self.agente.id)
        hora_fin_sesion = self.inicio_sesion_agente.time + timezone.timedelta(hours=8)
        self.fin_sesion_agente = ActividadAgenteLogFactory.create(
            time=hora_fin_sesion, event='REMOVEMEMBER', agente_id=self.agente.id)
        user_agente = self.crear_user_agente()
        self.agente1 = self.crear_agente_profile(user_agente)
        inicio_sesion = self.inicio_sesion_agente.time - timezone.timedelta(minutes=13)
        self.inicio_sesion_agente1 = ActividadAgenteLogFactory.create(
            event='ADDMEMBER', agente_id=self.agente1.id, time=inicio_sesion)
        fin_sesion = self.fin_sesion_agente.time + timezone.timedelta(minutes=37)
        self.fin_sesion_agente1 = ActividadAgenteLogFactory.create(
            time=fin_sesion, event='REMOVEMEMBER', agente_id=self.agente1.id)

        self.manual = CampanaFactory.create(type=Campana.TYPE_MANUAL)
        self.dialer = CampanaFactory.create(type=Campana.TYPE_DIALER)
        self.contacto_d = ContactoFactory(bd_contacto=self.dialer.bd_contacto)
        self.entrante = CampanaFactory.create(type=Campana.TYPE_ENTRANTE)
        self.preview = CampanaFactory.create(type=Campana.TYPE_PREVIEW)
        self.contacto_p = ContactoFactory(bd_contacto=self.preview.bd_contacto)

    def test_genera_correctamente_tiempo_inicio_sesion(self):
        """test que controla que los tiempo de sesion de los agentes
         se generen correcamente"""
        inicio_sesion_agente = self.inicio_sesion_agente.time - timezone.timedelta(
            minutes=17) - timezone.timedelta(days=1)
        ActividadAgenteLogFactory.create(
            event='ADDMEMBER', agente_id=self.agente.id, time=inicio_sesion_agente)
        fin_sesion_agente = self.fin_sesion_agente.time + timezone.timedelta(
            minutes=79) - timezone.timedelta(days=1)
        ActividadAgenteLogFactory.create(
            time=fin_sesion_agente, event='REMOVEMEMBER', agente_id=self.agente.id)

        # calculo el tiempo de sesion del agente
        tiempo_sesion_agente = self.fin_sesion_agente.time - self.inicio_sesion_agente.time
        tiempo_sesion_agente += fin_sesion_agente - inicio_sesion_agente
        # calculo el tiempo de sesion agente1
        tiempo_sesion_agente1 = self.fin_sesion_agente1.time - self.inicio_sesion_agente1.time

        # realizamos calculo con el modulo
        reportes_estadisticas = TiemposAgente()
        agentes = AgenteProfile.objects.obtener_activos()
        fecha_hoy = timezone.now() + timezone.timedelta(days=1)
        fecha_ayer = fecha_hoy - timezone.timedelta(days=2)
        reportes_estadisticas.calcular_tiempo_session(agentes, fecha_ayer, fecha_hoy)
        agentes_tiempo = reportes_estadisticas.agentes_tiempo

        for agente in agentes_tiempo:
            if agente.agente.id is self.agente.id:
                self.assertEqual(tiempo_sesion_agente, agente.tiempo_sesion)
            elif agente.agente.id is self.agente1.id:
                self.assertEqual(tiempo_sesion_agente1, agente.tiempo_sesion)
            else:
                self.fail("Agente no calculado revisar test")

    def test_genera_correctamente_tiempo_pausa(self):
        """test que controla que los tiempos de pausas de los agentes
         se generen correcamente"""
        pausa = PausaFactory.create()

        inicio_pausa = self.inicio_sesion_agente.time + timezone.timedelta(
            hours=1)
        ActividadAgenteLogFactory.create(
            event='PAUSEALL', agente_id=self.agente.id, time=inicio_pausa,
            pausa_id=pausa.id)
        fin_pausa = inicio_pausa + timezone.timedelta(minutes=19)
        total_pausa_agente = fin_pausa - inicio_pausa
        ActividadAgenteLogFactory.create(
            event='UNPAUSEALL', agente_id=self.agente.id, time=fin_pausa,
            pausa_id=pausa.id)
        pausa1 = PausaFactory.create()
        inicio_pausa = self.inicio_sesion_agente.time + timezone.timedelta(
            hours=2)
        ActividadAgenteLogFactory.create(
            event='PAUSEALL', agente_id=self.agente.id, time=inicio_pausa,
            pausa_id=pausa1.id)
        fin_pausa = inicio_pausa + timezone.timedelta(minutes=7)
        total_pausa_agente += fin_pausa - inicio_pausa
        ActividadAgenteLogFactory.create(
            event='UNPAUSEALL', agente_id=self.agente.id, time=fin_pausa,
            pausa_id=pausa1.id)
        inicio_pausa = self.inicio_sesion_agente1.time + timezone.timedelta(
            hours=1)
        ActividadAgenteLogFactory.create(
            event='PAUSEALL', agente_id=self.agente1.id, time=inicio_pausa,
            pausa_id=pausa.id)
        fin_pausa = inicio_pausa + timezone.timedelta(minutes=8)
        total_pausa_agente1 = fin_pausa - inicio_pausa
        ActividadAgenteLogFactory.create(
            event='UNPAUSEALL', agente_id=self.agente1.id, time=fin_pausa,
            pausa_id=pausa.id)

        # realizamos calculo con el modulo
        reportes_estadisticas = TiemposAgente()
        agentes = AgenteProfile.objects.obtener_activos()
        fecha_hoy = timezone.now() + timezone.timedelta(days=1)
        fecha_ayer = fecha_hoy - timezone.timedelta(days=2)
        reportes_estadisticas.calcular_tiempo_pausa(
            agentes, fecha_ayer, fecha_hoy)
        agentes_tiempo = reportes_estadisticas.agentes_tiempo

        for agente in agentes_tiempo:
            if agente.agente.id is self.agente.id:
                self.assertEqual(total_pausa_agente, agente.tiempo_pausa)
            elif agente.agente.id is self.agente1.id:
                self.assertEqual(total_pausa_agente1, agente.tiempo_pausa)
            else:
                self.fail("Agente no calculado revisar test")

    def test_genera_correctamente_duracion_llamada(self):
        generador = GeneradorDeLlamadaLogs()
        generador.generar_log(self.manual, True, 'COMPLETEAGENT', '123',
                              self.agente, duracion_llamada=44)
        generador.generar_log(self.dialer, False, 'COMPLETECALLER', '123',
                              self.agente, self.contacto_d, duracion_llamada=105,
                              )
        generador.generar_log(self.preview, False, 'COMPLETEAGENT', '123',
                              self.agente1, self.contacto_p, duracion_llamada=58
                              )

        # realizamos calculo con el modulo
        reportes_estadisticas = TiemposAgente()
        agentes = AgenteProfile.objects.obtener_activos()
        fecha_hoy = timezone.now() + timezone.timedelta(days=1)
        fecha_ayer = fecha_hoy - timezone.timedelta(days=2)
        reportes_estadisticas.calcular_tiempo_llamada(
            agentes, fecha_ayer, fecha_hoy)
        agentes_tiempo = reportes_estadisticas.agentes_tiempo

        for agente in agentes_tiempo:
            if agente.agente.id is self.agente.id:
                self.assertEqual(149, agente.tiempo_llamada)
            elif agente.agente.id is self.agente1.id:
                self.assertEqual(58, agente.tiempo_llamada)
            else:
                self.fail("Agente no calculado revisar test")

    def test_genera_correctamente_tiempos_porcentajes_agentes(self):
        """test que controla que los tiempo de sesion, tiempo pausa, tiempo en
        llamada, porcentajes de los tiempo en pausa, en espera y llamada
        de los agentes se generen correcamente"""
        # inicio de sesion de los agentes
        inicio_sesion_agente = self.inicio_sesion_agente.time - timezone.timedelta(
            minutes=17) - timezone.timedelta(days=1)
        ActividadAgenteLogFactory.create(
            event='ADDMEMBER', agente_id=self.agente.id, time=inicio_sesion_agente)
        fin_sesion_agente = self.fin_sesion_agente.time + timezone.timedelta(
            minutes=79) - timezone.timedelta(days=1)
        ActividadAgenteLogFactory.create(
            time=fin_sesion_agente, event='REMOVEMEMBER', agente_id=self.agente.id)

        # calculo el tiempo de sesion del agente
        tiempo_sesion_agente = self.fin_sesion_agente.time - self.inicio_sesion_agente.time
        tiempo_sesion_agente += fin_sesion_agente - inicio_sesion_agente
        # calculo el tiempo de sesion agente1
        tiempo_sesion_agente1 = self.fin_sesion_agente1.time - self.inicio_sesion_agente1.time

        # pausa de los agentes
        pausa = PausaFactory.create()

        inicio_pausa = self.inicio_sesion_agente.time + timezone.timedelta(
            hours=1)
        ActividadAgenteLogFactory.create(
            event='PAUSEALL', agente_id=self.agente.id, time=inicio_pausa,
            pausa_id=pausa.id)
        fin_pausa = inicio_pausa + timezone.timedelta(minutes=19)
        total_pausa_agente = fin_pausa - inicio_pausa
        ActividadAgenteLogFactory.create(
            event='UNPAUSEALL', agente_id=self.agente.id, time=fin_pausa,
            pausa_id=pausa.id)
        pausa1 = PausaFactory.create()
        inicio_pausa = self.inicio_sesion_agente.time + timezone.timedelta(
            hours=2)
        ActividadAgenteLogFactory.create(
            event='PAUSEALL', agente_id=self.agente.id, time=inicio_pausa,
            pausa_id=pausa1.id)
        fin_pausa = inicio_pausa + timezone.timedelta(minutes=7)
        total_pausa_agente += fin_pausa - inicio_pausa
        ActividadAgenteLogFactory.create(
            event='UNPAUSEALL', agente_id=self.agente.id, time=fin_pausa,
            pausa_id=pausa1.id)
        inicio_pausa = self.inicio_sesion_agente1.time + timezone.timedelta(
            hours=1)
        ActividadAgenteLogFactory.create(
            event='PAUSEALL', agente_id=self.agente1.id, time=inicio_pausa,
            pausa_id=pausa.id)
        fin_pausa = inicio_pausa + timezone.timedelta(minutes=8)
        total_pausa_agente1 = fin_pausa - inicio_pausa
        ActividadAgenteLogFactory.create(
            event='UNPAUSEALL', agente_id=self.agente1.id, time=fin_pausa,
            pausa_id=pausa.id)

        generador = GeneradorDeLlamadaLogs()
        generador.generar_log(self.manual, True, 'COMPLETEAGENT', '123',
                              self.agente, duracion_llamada=44)
        generador.generar_log(self.dialer, False, 'COMPLETECALLER', '123',
                              self.agente, self.contacto_d, duracion_llamada=105,
                              )
        generador.generar_log(self.preview, False, 'COMPLETEAGENT', '123',
                              self.agente1, self.contacto_p, duracion_llamada=58
                              )

        # calculo de porcentajes
        porcentaje_llamada_agente = 149 / tiempo_sesion_agente.total_seconds() * 100
        porcentaje_llamada_agente1 = 58 / tiempo_sesion_agente1.total_seconds() * 100
        porcentaje_pausa_agente = total_pausa_agente.total_seconds() /\
            tiempo_sesion_agente.total_seconds() * 100
        porcentaje_pausa_agente1 = total_pausa_agente1.total_seconds() /\
            tiempo_sesion_agente1.total_seconds() * 100
        tiempo_wait_agente = tiempo_sesion_agente.total_seconds() -\
            total_pausa_agente.total_seconds() - 149
        tiempo_wait_agente1 = tiempo_sesion_agente1.total_seconds() -\
            total_pausa_agente1.total_seconds() - 58
        porcentaje_wait_agente = tiempo_wait_agente / tiempo_sesion_agente.total_seconds() * 100
        porcentaje_wait_agente1 = tiempo_wait_agente1 / tiempo_sesion_agente1.total_seconds() * 100

        # realizamos calculo con el modulo
        reportes_estadisticas = TiemposAgente()
        agentes = AgenteProfile.objects.obtener_activos()
        fecha_hoy = timezone.now() + timezone.timedelta(days=1)
        fecha_ayer = fecha_hoy - timezone.timedelta(days=2)
        reportes_estadisticas.calcular_tiempo_session(
            agentes, fecha_ayer, fecha_hoy)
        reportes_estadisticas.calcular_tiempo_pausa(
            agentes, fecha_ayer, fecha_hoy)
        reportes_estadisticas.calcular_tiempo_llamada(
            agentes, fecha_ayer, fecha_hoy)
        agentes_tiempo = reportes_estadisticas.agentes_tiempo

        for agente in agentes_tiempo:
            if agente.agente.id is self.agente.id:
                self.assertEqual(149, agente.tiempo_llamada)
                self.assertEqual(tiempo_sesion_agente, agente.tiempo_sesion)
                self.assertEqual(total_pausa_agente, agente.tiempo_pausa)
                self.assertEqual(porcentaje_llamada_agente,
                                 agente.tiempo_porcentaje_llamada)
                self.assertEqual(porcentaje_pausa_agente,
                                 agente.tiempo_porcentaje_pausa)
                self.assertEqual(porcentaje_wait_agente,
                                 agente.tiempo_porcentaje_wait)

            elif agente.agente.id is self.agente1.id:
                self.assertEqual(58, agente.tiempo_llamada)
                self.assertEqual(tiempo_sesion_agente1, agente.tiempo_sesion)
                self.assertEqual(total_pausa_agente1, agente.tiempo_pausa)
                self.assertEqual(porcentaje_llamada_agente1,
                                 agente.tiempo_porcentaje_llamada)
                self.assertEqual(porcentaje_pausa_agente1,
                                 agente.tiempo_porcentaje_pausa)
                self.assertEqual(porcentaje_wait_agente1,
                                 agente.tiempo_porcentaje_wait)
            else:
                self.fail("Agente no calculado revisar test")
