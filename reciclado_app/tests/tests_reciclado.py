# -*- coding: utf-8 -*-

"""
Tests del metodo 'ominicontacto_app.models'
"""

from __future__ import unicode_literals

import random

from django.db.models import Count
from ominicontacto_app.tests.utiles import OMLBaseTest
from reciclado_app.resultado_contactacion import EstadisticasContactacion


class RecicladoTest(OMLBaseTest):
    MAP_LOG_WOMBAT = {
        "RS_LOST": 1,
        "RS_BUSY": 2,
        "RS_NOANSWER": 3,
        "RS_NUMBER": 4,
        "RS_ERROR": 5,
        "RS_REJECTED": 6,
        "CONTESTADOR": 7,
    }

    def setUp(self):
        base_datos = self.crear_base_datos_contacto(cant_contactos=100)
        self.campana = self.crear_campana_dialer(bd_contactos=base_datos)
        print self.campana.bd_contacto
        user_agente = self.crear_user_agente()
        self.agente = self.crear_agente_profile(user_agente)

    def test_devuelve_correctamente_no_contactacion(self):

        # estados no contactados:
        estados = ["RS_LOST", "RS_BUSY", "RS_NOANSWER", "RS_NUMBER",
                   "RS_ERROR", "RS_REJECTED", "SARASA", "TERMINATED"]

        contactos = self.campana.bd_contacto.contactos.all()

        for _ in range(0, 100):
            contacto = random.choice(contactos)
            estado = random.choice(estados)
            calificacion = ''
            if estado is "TERMINATED":
                calificacion = random.choice(["CONTESTADOR", ""])
            self.crear_wombat_log(self.campana, self.agente, contacto, estado,
                                  calificacion)

        estadisticas = EstadisticasContactacion()
        no_contactados = estadisticas.obtener_cantidad_no_contactados(self.campana)
        no_contactados_lista = {}
        for key, value in no_contactados.items():
            no_contactados_lista.update({key: value.cantidad})

        campana_log_wombat = self.campana.logswombat.filter(estado__in=estados)
        campana_log_wombat = campana_log_wombat.values(
            'estado', 'calificacion').annotate(Count('estado'))
        print campana_log_wombat
        print no_contactados
        print no_contactados_lista
        # for no_contacto in no_contactados_choice:
        #
        #     self.assertEquals()

