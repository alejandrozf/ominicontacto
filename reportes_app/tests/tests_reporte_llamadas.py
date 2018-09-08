# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

import json

from django.test import TestCase
from django.utils.timezone import now, timedelta
from django.core.urlresolvers import reverse

from ominicontacto_app.utiles import datetime_hora_minima_dia
from ominicontacto_app.models import Campana
from ominicontacto_app.tests.factories import SupervisorProfileFactory, AgenteProfileFactory,\
    CampanaFactory, ContactoFactory, UserFactory

from reportes_app.reporte_llamadas import ReporteDeLlamadas
from reportes_app.tests.utiles import GeneradorDeLlamadaLogs


class BaseReporteDeLlamadasTests(TestCase):

    def setUp(self):
        super(BaseReporteDeLlamadasTests, self).setUp()
        self.hasta = now()
        self.durante = now() - timedelta(days=1)
        self.desde = datetime_hora_minima_dia(self.hasta) - timedelta(days=1)

        self.supervisor = SupervisorProfileFactory(is_administrador=True)

        self.agente1 = AgenteProfileFactory()
        self.agente2 = AgenteProfileFactory()
        self.agente3 = AgenteProfileFactory()

        self.manual = CampanaFactory.create(type=Campana.TYPE_MANUAL, nombre='camp-manual-1',
                                            estado=Campana.ESTADO_ACTIVA)

        self.dialer = CampanaFactory.create(type=Campana.TYPE_DIALER, nombre='camp-dialer-1',
                                            estado=Campana.ESTADO_ACTIVA)
        self.contacto_d = ContactoFactory(bd_contacto=self.dialer.bd_contacto)

        self.entrante = CampanaFactory.create(type=Campana.TYPE_ENTRANTE, nombre='camp-entrante-1',
                                              estado=Campana.ESTADO_ACTIVA)

        self.preview = CampanaFactory.create(type=Campana.TYPE_PREVIEW, nombre='camp-preview-1',
                                             estado=Campana.ESTADO_ACTIVA)
        self.contacto_p = ContactoFactory(bd_contacto=self.preview.bd_contacto)

        self.campanas = [self.manual, self.dialer, self.entrante, self.preview, ]


