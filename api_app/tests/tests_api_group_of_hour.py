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
from __future__ import unicode_literals

import json
from mock import patch
from django.utils.translation import ugettext as _
from django.urls import reverse
from configuracion_telefonia_app.models import GrupoHorario
from configuracion_telefonia_app.tests.factories import (
    GrupoHorarioFactory, ValidacionFechaHoraFactory, ValidacionTiempoFactory)
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.models import User


class APITest(OMLBaseTest):
    """Tests para los Endpoints del API Rutas Salientes"""

    def setUp(self):
        super(APITest, self).setUp()
        usr_supervisor = self.crear_user_supervisor(username='sup1')
        self.crear_supervisor_profile(user=usr_supervisor, rol=User.SUPERVISOR)
        self.client.login(username=usr_supervisor.username, password=PASSWORD)
        self.grupo_horario = GrupoHorarioFactory()
        self.grupo_horario_con_validacion = GrupoHorarioFactory()
        self.validacion_fecha_hora = ValidacionFechaHoraFactory(
            grupo_horario=self.grupo_horario_con_validacion)
        self.validacion_tiempo = ValidacionTiempoFactory(grupo_horario=self.grupo_horario)

        self.dataForm = {
            "nombre": "GrupoHorarioNew",
            "validaciones_de_tiempo": [
                {
                    "id": None,
                    "tiempo_inicial": "11:00:00",
                    "tiempo_final": "19:00:00",
                    "dia_semana_inicial": 1,
                    "dia_semana_final": 3,
                    "dia_mes_inicio": 1,
                    "dia_mes_final": 20,
                    "mes_inicio": 1,
                    "mes_final": 12
                }
            ]
        }
        self.urls_api = {
            'List': 'api_group_of_hours_list',
            'Create': 'api_group_of_hours_create',
            'Detail': 'api_group_of_hours_detail',
            'Update': 'api_group_of_hours_update',
            'Delete': 'api_group_of_hours_delete'
        }


class GrupoHorarioTest(APITest):
    def test_listar(self):
        URL = reverse(self.urls_api['List'])
        response = self.client.get(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se obtuvieron los grupos horarios '
              'de forma exitosa'))

    def test_detalle(self):
        URL = reverse(
            self.urls_api['Detail'],
            args=[self.grupo_horario.pk, ])
        response = self.client.get(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['groupOfHour']['id'], self.grupo_horario.pk)
        self.assertEqual(
            response_json['groupOfHour']['nombre'],
            self.grupo_horario.nombre)
        self.assertEqual(
            response_json['message'],
            _('Se obtuvo la informacion el grupo horario '
              'de forma exitosa'))

    @patch('api_app.utils.group_of_hours.escribir_grupo_horario_config')
    @patch('configuracion_telefonia_app.regeneracion_configuracion_telefonia'
           '.SincronizadorDeConfiguracionGrupoHorarioAsterisk.regenerar_asterisk')
    def test_crear(self, regenerar_asterisk, escribir_grupo_horario_config):
        URL = reverse(self.urls_api['Create'])
        numBefore = GrupoHorario.objects.all().count()
        response = self.client.post(
            URL, json.dumps(self.dataForm),
            format='json', content_type='application/json')
        numAfter = GrupoHorario.objects.all().count()
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(numAfter, numBefore + 1)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se creo el grupo horario de forma exitosa'))

    @patch('api_app.utils.group_of_hours.eliminar_grupo_horario_config')
    @patch('configuracion_telefonia_app.regeneracion_configuracion_telefonia'
           '.SincronizadorDeConfiguracionGrupoHorarioAsterisk'
           '.eliminar_y_regenerar_asterisk')
    def test_eliminar(self, eliminar_y_regenerar_asterisk, eliminar_grupo_horario_config):
        pk = self.grupo_horario.pk
        URL = reverse(self.urls_api['Delete'], args=[pk, ])
        numBefore = GrupoHorario.objects.all().count()
        response = self.client.delete(URL, follow=True)
        numAfter = GrupoHorario.objects.all().count()
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(numAfter, numBefore - 1)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se elimino el grupo horario de forma exitosa'))

    def test_eliminar_con_validacion_fecha_y_hora(self):
        pk = self.grupo_horario_con_validacion.pk
        URL = reverse(self.urls_api['Delete'], args=[pk, ])
        response = self.client.delete(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(
            response_json['message'],
            _('No está permitido eliminar un '
              'grupo horario asociado a Validacion Fecha Hora'))

    @patch('api_app.utils.group_of_hours.escribir_grupo_horario_config')
    @patch('configuracion_telefonia_app.regeneracion_configuracion_telefonia'
           '.SincronizadorDeConfiguracionGrupoHorarioAsterisk.regenerar_asterisk')
    def test_actualizar(self, regenerar_asterisk, escribir_grupo_horario_config):
        pk = self.grupo_horario.pk
        URL = reverse(self.urls_api['Update'], args=[pk, ])
        request_data = {
            "nombre": "GrupoHorarioUpdate",
            "validaciones_de_tiempo": [
                {
                    "id": None,
                    "tiempo_inicial": "11:00:00",
                    "tiempo_final": "19:00:00",
                    "dia_semana_inicial": 1,
                    "dia_semana_final": 3,
                    "dia_mes_inicio": 1,
                    "dia_mes_final": 20,
                    "mes_inicio": 1,
                    "mes_final": 12
                }
            ]
        }
        response = self.client.put(
            URL, json.dumps(request_data),
            format='json', content_type='application/json')
        grupo_horario = GrupoHorario.objects.get(pk=pk)
        reqTimeValidation = request_data['validaciones_de_tiempo'][0]
        timeValidation = grupo_horario.validaciones_tiempo.first()
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(grupo_horario.nombre, request_data['nombre'])
        self.assertEqual(timeValidation.dia_semana_inicial, reqTimeValidation['dia_semana_inicial'])
        self.assertEqual(timeValidation.dia_semana_final, reqTimeValidation['dia_semana_final'])
        self.assertEqual(timeValidation.dia_mes_inicio, reqTimeValidation['dia_mes_inicio'])
        self.assertEqual(timeValidation.dia_mes_final, reqTimeValidation['dia_mes_final'])
        self.assertEqual(timeValidation.mes_inicio, reqTimeValidation['mes_inicio'])
        self.assertEqual(timeValidation.mes_final, reqTimeValidation['mes_final'])
        self.assertEqual(
            response_json['message'],
            _('Se actualizo el grupo horario de forma exitosa'))
