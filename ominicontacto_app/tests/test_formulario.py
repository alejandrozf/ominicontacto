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
Tests relacionados a los formularios de gestion
"""
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.tests.factories import FormularioFactory, FieldFormularioFactory
from ominicontacto_app.models import FieldFormulario


class TestsFormulario(OMLBaseTest):
    PWD = u'admin123'

    def setUp(self, *args, **kwargs):
        super(TestsFormulario, self).setUp(*args, **kwargs)
        self.admin = self.crear_administrador()
        self.agente = self.crear_user_agente()
        self.agente.set_password(self.PWD)
        self.admin.set_password(self.PWD)
        self.formulario = FormularioFactory()

        self.client.login(username=self.admin.username, password=self.PWD)

    def test_no_crear_campo_de_lista_vacia(self):
        url = reverse('formulario_field', args=[self.formulario.pk])
        post_data = {'formulario': self.formulario.pk, 'nombre_campo': 'campo',
                     'tipo': FieldFormulario.TIPO_LISTA, 'values_select': '',
                     'is_required': True}
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, _('No se pudo llevar a cabo la creacion de campo.'))
        self.assertEqual(response.context_data['form'].errors['values_select'],
                         [_('La lista no puede estar vacía')])

    def test_no_crear_formularios_vacios(self):
        url = reverse('formulario_vista_previa', args=[self.formulario.pk])
        response = self.client.get(url, follow=True)
        self.assertContains(response, _('No está permitido crear un formulario vacio.'))
        field_url = reverse('formulario_field', args=[self.formulario.pk])
        self.assertRedirects(response, field_url)

    def test_no_crear_campos_con_mismos_nombres(self):
        nombre_campo = 'test'
        field = FieldFormularioFactory(nombre_campo=nombre_campo)
        url = reverse('formulario_field', args=[field.formulario.pk])
        post_data = {'formulario': field.formulario.pk,
                     'nombre_campo': nombre_campo,
                     'tipo': FieldFormulario.TIPO_FECHA, 'values_select': '',
                     'is_required': True}
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, _('No se pudo llevar a cabo la creacion de campo.'))
        self.assertEqual(response.context_data['form'].errors['nombre_campo'],
                         [_('No se puede crear un campo ya existente')])