class ReporteDeLlamadasVacioTests(BaseReporteDeLlamadasTests):

    def test_get_campana_type_display(self):
        generador = ReporteDeLlamadas(self.desde, self.hasta, True, self.supervisor.user)
        self.assertEqual(generador._get_campana_type_display(Campana.TYPE_MANUAL),
                         Campana.TYPE_MANUAL_DISPLAY)
        self.assertEqual(generador._get_campana_type_display(Campana.TYPE_DIALER),
                         Campana.TYPE_DIALER_DISPLAY)
        self.assertEqual(generador._get_campana_type_display(Campana.TYPE_ENTRANTE),
                         Campana.TYPE_ENTRANTE_DISPLAY)
        self.assertEqual(generador._get_campana_type_display(Campana.TYPE_PREVIEW),
                         Campana.TYPE_PREVIEW_DISPLAY)

    def test_campanas_implicadas(self):

        self.manual.estado = Campana.ESTADO_FINALIZADA
        self.manual.save()
        self.dialer.estado = Campana.ESTADO_FINALIZADA
        self.dialer.save()
        self.entrante.estado = Campana.ESTADO_FINALIZADA
        self.entrante.save()
        self.preview.estado = Campana.ESTADO_FINALIZADA
        self.preview.save()

        # Incluir Finalizadas
        generador = ReporteDeLlamadas(self.desde, self.hasta, True, self.supervisor.user)
        campanas = generador._campanas_implicadas(self.supervisor.user, True)
        self.assertEqual(campanas.count(), 4)

        # No Incluir Finalizadas
        generador = ReporteDeLlamadas(self.desde, self.hasta, False, self.supervisor.user)
        campanas = generador._campanas_implicadas(self.supervisor.user, False)
        self.assertEqual(campanas.count(), 0)

    def test_genera_estructura_general_para_estadisticas(self):
        generador = ReporteDeLlamadas(self.desde, self.hasta, True, self.supervisor.user)
        estadisticas = generador.estadisticas

        self.assertIn('total_llamadas_procesadas', estadisticas)
        self.assertIn('llamadas_por_campana', estadisticas)
        self.assertEqual(len(estadisticas['llamadas_por_campana']), 4)

        nombres_tablas = ['llamadas_por_tipo',
                          'tipos_de_llamada_por_campana']
        for tabla in nombres_tablas:
            self.assertIn(tabla, estadisticas)
            for tipo, display in Campana.TYPES_CAMPANA:
                self.assertIn(display, estadisticas[tabla])

    def test_genera_estructura_estadisticas_llamadas_por_tipo(self):
        generador = ReporteDeLlamadas(self.desde, self.hasta, True, self.supervisor.user)
        estadisticas = generador.estadisticas
        llamadas_por_tipo = estadisticas['llamadas_por_tipo']

        data_manual = llamadas_por_tipo[Campana.TYPE_MANUAL_DISPLAY]
        self.assertIn('total', data_manual)
        self.assertIn('conectadas', data_manual)
        self.assertIn('no_conectadas', data_manual)
        data_manual = llamadas_por_tipo[Campana.TYPE_DIALER_DISPLAY]
        self.assertIn('total', data_manual)
        self.assertIn('atendidas', data_manual)
        self.assertIn('no_atendidas', data_manual)
        self.assertIn('perdidas', data_manual)
        data_manual = llamadas_por_tipo[Campana.TYPE_ENTRANTE_DISPLAY]
        self.assertIn('total', data_manual)
        self.assertIn('atendidas', data_manual)
        self.assertIn('expiradas', data_manual)
        self.assertIn('abandonadas', data_manual)
        data_manual = llamadas_por_tipo[Campana.TYPE_PREVIEW_DISPLAY]
        self.assertIn('total', data_manual)
        self.assertIn('conectadas', data_manual)
        self.assertIn('no_conectadas', data_manual)

    def test_genera_estructura_estadisticas_llamadas_por_campana(self):
        generador = ReporteDeLlamadas(self.desde, self.hasta, True, self.supervisor.user)
        estadisticas = generador.estadisticas
        tipos_de_llamada_por_campana = estadisticas['llamadas_por_campana']

        for campana in self.campanas:
            self.assertIn(campana.id, tipos_de_llamada_por_campana)
            datos_campana = tipos_de_llamada_por_campana[campana.id]
            self.assertEqual(datos_campana['nombre'], campana.nombre)
            self.assertEqual(datos_campana['total'], 0)
            self.assertEqual(datos_campana['manuales'], 0)
            tipo_campana = generador._get_campana_type_display(campana.type)
            self.assertEqual(datos_campana['tipo'], tipo_campana)

    def test_genera_estructura_estadisticas_tipos_de_llamada_por_campana(self):
        generador = ReporteDeLlamadas(self.desde, self.hasta, True, self.supervisor.user)
        estadisticas = generador.estadisticas
        tipos = estadisticas['tipos_de_llamada_por_campana']

        self.assertIn(self.manual.id, tipos[Campana.TYPE_MANUAL_DISPLAY])
        datos_campana = tipos[Campana.TYPE_MANUAL_DISPLAY][self.manual.id]
        self.assertEqual(len(datos_campana), 5)
        self.assertEqual(datos_campana['nombre'], self.manual.nombre)
        self.assertEqual(datos_campana['t_espera_conexion'], 0)
        self.assertEqual(datos_campana['efectuadas'], 0)
        self.assertEqual(datos_campana['conectadas'], 0)
        self.assertEqual(datos_campana['no_conectadas'], 0)

        self.assertIn(self.dialer.id, tipos[Campana.TYPE_DIALER_DISPLAY])
        datos_campana = tipos[Campana.TYPE_DIALER_DISPLAY][self.dialer.id]
        self.assertEqual(len(datos_campana), 13)
        self.assertEqual(datos_campana['nombre'], self.dialer.nombre)
        self.assertEqual(datos_campana['t_espera_conexion'], 0)
        self.assertEqual(datos_campana['efectuadas'], 0)
        self.assertEqual(datos_campana['conectadas'], 0)
        self.assertEqual(datos_campana['atendidas'], 0)
        self.assertEqual(datos_campana['expiradas'], 0)
        self.assertEqual(datos_campana['abandonadas'], 0)
        self.assertEqual(datos_campana['t_abandono'], 0)
        self.assertEqual(datos_campana['t_espera_atencion'], 0)
        self.assertEqual(datos_campana['efectuadas_manuales'], 0)
        self.assertEqual(datos_campana['conectadas_manuales'], 0)
        self.assertEqual(datos_campana['no_conectadas_manuales'], 0)
        self.assertEqual(datos_campana['t_espera_conexion_manuales'], 0)

        self.assertIn(self.entrante.id, tipos[Campana.TYPE_ENTRANTE_DISPLAY])
        datos_campana = tipos[Campana.TYPE_ENTRANTE_DISPLAY][self.entrante.id]
        self.assertEqual(len(datos_campana), 11)
        self.assertEqual(datos_campana['nombre'], self.entrante.nombre)
        self.assertEqual(datos_campana['t_espera_conexion'], 0)
        self.assertEqual(datos_campana['atendidas'], 0)
        self.assertEqual(datos_campana['expiradas'], 0)
        self.assertEqual(datos_campana['abandonadas'], 0)
        self.assertEqual(datos_campana['t_abandono'], 0)
        self.assertEqual(datos_campana['recibidas'], 0)
        self.assertEqual(datos_campana['efectuadas_manuales'], 0)
        self.assertEqual(datos_campana['conectadas_manuales'], 0)
        self.assertEqual(datos_campana['no_conectadas_manuales'], 0)
        self.assertEqual(datos_campana['t_espera_conexion_manuales'], 0)

        self.assertIn(self.preview.id, tipos[Campana.TYPE_PREVIEW_DISPLAY])
        datos_campana = tipos[Campana.TYPE_PREVIEW_DISPLAY][self.preview.id]
        self.assertEqual(len(datos_campana), 9)
        self.assertEqual(datos_campana['nombre'], self.preview.nombre)
        self.assertEqual(datos_campana['t_espera_conexion'], 0)
        self.assertEqual(datos_campana['efectuadas'], 0)
        self.assertEqual(datos_campana['conectadas'], 0)
        self.assertEqual(datos_campana['no_conectadas'], 0)
        self.assertEqual(datos_campana['efectuadas_manuales'], 0)
        self.assertEqual(datos_campana['conectadas_manuales'], 0)
        self.assertEqual(datos_campana['no_conectadas_manuales'], 0)
        self.assertEqual(datos_campana['t_espera_conexion_manuales'], 0)


