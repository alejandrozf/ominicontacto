# -*- coding: utf-8 -*-

"""
Tests sobre los procesos realicionados con la calificaciones de los contactos de las campañas
"""

from mock import patch

from django.core.urlresolvers import reverse

from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.tests.factories import (CampanaFactory, QueueFactory, UserFactory,
                                               ContactoFactory, AgenteProfileFactory,
                                               QueueMemberFactory, CalificacionClienteFactory,
                                               CalificacionFactory)


class CalificacionTests(OMLBaseTest):
    PWD = u'admin123'

    def setUp(self):
        self.usuario_agente = UserFactory(is_agente=True)
        self.usuario_agente.set_password(self.PWD)
        self.usuario_agente.save()

        self.campana = CampanaFactory.create()
        self.calificacion_gestion = CalificacionFactory.create(nombre=self.campana.gestion)
        self.campana.calificacion_campana.calificacion.add(self.calificacion_gestion)

        self.contacto = ContactoFactory.create()
        self.campana.bd_contacto.contactos.add(self.contacto)

        self.queue = QueueFactory.create(campana=self.campana)
        self.agente_profile = AgenteProfileFactory.create(user=UserFactory(is_agente=True))

        QueueMemberFactory.create(member=self.agente_profile, queue_name=self.queue)

        self.client.login(username=self.usuario_agente, password=self.PWD)

    def _obtener_post_data_calificacion_cliente(self):
        post_data = {
            'telefono': self.contacto.telefono,
            'calificacioncliente_set-TOTAL_FORMS': 1,
            'calificacioncliente_set-INITIAL_FORMS': 0,
            'calificacioncliente_set-MIN_NUM_FORMS': 0,
            'calificacioncliente_set-MAX_NUM_FORMS': 1,
            'calificacioncliente_set-0-calificacion': '',
            'calificacioncliente_set-0-campana': self.campana.pk,
            'calificacioncliente_set-0-contacto': self.contacto.pk,
            'calificacioncliente_set-0-es_venta': False,
            'calificacioncliente_set-0-agente': self.agente_profile.pk,
            'calificacioncliente_set-0-agendado': False,
            'calificacioncliente_set-0-id': ''}
        return post_data

    def test_no_se_admite_tipo_calificacion_cliente_vacia_en_creacion_calificacion(self):
        url = reverse('calificacion_formulario_create',
                      kwargs={'id_agente': self.agente_profile.pk,
                              'pk_campana': self.campana.pk,
                              'pk_contacto': self.contacto.pk,
                              'wombat_id': 0})
        post_data = self._obtener_post_data_calificacion_cliente()
        response = self.client.post(url, post_data, follow=True)
        calificacion_form = response.context_data.get('calificacion_form')
        self.assertFalse(calificacion_form.is_valid())

    def test_no_se_admite_tipo_calificacion_cliente_vacia_en_modificacion_calificacion(self):
        calificacion_cliente = CalificacionClienteFactory.create(
            campana=self.campana, contacto=self.contacto, agente=self.agente_profile)
        url = reverse('calificacion_formulario_update',
                      kwargs={'id_agente': self.agente_profile.pk,
                              'pk_campana': self.campana.pk,
                              'pk_contacto': self.contacto.pk,
                              'wombat_id': 0})
        post_data = self._obtener_post_data_calificacion_cliente()
        post_data['calificacioncliente_set-0-id'] = calificacion_cliente.pk
        response = self.client.post(url, post_data, follow=True)
        calificacion_form = response.context_data.get('calificacion_form')
        self.assertFalse(calificacion_form.is_valid())

    @patch('requests.post')
    def test_calificacion_cliente_creacion_redirecciona_formulario_gestion(self, post):
        url = reverse('calificacion_formulario_create',
                      kwargs={'id_agente': self.agente_profile.pk,
                              'pk_campana': self.campana.pk,
                              'pk_contacto': self.contacto.pk,
                              'wombat_id': 0})
        post_data = self._obtener_post_data_calificacion_cliente()
        post_data['calificacioncliente_set-0-calificacion'] = self.calificacion_gestion.pk
        response = self.client.post(url, post_data, follow=True)
        self.assertTemplateUsed(response, 'formulario/formulario_create.html')

    @patch('requests.post')
    def test_calificacion_cliente_modificacion_redirecciona_formulario_gestion(self, post):
        calificacion_cliente = CalificacionClienteFactory.create(
            campana=self.campana, contacto=self.contacto, agente=self.agente_profile)
        url = reverse('calificacion_formulario_update',
                      kwargs={'id_agente': self.agente_profile.pk,
                              'pk_campana': self.campana.pk,
                              'pk_contacto': self.contacto.pk,
                              'wombat_id': 0})
        post_data = self._obtener_post_data_calificacion_cliente()
        post_data['calificacioncliente_set-0-id'] = calificacion_cliente.pk
        post_data['calificacioncliente_set-0-calificacion'] = self.calificacion_gestion.pk
        post_data['calificacioncliente_set-INITIAL_FORMS'] = 1
        response = self.client.post(url, post_data, follow=True)
        self.assertTemplateUsed(response, 'formulario/formulario_create.html')
