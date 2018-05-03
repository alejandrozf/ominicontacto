# -*- coding: utf-8 -*-

from random import randint, choice

from django.core.management.base import BaseCommand, CommandError
from ominicontacto_app.tests.factories import (CampanaFactory, ContactoFactory, UserFactory,
                                               AgenteProfileFactory, )
from ominicontacto_app.models import Campana, User
from reportes_app.tests.utiles import GeneradorDeLlamadaLogs


class Command(BaseCommand):
    # TODO: actualizar este command con la nueva estructura del modelo Queuelog
    """
    Crea tantas llamadas como se especifique en el parametro, son asociadas aleatoriamente a
    distintos tipos de campañas
    """

    EVENTOS_NO_CONNECT = [
        'NOANSWER',
        'CANCEL',
        'BUSY',
        'CHANUNAVAIL',
        'OTHER',
        'FAIL',
        'AMD',
        'BLACKLIST',
    ]

    EVENTOS_NO_DIALOG = ['EXITWITHTIMEOUT', 'ABANDON']

    EVENTOS_COMPLETA = ['COMPLETECALLER', 'COMPLETEAGENT']

    EVENTOS_AGENTE = [
        'ADDMEMBER',
        'REMOVEMEMBER',
        'PAUSEALL',
        'UNPAUSEALL',
    ]

    help = 'Crea el número de llamadas de acuerdo al parámetro recibido'

    def add_arguments(self, parser):
        parser.add_argument('nro_llamadas', nargs=1, type=int)

    def crear_agentes(self):
        self.agentes = []
        for i in range(1, 5):
            try:
                usr = User.objects.get(username='agente_simulador_%i' % i)
                agente = usr.agente_profile
            except User.DoesNotExist:
                usr = UserFactory(username='agente_simulador_%i' % i, is_agente=True)
                agente = AgenteProfileFactory(user=usr)
            self.agentes.append(agente)

    def crear_campanas(self):
        estado = Campana.ESTADO_ACTIVA
        entrante = CampanaFactory.create(type=Campana.TYPE_ENTRANTE, estado=estado)
        for i in range(5):
            ContactoFactory(bd_contacto=entrante.bd_contacto)
        dialer = CampanaFactory.create(type=Campana.TYPE_DIALER, estado=estado)
        for i in range(5):
            ContactoFactory(bd_contacto=dialer.bd_contacto)
        manual = CampanaFactory.create(type=Campana.TYPE_MANUAL, estado=estado)
        for i in range(5):
            ContactoFactory(bd_contacto=manual.bd_contacto)
        preview = CampanaFactory.create(type=Campana.TYPE_PREVIEW, estado=estado)
        for i in range(5):
            ContactoFactory(bd_contacto=preview.bd_contacto)

        self.campanas = {Campana.TYPE_ENTRANTE: entrante,
                         Campana.TYPE_DIALER: dialer,
                         Campana.TYPE_MANUAL: manual,
                         Campana.TYPE_PREVIEW: preview}

    def obtener_contacto_al_azar(self, campana, permitir_ninguno=False):
        contactos = list(campana.bd_contacto.contactos.all())
        if permitir_ninguno:
            contactos = contactos + [None, ]
        return choice(contactos)

    def generar_entrante(self, generador, campana):
        finalizacion = choice(self.EVENTOS_NO_DIALOG)
        numero = randint(40000000, 351000000)
        agente = choice(self.agentes)
        contacto = None
        bridge_wait_time = randint(1, 20)
        duracion_llamada = -1
        archivo_grabacion = ''
        completa = randint(0, 1) == 1
        if completa:
            finalizacion = choice(self.EVENTOS_COMPLETA)
            duracion_llamada = randint(5, 120)
            archivo_grabacion = 'archivo_simulado_' + str(randint(1000, 10000))

        generador.generar_log(campana, False, finalizacion, numero, agente, contacto,
                              bridge_wait_time, duracion_llamada, archivo_grabacion)

    def generar_dialer(self, generador, campana):
        numero = randint(40000000, 351000000)
        agente = choice(self.agentes)
        contacto = self.obtener_contacto_al_azar(campana, permitir_ninguno=False)
        bridge_wait_time = randint(1, 20)
        duracion_llamada = -1
        archivo_grabacion = ''
        completitud = randint(0, 2)
        if completitud == 0:  # Incompleta sin Enterqueue
            finalizacion = choice(self.EVENTOS_NO_CONNECT)
        elif completitud == 1:  # Incompleta con Enterqueue
            finalizacion = choice(self.EVENTOS_NO_DIALOG)
            duracion_llamada = randint(5, 120)
        else:  # Completa
            finalizacion = choice(self.EVENTOS_COMPLETA)
            duracion_llamada = randint(5, 120)
            archivo_grabacion = 'archivo_simulado_' + str(randint(1000, 10000))

        generador.generar_log(campana, False, finalizacion, numero, agente, contacto,
                              bridge_wait_time, duracion_llamada, archivo_grabacion)

    def generar_manual(self, generador, campana):
        finalizacion = choice(self.EVENTOS_NO_CONNECT)
        numero = randint(40000000, 351000000)
        agente = choice(self.agentes)
        contacto = self.obtener_contacto_al_azar(campana, permitir_ninguno=True)
        bridge_wait_time = randint(1, 20)
        duracion_llamada = -1
        archivo_grabacion = ''
        completa = randint(0, 1) == 1
        if completa:
            finalizacion = choice(self.EVENTOS_COMPLETA)
            duracion_llamada = randint(5, 120)
            archivo_grabacion = 'archivo_simulado_' + str(randint(1000, 10000))

        generador.generar_log(campana, True, finalizacion, numero, agente, contacto,
                              bridge_wait_time, duracion_llamada, archivo_grabacion)

    def generar_preview(self, generador, campana):
        finalizacion = choice(self.EVENTOS_NO_CONNECT)
        numero = randint(40000000, 351000000)
        agente = choice(self.agentes)
        contacto = self.obtener_contacto_al_azar(campana, permitir_ninguno=False)
        bridge_wait_time = randint(1, 20)
        duracion_llamada = -1
        archivo_grabacion = ''
        completa = randint(0, 1) == 0
        if completa:
            finalizacion = choice(self.EVENTOS_COMPLETA)
            duracion_llamada = randint(5, 120)
            archivo_grabacion = 'archivo_simulado_' + str(randint(1000, 10000))

        generador.generar_log(campana, False, finalizacion, numero, agente, contacto,
                              bridge_wait_time, duracion_llamada, archivo_grabacion)

    def llamada_aleatoria(self, generador):
        """
        Crea registros Queuelog aleatorios para simular las distintas situaciones por las que puede
        transcurrir una llamada
        """
        es_manual = randint(0, 3) < 1  # 1/4 chances que sea manual
        campana = self.campanas[randint(0, 3) + 1]
        if es_manual:
            self.generar_manual(generador, campana)
        elif campana.type == Campana.TYPE_ENTRANTE:
            self.generar_entrante(generador, campana)
        elif campana.type == Campana.TYPE_DIALER:
            self.generar_dialer(generador, campana)
        elif campana.type == Campana.TYPE_MANUAL:
            self.generar_manual(generador, campana)
        elif campana.type == Campana.TYPE_PREVIEW:
            self.generar_preview(generador, campana)

    def generar_llamadas(self, nro_llamadas):
        self.crear_agentes()
        self.crear_campanas()
        generador = GeneradorDeLlamadaLogs()
        for i in range(nro_llamadas):
            try:
                self.llamada_aleatoria(generador)
            except Exception as e:
                raise CommandError('Fallo del comando: {0}'.format(e.message))

    def handle(self, *args, **options):
        nro_llamadas = options['nro_llamadas'][0]
        self.generar_llamadas(nro_llamadas)
        self.stdout.write(self.style.SUCCESS('Creada(s) {0} llamada(s)'.format(nro_llamadas)))