class ReporteDeLlamadasConLlamadasManualesTests(BaseReporteDeLlamadasTests):

    def test_incremental_llamada_manual(self):
        tipo = Campana.TYPE_MANUAL_DISPLAY
        campana = self.manual
        generador = GeneradorDeLlamadaLogs()

        # Genero una llamada manual que termina en BUSY
        generador.generar_log(campana, True, 'BUSY', '123', self.agente1, bridge_wait_time=5)
        self.hasta = now()
        reporte = ReporteDeLlamadas(self.desde, self.hasta, True, self.supervisor.user)
        estadisticas = reporte.estadisticas

        self.assertEqual(estadisticas['total_llamadas_procesadas'], 1)
        por_tipo = estadisticas['llamadas_por_tipo'][tipo]
        self.assertEqual(por_tipo['total'], 1)
        self.assertEqual(por_tipo['conectadas'], 0)
        self.assertEqual(por_tipo['no_conectadas'], 1)
        llamadas = estadisticas['llamadas_por_campana'][campana.id]
        self.assertEqual(llamadas['total'], 1)
        self.assertEqual(llamadas['manuales'], 1)
        tipos = estadisticas['tipos_de_llamada_por_campana'][tipo]
        self.assertEqual(tipos[campana.id]['t_espera_conexion'], 5)
        self.assertEqual(tipos[campana.id]['efectuadas'], 1)
        self.assertEqual(tipos[campana.id]['conectadas'], 0)
        self.assertEqual(tipos[campana.id]['no_conectadas'], 1)

        # Genero una llamada manual que termina en COMPLETEAGENT y otra en COMPLETECALLER
        generador.generar_log(campana, True, 'COMPLETEAGENT', '1234', self.agente1,
                              bridge_wait_time=4, duracion_llamada=20)
        generador.generar_log(campana, True, 'COMPLETECALLER', '1234', self.agente1,
                              bridge_wait_time=6, duracion_llamada=40)
        self.hasta = now()
        reporte = ReporteDeLlamadas(self.desde, self.hasta, True, self.supervisor.user)
        estadisticas = reporte.estadisticas

        self.assertEqual(estadisticas['total_llamadas_procesadas'], 3)
        por_tipo = estadisticas['llamadas_por_tipo'][tipo]
        self.assertEqual(por_tipo['total'], 3)
        self.assertEqual(por_tipo['conectadas'], 2)
        self.assertEqual(por_tipo['no_conectadas'], 1)
        llamadas = estadisticas['llamadas_por_campana'][campana.id]
        self.assertEqual(llamadas['total'], 3)
        self.assertEqual(llamadas['manuales'], 3)
        tipos = estadisticas['tipos_de_llamada_por_campana'][tipo]
        self.assertEqual(tipos[campana.id]['t_espera_conexion'], 5)
        self.assertEqual(tipos[campana.id]['efectuadas'], 3)
        self.assertEqual(tipos[campana.id]['conectadas'], 2)
        self.assertEqual(tipos[campana.id]['no_conectadas'], 1)

    def test_incremental_llamada_preview(self):
        tipo = Campana.TYPE_PREVIEW_DISPLAY
        campana = self.preview
        generador = GeneradorDeLlamadaLogs()

        # Genero una llamada preview que termina en BUSY
        generador.generar_log(campana, False, 'BUSY', '123', self.agente1, bridge_wait_time=5)
        self.hasta = now()
        reporte = ReporteDeLlamadas(self.desde, self.hasta, True, self.supervisor.user)
        estadisticas = reporte.estadisticas

        self.assertEqual(estadisticas['total_llamadas_procesadas'], 1)
        por_tipo = estadisticas['llamadas_por_tipo'][tipo]
        self.assertEqual(por_tipo['total'], 1)
        self.assertEqual(por_tipo['conectadas'], 0)
        self.assertEqual(por_tipo['no_conectadas'], 1)
        llamadas = estadisticas['llamadas_por_campana'][campana.id]
        self.assertEqual(llamadas['total'], 1)
        self.assertEqual(llamadas['manuales'], 0)
        tipos = estadisticas['tipos_de_llamada_por_campana'][tipo]
        self.assertEqual(tipos[campana.id]['t_espera_conexion'], 5)
        self.assertEqual(tipos[campana.id]['efectuadas'], 1)
        self.assertEqual(tipos[campana.id]['conectadas'], 0)
        self.assertEqual(tipos[campana.id]['no_conectadas'], 1)

        # Genero una llamada preview que termina en COMPLETEAGENT y otra en COMPLETECALLER
        generador.generar_log(campana, False, 'COMPLETEAGENT', '1234', self.agente1,
                              bridge_wait_time=4, duracion_llamada=20)
        generador.generar_log(campana, False, 'COMPLETECALLER', '1234', self.agente1,
                              bridge_wait_time=6, duracion_llamada=40)
        self.hasta = now()
        reporte = ReporteDeLlamadas(self.desde, self.hasta, True, self.supervisor.user)
        estadisticas = reporte.estadisticas

        self.assertEqual(estadisticas['total_llamadas_procesadas'], 3)
        por_tipo = estadisticas['llamadas_por_tipo'][tipo]
        self.assertEqual(por_tipo['total'], 3)
        self.assertEqual(por_tipo['conectadas'], 2)
        self.assertEqual(por_tipo['no_conectadas'], 1)
        llamadas = estadisticas['llamadas_por_campana'][campana.id]
        self.assertEqual(llamadas['total'], 3)
        self.assertEqual(llamadas['manuales'], 0)
        tipos = estadisticas['tipos_de_llamada_por_campana'][tipo]
        self.assertEqual(tipos[campana.id]['t_espera_conexion'], 5)
        self.assertEqual(tipos[campana.id]['efectuadas'], 3)
        self.assertEqual(tipos[campana.id]['conectadas'], 2)
        self.assertEqual(tipos[campana.id]['no_conectadas'], 1)

        # Genero llamadas preview manuales que terminan en BUSY y en COMPLETECALLER
        generador.generar_log(campana, True, 'BUSY', '1234', self.agente1,
                              bridge_wait_time=4)
        generador.generar_log(campana, True, 'COMPLETECALLER', '1234', self.agente1,
                              bridge_wait_time=8, duracion_llamada=40)
        self.hasta = now()
        reporte = ReporteDeLlamadas(self.desde, self.hasta, True, self.supervisor.user)
        estadisticas = reporte.estadisticas

        self.assertEqual(estadisticas['total_llamadas_procesadas'], 5)
        por_tipo_preview = estadisticas['llamadas_por_tipo'][tipo]
        self.assertEqual(por_tipo_preview['total'], 3)
        self.assertEqual(por_tipo_preview['conectadas'], 2)
        self.assertEqual(por_tipo_preview['no_conectadas'], 1)
        por_tipo_manual = estadisticas['llamadas_por_tipo'][Campana.TYPE_MANUAL_DISPLAY]
        self.assertEqual(por_tipo_manual['total'], 2)
        self.assertEqual(por_tipo_manual['conectadas'], 1)
        self.assertEqual(por_tipo_manual['no_conectadas'], 1)
        llamadas = estadisticas['llamadas_por_campana'][campana.id]
        self.assertEqual(llamadas['total'], 5)
        self.assertEqual(llamadas['manuales'], 2)
        tipos = estadisticas['tipos_de_llamada_por_campana'][tipo]
        self.assertEqual(tipos[campana.id]['t_espera_conexion'], 5)
        self.assertEqual(tipos[campana.id]['efectuadas'], 5)
        self.assertEqual(tipos[campana.id]['conectadas'], 3)
        self.assertEqual(tipos[campana.id]['no_conectadas'], 2)
        self.assertEqual(tipos[campana.id]['efectuadas_manuales'], 2)
        self.assertEqual(tipos[campana.id]['conectadas_manuales'], 1)
        self.assertEqual(tipos[campana.id]['no_conectadas_manuales'], 1)
        self.assertEqual(tipos[campana.id]['t_espera_conexion_manuales'], 6)

    def test_incremental_llamada_dialer(self):
        tipo = Campana.TYPE_DIALER_DISPLAY
        campana = self.dialer
        generador = GeneradorDeLlamadaLogs()

        # Genero una llamada DIALER que termina en BUSY
        generador.generar_log(campana, False, 'BUSY', '123', self.agente1, bridge_wait_time=5)
        self.hasta = now()
        reporte = ReporteDeLlamadas(self.desde, self.hasta, True, self.supervisor.user)
        estadisticas = reporte.estadisticas

        self.assertEqual(estadisticas['total_llamadas_procesadas'], 1)
        por_tipo = estadisticas['llamadas_por_tipo'][tipo]
        self.assertEqual(por_tipo['total'], 1)
        self.assertEqual(por_tipo['atendidas'], 0)
        self.assertEqual(por_tipo['no_atendidas'], 1)
        self.assertEqual(por_tipo['perdidas'], 0)
        llamadas = estadisticas['llamadas_por_campana'][campana.id]
        self.assertEqual(llamadas['total'], 1)
        self.assertEqual(llamadas['manuales'], 0)
        tipos = estadisticas['tipos_de_llamada_por_campana'][tipo]
        self.assertEqual(tipos[campana.id]['efectuadas'], 1)
        self.assertEqual(tipos[campana.id]['atendidas'], 0)
        self.assertEqual(tipos[campana.id]['conectadas'], 0)
        self.assertEqual(tipos[campana.id]['expiradas'], 0)
        self.assertEqual(tipos[campana.id]['abandonadas'], 0)
        self.assertEqual(tipos[campana.id]['t_espera_conexion'], 0)
        self.assertEqual(tipos[campana.id]['t_espera_atencion'], 0)
        self.assertEqual(tipos[campana.id]['t_abandono'], 0)

        # Genero una llamada DIALER que termina en ABANDON
        generador.generar_log(campana, False, 'ABANDON', '123', self.agente1, bridge_wait_time=5)
        self.hasta = now()
        reporte = ReporteDeLlamadas(self.desde, self.hasta, True, self.supervisor.user)
        estadisticas = reporte.estadisticas

        self.assertEqual(estadisticas['total_llamadas_procesadas'], 2)
        por_tipo = estadisticas['llamadas_por_tipo'][tipo]
        self.assertEqual(por_tipo['total'], 2)
        self.assertEqual(por_tipo['atendidas'], 1)
        self.assertEqual(por_tipo['no_atendidas'], 1)
        self.assertEqual(por_tipo['perdidas'], 1)
        llamadas = estadisticas['llamadas_por_campana'][campana.id]
        self.assertEqual(llamadas['total'], 2)
        self.assertEqual(llamadas['manuales'], 0)
        tipos = estadisticas['tipos_de_llamada_por_campana'][tipo]
        self.assertEqual(tipos[campana.id]['efectuadas'], 2)
        self.assertEqual(tipos[campana.id]['atendidas'], 1)
        self.assertEqual(tipos[campana.id]['conectadas'], 0)
        self.assertEqual(tipos[campana.id]['expiradas'], 0)
        self.assertEqual(tipos[campana.id]['abandonadas'], 1)
        self.assertEqual(tipos[campana.id]['t_espera_conexion'], 0)
        self.assertEqual(tipos[campana.id]['t_espera_atencion'], 5)
        self.assertEqual(tipos[campana.id]['t_abandono'], 5)

        # Genero una llamada DIALER que termina en EXITWITHTIMEOUT
        generador.generar_log(campana, False, 'EXITWITHTIMEOUT', '123', self.agente1,
                              bridge_wait_time=4)
        self.hasta = now()
        reporte = ReporteDeLlamadas(self.desde, self.hasta, True, self.supervisor.user)
        estadisticas = reporte.estadisticas

        self.assertEqual(estadisticas['total_llamadas_procesadas'], 3)
        por_tipo = estadisticas['llamadas_por_tipo'][tipo]
        self.assertEqual(por_tipo['total'], 3)
        self.assertEqual(por_tipo['atendidas'], 2)
        self.assertEqual(por_tipo['no_atendidas'], 1)
        self.assertEqual(por_tipo['perdidas'], 2)
        llamadas = estadisticas['llamadas_por_campana'][campana.id]
        self.assertEqual(llamadas['total'], 3)
        self.assertEqual(llamadas['manuales'], 0)
        tipos = estadisticas['tipos_de_llamada_por_campana'][tipo]
        self.assertEqual(tipos[campana.id]['efectuadas'], 3)
        self.assertEqual(tipos[campana.id]['atendidas'], 2)
        self.assertEqual(tipos[campana.id]['conectadas'], 0)
        self.assertEqual(tipos[campana.id]['expiradas'], 1)
        self.assertEqual(tipos[campana.id]['abandonadas'], 1)
        self.assertEqual(tipos[campana.id]['t_espera_conexion'], 0)
        self.assertEqual(tipos[campana.id]['t_espera_atencion'], 4)
        self.assertEqual(tipos[campana.id]['t_abandono'], 5)

        # Genero dos llamadas DIALER que terminan en COMPLETEAGENT y COMPLETECALLER
        generador.generar_log(campana, False, 'COMPLETEAGENT', '123', self.agente1,
                              bridge_wait_time=8, duracion_llamada=18)
        generador.generar_log(campana, False, 'COMPLETECALLER', '123', self.agente1,
                              bridge_wait_time=10, duracion_llamada=22)
        self.hasta = now()
        reporte = ReporteDeLlamadas(self.desde, self.hasta, True, self.supervisor.user)
        estadisticas = reporte.estadisticas

        self.assertEqual(estadisticas['total_llamadas_procesadas'], 5)
        por_tipo = estadisticas['llamadas_por_tipo'][tipo]
        self.assertEqual(por_tipo['total'], 5)
        self.assertEqual(por_tipo['atendidas'], 4)
        self.assertEqual(por_tipo['no_atendidas'], 1)
        self.assertEqual(por_tipo['perdidas'], 2)
        llamadas = estadisticas['llamadas_por_campana'][campana.id]
        self.assertEqual(llamadas['total'], 5)
        self.assertEqual(llamadas['manuales'], 0)
        tipos = estadisticas['tipos_de_llamada_por_campana'][tipo]
        self.assertEqual(tipos[campana.id]['efectuadas'], 5)
        self.assertEqual(tipos[campana.id]['atendidas'], 4)
        self.assertEqual(tipos[campana.id]['conectadas'], 2)
        self.assertEqual(tipos[campana.id]['expiradas'], 1)
        self.assertEqual(tipos[campana.id]['abandonadas'], 1)
        self.assertEqual(tipos[campana.id]['t_espera_conexion'], 9)
        self.assertEqual(tipos[campana.id]['t_espera_atencion'], 6)
        self.assertEqual(tipos[campana.id]['t_abandono'], 5)

        # Genero llamadas dialer Manuales CANCEL, COMPLETECALLER
        generador.generar_log(campana, True, 'CANCEL', '123', self.agente1,
                              bridge_wait_time=4)
        generador.generar_log(campana, True, 'COMPLETECALLER', '123', self.agente1,
                              bridge_wait_time=8, duracion_llamada=30)
        self.hasta = now()
        reporte = ReporteDeLlamadas(self.desde, self.hasta, True, self.supervisor.user)
        estadisticas = reporte.estadisticas

        self.assertEqual(estadisticas['total_llamadas_procesadas'], 7)
        por_tipo_dialer = estadisticas['llamadas_por_tipo'][tipo]
        self.assertEqual(por_tipo_dialer['total'], 5)
        self.assertEqual(por_tipo_dialer['atendidas'], 4)
        self.assertEqual(por_tipo_dialer['no_atendidas'], 1)
        self.assertEqual(por_tipo_dialer['perdidas'], 2)
        por_tipo_manual = estadisticas['llamadas_por_tipo'][Campana.TYPE_MANUAL_DISPLAY]
        self.assertEqual(por_tipo_manual['total'], 2)
        self.assertEqual(por_tipo_manual['conectadas'], 1)
        self.assertEqual(por_tipo_manual['no_conectadas'], 1)
        llamadas = estadisticas['llamadas_por_campana'][campana.id]
        self.assertEqual(llamadas['total'], 7)
        self.assertEqual(llamadas['manuales'], 2)
        tipos = estadisticas['tipos_de_llamada_por_campana'][tipo]
        self.assertEqual(tipos[campana.id]['efectuadas'], 5)
        self.assertEqual(tipos[campana.id]['atendidas'], 4)
        self.assertEqual(tipos[campana.id]['conectadas'], 2)
        self.assertEqual(tipos[campana.id]['expiradas'], 1)
        self.assertEqual(tipos[campana.id]['abandonadas'], 1)
        self.assertEqual(tipos[campana.id]['t_espera_conexion'], 9)
        self.assertEqual(tipos[campana.id]['t_espera_atencion'], 6)
        self.assertEqual(tipos[campana.id]['t_abandono'], 5)
        self.assertEqual(tipos[campana.id]['efectuadas_manuales'], 2)
        self.assertEqual(tipos[campana.id]['conectadas_manuales'], 1)
        self.assertEqual(tipos[campana.id]['no_conectadas_manuales'], 1)
        self.assertEqual(tipos[campana.id]['t_espera_conexion_manuales'], 6)

    def test_incremental_llamada_entrante(self):
        tipo = Campana.TYPE_ENTRANTE_DISPLAY
        campana = self.entrante
        generador = GeneradorDeLlamadaLogs()

        # Genero una llamada ENTRANTE que termina en ABANDON
        generador.generar_log(campana, False, 'ABANDON', '123', self.agente1, bridge_wait_time=5)
        self.hasta = now()
        reporte = ReporteDeLlamadas(self.desde, self.hasta, True, self.supervisor.user)
        estadisticas = reporte.estadisticas

        self.assertEqual(estadisticas['total_llamadas_procesadas'], 1)
        por_tipo = estadisticas['llamadas_por_tipo'][tipo]
        self.assertEqual(por_tipo['total'], 1)
        self.assertEqual(por_tipo['atendidas'], 0)
        self.assertEqual(por_tipo['expiradas'], 0)
        self.assertEqual(por_tipo['abandonadas'], 1)
        llamadas = estadisticas['llamadas_por_campana'][campana.id]
        self.assertEqual(llamadas['total'], 1)
        self.assertEqual(llamadas['manuales'], 0)
        tipos = estadisticas['tipos_de_llamada_por_campana'][tipo]
        self.assertEqual(tipos[campana.id]['recibidas'], 1)
        self.assertEqual(tipos[campana.id]['atendidas'], 0)
        self.assertEqual(tipos[campana.id]['expiradas'], 0)
        self.assertEqual(tipos[campana.id]['abandonadas'], 1)
        self.assertEqual(tipos[campana.id]['t_espera_conexion'], 0)
        self.assertEqual(tipos[campana.id]['t_abandono'], 5)

        # Genero una llamada ENTRANTE que termina en EXITWITHTIMEOUT
        generador.generar_log(campana, False, 'EXITWITHTIMEOUT', '123', self.agente1,
                              bridge_wait_time=6)
        self.hasta = now()
        reporte = ReporteDeLlamadas(self.desde, self.hasta, True, self.supervisor.user)
        estadisticas = reporte.estadisticas

        self.assertEqual(estadisticas['total_llamadas_procesadas'], 2)
        por_tipo = estadisticas['llamadas_por_tipo'][tipo]
        self.assertEqual(por_tipo['total'], 2)
        self.assertEqual(por_tipo['atendidas'], 0)
        self.assertEqual(por_tipo['expiradas'], 1)
        self.assertEqual(por_tipo['abandonadas'], 1)
        llamadas = estadisticas['llamadas_por_campana'][campana.id]
        self.assertEqual(llamadas['total'], 2)
        self.assertEqual(llamadas['manuales'], 0)
        tipos = estadisticas['tipos_de_llamada_por_campana'][tipo]
        self.assertEqual(tipos[campana.id]['recibidas'], 2)
        self.assertEqual(tipos[campana.id]['atendidas'], 0)
        self.assertEqual(tipos[campana.id]['expiradas'], 1)
        self.assertEqual(tipos[campana.id]['abandonadas'], 1)
        self.assertEqual(tipos[campana.id]['t_espera_conexion'], 0)
        self.assertEqual(tipos[campana.id]['t_abandono'], 5)

        # Genero una llamada ENTRANTE que termina en COMPLETECALLER
        generador.generar_log(campana, False, 'COMPLETECALLER', '123', self.agente1,
                              bridge_wait_time=7, duracion_llamada=30)
        self.hasta = now()
        reporte = ReporteDeLlamadas(self.desde, self.hasta, True, self.supervisor.user)
        estadisticas = reporte.estadisticas

        self.assertEqual(estadisticas['total_llamadas_procesadas'], 3)
        por_tipo = estadisticas['llamadas_por_tipo'][tipo]
        self.assertEqual(por_tipo['total'], 3)
        self.assertEqual(por_tipo['atendidas'], 1)
        self.assertEqual(por_tipo['expiradas'], 1)
        self.assertEqual(por_tipo['abandonadas'], 1)
        llamadas = estadisticas['llamadas_por_campana'][campana.id]
        self.assertEqual(llamadas['total'], 3)
        self.assertEqual(llamadas['manuales'], 0)
        tipos = estadisticas['tipos_de_llamada_por_campana'][tipo]
        self.assertEqual(tipos[campana.id]['recibidas'], 3)
        self.assertEqual(tipos[campana.id]['atendidas'], 1)
        self.assertEqual(tipos[campana.id]['expiradas'], 1)
        self.assertEqual(tipos[campana.id]['abandonadas'], 1)
        self.assertEqual(tipos[campana.id]['t_espera_conexion'], 7)
        self.assertEqual(tipos[campana.id]['t_abandono'], 5)

        # Genero llamadas diaer manuales CANCEL, COMPLETECALLER
        generador.generar_log(campana, True, 'CANCEL', '123', self.agente1,
                              bridge_wait_time=5)
        generador.generar_log(campana, True, 'COMPLETECALLER', '123', self.agente1,
                              bridge_wait_time=7, duracion_llamada=30)
        self.hasta = now()
        reporte = ReporteDeLlamadas(self.desde, self.hasta, True, self.supervisor.user)
        estadisticas = reporte.estadisticas

        por_tipo_entrante = estadisticas['llamadas_por_tipo'][tipo]
        self.assertEqual(por_tipo_entrante['total'], 3)
        self.assertEqual(por_tipo_entrante['atendidas'], 1)
        self.assertEqual(por_tipo_entrante['expiradas'], 1)
        self.assertEqual(por_tipo_entrante['abandonadas'], 1)
        por_tipo_manual = estadisticas['llamadas_por_tipo'][Campana.TYPE_MANUAL_DISPLAY]
        self.assertEqual(por_tipo_manual['total'], 2)
        self.assertEqual(por_tipo_manual['conectadas'], 1)
        self.assertEqual(por_tipo_manual['no_conectadas'], 1)
        llamadas = estadisticas['llamadas_por_campana'][campana.id]
        self.assertEqual(llamadas['total'], 5)
        self.assertEqual(llamadas['manuales'], 2)
        tipos = estadisticas['tipos_de_llamada_por_campana'][tipo]
        self.assertEqual(tipos[campana.id]['recibidas'], 3)
        self.assertEqual(tipos[campana.id]['atendidas'], 1)
        self.assertEqual(tipos[campana.id]['expiradas'], 1)
        self.assertEqual(tipos[campana.id]['abandonadas'], 1)
        self.assertEqual(tipos[campana.id]['t_espera_conexion'], 7)
        self.assertEqual(tipos[campana.id]['t_abandono'], 5)
        self.assertEqual(tipos[campana.id]['efectuadas_manuales'], 2)
        self.assertEqual(tipos[campana.id]['conectadas_manuales'], 1)
        self.assertEqual(tipos[campana.id]['no_conectadas_manuales'], 1)
        self.assertEqual(tipos[campana.id]['t_espera_conexion_manuales'], 6)


