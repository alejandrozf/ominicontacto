# -*- coding: utf-8 -*-

"""
Tests del metodo 'ominicontacto_app.models'
"""

from __future__ import unicode_literals

import random

from django.db.models import Count
from ominicontacto_app.tests.utiles import OMLBaseTest
from reciclado_app.resultado_contactacion import (
    EstadisticasContactacion, RecicladorContactosCampanaDIALER
)


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

    def test_devuelve_correctamente_calificados(self):
        """
        este test testea todos los resultados las cantidad de los
        contactdos chequeando que devuelva correctamente
        """

        contactos = self.campana.bd_contacto.contactos.all()

        for _ in range(0, 100):
            contacto = random.choice(contactos)
            opciones_calificacion = self.campana.opciones_calificacion.all()
            opcion_calificacion = random.choice(opciones_calificacion)
            self.crear_calificacion_cliente(self.agente, contacto, opcion_calificacion)

        estadisticas = EstadisticasContactacion()
        calificados = estadisticas.obtener_cantidad_calificacion(self.campana)

        calificaciones_query = self.campana.obtener_calificaciones_cliente().values(
            'opcion_calificacion__nombre', 'opcion_calificacion__id').annotate(
            Count('opcion_calificacion')).filter(
            opcion_calificacion__count__gt=0)

        contactados_dict = {}
        for contactado in calificados:
            contactados_dict.update({contactado.id: contactado.cantidad})
        for contactacion in calificaciones_query:
            self.assertEquals(contactacion['opcion_calificacion__count'],
                              contactados_dict[contactacion['opcion_calificacion__id']])

    def test_obtiene_contactos_reciclados(self):
        # estados no contactados:
        estados = [2, 3, 4, 5, 6]

        contactos = self.campana.bd_contacto.contactos.all()
        opciones_calificacion = self.campana.opciones_calificacion.all()

        for _ in range(0, 100):
            contacto = random.choice(contactos)
            es_contactado = random.choice([True, False])

            if es_contactado:
                opcion_calificacion = random.choice(opciones_calificacion)
                self.crear_calificacion_cliente(self.agente, contacto, opcion_calificacion)
            else:
                estado = random.choice(estados)
                calificacion = ''
                if estado is "TERMINATED":
                    calificacion = random.choice(["CONTESTADOR", ""])
                    self.crear_wombat_log(
                        self.campana, self.agente, contacto, estado, calificacion)

        estado_elegido = random.choice(estados)
        calificacion = random.choice(opciones_calificacion)
        estado_list = []
        estado_list.append(estado_elegido)
        calificacion_list = []
        calificacion_list.append(calificacion)

        # vamos a chequear que sea la misma cantidad de contactos reciclados
        # para los calificados
        calificaciones_query = self.campana.obtener_calificaciones_cliente().filter(
            opcion_calificacion__in=calificacion_list).distinct()
        reciclador = RecicladorContactosCampanaDIALER()
        contactos_reciclados = reciclador._obtener_contactos_calificados(
            self.campana, calificacion_list)
        self.assertEquals(calificaciones_query.count(), len(contactos_reciclados))

        # ahora vamos a chequear para los no contactados
        no_contactados_reciclados = reciclador._obtener_contactos_no_contactados(
            self.campana, estado_list)
        estados = [EstadisticasContactacion.MAP_LOG_WOMBAT[estado]
                   for estado_contactacion in estado_list]
        no_contactados = self.campana.logswombat.filter(estado__in=estados)

        self.assertEquals(len(no_contactados_reciclados), no_contactados.count())

        # ahora chequeamos para contestador
        contestadores = self.campana.logswombat.filter(
            estado="TERMINATED", calificacion='CONTESTADOR')
        no_contactados_reciclados = reciclador._obtener_contactos_no_contactados(
            self.campana, [7])

        self.assertEquals(len(no_contactados_reciclados), contestadores.count())

        # ahora chequeamos para agente no califico
        no_califico = self.campana.logswombat.filter(
            estado="TERMINATED", calificacion='')
        no_contactados_reciclados = reciclador._obtener_contactos_no_contactados(
            self.campana, [8])

        self.assertEquals(len(no_contactados_reciclados), no_califico.count())

        # ahora chequeamos para agente no disponible
        no_disponible = self.campana.logswombat.filter(
            estado="RS_LOST", calificacion='')
        no_contactados_reciclados = reciclador._obtener_contactos_no_contactados(
            self.campana, [1])

        self.assertEquals(len(no_contactados_reciclados), no_disponible.count())
