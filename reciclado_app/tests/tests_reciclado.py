# -*- coding: utf-8 -*-

"""
Tests del metodo 'ominicontacto_app.models'
"""

from __future__ import unicode_literals

import random

from mock import patch

from django.db.models import Count
from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.models import CalificacionCliente
from ominicontacto_app.services.audio_conversor import ConversorDeAudioService
from reciclado_app.resultado_contactacion import (
    EstadisticasContactacion, RecicladorContactosCampanaDIALER
)
from reportes_app.models import LlamadaLog
from reportes_app.tests.utiles import GeneradorDeLlamadaLogs


class RecicladoTest(OMLBaseTest):

    @patch.object(ConversorDeAudioService, '_convertir_audio')
    def setUp(self, _convertir_audio):
        base_datos = self.crear_base_datos_contacto(cant_contactos=100)
        self.campana = self.crear_campana_dialer(bd_contactos=base_datos)
        user_agente = self.crear_user_agente()
        self.agente = self.crear_agente_profile(user_agente)

    def test_devuelve_correctamente_no_contactacion(self):
        """
        este test testea todos los resultados las cantidad de los no
        contactdos chequeando que devuelva correctamente
        """

        # estados no contactados:
        estados = LlamadaLog.EVENTOS_NO_CONEXION

        contactos = self.campana.bd_contacto.contactos.all()

        generador = GeneradorDeLlamadaLogs()
        cant_llamados = 100
        for _ in range(0, cant_llamados):
            contacto = random.choice(contactos)
            estado = random.choice(estados)
            generador.generar_log(self.campana, False, estado, contacto.telefono, None, contacto)

        cantidades = {}
        for estado in estados:
            cantidades[EstadisticasContactacion.MAP_ESTADO_ID[estado]] = 0

        no_llamados = cant_llamados
        for contacto in contactos:
            logs = LlamadaLog.objects.filter(contacto_id=contacto.id).order_by('-id')
            if logs:
                log = logs[0]
                self.assertIn(log.event, estados)
                cantidades[EstadisticasContactacion.MAP_ESTADO_ID[log.event]] += 1
                no_llamados -= 1

        estadisticas = EstadisticasContactacion()
        no_contactados = estadisticas.obtener_cantidad_no_contactados(self.campana)
        for key, value in no_contactados.items():
            if key == EstadisticasContactacion.NO_LLAMADO:
                self.assertEqual(no_llamados, value.cantidad)
            else:
                self.assertEqual(cantidades[key], value.cantidad)

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

        calificaciones_query = self.campana.obtener_calificaciones().values(
            'opcion_calificacion__nombre', 'opcion_calificacion__id').annotate(
            Count('opcion_calificacion')).filter(
            opcion_calificacion__count__gt=0)

        contactados_dict = {}
        for contactado in calificados:
            contactados_dict.update({contactado.id: contactado.cantidad})
        for contactacion in calificaciones_query:
            self.assertEquals(contactacion['opcion_calificacion__count'],
                              contactados_dict[contactacion['opcion_calificacion__id']])

    def _generar_llamadas_y_calificaciones(self, estados):
        contactos = self.campana.bd_contacto.contactos.all()
        opciones_calificacion = self.campana.opciones_calificacion.all()

        generador = GeneradorDeLlamadaLogs()
        for _ in range(0, 100):
            contacto = random.choice(contactos)
            contactacion = random.choice(['contacta_califica', 'contacta_no_califica',
                                          'no_contacta', 'no_llama'])

            if contactacion == 'contacta_califica':
                generador.generar_log(self.campana, False, 'COMPLETECALLER', contacto.telefono,
                                      self.agente, contacto, 1, 1)
                opcion_calificacion = random.choice(opciones_calificacion)
                self.crear_calificacion_cliente(self.agente, contacto, opcion_calificacion)
            if contactacion == 'contacta_no_califica':
                generador.generar_log(self.campana, False, 'COMPLETECALLER', contacto.telefono,
                                      self.agente, contacto, 1, 1)
            if contactacion == 'no_contacta':
                estado = random.choice(estados)
                generador.generar_log(self.campana, False, estado, contacto.telefono,
                                      None, contacto)
            if contactacion == 'no_llama':
                pass

    def test_obtiene_contactos_reciclados_contactados_calificados(self):
        # estados no contactados:
        estados = LlamadaLog.EVENTOS_NO_CONEXION
        self._generar_llamadas_y_calificaciones(estados)
        reciclador = RecicladorContactosCampanaDIALER()

        # vamos a chequear que sea la misma cantidad de contactos reciclados
        # para los calificados
        for calificacion in self.campana.opciones_calificacion.all():
            contactos_reciclados = reciclador._obtener_contactos_calificados(
                self.campana, [calificacion])

            calificaciones_query = self.campana.obtener_calificaciones().filter(
                opcion_calificacion=calificacion).values_list('contacto_id', flat=True)
            self.assertEquals(calificaciones_query.count(), len(contactos_reciclados))

    def test_obtiene_contactos_reciclados_contactados_no_calificados(self):
        # estados no contactados:
        estados = LlamadaLog.EVENTOS_NO_CONEXION
        self._generar_llamadas_y_calificaciones(estados)
        reciclador = RecicladorContactosCampanaDIALER()

        # ahora chequeamos para agente no califico
        calificados = self.campana.obtener_calificaciones().values_list(
            'contacto_id', flat=True).distinct()
        contactados_no_calificados = LlamadaLog.objects.filter(event='CONNECT').exclude(
            contacto_id__in=calificados).values_list('contacto_id', flat=True)

        no_calificados_reciclados = reciclador._obtener_contactos_no_contactados(
            self.campana, [EstadisticasContactacion.AGENTE_NO_CALIFICO, ]).values_list(
            'id', flat=True)
        self.assertEqual(set(no_calificados_reciclados), set(contactados_no_calificados))

    def test_obtiene_contactos_reciclados_no_llamados(self):
        # estados no contactados:
        estados = LlamadaLog.EVENTOS_NO_CONEXION
        self._generar_llamadas_y_calificaciones(estados)
        reciclador = RecicladorContactosCampanaDIALER()

        # Ahora checkeamos para no llamados
        llamados = LlamadaLog.objects.filter(event='DIAL').values_list('contacto_id', flat=True)
        no_llamados = self.campana.bd_contacto.contactos.exclude(id__in=llamados)
        no_llamados_reciclados = reciclador._obtener_contactos_no_contactados(
            self.campana, [EstadisticasContactacion.NO_LLAMADO, ])
        self.assertEqual(set(no_llamados), set(no_llamados_reciclados))

    def test_obtiene_contactos_reciclados_no_contactados(self):
        # estados no contactados:
        estados = LlamadaLog.EVENTOS_NO_CONEXION
        reciclador = RecicladorContactosCampanaDIALER()

        # ahora vamos a chequear para los no contactados
        for estado in estados:
            id_estado = EstadisticasContactacion.MAP_ESTADO_ID[estado]
            no_contactados_reciclados = reciclador._obtener_contactos_no_contactados(
                self.campana, [id_estado, ])
            for contacto in no_contactados_reciclados:
                self.assertEqual(CalificacionCliente.objects.filter(
                    contacto_id=contacto.id).count(), 0)
                logs = LlamadaLog.objects.filter(contacto_id=contacto.id).order_by('-id')
                self.assertTrue(logs.count() > 0)
                self.assertEqual(logs[0].event, estado)
