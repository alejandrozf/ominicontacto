# -*- coding: utf-8 -*-

from django.test import TestCase

from ominicontacto_app.models import Campana
from ominicontacto_app.tests.factories import (UserFactory, CampanaFactory, AgenteProfileFactory,
                                               ContactoFactory)

from reportes_app.models import LlamadaLog
from reportes_app.tests.utiles import GeneradorDeLlamadaLogs


class GeneradorDeLlamadaLogsTests(TestCase):

    def setUp(self):
        super(GeneradorDeLlamadaLogsTests, self).setUp()
        self.manual = CampanaFactory.create(type=Campana.TYPE_MANUAL)
        self.usr_agente1 = UserFactory.create(username='agente1', is_agente=True)
        self.agente1 = AgenteProfileFactory.create(user=self.usr_agente1)

        self.dialer = CampanaFactory.create(type=Campana.TYPE_DIALER)
        self.contacto_d = ContactoFactory(bd_contacto=self.dialer.bd_contacto)

        self.entrante = CampanaFactory.create(type=Campana.TYPE_ENTRANTE)

        self.preview = CampanaFactory.create(type=Campana.TYPE_PREVIEW)
        self.contacto_p = ContactoFactory(bd_contacto=self.preview.bd_contacto)

    def set_de_eventos(self, queryset):
        return set(queryset.values_list('event', flat=True))

    # # MANUAL
    # # DIALER MANUAL
    def test_genera_manual_incompleta(self):
        generador = GeneradorDeLlamadaLogs()
        generador.generar_log(self.manual, True, 'BUSY', '123', self.agente1, bridge_wait_time=5)
        logs_generados = LlamadaLog.objects.filter(campana_id=self.manual.id)
        eventos_esperados = set(('DIAL', 'BUSY'))
        self.assertEqual(self.set_de_eventos(logs_generados), eventos_esperados)

        dial = logs_generados.get(event='DIAL')
        self.assertEqual(dial.campana_id, self.manual.id)
        self.assertEqual(dial.tipo_campana, self.manual.type)
        self.assertEqual(dial.tipo_llamada, self.manual.type)
        self.assertEqual(dial.agente_id, self.agente1.id)

        busy = logs_generados.get(event='BUSY')
        self.assertEqual(busy.campana_id, self.manual.id)
        self.assertEqual(busy.tipo_campana, self.manual.type)
        self.assertEqual(busy.tipo_llamada, self.manual.type)
        self.assertEqual(busy.bridge_wait_time, 5)

    def test_genera_manual_completa(self):
        generador = GeneradorDeLlamadaLogs()
        generador.generar_log(self.manual, True, 'COMPLETEAGENT', '123', self.agente1,
                              bridge_wait_time=5, duracion_llamada=44, archivo_grabacion='archi')
        logs_generados = LlamadaLog.objects.filter(campana_id=self.manual.id)
        eventos_esperados = set(('DIAL', 'ANSWER', 'COMPLETEAGENT'))
        self.assertEqual(self.set_de_eventos(logs_generados), eventos_esperados)

        dial = logs_generados.get(event='DIAL')
        self.assertEqual(dial.campana_id, self.manual.id)
        self.assertEqual(dial.tipo_campana, self.manual.type)
        self.assertEqual(dial.tipo_llamada, self.manual.type)
        self.assertEqual(dial.agente_id, self.agente1.id)

        answer = logs_generados.get(event='ANSWER')
        self.assertEqual(answer.campana_id, self.manual.id)
        self.assertEqual(answer.tipo_campana, self.manual.type)
        self.assertEqual(answer.tipo_llamada, self.manual.type)
        self.assertEqual(answer.agente_id, self.agente1.id)
        self.assertEqual(answer.bridge_wait_time, 5)

        complete = logs_generados.get(event='COMPLETEAGENT')
        self.assertEqual(complete.campana_id, self.manual.id)
        self.assertEqual(complete.tipo_campana, self.manual.type)
        self.assertEqual(complete.tipo_llamada, self.manual.type)
        self.assertEqual(complete.agente_id, self.agente1.id)
        self.assertEqual(complete.bridge_wait_time, 5)
        self.assertEqual(complete.duracion_llamada, 44)
        self.assertEqual(complete.archivo_grabacion, 'archi')

    def test_genera_dialer_manual_incompleta(self):
        generador = GeneradorDeLlamadaLogs()
        generador.generar_log(self.dialer, True, 'BUSY', '123', self.agente1, bridge_wait_time=5)
        logs_generados = LlamadaLog.objects.filter(campana_id=self.dialer.id)
        eventos_esperados = set(('DIAL', 'BUSY'))
        self.assertEqual(self.set_de_eventos(logs_generados), eventos_esperados)

        dial = logs_generados.get(event='DIAL')
        self.assertEqual(dial.campana_id, self.dialer.id)
        self.assertEqual(dial.tipo_campana, self.dialer.type)
        self.assertEqual(dial.tipo_llamada, Campana.TYPE_MANUAL)
        self.assertEqual(dial.agente_id, self.agente1.id)

        busy = logs_generados.get(event='BUSY')
        self.assertEqual(busy.campana_id, self.dialer.id)
        self.assertEqual(busy.tipo_campana, self.dialer.type)
        self.assertEqual(busy.tipo_llamada, Campana.TYPE_MANUAL)
        self.assertEqual(busy.agente_id, self.agente1.id)
        self.assertEqual(busy.bridge_wait_time, 5)

    def test_genera_dialer_manual_completa(self):
        generador = GeneradorDeLlamadaLogs()
        generador.generar_log(self.dialer, True, 'COMPLETECALLER', '123', self.agente1,
                              bridge_wait_time=5, duracion_llamada=44, archivo_grabacion='archi')
        logs_generados = LlamadaLog.objects.filter(campana_id=self.dialer.id)
        eventos_esperados = set(('DIAL', 'ANSWER', 'COMPLETECALLER'))
        self.assertEqual(self.set_de_eventos(logs_generados), eventos_esperados)

        dial = logs_generados.get(event='DIAL')
        self.assertEqual(dial.campana_id, self.dialer.id)
        self.assertEqual(dial.tipo_campana, self.dialer.type)
        self.assertEqual(dial.tipo_llamada, Campana.TYPE_MANUAL)
        self.assertEqual(dial.agente_id, self.agente1.id)

        answer = logs_generados.get(event='ANSWER')
        self.assertEqual(answer.campana_id, self.dialer.id)
        self.assertEqual(answer.tipo_campana, self.dialer.type)
        self.assertEqual(answer.tipo_llamada, Campana.TYPE_MANUAL)
        self.assertEqual(answer.agente_id, self.agente1.id)
        self.assertEqual(answer.bridge_wait_time, 5)

        complete = logs_generados.get(event='COMPLETECALLER')
        self.assertEqual(complete.campana_id, self.dialer.id)
        self.assertEqual(complete.tipo_campana, self.dialer.type)
        self.assertEqual(complete.tipo_llamada, Campana.TYPE_MANUAL)
        self.assertEqual(complete.agente_id, self.agente1.id)
        self.assertEqual(complete.bridge_wait_time, 5)
        self.assertEqual(complete.duracion_llamada, 44)
        self.assertEqual(complete.archivo_grabacion, 'archi')

    # # DIALER WOMBAT
    def test_genera_dialer_incompleta_sin_connect(self):
        generador = GeneradorDeLlamadaLogs()
        generador.generar_log(self.dialer, False, 'BUSY', '123', self.agente1, self.contacto_d,
                              bridge_wait_time=5)
        logs_generados = LlamadaLog.objects.filter(campana_id=self.dialer.id)
        eventos_esperados = set(('DIAL', 'BUSY'))
        self.assertEqual(self.set_de_eventos(logs_generados), eventos_esperados)

        dial = logs_generados.get(event='DIAL')
        self.assertEqual(dial.campana_id, self.dialer.id)
        self.assertEqual(dial.tipo_campana, self.dialer.type)
        self.assertEqual(dial.tipo_llamada, self.dialer.type)
        self.assertEqual(dial.agente_id, -1)
        self.assertEqual(dial.contacto_id, self.contacto_d.id)

        busy = logs_generados.get(event='BUSY')
        self.assertEqual(busy.campana_id, self.dialer.id)
        self.assertEqual(busy.tipo_campana, self.dialer.type)
        self.assertEqual(busy.tipo_llamada, self.dialer.type)
        self.assertEqual(busy.agente_id, -1)
        self.assertEqual(dial.contacto_id, self.contacto_d.id)
        self.assertEqual(busy.bridge_wait_time, 5)

    def test_genera_dialer_incompleta_por_abandon(self):
        generador = GeneradorDeLlamadaLogs()
        generador.generar_log(self.dialer, False, 'ABANDON', '123', self.agente1, self.contacto_d,
                              bridge_wait_time=5, duracion_llamada=44)
        logs_generados = LlamadaLog.objects.filter(campana_id=self.dialer.id)
        # ASUMO que al ser abandon, la pata dial detecta que el cliente abandonó
        eventos_esperados = set(('DIAL', 'ANSWER', 'COMPLETECALLER', 'ENTERQUEUE', 'ABANDON'))
        self.assertEqual(self.set_de_eventos(logs_generados), eventos_esperados)

        dial = logs_generados.get(event='DIAL')
        self.assertEqual(dial.campana_id, self.dialer.id)
        self.assertEqual(dial.tipo_campana, self.dialer.type)
        self.assertEqual(dial.tipo_llamada, self.dialer.type)
        self.assertEqual(dial.agente_id, -1)
        self.assertEqual(dial.contacto_id, self.contacto_d.id)
        self.assertEqual(dial.numero_marcado, '123')

        answer = logs_generados.get(event='ANSWER')
        self.assertEqual(answer.campana_id, self.dialer.id)
        self.assertEqual(answer.tipo_campana, self.dialer.type)
        self.assertEqual(answer.tipo_llamada, self.dialer.type)
        self.assertEqual(answer.agente_id, -1)
        self.assertEqual(answer.contacto_id, self.contacto_d.id)
        self.assertEqual(answer.bridge_wait_time, 5)

        complete = logs_generados.get(event='COMPLETECALLER', agente_id=-1)
        self.assertEqual(complete.campana_id, self.dialer.id)
        self.assertEqual(complete.tipo_campana, self.dialer.type)
        self.assertEqual(complete.tipo_llamada, self.dialer.type)
        self.assertEqual(complete.agente_id, -1)
        self.assertEqual(complete.contacto_id, self.contacto_d.id)
        self.assertEqual(complete.bridge_wait_time, 5)
        self.assertEqual(complete.duracion_llamada, 44)
        self.assertEqual(complete.archivo_grabacion, '')

        enterqueue = logs_generados.get(event='ENTERQUEUE')
        self.assertEqual(enterqueue.campana_id, self.dialer.id)
        self.assertEqual(enterqueue.tipo_campana, self.dialer.type)
        self.assertEqual(enterqueue.tipo_llamada, self.dialer.type)
        self.assertEqual(enterqueue.contacto_id, self.contacto_d.id)
        self.assertEqual(enterqueue.agente_id, -1)
        self.assertEqual(enterqueue.bridge_wait_time, -1)
        self.assertEqual(enterqueue.duracion_llamada, -1)
        self.assertEqual(enterqueue.archivo_grabacion, '')

        abandon = logs_generados.get(event='ABANDON')
        self.assertEqual(abandon.campana_id, self.dialer.id)
        self.assertEqual(abandon.tipo_campana, self.dialer.type)
        self.assertEqual(abandon.tipo_llamada, self.dialer.type)
        self.assertEqual(abandon.contacto_id, self.contacto_d.id)
        self.assertEqual(abandon.agente_id, -1)
        self.assertEqual(abandon.bridge_wait_time, 5)
        self.assertEqual(abandon.duracion_llamada, -1)
        self.assertEqual(abandon.archivo_grabacion, '')

    def test_genera_dialer_incompleta_por_exitwithtimeout(self):
        generador = GeneradorDeLlamadaLogs()
        generador.generar_log(self.dialer, False, 'EXITWITHTIMEOUT', '123', self.agente1,
                              self.contacto_d, bridge_wait_time=5, duracion_llamada=44)
        logs_generados = LlamadaLog.objects.filter(campana_id=self.dialer.id)
        # ASUMO que al ser EXITWITHTIMEOUT, la pata dial detecta que el agente terminó la conexión
        eventos_esperados = set(('DIAL', 'ANSWER', 'COMPLETEAGENT', 'ENTERQUEUE',
                                 'EXITWITHTIMEOUT'))
        self.assertEqual(self.set_de_eventos(logs_generados), eventos_esperados)

        dial = logs_generados.get(event='DIAL')
        self.assertEqual(dial.campana_id, self.dialer.id)
        self.assertEqual(dial.tipo_campana, self.dialer.type)
        self.assertEqual(dial.tipo_llamada, self.dialer.type)
        self.assertEqual(dial.agente_id, -1)
        self.assertEqual(dial.contacto_id, self.contacto_d.id)
        self.assertEqual(dial.numero_marcado, '123')

        answer = logs_generados.get(event='ANSWER')
        self.assertEqual(answer.campana_id, self.dialer.id)
        self.assertEqual(answer.tipo_campana, self.dialer.type)
        self.assertEqual(answer.tipo_llamada, self.dialer.type)
        self.assertEqual(answer.agente_id, -1)
        self.assertEqual(answer.contacto_id, self.contacto_d.id)
        self.assertEqual(answer.bridge_wait_time, 5)

        complete = logs_generados.get(event='COMPLETEAGENT', agente_id=-1)
        self.assertEqual(complete.campana_id, self.dialer.id)
        self.assertEqual(complete.tipo_campana, self.dialer.type)
        self.assertEqual(complete.tipo_llamada, self.dialer.type)
        self.assertEqual(complete.contacto_id, self.contacto_d.id)
        self.assertEqual(complete.bridge_wait_time, 5)
        self.assertEqual(complete.duracion_llamada, 44)
        self.assertEqual(complete.archivo_grabacion, '')

        enterqueue = logs_generados.get(event='ENTERQUEUE')
        self.assertEqual(enterqueue.campana_id, self.dialer.id)
        self.assertEqual(enterqueue.tipo_campana, self.dialer.type)
        self.assertEqual(enterqueue.tipo_llamada, self.dialer.type)
        self.assertEqual(enterqueue.contacto_id, self.contacto_d.id)
        self.assertEqual(enterqueue.agente_id, -1)
        self.assertEqual(enterqueue.bridge_wait_time, -1)
        self.assertEqual(enterqueue.duracion_llamada, -1)
        self.assertEqual(enterqueue.archivo_grabacion, '')

        abandon = logs_generados.get(event='EXITWITHTIMEOUT')
        self.assertEqual(abandon.campana_id, self.dialer.id)
        self.assertEqual(abandon.tipo_campana, self.dialer.type)
        self.assertEqual(abandon.tipo_llamada, self.dialer.type)
        self.assertEqual(abandon.contacto_id, self.contacto_d.id)
        self.assertEqual(abandon.agente_id, -1)
        self.assertEqual(abandon.bridge_wait_time, 5)
        self.assertEqual(abandon.duracion_llamada, -1)
        self.assertEqual(abandon.archivo_grabacion, '')

    def test_genera_dialer_completa_completeagent(self):
        generador = GeneradorDeLlamadaLogs()
        generador.generar_log(self.dialer, False, 'COMPLETEAGENT', '123', self.agente1,
                              self.contacto_d, bridge_wait_time=5, duracion_llamada=44,
                              archivo_grabacion='archi')
        logs_generados = LlamadaLog.objects.filter(campana_id=self.dialer.id)
        eventos_esperados = set(('DIAL', 'ANSWER', 'COMPLETEAGENT', 'ENTERQUEUE', 'CONNECT'))
        self.assertEqual(self.set_de_eventos(logs_generados), eventos_esperados)

        # Pata Dialer
        dial = logs_generados.get(event='DIAL')
        self.assertEqual(dial.campana_id, self.dialer.id)
        self.assertEqual(dial.tipo_campana, self.dialer.type)
        self.assertEqual(dial.tipo_llamada, self.dialer.type)
        self.assertEqual(dial.agente_id, -1)
        self.assertEqual(dial.contacto_id, self.contacto_d.id)

        answer = logs_generados.get(event='ANSWER')
        self.assertEqual(answer.campana_id, self.dialer.id)
        self.assertEqual(answer.tipo_campana, self.dialer.type)
        self.assertEqual(answer.tipo_llamada, self.dialer.type)
        self.assertEqual(answer.agente_id, -1)
        self.assertEqual(answer.contacto_id, self.contacto_d.id)
        self.assertEqual(answer.bridge_wait_time, 5)

        complete_dial = logs_generados.get(event='COMPLETEAGENT', agente_id=-1)
        self.assertEqual(complete_dial.campana_id, self.dialer.id)
        self.assertEqual(complete_dial.tipo_campana, self.dialer.type)
        self.assertEqual(complete_dial.tipo_llamada, self.dialer.type)
        self.assertEqual(complete_dial.agente_id, -1)
        self.assertEqual(complete_dial.contacto_id, self.contacto_d.id)
        self.assertEqual(complete_dial.bridge_wait_time, 5)
        self.assertEqual(complete_dial.duracion_llamada, 44)
        self.assertEqual(complete_dial.archivo_grabacion, '')

        # Pata Agente
        enterqueue = logs_generados.get(event='ENTERQUEUE')
        self.assertEqual(enterqueue.campana_id, self.dialer.id)
        self.assertEqual(enterqueue.tipo_campana, self.dialer.type)
        self.assertEqual(enterqueue.tipo_llamada, self.dialer.type)
        self.assertEqual(enterqueue.contacto_id, self.contacto_d.id)
        self.assertEqual(enterqueue.agente_id, -1)
        self.assertEqual(enterqueue.bridge_wait_time, -1)
        self.assertEqual(enterqueue.duracion_llamada, -1)
        self.assertEqual(enterqueue.archivo_grabacion, '')

        connect = logs_generados.get(event='CONNECT')
        self.assertEqual(connect.campana_id, self.dialer.id)
        self.assertEqual(connect.tipo_campana, self.dialer.type)
        self.assertEqual(connect.tipo_llamada, self.dialer.type)
        self.assertEqual(connect.agente_id, self.agente1.id)
        self.assertEqual(connect.contacto_id, self.contacto_d.id)
        self.assertEqual(connect.bridge_wait_time, 5)
        self.assertEqual(connect.duracion_llamada, -1)
        self.assertEqual(connect.archivo_grabacion, '')

        complete = logs_generados.get(event='COMPLETEAGENT', agente_id=self.agente1.id)
        self.assertEqual(complete.campana_id, self.dialer.id)
        self.assertEqual(complete.tipo_campana, self.dialer.type)
        self.assertEqual(complete.tipo_llamada, self.dialer.type)
        self.assertEqual(complete.agente_id, self.agente1.id)
        self.assertEqual(complete.contacto_id, self.contacto_d.id)
        self.assertEqual(complete.bridge_wait_time, 5)
        self.assertEqual(complete.duracion_llamada, 44)
        self.assertEqual(complete.archivo_grabacion, 'archi')

    # # ENTRANTE
    def test_genera_entrante_incompleta(self):
        generador = GeneradorDeLlamadaLogs()
        generador.generar_log(self.entrante, False, 'ABANDON', '123', self.agente1,
                              bridge_wait_time=5)
        logs_generados = LlamadaLog.objects.filter(campana_id=self.entrante.id)
        eventos_esperados = set(('ENTERQUEUE', 'ABANDON'))
        self.assertEqual(self.set_de_eventos(logs_generados), eventos_esperados)

        enterqueue = logs_generados.get(event='ENTERQUEUE')
        self.assertEqual(enterqueue.campana_id, self.entrante.id)
        self.assertEqual(enterqueue.tipo_campana, self.entrante.type)
        self.assertEqual(enterqueue.tipo_llamada, self.entrante.type)
        self.assertEqual(enterqueue.contacto_id, -1)
        self.assertEqual(enterqueue.agente_id, -1)
        self.assertEqual(enterqueue.bridge_wait_time, -1)
        self.assertEqual(enterqueue.duracion_llamada, -1)
        self.assertEqual(enterqueue.archivo_grabacion, '')

        abandon = logs_generados.get(event='ABANDON')
        self.assertEqual(abandon.campana_id, self.entrante.id)
        self.assertEqual(abandon.tipo_campana, self.entrante.type)
        self.assertEqual(abandon.tipo_llamada, self.entrante.type)
        self.assertEqual(abandon.contacto_id, -1)
        self.assertEqual(abandon.agente_id, -1)
        self.assertEqual(abandon.bridge_wait_time, 5)
        self.assertEqual(abandon.duracion_llamada, -1)
        self.assertEqual(abandon.archivo_grabacion, '')

    def test_genera_entrante_completa(self):
        generador = GeneradorDeLlamadaLogs()
        generador.generar_log(self.entrante, False, 'COMPLETEAGENT', '123', self.agente1,
                              bridge_wait_time=5, duracion_llamada=44, archivo_grabacion='archi')
        logs_generados = LlamadaLog.objects.filter(campana_id=self.entrante.id)
        eventos_esperados = set(('ENTERQUEUE', 'CONNECT', 'COMPLETEAGENT'))
        self.assertEqual(self.set_de_eventos(logs_generados), eventos_esperados)

        enterqueue = logs_generados.get(event='ENTERQUEUE')
        self.assertEqual(enterqueue.campana_id, self.entrante.id)
        self.assertEqual(enterqueue.tipo_campana, self.entrante.type)
        self.assertEqual(enterqueue.tipo_llamada, self.entrante.type)
        self.assertEqual(enterqueue.contacto_id, -1)
        self.assertEqual(enterqueue.agente_id, -1)
        self.assertEqual(enterqueue.bridge_wait_time, -1)
        self.assertEqual(enterqueue.duracion_llamada, -1)
        self.assertEqual(enterqueue.archivo_grabacion, '')

        connect = logs_generados.get(event='CONNECT')
        self.assertEqual(connect.campana_id, self.entrante.id)
        self.assertEqual(connect.tipo_campana, self.entrante.type)
        self.assertEqual(connect.tipo_llamada, self.entrante.type)
        self.assertEqual(connect.agente_id, self.agente1.id)
        self.assertEqual(connect.contacto_id, -1)
        self.assertEqual(connect.bridge_wait_time, 5)
        self.assertEqual(connect.duracion_llamada, -1)
        self.assertEqual(connect.archivo_grabacion, '')

        complete = logs_generados.get(event='COMPLETEAGENT')
        self.assertEqual(complete.campana_id, self.entrante.id)
        self.assertEqual(complete.tipo_campana, self.entrante.type)
        self.assertEqual(complete.tipo_llamada, self.entrante.type)
        self.assertEqual(complete.agente_id, self.agente1.id)
        self.assertEqual(complete.contacto_id, -1)
        self.assertEqual(complete.bridge_wait_time, 5)
        self.assertEqual(complete.duracion_llamada, 44)
        self.assertEqual(complete.archivo_grabacion, 'archi')

    # # PREVIEW
    def test_genera_preview_incompleta(self):
        generador = GeneradorDeLlamadaLogs()
        generador.generar_log(self.preview, False, 'BUSY', '123', self.agente1, self.contacto_p,
                              bridge_wait_time=5)
        logs_generados = LlamadaLog.objects.filter(campana_id=self.preview.id)
        eventos_esperados = set(('DIAL', 'BUSY'))
        self.assertEqual(self.set_de_eventos(logs_generados), eventos_esperados)

        dial = logs_generados.get(event='DIAL')
        self.assertEqual(dial.campana_id, self.preview.id)
        self.assertEqual(dial.tipo_campana, self.preview.type)
        self.assertEqual(dial.tipo_llamada, self.preview.type)
        self.assertEqual(dial.agente_id, self.agente1.id)

        busy = logs_generados.get(event='BUSY')
        self.assertEqual(busy.campana_id, self.preview.id)
        self.assertEqual(busy.tipo_campana, self.preview.type)
        self.assertEqual(busy.tipo_llamada, self.preview.type)
        self.assertEqual(busy.bridge_wait_time, 5)

    def test_genera_preview_completa(self):
        generador = GeneradorDeLlamadaLogs()
        generador.generar_log(self.preview, False, 'COMPLETEAGENT', '123', self.agente1,
                              self.contacto_p,
                              bridge_wait_time=5, duracion_llamada=44, archivo_grabacion='archi')
        logs_generados = LlamadaLog.objects.filter(campana_id=self.preview.id)
        eventos_esperados = set(('DIAL', 'ANSWER', 'COMPLETEAGENT'))
        self.assertEqual(self.set_de_eventos(logs_generados), eventos_esperados)

        dial = logs_generados.get(event='DIAL')
        self.assertEqual(dial.campana_id, self.preview.id)
        self.assertEqual(dial.tipo_campana, self.preview.type)
        self.assertEqual(dial.tipo_llamada, self.preview.type)
        self.assertEqual(dial.agente_id, self.agente1.id)
        self.assertEqual(dial.contacto_id, self.contacto_p.id)

        answer = logs_generados.get(event='ANSWER')
        self.assertEqual(answer.campana_id, self.preview.id)
        self.assertEqual(answer.tipo_campana, self.preview.type)
        self.assertEqual(answer.tipo_llamada, self.preview.type)
        self.assertEqual(answer.agente_id, self.agente1.id)
        self.assertEqual(answer.contacto_id, self.contacto_p.id)
        self.assertEqual(answer.bridge_wait_time, 5)

        complete = logs_generados.get(event='COMPLETEAGENT')
        self.assertEqual(complete.campana_id, self.preview.id)
        self.assertEqual(complete.tipo_campana, self.preview.type)
        self.assertEqual(complete.tipo_llamada, self.preview.type)
        self.assertEqual(complete.agente_id, self.agente1.id)
        self.assertEqual(complete.contacto_id, self.contacto_p.id)
        self.assertEqual(complete.bridge_wait_time, 5)
        self.assertEqual(complete.duracion_llamada, 44)
        self.assertEqual(complete.archivo_grabacion, 'archi')
