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

"""
Tests relacionados con la lista de contactos de los Agentes
"""
from __future__ import unicode_literals

import json
from mock import patch
from django.utils.translation import ugettext_lazy as _

from django.core.urlresolvers import reverse

from ominicontacto_app.tests.factories import (CampanaFactory, ContactoFactory, QueueFactory,
                                               QueueMemberFactory, AgenteEnContactoFactory)
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.models import AgenteEnContacto, Campana


class AsignacionDeContactosPreviewTests(OMLBaseTest):

    def setUp(self):
        self.agente_1 = self.crear_agente_profile()
        self.agente_2 = self.crear_agente_profile()
        self.supervisor = self.crear_supervisor_profile()
        self.campana_preview = CampanaFactory.create(
            type=Campana.TYPE_PREVIEW, tiempo_desconexion=2, estado=Campana.ESTADO_ACTIVA)
        QueueFactory.create(campana=self.campana_preview)
        self._hacer_miembro(self.agente_1, self.campana_preview)
        self._hacer_miembro(self.agente_2, self.campana_preview)
        self.contacto_1 = ContactoFactory.create(bd_contacto=self.campana_preview.bd_contacto)
        self.contacto_2 = ContactoFactory.create(bd_contacto=self.campana_preview.bd_contacto)
        self.campana_preview.establecer_valores_iniciales_agente_contacto()
        self.client.login(username=self.agente_1.user.username, password=PASSWORD)

    def _hacer_miembro(self, agente, campana):
        QueueMemberFactory.create(
            member=agente, queue_name=campana.queue_campana,
            id_campana='{0}_{1}'.format(campana.pk, campana.nombre))

    def test_valida_contacto_no_asignado_devuelve_false(self):
        # Contacto 1 no esta reservado
        url = reverse('validar_contacto_asignado')
        post_data = {'pk_campana': self.campana_preview.id,
                     'pk_contacto': self.contacto_1.id,
                     'pk_agente': self.agente_1.id}
        response = self.client.post(url, post_data, follow=True)
        resultado = json.loads(response.content)
        self.assertEqual(resultado['contacto_asignado'], False)

    def test_reserva_de_contacto_otorga_uno_libre(self):
        # Pido un contacto.
        url = reverse('campana_preview_dispatcher', args=[self.campana_preview.pk])
        response = self.client.post(url, follow=True)
        resultado = json.loads(response.content)
        self.assertEqual(resultado['result'], 'OK')
        self.assertEqual(resultado['code'], 'contacto-entregado')
        id_contacto = resultado['contacto_id']
        self.assertEqual(response.status_code, 200)

        # Contacto reservado
        self.assertTrue(AgenteEnContacto.objects.filter(agente_id=self.agente_1.id,
                        contacto_id=id_contacto,
                        campana_id=self.campana_preview.id,
                        estado=AgenteEnContacto.ESTADO_ENTREGADO).exists())

        # El otro contacto no esta reservado
        contacto_id_2 = self.contacto_1.id
        if id_contacto == self.contacto_1.id:
            contacto_id_2 = self.contacto_2.id
        self.assertTrue(AgenteEnContacto.objects.filter(contacto_id=contacto_id_2,
                        campana_id=self.campana_preview.id,
                        estado=AgenteEnContacto.ESTADO_INICIAL).exists())

    def test_reserva_de_contacto_devuelve_siempre_contacto_asignado_al_agente(self):
        AgenteEnContacto.objects.filter(contacto_id=self.contacto_1.id).update(
            agente_id=self.agente_1.id, estado=AgenteEnContacto.ESTADO_ASIGNADO)
        # Pido un contacto.
        url = reverse('campana_preview_dispatcher', args=[self.campana_preview.pk])
        response = self.client.post(url, follow=True)
        resultado = json.loads(response.content)
        self.assertEqual(resultado['result'], 'OK')
        self.assertEqual(resultado['code'], 'contacto-asignado')
        self.assertEqual(self.contacto_1.id, resultado['contacto_id'])
        self.assertEqual(response.status_code, 200)

        # Contacto sigue asignado
        self.assertTrue(AgenteEnContacto.objects.filter(agente_id=self.agente_1.id,
                        contacto_id=self.contacto_1.id,
                        campana_id=self.campana_preview.id,
                        estado=AgenteEnContacto.ESTADO_ASIGNADO).exists())

    @patch('ominicontacto_app.views_agente.LlamarContactoView._call_originate')
    def test_c2c_con_reserva_asigna_de_contacto(self, _call_originate):
        # Al llamar contacto reservado asigna el contacto
        AgenteEnContacto.objects.filter(contacto_id=self.contacto_1.id).update(
            agente_id=self.agente_1.id, estado=AgenteEnContacto.ESTADO_ENTREGADO)

        post_data = {'pk_campana': self.campana_preview.id,
                     'pk_agente': self.agente_1.id,
                     'pk_contacto': self.contacto_1.id,
                     'click2call_type': 'preview',
                     'tipo_campana': '',
                     'campana_nombre': ''}
        response = self.client.post(reverse('agente_llamar_contacto'), post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(_call_originate.called)

        self.assertTrue(AgenteEnContacto.objects.filter(agente_id=self.agente_1.id,
                        contacto_id=self.contacto_1.id,
                        campana_id=self.campana_preview.id,
                        estado=AgenteEnContacto.ESTADO_ASIGNADO).exists())

    @patch('ominicontacto_app.views_agente.LlamarContactoView._call_originate')
    def test_c2c_sin_reserva_de_contacto_agente_no_puede_llamar(self, _call_originate):
        # Un contacto asignado a otro agente no puede ser llamado
        post_data = {'pk_campana': self.campana_preview.id,
                     'pk_agente': self.agente_1.id,
                     'pk_contacto': self.contacto_1.id,
                     'click2call_type': 'preview',
                     'tipo_campana': '',
                     'campana_nombre': ''}
        response = self.client.post(reverse('agente_llamar_contacto'), post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(_call_originate.called)
        inicial = AgenteEnContacto.ESTADO_INICIAL
        self.assertFalse(AgenteEnContacto.objects.exclude(estado=inicial).exists())
        self.assertContains(response, u'No es posible llamar al contacto.')

    def test_agente_libera_contacto_asignado(self):
        # Un agente puede liberar un contacto asignado
        AgenteEnContacto.objects.filter(contacto_id=self.contacto_1.id).update(
            agente_id=self.agente_1.id, estado=AgenteEnContacto.ESTADO_ASIGNADO)
        post_data = {'campana_id': self.campana_preview.id}
        response = self.client.post(reverse('liberar_contacto_asignado_agente'),
                                    post_data, follow=True)
        resultado = json.loads(response.content)
        self.assertEqual(resultado['status'], 'OK')
        self.assertTrue(AgenteEnContacto.objects.filter(agente_id=-1,
                        contacto_id=self.contacto_1.id,
                        campana_id=self.campana_preview.id,
                        estado=AgenteEnContacto.ESTADO_INICIAL).exists())

    def test_agente_no_libera_contacto_asignado_a_otro(self):
        # Un agente no puede liberar un contacto asignado a otro agente
        AgenteEnContacto.objects.filter(contacto_id=self.contacto_1.id).update(
            agente_id=self.agente_2.id, estado=AgenteEnContacto.ESTADO_ASIGNADO)
        post_data = {'campana_id': self.campana_preview.id}
        response = self.client.post(reverse('liberar_contacto_asignado_agente'),
                                    post_data, follow=True)
        resultado = json.loads(response.content)
        self.assertEqual(resultado['status'], 'ERROR')
        self.assertTrue(AgenteEnContacto.objects.filter(agente_id=self.agente_2.id,
                        contacto_id=self.contacto_1.id,
                        campana_id=self.campana_preview.id,
                        estado=AgenteEnContacto.ESTADO_ASIGNADO).exists())

    def test_supervisor_ve_contactos_asignados(self):
        # Un supervisor ve contactos asignados en la lista
        self.client.logout()
        self.client.login(username=self.supervisor.user.username, password=PASSWORD)
        AgenteEnContacto.objects.filter(contacto_id=self.contacto_1.id).update(
            agente_id=self.agente_1.id, estado=AgenteEnContacto.ESTADO_ASIGNADO)
        response = self.client.get(reverse('contactos_preview_asignados',
                                           args=[self.campana_preview.id]))
        self.assertContains(response, self.agente_1.user.get_full_name())
        self.assertContains(response, self.contacto_1.telefono)

    def test_supervisor_puede_desasignar_contactos(self):
        # Un supervisor puede liberar un contacto asignado
        self.client.logout()
        self.client.login(username=self.supervisor.user.username, password=PASSWORD)
        AgenteEnContacto.objects.filter(contacto_id=self.contacto_1.id).update(
            agente_id=self.agente_1.id, estado=AgenteEnContacto.ESTADO_ASIGNADO)
        post_data = {'campana_id': self.campana_preview.id,
                     'agente_id': self.agente_1.id}
        response = self.client.post(reverse('liberar_contacto_asignado'), post_data, follow=True)
        self.assertContains(response, _(u'El Contacto ha sido liberado.'))
        self.assertNotContains(response, self.contacto_1.telefono)
        self.assertNotContains(response, self.agente_1.user.get_full_name())

    def test_nunca_se_reservan_contactos_asignados_a_otro_agente(self):
        # Al pedir un contacto nunca se entrega uno asignado a OTRO agente
        AgenteEnContacto.objects.filter(contacto_id=self.contacto_1.id).update(
            agente_id=self.agente_1.id, estado=AgenteEnContacto.ESTADO_ASIGNADO)
        # Al pedir un contacto para otro agente no debe entregar el contacto asignado
        entrega = AgenteEnContacto.entregar_contacto(self.agente_2,
                                                     self.campana_preview.id)
        self.assertEqual(entrega['result'], 'OK')
        self.assertEqual(entrega['code'], 'contacto-entregado')
        self.assertNotEqual(entrega['contacto_id'], self.contacto_1.id)
        # En particular, al ser 2 contactos nada más, solo puede entregar el otro
        self.assertEqual(entrega['contacto_id'], self.contacto_2.id)

    def test_modificacion_contacto_desde_lista_de_contactos_actualiza_agente_en_contacto(self):
        contacto = ContactoFactory()
        agente_en_contacto = AgenteEnContactoFactory(
            contacto_id=contacto.pk, telefono_contacto=contacto.telefono)
        telefono_nuevo = contacto.telefono + 111
        self.assertEqual(agente_en_contacto.telefono_contacto, contacto.telefono)
        url = reverse('contacto_update', args=[contacto.pk])
        post_data = {
            'telefono': telefono_nuevo,
            'datos': str(["xxxxxx", "yyyyy", "CORDOBA", "21000003"]),
            'bd_contacto': contacto.bd_contacto.pk
        }
        self.client.post(url, post_data)
        agente_en_contacto.refresh_from_db()
        self.assertEqual(agente_en_contacto.telefono_contacto, unicode(telefono_nuevo))
