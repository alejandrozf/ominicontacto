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

    def setUp(self):
        base_datos = self.crear_base_datos_contacto(cant_contactos=100)
        self.campana = self.crear_campana_dialer(bd_contactos=base_datos)
        print self.campana.bd_contacto
        user_agente = self.crear_user_agente()
        self.agente = self.crear_agente_profile(user_agente)

    def test_devuelve_correctamente_no_contactacion(self):
        """
        este test testea todos los resultados las cantidad de los no
        contactdos chequeando que devuelva correctamente
        """

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

        for log in campana_log_wombat:
            estado = log['estado']
            if estado == "RS_LOST" and log['calificacion'] == "":
                id_estado = EstadisticasContactacion.AGENTE_NO_DISPONIBLE
                self.assertEquals(no_contactados_lista[id_estado], log['estado__count'])
            elif estado == "RS_BUSY":
                id_estado = EstadisticasContactacion.OCUPADO
                self.assertEquals(no_contactados_lista[id_estado],
                                  log['estado__count'])
            elif estado == "RS_NOANSWER":
                id_estado = EstadisticasContactacion.NO_CONTESTA
                self.assertEquals(no_contactados_lista[id_estado],
                                  log['estado__count'])
            elif estado == "RS_NUMBER":
                id_estado = EstadisticasContactacion.NUMERO_ERRONEO
                self.assertEquals(no_contactados_lista[id_estado],
                                  log['estado__count'])
            elif estado == "RS_ERROR":
                id_estado = EstadisticasContactacion.ERROR_DE_SISTEMA
                self.assertEquals(no_contactados_lista[id_estado],
                                  log['estado__count'])
            elif estado == "RS_REJECTED":
                id_estado = EstadisticasContactacion.CONGESTION
                self.assertEquals(no_contactados_lista[id_estado],
                                  log['estado__count'])
            elif estado == "TERMINATED" and log['calificacion'] == "CONTESTADOR":
                id_estado = EstadisticasContactacion.CONTESTADOR
                self.assertEquals(no_contactados_lista[id_estado],
                                  log['estado__count'])
            elif estado == "TERMINATED" and log['calificacion'] == "":
                id_estado = EstadisticasContactacion.AGENTE_NO_CALIFICO
                self.assertEquals(no_contactados_lista[id_estado],
                                  log['estado__count'])
