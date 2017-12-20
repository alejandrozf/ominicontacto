# -*- coding: utf-8 -*-

"""
Tests relacionados con la lista de contactos de los Agentes
"""
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from ominicontacto_app.tests.factories import (CampanaFactory, ContactoFactory, UserFactory,
                                               QueueFactory, AgenteProfileFactory,
                                               AgenteEnContactoFactory, QueueMemberFactory,
                                               CalificacionClienteFactory)
from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.models import Campana


class AgentesContactosTests(OMLBaseTest):

    PWD = u'admin123'

    def setUp(self):

        self.usuario_agente = UserFactory(is_staff=False, is_supervisor=False)
        self.usuario_agente.set_password(self.PWD)
        self.usuario_agente.save()
        self.agente_profile = AgenteProfileFactory.create(user=self.usuario_agente)

        self.tiempo_desconexion = 3
        self.campana = CampanaFactory.create()
        self.campana_activa_propia = CampanaFactory.create(
            estado=Campana.ESTADO_ACTIVA, type=Campana.TYPE_PREVIEW,
            tiempo_desconexion=self.tiempo_desconexion)

        self.contacto = ContactoFactory.create(bd_contacto=self.campana_activa_propia.bd_contacto)
        self.campana_activa_propia.bd_contacto.contactos.add(self.contacto)
        self.queue = QueueFactory.create(campana=self.campana_activa_propia)
        self.queue_member = QueueMemberFactory.create(member=self.agente_profile, 
            queue_name=self.queue)


        self.usuario_agente_2 = UserFactory(is_staff=False, is_supervisor=False)
        self.usuario_agente_2.set_password(self.PWD)
        self.usuario_agente_2.save()
        self.agente_profile_2 = AgenteProfileFactory.create(user=self.usuario_agente_2)

        self.campana_activa_ajena = CampanaFactory.create(
            estado=Campana.ESTADO_ACTIVA, type=Campana.TYPE_PREVIEW,
            tiempo_desconexion=self.tiempo_desconexion)
        self.contacto_ajeno = ContactoFactory.create(
        	bd_contacto=self.campana_activa_ajena.bd_contacto)
        self.queue_ajena = QueueFactory.create(campana=self.campana_activa_ajena)
        self.queue_member_ajeno = QueueMemberFactory.create(member=self.agente_profile_2, 
			queue_name=self.queue_ajena)


    def test_agente_profile_contactos_de_campanas_de_las_que_es_miembro(self):
    	contactos = self.agente_profile.get_contactos_de_campanas_miembro()

    	self.assertEqual(contactos.count(), 1)
    	self.assertEqual(self.contacto, contactos[0])

    def test_contacto_list_muestra_solo_contactos_de_campanas_de_las_que_es_miembro(self):
        self.client.login(username = self.usuario_agente.username, password=self.PWD)
        url = reverse('contacto_list', args=[1])
        response = self.client.get(url, follow=True)

        self.assertContains(response, self.contacto.telefono)
        self.assertNotContains(response, self.contacto_ajeno.telefono)
