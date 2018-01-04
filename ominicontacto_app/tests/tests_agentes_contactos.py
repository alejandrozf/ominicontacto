# -*- coding: utf-8 -*-

"""
Tests relacionados con la lista de contactos de los Agentes
"""
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from ominicontacto_app.tests.factories import (CampanaFactory, ContactoFactory, UserFactory,
                                               QueueFactory, AgenteProfileFactory,
                                               QueueMemberFactory)
from ominicontacto_app.tests.utiles import OMLBaseTest


class AgentesContactosTests(OMLBaseTest):

    PWD = u'admin123'

    def setUp(self):
        """
        Creo dos agentes con una campaña con un contacto cada una.
        """
        self.usuario_agente, self.campana_propia, self.contacto_propio = \
            self._crear_agente_con_campana_y_contacto()

        self.usuario_agente_2, self.campana_ajena, self.contacto_ajeno = \
            self._crear_agente_con_campana_y_contacto()

    def _crear_agente_con_campana_y_contacto(self):
        usuario = self._crear_agente()
        campana = CampanaFactory.create(tiempo_desconexion=3)
        self._hacer_miembro(usuario, campana)
        contacto = ContactoFactory.create(bd_contacto=campana.bd_contacto)
        return usuario, campana, contacto

    def _crear_agente(self):
        usuario_agente = UserFactory(is_staff=False, is_supervisor=False)
        usuario_agente.set_password(self.PWD)
        usuario_agente.save()
        AgenteProfileFactory.create(user=usuario_agente)
        return usuario_agente

    def _hacer_miembro(self, usuario_agente, campana):
        agente = usuario_agente.get_agente_profile()
        queue = QueueFactory.create(campana=campana)
        QueueMemberFactory.create(member=agente, queue_name=queue)

    def test_agente_profile_contactos_de_campanas_de_las_que_es_miembro(self):
        agente_profile = self.usuario_agente.get_agente_profile()
        contactos = agente_profile.get_contactos_de_campanas_miembro()

        self.assertEqual(contactos.count(), 1)
        self.assertEqual(self.contacto_propio, contactos[0])

    def test_contacto_list_muestra_solo_contactos_de_campanas_de_las_que_es_miembro(self):
        self.client.login(username=self.usuario_agente.username, password=self.PWD)
        url = reverse('contacto_list', args=[1])
        response = self.client.get(url, follow=True)

        self.assertContains(response, self.contacto_propio.telefono)
        self.assertNotContains(response, self.contacto_ajeno.telefono)
