# -*- coding: utf-8 -*-

from random import randint

from django.core.management.base import BaseCommand, CommandError
from ominicontacto_app.tests.factories import CampanaFactory, QueuelogFactory
from ominicontacto_app.models import Campana


class Command(BaseCommand):
    """
    Crea tantas llamadas como se especifique en el parametro, son asociadas aleatoriamente a
    distintos tipos de campañas
    """

    EVENTOS = ['CONNECT', 'ABANDON', 'EXITWITHTIMEOUT']

    help = 'Crea el número de llamadas de acuerdo al parámetro recibido'

    def add_arguments(self, parser):
        parser.add_argument('nro_llamadas', nargs=1, type=int)

    def crear_campanas(self):
        id_campana_entrante = CampanaFactory.create(type=Campana.TYPE_ENTRANTE).pk
        id_campana_dialer = CampanaFactory.create(type=Campana.TYPE_DIALER).pk
        id_campana_manual = CampanaFactory.create(type=Campana.TYPE_MANUAL).pk

        return [id_campana_dialer, id_campana_entrante, id_campana_manual]

    def llamada_aleatoria(self, campanas_ids):
        """
        Crea registros Queuelog aleatorios para simular las distintas situaciones por la que puede
        """
        evento = randint(0, 2)
        campana = randint(0, 2)

        callid = QueuelogFactory.create(event='ENTERQUEUE').callid
        campana_id = campanas_ids[campana]
        if campana == Campana.TYPE_MANUAL:
            data4 = 'saliente'
        else:
            data4 = ''
        print campana_id
        QueuelogFactory.create(
            event=self.EVENTOS[evento], callid=callid, campana_id=campana_id, data4=data4)

    def handle(self, *args, **options):
        nro_llamadas = options['nro_llamadas'][0]
        campanas_ids = self.crear_campanas()
        for i in range(nro_llamadas):
            try:
                self.llamada_aleatoria(campanas_ids)
            except Exception as e:
                raise CommandError('Fallo del comando: {0}'.format(e.message))
        self.stdout.write(self.style.SUCCESS('Creada(s) {0} llamada(s)'.format(nro_llamadas)))
