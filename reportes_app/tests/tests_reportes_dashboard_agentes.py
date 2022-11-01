# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3, as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

"""
Tests relacionados con la lista de contactos de los Agentes
"""
from __future__ import unicode_literals

from django.utils.timezone import now, timedelta

from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.tests.factories import (CampanaFactory, UserFactory,
                                               ActividadAgenteLogFactory, PausaFactory)
from ominicontacto_app.models import Campana, Pausa

from reportes_app.tests.utiles import GeneradorDeLlamadaLogs
from reportes_app.reportes.reporte_estadisticas_agentes import ReporteEstadisticasDiariaAgente


class DashboardAgenteTests(OMLBaseTest):

    PWD = u'admin123'

    def setUp(self):
        self.usuario_admin_supervisor = UserFactory(is_staff=True, is_supervisor=True)
        self.usuario_admin_supervisor.set_password(self.PWD)
        self.usuario_admin_supervisor.save()
        super(DashboardAgenteTests, self).setUp()
        self.agente_profile = self.crear_agente_profile()
        self.campana_activa = CampanaFactory.create(
            estado=Campana.ESTADO_ACTIVA, type=Campana.TYPE_PREVIEW)
        self.generador = GeneradorDeLlamadaLogs()

    def test_se_muestran_estadisticas_del_dia_actual(self):
        ayer = now() - timedelta(days=1)
        self.generador.generar_log(self.campana_activa, False, 'COMPLETEAGENT', '35100001111',
                                   agente=self.agente_profile, contacto=None, bridge_wait_time=-1,
                                   duracion_llamada=10, archivo_grabacion='', time=ayer)
        self.generador.generar_log(self.campana_activa, False, 'COMPLETEOUTNUM', '35100001112',
                                   agente=self.agente_profile, contacto=None, bridge_wait_time=-1,
                                   duracion_llamada=10, archivo_grabacion='', time=None)
        reporte = ReporteEstadisticasDiariaAgente()
        logs_agente_reporte = reporte.estadisticas[self.agente_profile.pk]['logs']
        self.assertEqual(len(logs_agente_reporte), 1)

    def test_se_muestran_las_ultimas_10_llamadas(self):
        numero_llamada_excluida = '3510000111'
        ahora = now()
        self.generador.generar_log(self.campana_activa, False, 'COMPLETEAGENT',
                                   numero_llamada_excluida,
                                   agente=self.agente_profile, contacto=None, bridge_wait_time=-1,
                                   duracion_llamada=10, archivo_grabacion='',
                                   time=ahora)
        for i in range(1, 11):
            time_llamada = ahora + timedelta(minutes=i)
            self.generador.generar_log(self.campana_activa, False, 'COMPLETEAGENT', '35100213121',
                                       agente=self.agente_profile, contacto=None,
                                       bridge_wait_time=-1,
                                       duracion_llamada=10, archivo_grabacion='', time=time_llamada)
        reporte = ReporteEstadisticasDiariaAgente()
        reporte_agente = reporte.estadisticas[self.agente_profile.pk]
        llamada_excluida_encontrada = False
        for log in reporte_agente['logs']:
            if log['phone'] == numero_llamada_excluida:
                llamada_excluida_encontrada = True
        self.assertFalse(llamada_excluida_encontrada)

    def test_se_muestra_el_tiempo_de_sesion_correctamente(self):
        horas_sesion = 1
        tiempo_inicial = now()
        ActividadAgenteLogFactory.create(
            event='UNPAUSEALL', agente_id=self.agente_profile.id, time=tiempo_inicial)
        tiempo_removemember_1 = tiempo_inicial + timedelta(microseconds=20000)
        ActividadAgenteLogFactory.create(
            event='REMOVEMEMBER', agente_id=self.agente_profile.id, time=tiempo_removemember_1)
        tiempo_addmember = tiempo_removemember_1 + timedelta(microseconds=3000)
        ActividadAgenteLogFactory.create(
            time=tiempo_addmember, event='ADDMEMBER', agente_id=self.agente_profile.id,
            pausa_id='')
        tiempo_removemember_2 = tiempo_addmember + timedelta(hours=horas_sesion)
        ActividadAgenteLogFactory.create(
            time=tiempo_removemember_2, event='REMOVEMEMBER', agente_id=self.agente_profile.id,
            pausa_id='')
        reporte = ReporteEstadisticasDiariaAgente()
        reporte_agente = reporte.estadisticas[self.agente_profile.pk]
        self.assertEqual(reporte_agente['tiempos'].sesion, timedelta(hours=horas_sesion))

    def test_se_muestran_los_tiempos_de_pausa_correctamente(self):
        horas_sesion = 1
        tiempo_inicial = now()
        pausa1 = PausaFactory(tipo=Pausa.TIPO_PRODUCTIVA)
        pausa2 = PausaFactory(tipo=Pausa.TIPO_RECREATIVA)
        ActividadAgenteLogFactory.create(
            event='UNPAUSEALL', agente_id=self.agente_profile.id, time=tiempo_inicial)
        tiempo_removemember_1 = tiempo_inicial + timedelta(microseconds=20000)
        ActividadAgenteLogFactory.create(
            event='REMOVEMEMBER', agente_id=self.agente_profile.id, time=tiempo_removemember_1)
        tiempo_addmember = tiempo_removemember_1 + timedelta(microseconds=3000)
        ActividadAgenteLogFactory.create(
            time=tiempo_addmember, event='ADDMEMBER', agente_id=self.agente_profile.id,
            pausa_id='')
        tiempo_inicio_pausa_1 = tiempo_addmember + timedelta(minutes=2)
        ActividadAgenteLogFactory.create(
            time=tiempo_inicio_pausa_1, event='PAUSEALL', agente_id=self.agente_profile.id,
            pausa_id=pausa1.id)
        tiempo_final_pausa_1 = tiempo_inicio_pausa_1 + timedelta(minutes=2)
        ActividadAgenteLogFactory.create(
            time=tiempo_final_pausa_1, event='UNPAUSEALL', agente_id=self.agente_profile.id,
            pausa_id=pausa1.id)
        tiempo_inicio_pausa_2 = tiempo_final_pausa_1 + timedelta(minutes=2)
        ActividadAgenteLogFactory.create(
            time=tiempo_inicio_pausa_2, event='PAUSEALL', agente_id=self.agente_profile.id,
            pausa_id=pausa2.id)
        tiempo_final_pausa_2 = tiempo_inicio_pausa_2 + timedelta(minutes=2)
        ActividadAgenteLogFactory.create(
            time=tiempo_final_pausa_2, event='UNPAUSEALL', agente_id=self.agente_profile.id,
            pausa_id=pausa2.id)
        tiempo_removemember_2 = tiempo_final_pausa_2 + timedelta(hours=horas_sesion)
        ActividadAgenteLogFactory.create(
            time=tiempo_removemember_2, event='REMOVEMEMBER', agente_id=self.agente_profile.id,
            pausa_id='')
        reporte = ReporteEstadisticasDiariaAgente()
        reporte_agente = reporte.estadisticas[self.agente_profile.pk]
        self.assertEqual(reporte_agente['tiempos'].pausa, timedelta(minutes=4))
        self.assertEqual(reporte_agente['tiempos'].pausa_recreativa, timedelta(minutes=2))
