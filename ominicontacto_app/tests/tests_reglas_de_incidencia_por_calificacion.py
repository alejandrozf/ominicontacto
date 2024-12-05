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
Tests sobre los procesos realicionados con la calificaciones de los contactos de las campañas
"""
import json
from mock import patch

from django.urls import reverse

from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.tests.factories import (CampanaFactory, QueueFactory, QueueMemberFactory,
                                               ContactoFactory,
                                               NombreCalificacionFactory,
                                               OpcionCalificacionFactory,
                                               FormularioFactory, FieldFormularioFactory)

from ominicontacto_app.models import (
    ReglaIncidenciaPorCalificacion, OpcionCalificacion, Campana
)
from reportes_app.models import LlamadaLog


class ReglaIncidenciaPorCalificacionTests(OMLBaseTest):

    def setUp(self):
        super(ReglaIncidenciaPorCalificacionTests, self).setUp()

        self.admin = self.crear_administrador()
        self.client.login(username=self.admin.username, password=PASSWORD)

        self.formulario = FormularioFactory()
        self.campo_formulario = FieldFormularioFactory(formulario=self.formulario)
        self.campana = CampanaFactory.create(type=Campana.TYPE_DIALER)
        self.nombre_opcion_1 = NombreCalificacionFactory.create()
        self.opcion_calificacion_1 = OpcionCalificacionFactory.create(
            campana=self.campana, nombre=self.nombre_opcion_1.nombre,
            tipo=OpcionCalificacion.GESTION, formulario=self.formulario)
        self.campana.opciones_calificacion.add(self.opcion_calificacion_1)
        self.nombre_opcion_2 = NombreCalificacionFactory.create()
        self.opcion_calificacion_2 = OpcionCalificacionFactory.create(
            campana=self.campana, nombre=self.nombre_opcion_2.nombre,
            tipo=OpcionCalificacion.NO_ACCION)
        self.campana.opciones_calificacion.add(self.opcion_calificacion_2)
        self.contacto = ContactoFactory.create()
        self.campana.bd_contacto.contactos.add(self.contacto)

        self.campana_extra = CampanaFactory.create(type=Campana.TYPE_DIALER)
        self.nombre_opcion_extra = NombreCalificacionFactory.create()
        self.opcion_calificacion_extra = OpcionCalificacionFactory.create(
            campana=self.campana_extra, nombre=self.nombre_opcion_extra.nombre,
            tipo=OpcionCalificacion.NO_ACCION)
        self.campana_extra.opciones_calificacion.add(self.opcion_calificacion_extra)

    def test_crear_regla_view_muestra_opciones(self):
        url = reverse('disposition_incidence_create', kwargs={'pk_campana': self.campana.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = str(response.content)
        self.assertIn(self.opcion_calificacion_1.nombre, content)
        self.assertIn(self.opcion_calificacion_2.nombre, content)
        self.assertNotIn(self.opcion_calificacion_extra.nombre, content)

    @patch('ominicontacto_app.services.dialer.campana_wombat.CampanaService.reload_campana_wombat')
    @patch('ominicontacto_app.services.dialer.wombat_config.ConfigFile.write')
    @patch('ominicontacto_app.services.dialer.wombat_api.WombatAPI.update_config_wombat')
    def test_crear_regla_impacta_wombat(self, update_config_wombat, write, reload_campana):
        url = reverse('disposition_incidence_create', kwargs={'pk_campana': self.campana.id})
        post_data = {
            'opcion_calificacion': self.opcion_calificacion_1.id, 'intento_max': 5,
            'reintentar_tarde': 60, 'en_modo': ReglaIncidenciaPorCalificacion.FIXED
        }
        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        update_config_wombat.assert_called_with(
            'newcampaign_reschedule.json', 'api/edit/campaign/reschedule/?mode=E&parent={0}'.format(
                self.campana.campaign_id_wombat))
        write.assert_called()
        file_data = json.loads(write.call_args[0][0])
        regla = ReglaIncidenciaPorCalificacion.objects.get(
            opcion_calificacion=self.opcion_calificacion_1)
        expected_data = {
            "status": ReglaIncidenciaPorCalificacion.ESTADO_WOMBAT, "statusExt": regla.wombat_id,
            "maxAttempts": 5, "retryAfterS": 60, "mode": regla.get_en_modo_wombat()}
        self.assertEqual(file_data, expected_data)

    @patch('ominicontacto_app.services.dialer.campana_wombat.CampanaService.reload_campana_wombat')
    @patch('ominicontacto_app.services.dialer.wombat_api.WombatAPI.list_config_wombat')
    @patch('ominicontacto_app.services.dialer.wombat_api.WombatAPI.post_json')
    def test_borrar_regla_impacta_wombat(self, post_json, list_config_wombat, reload_campana):
        regla = ReglaIncidenciaPorCalificacion(
            opcion_calificacion=self.opcion_calificacion_1, intento_max=5, reintentar_tarde=60,
            en_modo=ReglaIncidenciaPorCalificacion.FIXED)
        regla.save()
        matching_rule = {'statusExt': regla.wombat_id, 'DATA': 'EXPECTED'}
        list_config_wombat.return_value = {
            "status": "OK",
            "results": [
                {'statusExt': regla.wombat_id + 'basura', 'DATA': 'IGNORED'},
                matching_rule
            ]
        }
        post_json.return_value = {'status': 'OK'}

        url = reverse('disposition_incidence_delete', kwargs={'pk': regla.id})
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        list_url = "api/edit/campaign/reschedule/?mode=L&parent={0}".format(
            self.campana.campaign_id_wombat)
        list_config_wombat.assert_called_with(list_url)
        post_json.assert_called_with('api/edit/campaign/reschedule/?mode=D&parent={0}'.format(
            self.campana.campaign_id_wombat), matching_rule)
        self.assertFalse(ReglaIncidenciaPorCalificacion.objects.filter(
            opcion_calificacion=self.opcion_calificacion_1).exists())

    @patch('ominicontacto_app.services.dialer.campana_wombat.CampanaService.reload_campana_wombat')
    @patch('ominicontacto_app.services.dialer.wombat_api.WombatAPI.list_config_wombat')
    @patch('ominicontacto_app.services.dialer.wombat_api.WombatAPI.post_json')
    def test_editar_regla_impacta_wombat(self, post_json, list_config_wombat, reload_campana):
        regla = ReglaIncidenciaPorCalificacion(
            opcion_calificacion=self.opcion_calificacion_1, intento_max=5, reintentar_tarde=60,
            en_modo=ReglaIncidenciaPorCalificacion.FIXED)
        regla.save()
        matching_rule = {'statusExt': regla.wombat_id, 'DATA': 'EXPECTED'}
        list_config_wombat.return_value = {
            "status": "OK",
            "results": [
                {'statusExt': regla.wombat_id + 'basura', 'DATA': 'IGNORED'},
                matching_rule
            ]
        }
        post_json.return_value = {'status': 'OK'}

        url = reverse('disposition_incidence_edit', kwargs={'pk': regla.id})
        post_data = {
            'opcion_calificacion': self.opcion_calificacion_2.id, 'intento_max': 8,
            'reintentar_tarde': 120, 'en_modo': ReglaIncidenciaPorCalificacion.MULT
        }

        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        list_url = "api/edit/campaign/reschedule/?mode=L&parent={0}".format(
            self.campana.campaign_id_wombat)
        list_config_wombat.assert_called_with(list_url)
        matching_rule['statusExt'] = regla.wombat_id
        matching_rule['maxAttempts'] = 8
        matching_rule['retryAfterS'] = 120
        matching_rule['mode'] = 'MULT'

        post_json.assert_called_with('api/edit/campaign/reschedule/?mode=E&parent={0}'.format(
            self.campana.campaign_id_wombat), matching_rule)
        self.assertFalse(ReglaIncidenciaPorCalificacion.objects.filter(
            opcion_calificacion=self.opcion_calificacion_1).exists())

    @patch('notification_app.notification.RedisStreamNotifier.send')
    @patch('ominicontacto_app.services.dialer.wombat_api.WombatAPI.set_call_ext_status')
    def test_calificar_usando_opcion_con_regla_de_incidencia_impacta_wombat(
            self, set_call_ext_status, send):
        agente = self.crear_agente_profile()
        self.client.logout()
        self.client.login(username=agente.user.username, password=PASSWORD)
        queue = QueueFactory.create(campana=self.campana)
        QueueMemberFactory.create(member=agente, queue_name=queue)

        dialer_call_id = '12345'
        regla = ReglaIncidenciaPorCalificacion(
            opcion_calificacion=self.opcion_calificacion_1, intento_max=5, reintentar_tarde=60,
            en_modo=ReglaIncidenciaPorCalificacion.FIXED)
        regla.save()
        call_data = {"id_campana": self.campana.id,
                     "campana_type": self.campana.type,
                     "telefono": "3512349992",
                     "call_id": '123456789',
                     "call_type": LlamadaLog.LLAMADA_DIALER,
                     "id_contacto": self.contacto.id,
                     "rec_filename": "",
                     "call_wait_duration": "",
                     'dialer_id': dialer_call_id, }
        url = reverse('calificar_llamada', kwargs={'call_data_json': json.dumps(call_data)})

        post_data = {
            'opcion_calificacion': self.opcion_calificacion_1.id,
            'contacto_form-telefono': self.contacto.telefono,
        }
        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        send.assert_called_with('calification', agente.id)

        url_notify = '/api/calls/?op=extstatus&wombatid={0}&status={1}'.format(
            dialer_call_id, regla.wombat_id)
        set_call_ext_status.assert_called_with(url_notify)
