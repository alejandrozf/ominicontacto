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
from ominicontacto_app.utiles import cast_datetime_part_date


class ReportesAgenteTiemposTest(OMLBaseTest):

    def setUp(self):
        super(ReportesAgenteTiemposTest, self).setUp()
        user_agente = self.crear_user_agente(first_name="Leo", last_name="Messi")
        self.agente = self.crear_agente_profile(user_agente)
        self.inicio_sesion_agente = ActividadAgenteLogFactory.create(
            event='ADDMEMBER', agente_id=self.agente.id)
        hora_fin_sesion = self.inicio_sesion_agente.time + timezone.timedelta(hours=8)
        self.fin_sesion_agente = ActividadAgenteLogFactory.create(
            time=hora_fin_sesion, event='REMOVEMEMBER', agente_id=self.agente.id)
        user_agente = self.crear_user_agente(first_name="Frank", last_name="Kudelca")
        self.agente1 = self.crear_agente_profile(user_agente)
        inicio_sesion = self.inicio_sesion_agente.time - timezone.timedelta(minutes=13)
        self.inicio_sesion_agente1 = ActividadAgenteLogFactory.create(
            event='ADDMEMBER', agente_id=self.agente1.id, time=inicio_sesion)
        fin_sesion = self.fin_sesion_agente.time + timezone.timedelta(minutes=37)
        self.fin_sesion_agente1 = ActividadAgenteLogFactory.create(
            time=fin_sesion, event='REMOVEMEMBER', agente_id=self.agente1.id)

        self.user_supervisor = self.crear_user_supervisor()
        self.manual = CampanaFactory.create(
            type=Campana.TYPE_MANUAL, reported_by=self.user_supervisor, estado=Campana.ESTADO_ACTIVA)
        self.dialer = CampanaFactory.create(
            type=Campana.TYPE_DIALER, reported_by=self.user_supervisor, estado=Campana.ESTADO_ACTIVA)
        self.contacto_d = ContactoFactory(bd_contacto=self.dialer.bd_contacto)
        self.entrante = CampanaFactory.create(
            type=Campana.TYPE_ENTRANTE, reported_by=self.user_supervisor, estado=Campana.ESTADO_ACTIVA)
        self.contacto_e = ContactoFactory(bd_contacto=self.entrante.bd_contacto)
        self.preview = CampanaFactory.create(
            type=Campana.TYPE_PREVIEW, reported_by=self.user_supervisor, estado=Campana.ESTADO_ACTIVA)
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
        llamada, porcentajes de los tiempo en pausa, en espera y llamada,
        cantidad de llamadas procesadas y promedios en llamadas
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

        # calculamos los porcentajes
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

        # calculamos los promedios
        promedio_agente = 149 / 2
        promedio_agente1 = 58 / 1

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
        reportes_estadisticas.calcular_cantidad_llamadas(
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
                self.assertEqual(2, agente.cantidad_llamadas_procesadas)
                self.assertEqual(promedio_agente, agente.get_promedio_llamadas())
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
                self.assertEqual(1, agente.cantidad_llamadas_procesadas)
                self.assertEqual(promedio_agente1, agente.get_promedio_llamadas())
            else:
                self.fail("Agente no calculado revisar test")

    def test_genera_correctamente_intentos_fallidos(self):
        """test que controla que la cantidad de intentos fallidos se genere
        correcamente"""
        generador = GeneradorDeLlamadaLogs()
        generador.generar_log(self.manual, True, 'BUSY', '1234',
                              self.agente, bridge_wait_time=5)
        generador.generar_log(self.preview, False, 'NOANSWER', '12334645',
                              self.agente, self.contacto_p,
                              bridge_wait_time=5
                              )
        generador.generar_log(self.dialer, False, 'COMPLETECALLER', '123',
                              self.agente, self.contacto_d, duracion_llamada=105,
                              )
        generador.generar_log(self.preview, False, 'FAIL', '12334645',
                              self.agente1, self.contacto_p, duracion_llamada=58
                              )
        # realizamos calculo con el modulo
        reportes_estadisticas = TiemposAgente()
        agentes = AgenteProfile.objects.obtener_activos()
        fecha_hoy = timezone.now() + timezone.timedelta(days=1)
        fecha_ayer = fecha_hoy - timezone.timedelta(days=2)
        reportes_estadisticas.calcular_intentos_fallidos(
            agentes, fecha_ayer, fecha_hoy)
        agentes_tiempo = reportes_estadisticas.agentes_tiempo

        for agente in agentes_tiempo:
            if agente.agente.id is self.agente.id:
                self.assertEqual(2, agente.cantidad_intentos_fallidos)
            elif agente.agente.id is self.agente1.id:
                self.assertEqual(1, agente.cantidad_intentos_fallidos)
            else:
                self.fail("Agente no calculado revisar test")

    def test_genera_correctamente_tiempo_pausa_tipo(self):
        """test que controla que los tiempos de pausas por tipo de pausa de los
        agentes se generen correcamente"""
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
        inicio_pausa = fin_pausa + timezone.timedelta(
            hours=1)
        ActividadAgenteLogFactory.create(
            event='PAUSEALL', agente_id=self.agente.id, time=inicio_pausa,
            pausa_id=pausa.id)
        fin_pausa = inicio_pausa + timezone.timedelta(minutes=23)
        total_pausa_agente += fin_pausa - inicio_pausa
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
        total_pausa_agente_1 = fin_pausa - inicio_pausa
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
        agentes_tiempo = reportes_estadisticas.calcular_tiempo_pausa_tipo(
            agentes, fecha_ayer, fecha_hoy)

        for agente in agentes_tiempo:
            if agente['id'] is self.agente.id:
                if int(agente['pausa_id']) is pausa.id:
                    self.assertEqual(str(total_pausa_agente), agente['tiempo'])
                elif int(agente['pausa_id']) is pausa1.id:
                    self.assertEqual(str(total_pausa_agente_1), agente['tiempo'])
                else:
                    self.fail("pausa no calculada revisar test")
            elif agente['id'] is self.agente1.id:
                self.assertEqual(str(total_pausa_agente1), agente['tiempo'])
            else:
                self.fail("Agente no calculado revisar test")

    def test_genera_correctamente_llamadas_procesadas_por_campana(self):
        """test que controla que la cantidad de llamadas procesadas por
        campana y el promedio de las mismas se genere correctamente"""

        generador = GeneradorDeLlamadaLogs()
        generador.generar_log(self.manual, True, 'COMPLETEAGENT', '123',
                              self.agente, duracion_llamada=76)
        generador.generar_log(self.manual, True, 'COMPLETEAGENT', '123',
                              self.agente, duracion_llamada=61)
        generador.generar_log(self.manual, True, 'COMPLETEAGENT', '123',
                              self.agente, duracion_llamada=44)
        generador.generar_log(self.dialer, False, 'COMPLETECALLER', '123',
                              self.agente, self.contacto_d, duracion_llamada=105,
                              )
        generador.generar_log(self.dialer, False, 'COMPLETECALLER', '123',
                              self.agente, self.contacto_d, duracion_llamada=65,
                              )
        generador.generar_log(self.preview, False, 'COMPLETEAGENT', '123',
                              self.agente1, self.contacto_p, duracion_llamada=58
                              )
        generador.generar_log(self.entrante, False, 'COMPLETEAGENT', '123',
                              self.agente1, self.contacto_e, duracion_llamada=29
                              )

        # realizamos calculo con el modulo
        reportes_estadisticas = TiemposAgente()
        agentes = AgenteProfile.objects.obtener_activos()
        fecha_hoy = timezone.now() + timezone.timedelta(days=1)
        fecha_ayer = fecha_hoy - timezone.timedelta(days=2)
        agentes_tiempo = reportes_estadisticas.obtener_count_llamadas_campana(
            agentes, fecha_ayer, fecha_hoy, self.user_supervisor)

        for agente in agentes_tiempo:
            if agente[0] == self.agente.user.get_full_name():
                if agente[1] == self.manual.nombre:
                    self.assertEqual(str(timezone.timedelta(0, 181)), agente[2])
                    self.assertEqual(3, agente[3])
                elif agente[1] == self.dialer.nombre:
                    self.assertEqual(str(timezone.timedelta(0, 170)), agente[2])
                    self.assertEqual(2, agente[3])
                else:
                    self.fail("Calculo de campana no calculado revisar test")
            elif agente[0] == self.agente1.user.get_full_name():
                if agente[1] == self.preview.nombre:
                    self.assertEqual(str(timezone.timedelta(0, 58)), agente[2])
                    self.assertEqual(1, agente[3])
                elif agente[1] == self.entrante.nombre:
                    self.assertEqual(str(timezone.timedelta(0, 29)), agente[2])
                    self.assertEqual(1, agente[3])
                else:
                    self.fail("Calculo de campana no calculado revisar test")
            else:
                self.fail("Agente no calculado revisar test")

    def test_genera_correctamente_por_tipo_llamada_agente(self):
        """test que controla que la cantidad por tipo de llamadas y por cada
        agente"""

        generador = GeneradorDeLlamadaLogs()
        generador.generar_log(self.manual, True, 'COMPLETEAGENT', '123',
                              self.agente, duracion_llamada=76)
        generador.generar_log(self.manual, True, 'COMPLETEAGENT', '123',
                              self.agente, duracion_llamada=61)
        generador.generar_log(self.manual, True, 'COMPLETEAGENT', '123',
                              self.agente, duracion_llamada=44)
        generador.generar_log(self.dialer, False, 'COMPLETECALLER', '123',
                              self.agente, self.contacto_d, duracion_llamada=105,
                              )
        generador.generar_log(self.dialer, False, 'COMPLETECALLER', '123',
                              self.agente, self.contacto_d, duracion_llamada=65,
                              )
        generador.generar_log(self.preview, False, 'COMPLETEAGENT', '123',
                              self.agente, self.contacto_p, duracion_llamada=58
                              )
        generador.generar_log(self.preview, False, 'COMPLETEAGENT', '123',
                              self.agente, self.contacto_p, duracion_llamada=58
                              )
        generador.generar_log(self.entrante, False, 'COMPLETEAGENT', '123',
                              self.agente, self.contacto_e, duracion_llamada=29
                              )
        generador.generar_log(self.preview, False, 'COMPLETEAGENT', '123',
                              self.agente1, self.contacto_p, duracion_llamada=58
                              )
        generador.generar_log(self.entrante, False, 'COMPLETEAGENT', '123',
                              self.agente1, self.contacto_e, duracion_llamada=29
                              )
        generador.generar_log(self.entrante, False, 'COMPLETEAGENT', '123',
                              self.agente1, self.contacto_e, duracion_llamada=29
                              )
        generador.generar_log(self.entrante, False, 'COMPLETEAGENT', '123',
                              self.agente1, self.contacto_e, duracion_llamada=29
                              )
        generador.generar_log(self.dialer, False, 'COMPLETECALLER', '123',
                              self.agente1, self.contacto_d, duracion_llamada=65,
                              )

        # realizamos calculo con el modulo
        reportes_estadisticas = TiemposAgente()
        agentes = AgenteProfile.objects.obtener_activos()
        fecha_hoy = timezone.now() + timezone.timedelta(days=1)
        fecha_ayer = fecha_hoy - timezone.timedelta(days=2)
        dict_agentes = reportes_estadisticas._obtener_total_agentes_tipos_llamadas(
            agentes, fecha_ayer, fecha_hoy)

        self.assertEqual([2, 1], dict_agentes['total_agente_preview'])
        self.assertEqual([3, 0], dict_agentes['total_agente_manual'])
        self.assertEqual([1, 3], dict_agentes['total_agente_inbound'])
        self.assertEqual([2, 1], dict_agentes['total_agente_dialer'])
        self.assertEqual([8, 5], dict_agentes['total_agentes'])
        self.assertEqual([self.agente.user.get_full_name(),
                          self.agente1.user.get_full_name()],
                         dict_agentes['nombres_agentes'])

    def test_genera_correctamente_tiempo_inicio_sesion_fecha(self):
        """test que controla que los tiempo de sesion de los agentes
         se generen correcamente"""
        inicio_sesion_agente = self.inicio_sesion_agente.time - timezone.timedelta(
            minutes=17) - timezone.timedelta(days=10)
        ActividadAgenteLogFactory.create(
            event='ADDMEMBER', agente_id=self.agente.id, time=inicio_sesion_agente)
        fin_sesion_agente = self.fin_sesion_agente.time + timezone.timedelta(
            minutes=79) - timezone.timedelta(days=10)
        ActividadAgenteLogFactory.create(
            time=fin_sesion_agente, event='REMOVEMEMBER', agente_id=self.agente.id)

        # calculo el tiempo de sesion del agente
        tiempo_sesion_agente = self.fin_sesion_agente.time - self.inicio_sesion_agente.time
        tiempo_sesion_agente1 = fin_sesion_agente - inicio_sesion_agente

        # realizamos calculo con el modulo
        reportes_estadisticas = TiemposAgente()
        fecha_hoy = timezone.now()
        fecha_inferior = fecha_hoy - timezone.timedelta(days=20)
        agentes_tiempo = reportes_estadisticas.calcular_tiempo_session_fecha_agente(
            self.agente, fecha_inferior, fecha_hoy, [])

        time_sesion = cast_datetime_part_date(self.fin_sesion_agente.time)
        time_sesion1 = cast_datetime_part_date(fin_sesion_agente)

        for agente in agentes_tiempo:
            if time_sesion == agente.agente:
                self.assertEqual(tiempo_sesion_agente, agente.tiempo_sesion)
            elif time_sesion1 == agente.agente:
                self.assertEqual(tiempo_sesion_agente1, agente.tiempo_sesion)
            else:
                self.fail("Fecha no calculado para agente revisar test")
