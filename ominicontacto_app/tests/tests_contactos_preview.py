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

from django.urls import reverse

from ominicontacto_app.tests.factories import (CampanaFactory, ContactoFactory, QueueFactory,
                                               AgenteEnContactoFactory)
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.models import AgenteEnContacto, Campana, User


class AsignacionDeContactosPreviewTests(OMLBaseTest):

    def setUp(self):
        self.agente_1 = self.crear_agente_profile()
        self.agente_2 = self.crear_agente_profile()
        self.supervisor = self.crear_supervisor_profile(rol=User.SUPERVISOR)
        self.campana_preview = CampanaFactory.create(
            type=Campana.TYPE_PREVIEW, tiempo_desconexion=2, estado=Campana.ESTADO_ACTIVA)
        QueueFactory.create(campana=self.campana_preview)
        self._hacer_miembro(self.agente_1, self.campana_preview)
        self._hacer_miembro(self.agente_2, self.campana_preview)
        self.contacto_1 = ContactoFactory.create(bd_contacto=self.campana_preview.bd_contacto)
        self.contacto_2 = ContactoFactory.create(bd_contacto=self.campana_preview.bd_contacto)
        self.campana_preview.establecer_valores_iniciales_agente_contacto(False, False)
        self.client.login(username=self.agente_1.user.username, password=PASSWORD)

    def test_valida_contacto_no_asignado_devuelve_false(self):
        # Contacto 1 no esta reservado
        url = reverse('validar_contacto_asignado')
        post_data = {'pk_campana': self.campana_preview.id,
                     'pk_contacto': self.contacto_1.id,
                     'pk_agente': self.agente_1.id}
        response = self.client.post(url, post_data, follow=True)
        resultado = json.loads(response.content)
        self.assertEqual(resultado['contacto_asignado'], False)

    @patch('redis.Redis.hgetall')
    def test_reserva_de_contacto_otorga_uno_libre(self, hgetall):
        hgetall.return_value = {}
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

    @patch('redis.Redis.hgetall')
    def test_reserva_de_contacto_otorga_uno_asignado_inicialmente_al_agente(self, hgetall):
        hgetall.return_value = {}
        # asignamos los contactos inicialmente uno a cada agente
        for agente, agente_en_contacto in zip([self.agente_1, self.agente_2],
                                              AgenteEnContacto.objects.all()):
            agente_en_contacto.agente_id = agente.pk
            agente_en_contacto.save()
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

        # El otro contacto no esta reservado y se encuentra asignado al otro agente
        contacto_id_2 = self.contacto_1.id
        if id_contacto == self.contacto_1.id:
            contacto_id_2 = self.contacto_2.id
        self.assertTrue(AgenteEnContacto.objects.filter(contacto_id=contacto_id_2,
                        campana_id=self.campana_preview.id, agente_id=self.agente_2.id,
                        estado=AgenteEnContacto.ESTADO_INICIAL).exists())

    @patch('redis.Redis.hgetall')
    def test_reserva_de_contacto_devuelve_siempre_contacto_asignado_al_agente(self, hgetall):
        hgetall.return_value = {}
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

    @patch('ominicontacto_app.services.click2call.Click2CallOriginator.call_originate')
    def test_c2c_con_reserva_asigna_de_contacto(self, _call_originate):
        # Al llamar contacto reservado asigna el contacto
        AgenteEnContacto.objects.filter(contacto_id=self.contacto_1.id).update(
            agente_id=self.agente_1.id, estado=AgenteEnContacto.ESTADO_ENTREGADO)

        post_data = {'pk_campana': self.campana_preview.id,
                     'pk_agente': self.agente_1.id,
                     'pk_contacto': self.contacto_1.id,
                     'click2call_type': 'preview',
                     'tipo_campana': ''}
        response = self.client.post(reverse('agente_llamar_contacto'), post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(_call_originate.called)

        self.assertTrue(AgenteEnContacto.objects.filter(agente_id=self.agente_1.id,
                        contacto_id=self.contacto_1.id,
                        campana_id=self.campana_preview.id,
                        estado=AgenteEnContacto.ESTADO_ASIGNADO).exists())

    @patch('ominicontacto_app.services.click2call.Click2CallOriginator.call_originate')
    def test_c2c_sin_reserva_de_contacto_agente_no_puede_llamar(self, _call_originate):
        # Un contacto asignado a otro agente no puede ser llamado
        post_data = {'pk_campana': self.campana_preview.id,
                     'pk_agente': self.agente_1.id,
                     'pk_contacto': self.contacto_1.id,
                     'click2call_type': 'preview',
                     'tipo_campana': ''}
        response = self.client.post(reverse('agente_llamar_contacto'), post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(_call_originate.called)
        inicial = AgenteEnContacto.ESTADO_INICIAL
        self.assertFalse(AgenteEnContacto.objects.exclude(estado=inicial).exists())
        self.assertContains(response, _(u'No es posible llamar al contacto.'))

    # Unitests para Vista de contactos asignados
    def test_reservar_contacto_estado_asignado_entregado(self):
        AgenteEnContacto.objects.filter(contacto_id=self.contacto_1.id).update(
            agente_id=self.agente_1.id, estado=AgenteEnContacto.ESTADO_ASIGNADO)
        contactos = []
        contactos.append(self.contacto_1.id)
        post_data = {'campana_id': self.campana_preview.id, 'id_agente': self.agente_1.id,
                     'contacts_selected': str(contactos), 'accion': 'reservar'}
        self.client.post(reverse('liberar_reservar_contacto_asignado'),
                         post_data, follow=True)
        self.assertTrue(AgenteEnContacto.objects.filter(
            agente_id=self.agente_1.id,
            contacto_id=self.contacto_1.id,
            campana_id=self.campana_preview.id,
            estado=AgenteEnContacto.ESTADO_ASIGNADO).exists())

    def test_reservar_contacto_estado_inicial_liberado(self):
        AgenteEnContacto.objects.filter(contacto_id=self.contacto_1.id).update(
            agente_id=-1, estado=AgenteEnContacto.ESTADO_INICIAL)
        contactos = []
        contactos.append(self.contacto_1.id)
        post_data = {'campana_id': self.campana_preview.id, 'id_agente': self.agente_1.id,
                     'contacts_selected': str(contactos), 'accion': 'reservar'}
        self.client.post(reverse('liberar_reservar_contacto_asignado'),
                         post_data, follow=True)
        self.assertTrue(AgenteEnContacto.objects.filter(
            agente_id=self.agente_1.id,
            contacto_id=self.contacto_1.id,
            campana_id=self.campana_preview.id,
            estado=AgenteEnContacto.ESTADO_INICIAL).exists())

    def test_reservar_contacto_estado_finalizado(self):
        AgenteEnContacto.objects.filter(contacto_id=self.contacto_1.id).update(
            agente_id=self.agente_1.id, estado=AgenteEnContacto.ESTADO_FINALIZADO)
        contactos = []
        contactos.append(self.contacto_1.id)
        post_data = {'campana_id': self.campana_preview.id, 'id_agente': self.agente_1.id,
                     'contacts_selected': str(contactos), 'accion': 'reservar'}
        self.client.post(reverse('liberar_reservar_contacto_asignado'),
                         post_data, follow=True)
        self.assertTrue(AgenteEnContacto.objects.filter(
            agente_id=self.agente_1.id,
            contacto_id=self.contacto_1.id,
            campana_id=self.campana_preview.id,
            estado=AgenteEnContacto.ESTADO_FINALIZADO).exists())

    def test_reservar_contacto_de_otro_agente(self):
        AgenteEnContacto.objects.filter(contacto_id=self.contacto_1.id).update(
            agente_id=self.agente_2.id, estado=AgenteEnContacto.ESTADO_ASIGNADO)
        contactos = []
        contactos.append(self.contacto_1.id)
        post_data = {'campana_id': self.campana_preview.id, 'id_agente': self.agente_1.id,
                     'contacts_selected': str(contactos), 'accion': 'reservar'}
        self.client.post(reverse('liberar_reservar_contacto_asignado'),
                         post_data, follow=True)
        self.assertTrue(AgenteEnContacto.objects.filter(
            agente_id=self.agente_1.id,
            contacto_id=self.contacto_1.id,
            campana_id=self.campana_preview.id,
            estado=AgenteEnContacto.ESTADO_INICIAL).exists())

    def test_liberar_contacto_estado_asignado_entregado(self):
        AgenteEnContacto.objects.filter(contacto_id=self.contacto_1.id).update(
            agente_id=self.agente_1.id, estado=AgenteEnContacto.ESTADO_ASIGNADO)
        contactos = []
        contactos.append(self.contacto_1.id)
        post_data = {'campana_id': self.campana_preview.id, 'id_agente': self.agente_1.id,
                     'contacts_selected': str(contactos), 'accion': 'liberar'}
        self.client.post(reverse('liberar_reservar_contacto_asignado'),
                         post_data, follow=True)
        self.assertTrue(AgenteEnContacto.objects.filter(
            agente_id=-1,
            contacto_id=self.contacto_1.id,
            campana_id=self.campana_preview.id,
            estado=AgenteEnContacto.ESTADO_INICIAL).exists())

    def test_liberar_contacto_estado_inicial(self):
        AgenteEnContacto.objects.filter(contacto_id=self.contacto_1.id).update(
            agente_id=self.agente_1.id, estado=AgenteEnContacto.ESTADO_INICIAL)
        contactos = []
        contactos.append(self.contacto_1.id)
        post_data = {'campana_id': self.campana_preview.id, 'id_agente': self.agente_1.id,
                     'contacts_selected': str(contactos), 'accion': 'liberar'}
        self.client.post(reverse('liberar_reservar_contacto_asignado'),
                         post_data, follow=True)
        self.assertTrue(AgenteEnContacto.objects.filter(
            agente_id=-1,
            contacto_id=self.contacto_1.id,
            campana_id=self.campana_preview.id,
            estado=AgenteEnContacto.ESTADO_INICIAL).exists())

    def test_liberar_contacto_estado_finalizado(self):
        AgenteEnContacto.objects.filter(contacto_id=self.contacto_1.id).update(
            agente_id=self.agente_1.id, estado=AgenteEnContacto.ESTADO_FINALIZADO)
        contactos = []
        contactos.append(self.contacto_1.id)
        post_data = {'campana_id': self.campana_preview.id, 'id_agente': self.agente_1.id,
                     'contacts_selected': str(contactos), 'accion': 'liberar'}
        self.client.post(reverse('liberar_reservar_contacto_asignado'),
                         post_data, follow=True)
        self.assertTrue(AgenteEnContacto.objects.filter(
            agente_id=self.agente_1.id,
            contacto_id=self.contacto_1.id,
            campana_id=self.campana_preview.id,
            estado=AgenteEnContacto.ESTADO_FINALIZADO).exists())

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
            contacto_id=contacto.pk, campana_id=self.campana_preview.id,
            telefono_contacto=contacto.telefono)
        telefono_nuevo = contacto.telefono + '111'
        self.assertEqual(agente_en_contacto.telefono_contacto, contacto.telefono)
        url = reverse('contacto_update', args=[self.campana_preview.pk, contacto.pk])
        post_data = {
            'telefono': telefono_nuevo,
            'datos': str(["xxxxxx", "yyyyy", "CORDOBA", "21000003"]),
        }
        self.client.post(url, post_data)
        contacto.refresh_from_db()
        self.assertEqual(contacto.telefono, str(telefono_nuevo))
        agente_en_contacto.refresh_from_db()
        self.assertEqual(agente_en_contacto.telefono_contacto, str(telefono_nuevo))

    @patch('redis.Redis.hgetall')
    def test_se_entregan_contactos_de_acuerdo_al_orden(self, hgetall):
        hgetall.return_value = {}
        # el primero sera el entregado de acuerdo al orden
        # ya que es el orden definido en la campaña
        pk_campana = self.campana_preview.pk
        agente_en_contacto = AgenteEnContacto.objects.filter(campana_id=pk_campana).first()
        url = reverse('campana_preview_dispatcher', args=[pk_campana])
        response = self.client.post(url, follow=True)
        resultado = json.loads(response.content)
        id_contacto = resultado['contacto_id']
        self.assertEqual(id_contacto, agente_en_contacto.contacto_id)

    @patch('redis.Redis.hgetall')
    def test_se_entregan_contactos_consecutivamente_de_acuerdo_al_orden(self, hgetall):
        hgetall.return_value = {}
        pk_campana = self.campana_preview.pk
        agentes_en_contactos = list(AgenteEnContacto.objects.filter(campana_id=pk_campana))
        agente_en_contacto1 = agentes_en_contactos[0]
        agente_en_contacto1.estado = AgenteEnContacto.ESTADO_ENTREGADO
        agente_en_contacto1.agente_id = self.agente_1.pk
        agente_en_contacto1.save()
        agente_en_contacto2 = agentes_en_contactos[1]
        url = reverse('campana_preview_dispatcher', args=[pk_campana])
        response = self.client.post(url, follow=True)
        resultado = json.loads(response.content)
        id_contacto = resultado['contacto_id']
        self.assertEqual(id_contacto, agente_en_contacto2.contacto_id)

    @patch('redis.Redis.hgetall')
    def test_se_entregan_contactos_circularmente_de_acuerdo_al_orden(self, hgetall):
        hgetall.return_value = {}
        pk_campana = self.campana_preview.pk
        agentes_en_contactos = list(AgenteEnContacto.objects.filter(campana_id=pk_campana))
        agente_en_contacto2 = agentes_en_contactos[1]
        agente_en_contacto2.estado = AgenteEnContacto.ESTADO_ENTREGADO
        agente_en_contacto2.agente_id = self.agente_1.pk
        agente_en_contacto2.save()
        agente_en_contacto1 = agentes_en_contactos[0]
        url = reverse('campana_preview_dispatcher', args=[pk_campana])
        response = self.client.post(url, follow=True)
        resultado = json.loads(response.content)
        id_contacto = resultado['contacto_id']
        self.assertEqual(id_contacto, agente_en_contacto1.contacto_id)

    @patch('redis.Redis.hgetall')
    def test_no_se_entregan_contactos_desactivados_con_FALSE(self, hgetall):
        hgetall.return_value = {}
        pk_campana = self.campana_preview.pk
        self.campana_preview.campo_desactivacion = 'dni'
        self.campana_preview.save()
        agentes_en_contactos = list(AgenteEnContacto.objects.filter(campana_id=pk_campana))
        agente_en_contacto1 = agentes_en_contactos[0]
        agente_en_contacto2 = agentes_en_contactos[1]
        datos_contacto = agente_en_contacto1.datos_contacto
        datos_contacto_dict = json.loads(datos_contacto)
        datos_contacto_dict['dni'] = 'FALSE'
        datos_contacto = json.dumps(datos_contacto_dict)
        agente_en_contacto1.datos_contacto = datos_contacto
        agente_en_contacto1.save()
        url = reverse('campana_preview_dispatcher', args=[pk_campana])
        response = self.client.post(url, follow=True)
        resultado = json.loads(response.content)
        id_contacto = resultado['contacto_id']
        self.assertEqual(id_contacto, agente_en_contacto2.contacto_id)

    @patch('redis.Redis.hgetall')
    def test_no_se_entregan_contactos_desactivados_con_0(self, hgetall):
        hgetall.return_value = {}
        pk_campana = self.campana_preview.pk
        self.campana_preview.campo_desactivacion = 'dni'
        self.campana_preview.save()
        agentes_en_contactos = list(AgenteEnContacto.objects.filter(campana_id=pk_campana))
        agente_en_contacto1 = agentes_en_contactos[0]
        agente_en_contacto2 = agentes_en_contactos[1]
        datos_contacto = agente_en_contacto1.datos_contacto
        datos_contacto_dict = json.loads(datos_contacto)
        datos_contacto_dict['dni'] = '0'
        datos_contacto = json.dumps(datos_contacto_dict)
        agente_en_contacto1.datos_contacto = datos_contacto
        agente_en_contacto1.save()
        url = reverse('campana_preview_dispatcher', args=[pk_campana])
        response = self.client.post(url, follow=True)
        resultado = json.loads(response.content)
        id_contacto = resultado['contacto_id']
        self.assertEqual(id_contacto, agente_en_contacto2.contacto_id)

    def test_campos_bloqueados_no_se_modifican(self):
        self.campana_preview.campos_bd_no_editables = json.dumps(['telefono'])
        self.campana_preview.save()
        contacto = ContactoFactory()
        agente_en_contacto = AgenteEnContactoFactory(
            contacto_id=contacto.pk, campana_id=self.campana_preview.id,
            telefono_contacto=contacto.telefono)

        telefono_viejo = contacto.telefono
        telefono_nuevo = contacto.telefono + '111'
        url = reverse('contacto_update', args=[self.campana_preview.pk, contacto.pk])
        post_data = {
            'telefono': telefono_nuevo,
            'datos': str(["xxxxxx", "yyyyy", "CORDOBA", "21000003"]),
            'bd_contacto': contacto.bd_contacto.pk
        }
        self.client.post(url, post_data)
        contacto.refresh_from_db()
        agente_en_contacto.refresh_from_db()
        self.assertEqual(contacto.telefono, telefono_viejo)
        self.assertEqual(agente_en_contacto.telefono_contacto, str(telefono_viejo))
