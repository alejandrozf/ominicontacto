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
from __future__ import unicode_literals

import json
from django.utils.translation import ugettext as _
from django.urls import reverse

from ominicontacto_app.models import Contacto, AgenteEnContacto
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.tests.factories import (
    SistemaExternoFactory, QueueMemberFactory, CampanaFactory, QueueFactory
)

from ominicontacto_app.models import AgenteEnSistemaExterno, Campana, User


class APITest(OMLBaseTest):
    """ Tests para la api de Click2Call"""

    def setUp(self):
        super(APITest, self).setUp()

        self.sistema_externo = SistemaExternoFactory()
        # self.sistema_externo_2 = SistemaExternoFactory()
        usr_supervisor = self.crear_user_supervisor(username='sup1')
        self.crear_supervisor_profile(user=usr_supervisor, rol=User.SUPERVISOR)
        usr_supervisor2 = self.crear_user_supervisor(username='sup2')
        self.crear_supervisor_profile(user=usr_supervisor2, rol=User.SUPERVISOR)

        usr_agente = self.crear_user_agente(username='agente1')
        self.agente = self.crear_agente_profile(usr_agente)

        self.client.login(username=usr_agente.username, password=PASSWORD)

        self.agente_2 = self.crear_agente_profile()

        bd_contacto = self.crear_base_datos_contacto(cant_contactos=3, columna_id_externo='id_ext')
        self.campana = self.crear_campana_manual(cant_contactos=3,
                                                 user=usr_supervisor,
                                                 bd_contactos=bd_contacto)
        self.campana.sistema_externo = self.sistema_externo
        self.campana.id_externo = 'c1'
        self.campana.estado = Campana.ESTADO_ACTIVA
        self.campana.save()

        # self.campana_2 = self.crear_campana_manual(cant_contactos=3,
        #                                            user=usr_supervisor)
        # self.campana_2.sistema_externo = self.sistema_externo
        # self.campana_2.estado = Campana.ESTADO_ACTIVA
        # self.campana_2.save()

        # queue_campana = QueueFactory(campana=self.campana)
        QueueMemberFactory.create(member=self.agente, queue_name=self.campana.queue_campana)
        # QueueMemberFactory.create(member=self.agente_2, queue_name=self.campana_2.queue_campana)

        agente_externo_1 = AgenteEnSistemaExterno(agente=self.agente,
                                                  sistema_externo=self.sistema_externo,
                                                  id_externo_agente='id_ag_1')
        agente_externo_1.save()
        # agente_externo_2 = AgenteEnSistemaExterno(agente=self.agente_2,
        #                                           sistema_externo=self.sistema_externo_2,
        #                                           id_externo_agente='id_ag_2')
        # agente_externo_2.save()
        self.contacto_1 = self.campana.bd_contacto.contactos.first()
        self.contacto_1.id_externo = 'c1'
        self.contacto_1.save()

        self.contacto_2 = bd_contacto.contactos.first()

        self.metadata_ok = {
            u'status': u'OK',
            u'main_phone': u'TELEFONO',
            u'external_id': u'id_ext',
            u'fields': [u'TELEFONO', u'NOMBRE', u'FECHA', u'HORA', u'id_ext']
        }

        self.post_data_contacto = {
            'idCampaign': str(self.campana.id),
            'TELEFONO': '3511111111',
            'NOMBRE': 'nombre',
            'FECHA': '2000/01/01',
            'HORA': '16:22',
        }

        self.post_data_contacto_externo = {
            'idExternalSystem': str(self.sistema_externo.id),
            'idCampaign': self.campana.id_externo,
            'TELEFONO': '3511111111',
            'NOMBRE': 'nombre',
            'FECHA': '2000/01/01',
            'HORA': '16:22',
            'id_ext': 'c2',
        }

        self.contacto_ok = {
            u'status': u'OK',
            u'message': _(u'Contacto agregado'),
            u'contacto': {
                u'HORA': u'16:22',
                u'NOMBRE': u'nombre',
                u'FECHA': u'2000/01/01',
                u'TELEFONO': u'3511111111',
                u'id_ext': None
            },
            u'id': 0
        }