class AccesoReportesTests(TestCase):
    PWD = u'admin123'

    def setUp(self):
        self.usuario_admin_supervisor = UserFactory(is_staff=True, is_supervisor=True)
        self.usuario_admin_supervisor.set_password(self.PWD)
        self.usuario_admin_supervisor.save()
        self.client.login(username=self.usuario_admin_supervisor.username, password=self.PWD)

        hasta = now()
        desde = datetime_hora_minima_dia(hasta)
        reporte = ReporteDeLlamadas(desde, hasta, True, self.usuario_admin_supervisor)
        self.estadisticas = reporte.estadisticas

    def test_usuario_logueado_accede_a_pagina_ppal_reportes_llamadas(self):
        url = reverse('reporte_llamadas')
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, 'reporte_llamadas.html')
        self.assertIn('estadisticas', response.context)
        self.assertIn('estadisticas_por_fecha', response.context)
        self.assertIn('graficos', response.context)
        self.assertIn('estadisticas_json', response.context)
        self.assertIn('desde', response.context)
        self.assertIn('hasta', response.context)

    def test_usuario_no_logueado_no_accede_a_pagina_ppal_reportes_llamadas(self):
        url = reverse('reporte_llamadas')
        self.client.logout()
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, u'registration/login.html')

    def test_usuario_logueado_accede_a_realizar_reporte_llamadas_por_tipo_csv(self):
        url = reverse('csv_reporte_llamadas')
        data = {'tipo_reporte': 'llamadas_por_tipo', 'estadisticas': json.dumps(self.estadisticas)}
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.serialize().find('llamadas_por_tipo.csv') > -1)

    def test_usuario_logueado_con_mal_parametro_tira_400(self):
        url = reverse('csv_reporte_llamadas')
        data = {'tipo_reporte': 'reporte_inexistente',
                'estadisticas': json.dumps(self.estadisticas)}
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, u'400.html')

    def test_usuario_no_logueado_no_accede_a_realizar_reporte_total_llamadas_csv(self):
        url = reverse('csv_reporte_llamadas')
        data = {'tipo_reporte': 'llamadas_por_tipo', 'estadisticas': json.dumps(self.estadisticas)}
        self.client.logout()
        response = self.client.post(url, data=data, follow=True)
        self.assertFalse(response.serialize().find('llamadas_por_tipo.csv') > -1)

    def test_usuario_logueado_accede_a_zip_reportes_llamadas(self):
        url = reverse('zip_reportes_llamadas')
        data = {'estadisticas': json.dumps(self.estadisticas)}
        response = self.client.post(url, data=data, follow=True)
        self.assertTrue(response.serialize().find('llamadas_por_tipo.csv') > -1)
        self.assertTrue(response.serialize().find('llamadas_por_campana.csv') > -1)
        self.assertTrue(response.serialize().find('tipos_de_llamada_manual.csv') > -1)
        self.assertTrue(response.serialize().find('tipos_de_llamada_dialer.csv') > -1)
        self.assertTrue(response.serialize().find('tipos_de_llamada_entrante.csv') > -1)
        self.assertTrue(response.serialize().find('tipos_de_llamada_preview.csv') > -1)

    def test_usuario_no_logueado_no_accede_a_zip_reportes_llamadas(self):
        url = reverse('zip_reportes_llamadas')
        data = {'estadisticas': json.dumps(self.estadisticas)}
        self.client.logout()
        response = self.client.post(url, data=data, follow=True)
        self.assertFalse(response.serialize().find('total_llamadas.csv') > -1)

    def test_usuario_logueado_con_mal_parametro_tira_400_zip(self):
        url = reverse('zip_reportes_llamadas')
        data = {'estadisticas': self.estadisticas}
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, u'400.html')


