# -*- coding: utf-8 -*-

"""
Tests del los reportes que realiza el sistema
"""

from django.utils import timezone

from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.tests.factories import CampanaFactory, QueuelogFactory
from ominicontacto_app.models import Campana
from ominicontacto_app.services.reporte_grafico import GraficoService


class ReportesTests(OMLBaseTest):
    def setUp(self):
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
            event=self.evento_llamadas_ingresadas)
        self.queues_campanas_manuales_atendidas = QueuelogFactory.create_batch(
            self.NRO_QUEUES_MANUALES_ATENDIDAS, campana_id=self.campanas_manuales[1].pk,
            event=self.evento_llamadas_atendidas)
        self.queues_campanas_manuales_abandonadas = QueuelogFactory.create_batch(
            self.NRO_QUEUES_MANUALES_ABANDONADAS, campana_id=self.campanas_manuales[2].pk,
            event=self.evento_llamadas_abandonadas)

    def _get_llamadas_list_counts_dia_hoy_todas_las_campanas(self):
        fecha_inicio = fecha_fin = timezone.now()
        campanas = Campana.objects.all()
        llamadas_list_counts = GraficoService().obtener_total_llamadas(
            fecha_inicio, fecha_fin, campanas)
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