class DatabaseMetadataTest(APITest):
    URL = reverse('api_campaign_database_metadata')

    def test_usuario_no_loggeado(self):
        self.client.logout()
        response = self.client.post(self.URL, {'idCampaign': str(self.campana.id), })
        self.assertEqual(response.status_code, 403)

    def test_usuario_supervisor_no_asignado(self):
        self.client.logout()
        self.client.login(username='sup2', password=PASSWORD)
        response = self.client.post(self.URL, {'idCampaign': str(self.campana.id), })
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.content)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(response_json['errors']['idCampaign'],
                         [_('No tiene permiso para editar la campaña.')])

    def test_usuario_supervisor_asignado(self):
        self.client.logout()
        self.client.login(username='sup1', password=PASSWORD)
        response = self.client.post(self.URL, {'idCampaign': str(self.campana.id), })
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertEqual(response_json, self.metadata_ok)

    def test_usuario_agente_no_asignado(self):
        self.client.logout()
        self.client.login(username=self.agente_2.user.username, password=PASSWORD)
        response = self.client.post(self.URL, {'idCampaign': str(self.campana.id), })
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.content)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(response_json['errors']['idCampaign'],
                         [_('No tiene permiso para editar la campaña.')])

    def test_id_sitio_externo_inexistente(self):
        id_externo = str(self.sistema_externo.id) + '1'
        response = self.client.post(self.URL, {'idCampaign': 'c1',
                                               'idExternalSystem': id_externo})
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(response_json['errors']['idExternalSystem'],
                         [_('Sistema externo inexistente.')])

    def test_id_campana_oml_inexistente(self):
        response = self.client.post(self.URL, {'idCampaign': str(self.campana.id) + '1', })
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.content)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(response_json['errors']['idCampaign'],
                         [_('Campaña inexistente.')])

    def test_id_campana_oml_invalido(self):
        response = self.client.post(self.URL, {'idCampaign': str(self.campana.id) + 'xxx', })
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.content)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(response_json['errors']['idCampaign'],
                         [_('Debe indicar un idCampaign válido.')])

    def test_id_campana_sitio_externo_inexistente(self):
        response = self.client.post(self.URL, {'idCampaign': 'c11',
                                               'idExternalSystem': str(self.sistema_externo.id)})
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.content)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(response_json['errors']['idCampaign'],
                         [_('Campaña inexistente.')])

    def test_usuario_agente_id_sitio_externo_ok(self):
        response = self.client.post(self.URL, {'idCampaign': 'c1',
                                               'idExternalSystem': str(self.sistema_externo.id)})
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertEqual(response_json, self.metadata_ok)

    def test_usuario_agente_id_oml_ok(self):
        response = self.client.post(self.URL, {'idCampaign': str(self.campana.id), })
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertEqual(response_json, self.metadata_ok)