class DatosPorFechaReporteLlamadasTests(BaseReporteDeLlamadasTests):

    def test_llamadas_de_tipo_por_fecha(self):
        tipo = Campana.TYPE_ENTRANTE_DISPLAY
        campana = self.entrante
        generador = GeneradorDeLlamadaLogs()
        for i in range(5):
            generador.generar_log(campana, False, 'COMPLETECALLER', '123',
                                  self.agente1, bridge_wait_time=4, time=self.durante)
        for i in range(3):
            generador.generar_log(campana, False, 'COMPLETEAGENT', '123',
                                  self.agente1, bridge_wait_time=6)

        str_ayer = self.durante.strftime('%d-%m-%Y')
        str_hoy = self.hasta.strftime('%d-%m-%Y')

        self.hasta = now()
        reporte = ReporteDeLlamadas(self.desde, self.hasta, True, self.supervisor.user)
        self.assertIn(tipo, reporte.estadisticas_por_fecha['llamadas_por_tipo'])
        self.assertIn(str_ayer, reporte.estadisticas_por_fecha['llamadas_por_tipo'][tipo])
        self.assertIn(str_hoy, reporte.estadisticas_por_fecha['llamadas_por_tipo'][tipo])
        datos_ayer = reporte.estadisticas_por_fecha['llamadas_por_tipo'][tipo][str_ayer]
        datos_hoy = reporte.estadisticas_por_fecha['llamadas_por_tipo'][tipo][str_hoy]
        self.assertEqual(datos_ayer['atendidas'], 5)
        self.assertEqual(datos_ayer['total'], 5)
        self.assertEqual(datos_hoy['atendidas'], 3)
        self.assertEqual(datos_hoy['total'], 3)

        self.assertIn(tipo, reporte.estadisticas_por_fecha['tipos_de_llamada_por_campana'])
        tipos_por_campana = reporte.estadisticas_por_fecha['tipos_de_llamada_por_campana'][tipo]
        self.assertIn(str_ayer, tipos_por_campana[self.entrante.id])
        self.assertIn(str_hoy, tipos_por_campana[self.entrante.id])
        datos_ayer = tipos_por_campana[self.entrante.id][str_ayer]
        datos_hoy = tipos_por_campana[self.entrante.id][str_hoy]
        self.assertEqual(datos_ayer['atendidas'], 5)
        self.assertEqual(datos_ayer['recibidas'], 5)
        self.assertEqual(datos_ayer['t_espera_conexion'], 4)
        self.assertEqual(datos_hoy['atendidas'], 3)
        self.assertEqual(datos_hoy['recibidas'], 3)
        self.assertEqual(datos_hoy['t_espera_conexion'], 6)
