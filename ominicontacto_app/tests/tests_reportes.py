# -*- coding: utf-8 -*-

"""
Tests del los reportes que realiza el sistema
"""

from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.tests.factories import CampanaFactory, QueuelogFactory
from ominicontacto_app.models import Campana

NRO_CAMPANAS_DIALER = 10
NRO_CAMPANAS_ENTRANTES = 7
NRO_CAMPANAS_MANUALES = 5

NRO_QUEUES_DIALER = 100
NRO_QUEUES_ENTRANTES = 80
NRO_QUEUES_MANUALES = 80


class ReportesTests(OMLBaseTest):
    def setUp(self):
        self.campanas_dialer = CampanaFactory.create_batch(
            NRO_CAMPANAS_DIALER, type=Campana.TYPE_DIALER)
        self.campana_entrantes = CampanaFactory.create_batch(
            NRO_CAMPANAS_ENTRANTES, type=Campana.TYPE_ENTRANTE)
        self.campana_entrantes = CampanaFactory.create_batch(
            NRO_CAMPANAS_MANUALES, type=Campana.TYPE_MANUAL)

        self.queues_campanas_dialer = QueuelogFactory.create_batch(
            NRO_QUEUES_DIALER, campana_id=self.campanas_dialer.objects.first().pk)

        self.queues_campanas_entrantes = QueuelogFactory.create_batch(
            NRO_QUEUES_ENTRANTES, campana_id=self.campanas_entrantes.objects.first().pk)

        self.queues_campanas_manuales = QueuelogFactory.create_batch(
            NRO_QUEUES_MANUALES, campana_id=self.campanas_manuales.objects.first().pk)

    def test_es_correcto_el_calculo_de_el_reporte_de_llamadas(self):
        pass
