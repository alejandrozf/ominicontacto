# -*- coding: utf-8 -*-

"""
Tests del los reportes que realiza el sistema
"""
from random import choice
from unittest import skipIf

from django.conf import settings
from django.db import connection
from django.utils import timezone

from ominicontacto_app.tests.utiles import OMLBaseTest
from reportes_app.models import ActividadAgenteLog, LlamadaLog

# Valores por defecto para insertar en la tabla queue_log
CALLID = '2312312.233'
EVENT = 'ENTERQUEUE'
TELEFONO = '1234567890'
CONTACTO_ID = 1
BRIDGE_WAIT_TIME = 5
DURACION_LLAMADA = 60
ARCHIVO_GRABACION = 'grabacion.mp3'


class TriggerQueuelogTest(OMLBaseTest):

    def _aplicar_sql_query(self, queuename, time=timezone.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                           callid=CALLID, agent=1, event=EVENT, data1=TELEFONO,
                           data2=CONTACTO_ID, data3=BRIDGE_WAIT_TIME, data4=DURACION_LLAMADA,
                           data5=ARCHIVO_GRABACION):
        fields = "(time, callid, queuename, agent, event, data1, data2, data3, data4, data5)"
        values = (time, callid, queuename, agent, event, data1, data2, data3, data4, data5)
        sql_query = "insert into queue_log {0} values {1};".format(fields, str(values))
        with connection.cursor() as c:
            c.execute(sql_query)

    @skipIf(hasattr(settings, 'DESHABILITAR_MIGRACIONES_EN_TESTS') and
            settings.DESHABILITAR_MIGRACIONES_EN_TESTS,
            'Sin migraciones no existe la tabla ´queue_log´')
    def test_adicion_eventos_llamadas_inserta_en_modelo_logs_llamadas(self):
        queuename = '1-1-1'
        EVENTOS_LLAMADAS = [
            'DIAL',
            'ANSWER',
            'CONNECT',
            'COMPLETEAGENT',
            'COMPLETECALLER',
            'ENTERQUEUE',
            'EXITWITHTIMEOUT',
            'ABANDON',
            'NOANSWER',
            'CANCEL',
            'BUSY',
            'CHANUNAVAIL',
            'OTHER',
            'FAIL',
            'AMD',
            'BLACKLIST',
            'RINGNOANSWER',
        ]
        evento = choice(EVENTOS_LLAMADAS)
        self._aplicar_sql_query(queuename, event=evento)
        self.assertTrue(LlamadaLog.objects.all().exists())

    @skipIf(hasattr(settings, 'DESHABILITAR_MIGRACIONES_EN_TESTS') and
            settings.DESHABILITAR_MIGRACIONES_EN_TESTS,
            'Sin migraciones no existe la tabla ´queue_log´')
    def test_adicion_info_campanas_pasa_correctamente_a_modelo_de_logs_llamadas(self):
        queuename = '1-1-1'
        campana_id, tipo_campana, tipo_llamada = queuename.split("-")
        self._aplicar_sql_query(queuename)
        llamada_log = LlamadaLog.objects.first()
        self.assertEqual(llamada_log.campana_id, int(campana_id))
        self.assertEqual(llamada_log.tipo_campana, int(tipo_campana))
        self.assertEqual(llamada_log.tipo_llamada, int(tipo_llamada))

    @skipIf(hasattr(settings, 'DESHABILITAR_MIGRACIONES_EN_TESTS') and
            settings.DESHABILITAR_MIGRACIONES_EN_TESTS,
            'Sin migraciones no existe la tabla ´queue_log´')
    def test_adicion_info_incorrecta_campanas_pasa_valores_error_a_logs_llamadas(self):
        queuename = ''
        self._aplicar_sql_query(queuename)
        llamada_log = LlamadaLog.objects.first()
        self.assertEqual(llamada_log.campana_id, -1)
        self.assertEqual(llamada_log.tipo_campana, -1)
        self.assertEqual(llamada_log.tipo_llamada, -1)

    @skipIf(hasattr(settings, 'DESHABILITAR_MIGRACIONES_EN_TESTS') and
            settings.DESHABILITAR_MIGRACIONES_EN_TESTS,
            'Sin migraciones no existe la tabla ´queue_log´')
    def test_eventos_sesion_actividad_agente_insertan_info_en_tabla_logs_actividades_agente(self):
        queuename = 'ALL'
        evento_agente = choice(['ADDMEMBER', 'REMOVEMEMBER', 'PAUSEALL', 'UNPAUSEALL'])
        self._aplicar_sql_query(queuename, event=evento_agente)
        actividad_agente_log = ActividadAgenteLog.objects.first()
        self.assertEqual(actividad_agente_log.event, evento_agente)

    @skipIf(hasattr(settings, 'DESHABILITAR_MIGRACIONES_EN_TESTS') and
            settings.DESHABILITAR_MIGRACIONES_EN_TESTS,
            'Sin migraciones no existe la tabla ´queue_log´')
    def test_evento_no_logueable_no_se_inserta_en_logs_llamadas_actividades_agentes(self):
        queuename = '1-1-1'
        evento_no_logueable = 'NO_LOGUEAR'
        self._aplicar_sql_query(queuename, event=evento_no_logueable)
        self.assertFalse(LlamadaLog.objects.all().exists())
        self.assertFalse(ActividadAgenteLog.objects.all().exists())

    def test_eventos_llamadas_tranferencias_se_insertan_en_logs_llamadas_actividades(self):
        # TODO: este test documenta la posibilidad de inserción de nuevos eventos de llamadas
        # pero se debería realizar un testing más profundo del manejo que se hace sobre estos
        # logs
        EVENTOS_TRANSFERENCIAS = [
            'BT-TRY',
            'BT-ANSWER',
            'BT-BUSY',
            'BT-CANCEL',
            'BT-CHANUNAVAIL',
            'BT-CONGESTION',
            'BT-ABANDON',
            'CAMPT-TRY',
            'CAMPT-FAIL',
            'CAMPT-COMPLETE',
            'ENTERQUEUE-TRANSFER',
            'CT-TRY',
            'CT-ANSWER',
            'CT-ACCEPT',
            'CT-COMPLETE',
            'CT-DISCARD',
            'CT-BUSY',
            'CT-CANCEL',
            'CT-CHANUNAVAIL',
            'CT-CONGESTION',
            'BTOUT-TRY',
            'BTOUT-ANSWER',
            'BTOUT-BUSY',
            'BTOUT-CANCEL',
            'BTOUT-CONGESTION',
            'BTOUT-CHANUNAVAIL',
            'BTOUT-ABANDON',
            'CTOUT-TRY',
            'CTOUT-ANSWER',
            'CTOUT-ACCEPT',
            'CTOUT-COMPLETE',
            'CTOUT-DISCARD',
            'CTOUT-BUSY',
            'CTOUT-CANCEL',
            'CTOUT-CHANUNAVAIL',
            'CTOUT-CONGESTION',
        ]

        for evento_transferencia in EVENTOS_TRANSFERENCIAS:
            queuename = '1-1-1'
            self._aplicar_sql_query(queuename, event=evento_transferencia)
        self.assertEqual(set(LlamadaLog.objects.values_list('event')), set(EVENTOS_TRANSFERENCIAS))
