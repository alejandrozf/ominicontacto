# -*- coding: utf-8 -*-

"""
Tests del los reportes que realiza el sistema
"""
from random import choice
from unittest import skipIf

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import connection
from django.utils import timezone

from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.tests.factories import CampanaFactory, UserFactory
from ominicontacto_app.models import Campana
from reportes.models import ActividadAgenteLog, LlamadaLog
from ominicontacto_app.services.reporte_grafico import GraficoService


class BaseReportesTests(OMLBaseTest):
    PWD = u'admin123'

    def setUp(self):
        self.usuario_admin_supervisor = UserFactory(is_staff=True, is_supervisor=True)
        self.usuario_admin_supervisor.set_password(self.PWD)
        self.usuario_admin_supervisor.save()

        self.client.login(username=self.usuario_admin_supervisor.username,
                          password=self.PWD)


class ReportesTests(BaseReportesTests):

    def setUp(self):
        super(ReportesTests, self).setUp()
        self.fecha_inicio = timezone.now()

        self.evento_llamadas_ingresadas = 'ENTERQUEUE'
        self.evento_llamadas_atendidas = 'CONNECT'
        self.evento_llamadas_abandonadas = 'ABANDON'
        self.evento_llamadas_expiradas = 'EXITWITHTIMEOUT'

        self.NRO_CAMPANAS_DIALER = 10
        self.NRO_CAMPANAS_ENTRANTES = 7
        self.NRO_CAMPANAS_MANUALES = 5
        self.NRO_CAMPANAS_PREVIEW = 4

        self.NRO_QUEUES_DIALER_INGRESADAS = 100
        self.NRO_QUEUES_DIALER_ATENDIDAS = 40
        self.NRO_QUEUES_DIALER_ABANDONADAS = 35
        self.NRO_QUEUES_DIALER_EXPIRADAS = 25

        self.NRO_QUEUES_ENTRANTES_INGRESADAS = 80
        self.NRO_QUEUES_ENTRANTES_ATENDIDAS = 10
        self.NRO_QUEUES_ENTRANTES_ABANDONADAS = 50
        self.NRO_QUEUES_ENTRANTES_EXPIRADAS = 20

        self.NRO_QUEUES_MANUALES_INGRESADAS = 80
        self.NRO_QUEUES_MANUALES_ATENDIDAS = 55
        self.NRO_QUEUES_MANUALES_ABANDONADAS = 25

        self.NRO_QUEUES_PREVIEW_INGRESADAS = 70
        self.NRO_QUEUES_PREVIEW_ATENDIDAS = 45
        self.NRO_QUEUES_PREVIEW_ABANDONADAS = 25

        self.campanas_dialer = CampanaFactory.create_batch(
            self.NRO_CAMPANAS_DIALER, type=Campana.TYPE_DIALER, estado=Campana.ESTADO_ACTIVA,
            reported_by=self.usuario_admin_supervisor)
        self.campanas_entrantes = CampanaFactory.create_batch(
            self.NRO_CAMPANAS_ENTRANTES, type=Campana.TYPE_ENTRANTE, estado=Campana.ESTADO_ACTIVA,
            reported_by=self.usuario_admin_supervisor)
        self.campanas_manuales = CampanaFactory.create_batch(
            self.NRO_CAMPANAS_MANUALES, type=Campana.TYPE_MANUAL, estado=Campana.ESTADO_ACTIVA,
            reported_by=self.usuario_admin_supervisor)
        self.campanas_preview = CampanaFactory.create_batch(
            self.NRO_CAMPANAS_PREVIEW, type=Campana.TYPE_PREVIEW, estado=Campana.ESTADO_ACTIVA,
            reported_by=self.usuario_admin_supervisor)

        # self.queues_campanas_dialer_ingresadas = QueuelogFactory.create_batch(
        #     self.NRO_QUEUES_DIALER_INGRESADAS, campana_id=self.campanas_dialer[0].pk,
        #     event=self.evento_llamadas_ingresadas, data5=Campana.TYPE_DIALER)
        # self.queues_campanas_dialer_atendidas = QueuelogFactory.create_batch(
        #     self.NRO_QUEUES_DIALER_ATENDIDAS, campana_id=self.campanas_dialer[1].pk,
        #     event=self.evento_llamadas_atendidas, data5=Campana.TYPE_DIALER)
        # self.queues_campanas_dialer_abandonadas = QueuelogFactory.create_batch(
        #     self.NRO_QUEUES_DIALER_ABANDONADAS, campana_id=self.campanas_dialer[2].pk,
        #     event=self.evento_llamadas_abandonadas, data5=Campana.TYPE_DIALER)
        # self.queues_campanas_dialer_expiradas = QueuelogFactory.create_batch(
        #     self.NRO_QUEUES_DIALER_EXPIRADAS, campana_id=self.campanas_dialer[3].pk,
        #     event=self.evento_llamadas_expiradas, data5=Campana.TYPE_DIALER)

        # self.queues_campanas_entrantes_ingresadas = QueuelogFactory.create_batch(
        #     self.NRO_QUEUES_ENTRANTES_INGRESADAS, campana_id=self.campanas_entrantes[0].pk,
        #     event=self.evento_llamadas_ingresadas, data5=Campana.TYPE_ENTRANTE)
        # self.queues_campanas_entrantes_atendidas = QueuelogFactory.create_batch(
        #     self.NRO_QUEUES_ENTRANTES_ATENDIDAS, campana_id=self.campanas_entrantes[1].pk,
        #     event=self.evento_llamadas_atendidas, data5=Campana.TYPE_ENTRANTE)
        # self.queues_campanas_entrantes_abandonadas = QueuelogFactory.create_batch(
        #     self.NRO_QUEUES_ENTRANTES_ABANDONADAS, campana_id=self.campanas_entrantes[2].pk,
        #     event=self.evento_llamadas_abandonadas, data5=Campana.TYPE_ENTRANTE)
        # self.queues_campanas_entrantes_expiradas = QueuelogFactory.create_batch(
        #     self.NRO_QUEUES_ENTRANTES_EXPIRADAS, campana_id=self.campanas_entrantes[3].pk,
        #     event=self.evento_llamadas_expiradas, data5=Campana.TYPE_ENTRANTE)

        # self.queues_campanas_manuales_ingresadas = QueuelogFactory.create_batch(
        #     self.NRO_QUEUES_MANUALES_INGRESADAS, campana_id=self.campanas_manuales[0].pk,
        #     event=self.evento_llamadas_ingresadas, data4='saliente', data5=Campana.TYPE_MANUAL)
        # self.queues_campanas_manuales_atendidas = QueuelogFactory.create_batch(
        #     self.NRO_QUEUES_MANUALES_ATENDIDAS, campana_id=self.campanas_manuales[1].pk,
        #     event=self.evento_llamadas_atendidas, data4='saliente', data5=Campana.TYPE_MANUAL)
        # self.queues_campanas_manuales_abandonadas = QueuelogFactory.create_batch(
        #     self.NRO_QUEUES_MANUALES_ABANDONADAS, campana_id=self.campanas_manuales[2].pk,
        #     event=self.evento_llamadas_abandonadas, data4='saliente', data5=Campana.TYPE_MANUAL)

        # self.queues_campanas_preview_ingresadas = QueuelogFactory.create_batch(
        #     self.NRO_QUEUES_PREVIEW_INGRESADAS, campana_id=self.campanas_preview[0].pk,
        #     event=self.evento_llamadas_ingresadas, data4='preview', data5=Campana.TYPE_PREVIEW)
        # self.queues_campanas_preview_atendidas = QueuelogFactory.create_batch(
        #     self.NRO_QUEUES_PREVIEW_ATENDIDAS, campana_id=self.campanas_preview[1].pk,
        #     event=self.evento_llamadas_atendidas, data4='preview', data5=Campana.TYPE_PREVIEW)
        # self.queues_campanas_preview_abandonadas = QueuelogFactory.create_batch(
        #     self.NRO_QUEUES_PREVIEW_ABANDONADAS, campana_id=self.campanas_preview[2].pk,
        #     event=self.evento_llamadas_abandonadas, data4='preview', data5=Campana.TYPE_PREVIEW)

    def test_datos_reporte_total_llamadas_csv_contiene_tabla_totales_llamadas_por_tipo(self):
        # el usuario debe primero acceder a la página de los reportes y a partir
        # de allí realizar la descarga haciendo click en una de las opciones existentes
        url_vista_llamadas = reverse('reporte_llamadas')
        url_reporte_total_llamadas = reverse('exportar_llamadas',
                                             kwargs={'tipo_reporte': 'total_llamadas'})
        response_web = self.client.get(url_vista_llamadas)
        post_data = {
            'total_llamadas': response_web.context_data['graficos_estadisticas']['estadisticas']
            ['total_llamadas_json']}
        response_csv = self.client.post(url_reporte_total_llamadas, post_data)
        self.assertContains(response_csv, 'Total llamadas,Cantidad')
        self.assertContains(response_csv, 'Total llamadas procesadas por OmniLeads')
        self.assertContains(response_csv, 'Total de llamadas Salientes Discador')
        self.assertContains(response_csv, 'Total llamadas Entrantes')
        self.assertContains(response_csv, 'Total llamadas Salientes Manuales')
        self.assertContains(response_csv, 'Total llamadas Salientes Preview')

    def test_totales_del_dia_en_context(self):
        url_vista_llamadas = reverse('reporte_llamadas')
        response_web = self.client.get(url_vista_llamadas)
        context_data = response_web.context_data
        totales = context_data['graficos_estadisticas']['estadisticas']['total_llamadas_dict']
        total_ingresada = self.NRO_QUEUES_PREVIEW_INGRESADAS + self.NRO_QUEUES_DIALER_INGRESADAS + \
            self.NRO_QUEUES_MANUALES_INGRESADAS + self.NRO_QUEUES_ENTRANTES_INGRESADAS

        self.assertEqual(totales['total_llamadas_ingresadas'], total_ingresada)

        self.assertEqual(totales['llamadas_ingresadas_dialer'], self.NRO_QUEUES_DIALER_INGRESADAS)
        self.assertEqual(totales['llamadas_gestionadas_dialer'], self.NRO_QUEUES_DIALER_ATENDIDAS)
        self.assertEqual(totales['llamadas_perdidas_dialer'],
                         self.NRO_QUEUES_DIALER_ABANDONADAS + self.NRO_QUEUES_DIALER_EXPIRADAS)

        self.assertEqual(totales['llamadas_ingresadas_entrantes'],
                         self.NRO_QUEUES_ENTRANTES_INGRESADAS)
        self.assertEqual(totales['llamadas_atendidas_entrantes'],
                         self.NRO_QUEUES_ENTRANTES_ATENDIDAS)
        self.assertEqual(totales['llamadas_expiradas_entrantes'],
                         self.NRO_QUEUES_ENTRANTES_EXPIRADAS)
        self.assertEqual(totales['llamadas_abandonadas_entrantes'],
                         self.NRO_QUEUES_ENTRANTES_ABANDONADAS)

        self.assertEqual(totales['llamadas_ingresadas_manuales'],
                         self.NRO_QUEUES_MANUALES_INGRESADAS)
        self.assertEqual(totales['llamadas_atendidas_manuales'],
                         self.NRO_QUEUES_MANUALES_ATENDIDAS)
        self.assertEqual(totales['llamadas_abandonadas_manuales'],
                         self.NRO_QUEUES_MANUALES_ABANDONADAS)

        self.assertEqual(totales['llamadas_ingresadas_preview'], self.NRO_QUEUES_PREVIEW_INGRESADAS)
        self.assertEqual(totales['llamadas_atendidas_preview'], self.NRO_QUEUES_PREVIEW_ATENDIDAS)
        self.assertEqual(totales['llamadas_abandonadas_preview'],
                         self.NRO_QUEUES_PREVIEW_ABANDONADAS)

    def _obtener_total_llamadas(self, fecha_inicio, fecha_fin, campanas):
        service = GraficoService()
        estadisticas = service._calcular_estadisticas(fecha_inicio, fecha_fin,
                                                      self.usuario_admin_supervisor,
                                                      True)
        return estadisticas['total_llamadas_dict']

    def _get_llamadas_list_counts_dia_hoy_todas_las_campanas(self):
        fecha_fin = timezone.now()
        campanas = Campana.objects.all()
        llamadas_list_counts = self._obtener_total_llamadas(
            self.fecha_inicio, fecha_fin, campanas)
        return llamadas_list_counts

    def test_total_llamadas_ingresadas_igual_suma_todos_los_tipos_de_llamadas_existentes(self):
        llamadas_list_counts = self._get_llamadas_list_counts_dia_hoy_todas_las_campanas()
        total_llamadas_ingresadas = self.NRO_QUEUES_DIALER_INGRESADAS + \
            self.NRO_QUEUES_ENTRANTES_INGRESADAS + \
            self.NRO_QUEUES_MANUALES_INGRESADAS + \
            self.NRO_QUEUES_PREVIEW_INGRESADAS
        self.assertEqual(llamadas_list_counts['total_llamadas_ingresadas'],
                         total_llamadas_ingresadas)

    def test_total_llamadas_ingresadas_campanas_dialer_igual_suma_gestionadas_perdidas(self):
        llamadas_list_counts = self._get_llamadas_list_counts_dia_hoy_todas_las_campanas()
        total_llamadas_campanas_dialer = self.NRO_QUEUES_DIALER_ATENDIDAS + \
            self.NRO_QUEUES_DIALER_ABANDONADAS + self.NRO_QUEUES_DIALER_EXPIRADAS
        self.assertEqual(llamadas_list_counts['llamadas_ingresadas_dialer'],
                         total_llamadas_campanas_dialer)
        self.assertEqual(llamadas_list_counts['llamadas_ingresadas_dialer'],
                         self.NRO_QUEUES_DIALER_INGRESADAS)

    def test_total_llamadas_ingresadas_campanas_entrantes_igual_suma_gestionadas_perdidas(self):
        llamadas_list_counts = self._get_llamadas_list_counts_dia_hoy_todas_las_campanas()
        total_llamadas_campanas_entrantes = self.NRO_QUEUES_ENTRANTES_ATENDIDAS + \
            self.NRO_QUEUES_ENTRANTES_ABANDONADAS + self.NRO_QUEUES_ENTRANTES_EXPIRADAS
        self.assertEqual(llamadas_list_counts['llamadas_ingresadas_entrantes'],
                         total_llamadas_campanas_entrantes)
        self.assertEqual(llamadas_list_counts['llamadas_ingresadas_entrantes'],
                         self.NRO_QUEUES_ENTRANTES_INGRESADAS)

    def test_total_llamadas_ingresadas_campanas_manuales_igual_suma_gestionadas_perdidas(self):
        llamadas_list_counts = self._get_llamadas_list_counts_dia_hoy_todas_las_campanas()
        total_llamadas_campanas_manuales = self.NRO_QUEUES_MANUALES_ATENDIDAS + \
            self.NRO_QUEUES_MANUALES_ABANDONADAS
        self.assertEqual(llamadas_list_counts['llamadas_ingresadas_manuales'],
                         total_llamadas_campanas_manuales)
        self.assertEqual(llamadas_list_counts['llamadas_ingresadas_manuales'],
                         self.NRO_QUEUES_MANUALES_INGRESADAS)

    def test_total_llamadas_ingresadas_campanas_preview_igual_suma_gestionadas_perdidas(self):
        llamadas_list_counts = self._get_llamadas_list_counts_dia_hoy_todas_las_campanas()
        total_llamadas_campanas_preview = self.NRO_QUEUES_PREVIEW_ATENDIDAS + \
            self.NRO_QUEUES_PREVIEW_ABANDONADAS
        self.assertEqual(llamadas_list_counts['llamadas_ingresadas_preview'],
                         total_llamadas_campanas_preview)
        self.assertEqual(llamadas_list_counts['llamadas_ingresadas_preview'],
                         self.NRO_QUEUES_PREVIEW_INGRESADAS)


