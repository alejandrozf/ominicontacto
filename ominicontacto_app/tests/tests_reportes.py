# -*- coding: utf-8 -*-

"""
Tests del los reportes que realiza el sistema
"""

from django.core.urlresolvers import reverse
from django.db import connection
from django.utils import timezone

from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.tests.factories import CampanaFactory, QueuelogFactory, UserFactory
from ominicontacto_app.models import Campana, Queuelog
from ominicontacto_app.services.reporte_grafico import GraficoService


class ReportesTests(OMLBaseTest):
    PWD = u'admin123'

    def setUp(self):

        self.usuario_admin_supervisor = UserFactory(is_staff=True, is_supervisor=True)
        self.usuario_admin_supervisor.set_password(self.PWD)
        self.usuario_admin_supervisor.save()

        self.evento_llamadas_ingresadas = 'ENTERQUEUE'
        self.evento_llamadas_atendidas = 'CONNECT'
        self.evento_llamadas_abandonadas = 'ABANDON'
        self.evento_llamadas_expiradas = 'EXITWITHTIMEOUT'

        self.NRO_CAMPANAS_DIALER = 10
        self.NRO_CAMPANAS_ENTRANTES = 7
        self.NRO_CAMPANAS_MANUALES = 5

        self.NRO_QUEUES_DIALER_INGRESADAS = 100
        self.NRO_QUEUES_DIALER_ATENDIDAS = 40
        self.NRO_QUEUES_DIALER_ABANDONADAS = 30
        self.NRO_QUEUES_DIALER_EXPIRADAS = 30

        self.NRO_QUEUES_ENTRANTES_INGRESADAS = 80
        self.NRO_QUEUES_ENTRANTES_ATENDIDAS = 10
        self.NRO_QUEUES_ENTRANTES_ABANDONADAS = 50
        self.NRO_QUEUES_ENTRANTES_EXPIRADAS = 20

        self.NRO_QUEUES_MANUALES_INGRESADAS = 80
        self.NRO_QUEUES_MANUALES_ATENDIDAS = 55
        self.NRO_QUEUES_MANUALES_ABANDONADAS = 25

        self.campanas_dialer = CampanaFactory.create_batch(
            self.NRO_CAMPANAS_DIALER, type=Campana.TYPE_DIALER)
        self.campanas_entrantes = CampanaFactory.create_batch(
            self.NRO_CAMPANAS_ENTRANTES, type=Campana.TYPE_ENTRANTE)
        self.campanas_manuales = CampanaFactory.create_batch(
            self.NRO_CAMPANAS_MANUALES, type=Campana.TYPE_MANUAL)

        self.queues_campanas_dialer_ingresadas = QueuelogFactory.create_batch(
            self.NRO_QUEUES_DIALER_INGRESADAS, campana_id=self.campanas_dialer[0].pk,
            event=self.evento_llamadas_ingresadas)
        self.queues_campanas_dialer_atendidas = QueuelogFactory.create_batch(
            self.NRO_QUEUES_DIALER_ATENDIDAS, campana_id=self.campanas_dialer[1].pk,
            event=self.evento_llamadas_atendidas)
        self.queues_campanas_dialer_abandonadas = QueuelogFactory.create_batch(
            self.NRO_QUEUES_DIALER_ABANDONADAS, campana_id=self.campanas_dialer[2].pk,
            event=self.evento_llamadas_abandonadas)
        self.queues_campanas_dialer_expiradas = QueuelogFactory.create_batch(
            self.NRO_QUEUES_DIALER_EXPIRADAS, campana_id=self.campanas_dialer[3].pk,
            event=self.evento_llamadas_expiradas)

        self.queues_campanas_entrantes_ingresadas = QueuelogFactory.create_batch(
            self.NRO_QUEUES_ENTRANTES_INGRESADAS, campana_id=self.campanas_entrantes[0].pk,
            event=self.evento_llamadas_ingresadas)
        self.queues_campanas_entrantes_atendidas = QueuelogFactory.create_batch(
            self.NRO_QUEUES_ENTRANTES_ATENDIDAS, campana_id=self.campanas_entrantes[1].pk,
            event=self.evento_llamadas_atendidas)
        self.queues_campanas_entrantes_abandonadas = QueuelogFactory.create_batch(
            self.NRO_QUEUES_ENTRANTES_ABANDONADAS, campana_id=self.campanas_entrantes[2].pk,
            event=self.evento_llamadas_abandonadas)
        self.queues_campanas_entrantes_expiradas = QueuelogFactory.create_batch(
            self.NRO_QUEUES_ENTRANTES_EXPIRADAS, campana_id=self.campanas_entrantes[3].pk,
            event=self.evento_llamadas_expiradas)

        self.queues_campanas_manuales_ingresadas = QueuelogFactory.create_batch(
            self.NRO_QUEUES_MANUALES_INGRESADAS, campana_id=self.campanas_manuales[0].pk,
            event=self.evento_llamadas_ingresadas, data4='saliente')
        self.queues_campanas_manuales_atendidas = QueuelogFactory.create_batch(
            self.NRO_QUEUES_MANUALES_ATENDIDAS, campana_id=self.campanas_manuales[1].pk,
            event=self.evento_llamadas_atendidas, data4='saliente')
        self.queues_campanas_manuales_abandonadas = QueuelogFactory.create_batch(
            self.NRO_QUEUES_MANUALES_ABANDONADAS, campana_id=self.campanas_manuales[2].pk,
            event=self.evento_llamadas_abandonadas, data4='saliente')

        self.client.login(username=self.usuario_admin_supervisor.username,
                          password=self.PWD)

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

    def _get_llamadas_list_counts_dia_hoy_todas_las_campanas(self):
        fecha_inicio = fecha_fin = timezone.now()
        campanas = Campana.objects.all()
        llamadas_list_counts = GraficoService().obtener_total_llamadas(
            fecha_inicio, fecha_fin, campanas).values()
        return llamadas_list_counts

    def test_total_llamadas_ingresadas_igual_suma_todos_los_tipos_de_llamadas_existentes(self):
        llamadas_list_counts = self._get_llamadas_list_counts_dia_hoy_todas_las_campanas()
        total_llamadas_ingresadas = self.NRO_QUEUES_DIALER_INGRESADAS + \
            self.NRO_QUEUES_ENTRANTES_INGRESADAS + \
            self.NRO_QUEUES_MANUALES_INGRESADAS
        self.assertEqual(llamadas_list_counts[0], total_llamadas_ingresadas)

    def test_total_llamadas_ingresadas_campanas_dialer_igual_suma_gestionadas_perdidas(self):
        llamadas_list_counts = self._get_llamadas_list_counts_dia_hoy_todas_las_campanas()
        total_llamadas_campanas_dialer = self.NRO_QUEUES_DIALER_ATENDIDAS + \
            self.NRO_QUEUES_DIALER_ABANDONADAS + self.NRO_QUEUES_DIALER_EXPIRADAS
        self.assertEqual(llamadas_list_counts[1], total_llamadas_campanas_dialer)
        self.assertEqual(llamadas_list_counts[1], self.NRO_QUEUES_DIALER_INGRESADAS)

    def test_total_llamadas_ingresadas_campanas_entrantes_igual_suma_gestionadas_perdidas(self):
        llamadas_list_counts = self._get_llamadas_list_counts_dia_hoy_todas_las_campanas()
        total_llamadas_campanas_entrantes = self.NRO_QUEUES_ENTRANTES_ATENDIDAS + \
            self.NRO_QUEUES_ENTRANTES_ABANDONADAS + self.NRO_QUEUES_ENTRANTES_EXPIRADAS
        self.assertEqual(llamadas_list_counts[4], total_llamadas_campanas_entrantes)
        self.assertEqual(llamadas_list_counts[4], self.NRO_QUEUES_ENTRANTES_INGRESADAS)

    def test_total_llamadas_ingresadas_campanas_manuales_igual_suma_gestionadas_perdidas(self):
        llamadas_list_counts = self._get_llamadas_list_counts_dia_hoy_todas_las_campanas()
        total_llamadas_campanas_manuales = self.NRO_QUEUES_MANUALES_ATENDIDAS + \
            self.NRO_QUEUES_MANUALES_ABANDONADAS
        self.assertEqual(llamadas_list_counts[8], total_llamadas_campanas_manuales)
        self.assertEqual(llamadas_list_counts[8], self.NRO_QUEUES_MANUALES_INGRESADAS)

    def _aplicar_sql_query(self, tipo_campana, queuename):
        fields = "(time, callid, queuename, agent, event, data1, data2, data3, data4, data5)"
        values = ('2017-12-22 03:45:00.0000', '2312312.233', queuename, 'agente_test', 'CONNECT',
                  'data1', 'data2', 'data3', tipo_campana, '')
        sql_query = "insert into queue_log {0} values {1};".format(fields, str(values))
        with connection.cursor() as c:
            c.execute(sql_query)

    def test_adicion_info_tipo_campana_entrantes(self):
        queuename = "1_cp1"
        self._aplicar_sql_query('IN', queuename)
        queuelog = Queuelog.objects.get(queuename=queuename)
        self.assertEqual(queuelog.data5, str(Campana.TYPE_ENTRANTE))

    def test_adicion_info_tipo_campana_dialer(self):
        queuename = "1_cp1"
        self._aplicar_sql_query('DIALER', queuename)
        queuelog = Queuelog.objects.get(queuename=queuename)
        self.assertEqual(queuelog.data5, str(Campana.TYPE_DIALER))

    def test_adicion_info_tipo_campana_manual(self):
        queuename = "1_cp1"
        self._aplicar_sql_query('saliente', queuename)
        queuelog = Queuelog.objects.get(queuename=queuename)
        self.assertEqual(queuelog.data5, str(Campana.TYPE_MANUAL))

    def test_adicion_info_tipo_campana_pre(self):
        queuename = "1_cp1"
        self._aplicar_sql_query('preview', queuename)
        queuelog = Queuelog.objects.get(queuename=queuename)
        self.assertEqual(queuelog.data5, str(Campana.TYPE_PREVIEW))