class CrearContactoTest(APITest):
    URL = reverse('api_new_contact')

    def test_usuario_no_loggeado(self):
        self.client.logout()
        response = self.client.post(self.URL, json.dumps(self.post_data_contacto),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_usuario_supervisor_no_asignado(self):
        self.client.logout()
        self.client.login(username='sup2', password=PASSWORD)
        response = self.client.post(self.URL, json.dumps(self.post_data_contacto),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.content)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(response_json['errors']['idCampaign'],
                         [_('No tiene permiso para editar la campaña.')])

    def test_usuario_supervisor_asignado(self):
        self.client.logout()
        self.client.login(username='sup1', password=PASSWORD)
        cant_inicial = Contacto.objects.count()
        response = self.client.post(self.URL, json.dumps(self.post_data_contacto),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contacto.objects.count(), cant_inicial + 1)
        response_json = response.json()
        self.contacto_ok['id'] = Contacto.objects.last().id
        self.assertEqual(response_json, self.contacto_ok)

    def test_usuario_agente_no_asignado(self):
        self.client.logout()
        self.client.login(username=self.agente_2.user.username, password=PASSWORD)
        response = self.client.post(self.URL, json.dumps(self.post_data_contacto),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.content)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(response_json['errors']['idCampaign'],
                         [_('No tiene permiso para editar la campaña.')])

    def test_id_sitio_externo_inexistente(self):
        self.post_data_contacto_externo['idExternalSystem'] = str(self.sistema_externo.id) + '1'
        response = self.client.post(self.URL, json.dumps(self.post_data_contacto_externo),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(response_json['errors']['idExternalSystem'],
                         [_('Sistema externo inexistente.')])

    def test_id_campana_oml_inexistente(self):
        self.post_data_contacto_externo['idCampaign'] = str(self.campana.id) + '1'
        response = self.client.post(self.URL, json.dumps(self.post_data_contacto_externo),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.content)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(response_json['errors']['idCampaign'],
                         [_('Campaña inexistente.')])

    def test_id_campana_oml_invalido(self):
        self.post_data_contacto['idCampaign'] = str(self.campana.id) + 'xxx'
        response = self.client.post(self.URL, json.dumps(self.post_data_contacto),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.content)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(response_json['errors']['idCampaign'],
                         [_('Debe indicar un idCampaign válido.')])

    def test_id_campana_sitio_externo_inexistente(self):
        self.post_data_contacto_externo['idCampaign'] = self.campana.id_externo + 'x'
        response = self.client.post(self.URL, json.dumps(self.post_data_contacto_externo),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.content)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(response_json['errors']['idCampaign'],
                         [_('Campaña inexistente.')])

    def test_usuario_agente_id_sitio_externo_repetido(self):
        self.post_data_contacto_externo['id_ext'] = self.contacto_1.id_externo
        response = self.client.post(self.URL, json.dumps(self.post_data_contacto_externo),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(response_json['errors']['id_ext'],
                         [_('Ya existe un contacto con ese id externo en la base de datos')])

    def test_usuario_agente_id_sitio_externo_ok(self):
        cant_inicial = Contacto.objects.count()
        response = self.client.post(self.URL, json.dumps(self.post_data_contacto_externo),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contacto.objects.count(), cant_inicial + 1)
        self.contacto_ok['contacto']['id_ext'] = 'c2'
        self.contacto_ok['id'] = Contacto.objects.last().id
        response_json = response.json()
        self.assertEqual(response_json, self.contacto_ok)

    def test_usuario_agente_id_oml_ok(self):
        cant_inicial = Contacto.objects.count()
        response = self.client.post(self.URL, json.dumps(self.post_data_contacto),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contacto.objects.count(), cant_inicial + 1)
        self.contacto_ok['id'] = Contacto.objects.last().id
        response_json = response.json()
        self.assertEqual(response_json, self.contacto_ok)

    def test_error_sin_telefono(self):
        self.post_data_contacto.pop('TELEFONO')
        response = self.client.post(self.URL, json.dumps(self.post_data_contacto),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(response_json['errors'], 'TELEFONO')
        self.assertEqual(response_json['message'],
                         _('El campo es obligatorio'))

    def test_error_campo_erroneo(self):
        self.post_data_contacto['TELEFONO2'] = '123'
        response = self.client.post(self.URL, json.dumps(self.post_data_contacto),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(response_json['errors'], ['TELEFONO2'])
        self.assertEqual(response_json['message'],
                         _('Se recibieron campos incorrectos'))

    def test_usuario_agente_id_sitio_externo_sin_id_ext_ok(self):
        cant_inicial = Contacto.objects.count()
        self.post_data_contacto_externo.pop('id_ext')
        response = self.client.post(self.URL, json.dumps(self.post_data_contacto_externo),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contacto.objects.count(), cant_inicial + 1)
        self.contacto_ok['id'] = Contacto.objects.last().id
        response_json = response.json()
        self.assertEqual(response_json, self.contacto_ok)
        response = self.client.post(self.URL, json.dumps(self.post_data_contacto_externo),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contacto.objects.count(), cant_inicial + 2)
        self.contacto_ok['id'] = Contacto.objects.last().id
        response_json = response.json()
        self.assertEqual(response_json, self.contacto_ok)

    def test_creacion_usuario_preview_por_agente_crea_agente_en_contacto(self):
        campana = CampanaFactory(type=Campana.TYPE_PREVIEW, estado=Campana.ESTADO_ACTIVA,
                                 bd_contacto=self.campana.bd_contacto)
        QueueFactory(campana=campana)
        QueueMemberFactory.create(member=self.agente, queue_name=campana.queue_campana)
        post_data = self.post_data_contacto
        post_data['idCampaign'] = str(campana.id)
        response = self.client.post(self.URL, json.dumps(post_data),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        agente_en_contacto = AgenteEnContacto.objects.filter(
            campana_id=campana.id, contacto_id=response.json()['id'],
            agente_id=self.agente.id, es_originario=False)
        self.assertEqual(agente_en_contacto.count(), 1)

    def test_creacion_usuario_preview_por_supervisor_crea_agente_en_contacto(self):
        usr_supervisor = self.campana.reported_by
        campana = CampanaFactory(type=Campana.TYPE_PREVIEW, estado=Campana.ESTADO_ACTIVA,
                                 bd_contacto=self.campana.bd_contacto,
                                 reported_by=usr_supervisor)
        campana.supervisors.add(usr_supervisor)
        QueueFactory(campana=campana)
        QueueMemberFactory.create(member=self.agente, queue_name=campana.queue_campana)
        self.client.logout()
        self.client.login(username=usr_supervisor.username, password=PASSWORD)

        post_data = self.post_data_contacto
        post_data['idCampaign'] = str(campana.id)
        response = self.client.post(self.URL, json.dumps(post_data),
                                    format='json', content_type='application/json')

        self.assertEqual(response.status_code, 200)
        agente_en_contacto = AgenteEnContacto.objects.filter(
            campana_id=campana.id, contacto_id=response.json()['id'],
            agente_id=-1, es_originario=True)
        self.assertEqual(agente_en_contacto.count(), 1)