class AccesoReportesTests(BaseReportesTests):

    def test_usuario_logueado_accede_a_pagina_ppal_reportes_llamadas(self):
        url = reverse('reporte_llamadas')
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, 'grabaciones/total_llamadas.html')

    def test_usuario_no_logueado_no_accede_a_pagina_ppal_reportes_llamadas(self):
        url = reverse('reporte_llamadas')
        self.client.logout()
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, u'registration/login.html')

    def test_usuario_logueado_accede_a_realizar_reporte_total_llamadas_csv(self):
        url = reverse('exportar_llamadas', kwargs={'tipo_reporte': 'total_llamadas'})
        response = self.client.post(url, follow=True)
        self.assertTrue(response.serialize().find('total_llamadas.csv') > -1)

    def test_usuario_no_logueado_no_accede_a_realizar_reporte_total_llamadas_csv(self):
        url = reverse('exportar_llamadas', kwargs={'tipo_reporte': 'total_llamadas'})
        self.client.logout()
        response = self.client.post(url, follow=True)
        self.assertFalse(response.serialize().find('total_llamadas.csv') > -1)

    def test_usuario_logueado_accede_a_realizar_reporte_general_llamadas_csv(self):
        url = reverse('exportar_zip_reportes')
        response = self.client.post(url, follow=True)
        self.assertTrue(response.serialize().find('total_llamadas.csv') > -1)

    def test_usuario_no_logueado_no_accede_a_realizar_reporte_general_llamadas_csv(self):
        url = reverse('exportar_zip_reportes')
        self.client.logout()
        response = self.client.post(url, follow=True)
        self.assertFalse(response.serialize().find('total_llamadas.csv') > -1)


# Valores por defecto para insertar en la tabla queue_log
CALLID = '2312312.233'
EVENT = 'ENTERQUEUE'
TELEFONO = '1234567890'
CONTACTO_ID = 1
TIEMPO_RING = 5
DURACION_LLAMADA = 60


class TriggerQueuelogTest(OMLBaseTest):

    def _aplicar_sql_query(self, queuename, time=timezone.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                           callid=CALLID, agent=1, event=EVENT, data1=TELEFONO,
                           data2=CONTACTO_ID, data3='', data4=TIEMPO_RING, data5=DURACION_LLAMADA):
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
