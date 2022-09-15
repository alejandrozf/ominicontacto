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
Tests sobre los procesos realicionados con la calificaciones de los contactos de las campañas
"""
import json

from mock import patch

from django.utils.translation import gettext as _
from django.conf import settings
from django.urls import reverse
from django.forms import ValidationError
from django.utils import timezone

from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.tests.factories import (CampanaFactory, QueueFactory,
                                               ContactoFactory,
                                               QueueMemberFactory,
                                               SitioExternoFactory, ParametrosCrmFactory,
                                               CalificacionClienteFactory,
                                               NombreCalificacionFactory,
                                               OpcionCalificacionFactory,
                                               FormularioFactory, FieldFormularioFactory,
                                               RespuestaFormularioGestionFactory,
                                               AgendaContactoFactory)

from ominicontacto_app.models import (AgendaContacto, NombreCalificacion, Campana, SitioExterno,
                                      OpcionCalificacion, CalificacionCliente)


class CalificacionTests(OMLBaseTest):

    def setUp(self):
        super(CalificacionTests, self).setUp()

        self.agente_profile = self.crear_agente_profile()
        self.usuario_agente = self.agente_profile.user

        self.campana = CampanaFactory.create()
        self.nombre_opcion_gestion = NombreCalificacionFactory.create()
        self.nombre_calificacion_agenda = NombreCalificacion.objects.get(
            nombre=settings.CALIFICACION_REAGENDA)
        self.formulario = FormularioFactory()
        self.campo_formulario = FieldFormularioFactory(formulario=self.formulario)
        self.opcion_calificacion_gestion = OpcionCalificacionFactory.create(
            campana=self.campana, nombre=self.nombre_opcion_gestion.nombre,
            tipo=OpcionCalificacion.GESTION, formulario=self.formulario)
        self.opcion_calificacion_agenda = OpcionCalificacionFactory.create(
            campana=self.campana, nombre=self.nombre_calificacion_agenda.nombre,
            tipo=OpcionCalificacion.AGENDA)
        self.opcion_calificacion_camp_manual = OpcionCalificacionFactory.create(
            campana=self.campana, nombre=self.nombre_opcion_gestion.nombre)
        self.opcion_calificacion_no_accion = OpcionCalificacionFactory.create(
            campana=self.campana, tipo=OpcionCalificacion.NO_ACCION)

        self.contacto = ContactoFactory.create()
        self.campana.bd_contacto.contactos.add(self.contacto)

        self.queue = QueueFactory.create(campana=self.campana)

        self.calificacion_cliente = CalificacionClienteFactory(
            opcion_calificacion=self.opcion_calificacion_camp_manual, agente=self.agente_profile,
            contacto=self.contacto)

        QueueMemberFactory.create(member=self.agente_profile, queue_name=self.queue)

        self.client.login(username=self.usuario_agente.username, password=PASSWORD)

    def _setUp_campana_dialer(self):
        self.campana_dialer = CampanaFactory.create(type=Campana.TYPE_DIALER)
        self.campana_dialer.opciones_calificacion.add(self.opcion_calificacion_gestion)
        self.campana_dialer.opciones_calificacion.add(self.opcion_calificacion_agenda)

        self.contacto_dialer = ContactoFactory.create()
        self.campana_dialer.bd_contacto.contactos.add(self.contacto_dialer)

        self.queue_dialer = QueueFactory.create(campana=self.campana_dialer)

        QueueMemberFactory.create(member=self.agente_profile, queue_name=self.queue_dialer)

    def _obtener_post_data_calificacion_cliente(self, campana=None, contacto=None):
        if campana is None:
            campana = self.campana
        if contacto is None:
            contacto = self.contacto
        post_data = {
            'contacto_form-telefono': contacto.telefono,
            'campana': campana.pk,
            'contacto': contacto.pk,
            'agente': self.agente_profile.pk,
            'opcion_calificacion': '',
        }
        return post_data

    def test_no_se_admite_tipo_calificacion_cliente_vacia_en_creacion_calificacion(self):
        url = reverse('calificacion_formulario_update_or_create',
                      kwargs={'pk_campana': self.campana.pk,
                              'pk_contacto': self.contacto.pk})
        post_data = self._obtener_post_data_calificacion_cliente()
        response = self.client.post(url, post_data, follow=True)
        calificacion_form = response.context_data.get('calificacion_form')
        self.assertFalse(calificacion_form.is_valid())

    def test_no_se_admite_tipo_calificacion_cliente_vacia_en_modificacion_calificacion(self):
        url = reverse('calificacion_formulario_update_or_create',
                      kwargs={'pk_campana': self.campana.pk,
                              'pk_contacto': self.contacto.pk})
        post_data = self._obtener_post_data_calificacion_cliente()
        response = self.client.post(url, post_data, follow=True)
        calificacion_form = response.context_data.get('calificacion_form')
        self.assertFalse(calificacion_form.is_valid())

    def no_puede_calificar_si_no_esta_asignado(self):
        campana2 = CampanaFactory.create()
        contacto2 = ContactoFactory.create(bd_contacto=campana2.bd_contacto)

        url = reverse('calificacion_formulario_update_or_create',
                      kwargs={'pk_campana': campana2.pk,
                              'pk_contacto': contacto2.pk})
        response = self.client.get(url, follow=True)
        self.assertContains(response, _("No tiene permiso para calificar llamadas de esa campaña."))

    @patch('requests.post')
    def test_calificacion_cliente_creacion_redirecciona_formulario_gestion(self, post):
        url = reverse('calificacion_formulario_update_or_create',
                      kwargs={'pk_campana': self.campana.pk,
                              'pk_contacto': self.contacto.pk})
        post_data = self._obtener_post_data_calificacion_cliente()
        post_data['opcion_calificacion'] = self.opcion_calificacion_gestion.pk
        response = self.client.post(url, post_data, follow=True)
        self.assertTemplateUsed(response, 'formulario/respuesta_formulario_gestion_agente.html')
        self.assertTrue(self.campo_formulario.nombre_campo in response.context_data['form'].fields)

    @patch('requests.post')
    def test_calificacion_cliente_creacion_redirecciona_a_otro_formulario_gestion(self, post):
        nuevo_formulario = FormularioFactory()
        campo_formulario = FieldFormularioFactory(
            formulario=nuevo_formulario, nombre_campo='otro_campo')
        nombre_opcion = NombreCalificacionFactory.create(nombre='otra opcion')
        opcion_calificacion = OpcionCalificacionFactory.create(
            campana=self.campana, nombre=nombre_opcion,
            tipo=OpcionCalificacion.GESTION, formulario=nuevo_formulario)
        url = reverse('calificacion_formulario_update_or_create',
                      kwargs={'pk_campana': self.campana.pk,
                              'pk_contacto': self.contacto.pk})
        post_data = self._obtener_post_data_calificacion_cliente()
        post_data['opcion_calificacion'] = opcion_calificacion.pk
        response = self.client.post(url, post_data, follow=True)
        self.assertTemplateUsed(response, 'formulario/respuesta_formulario_gestion_agente.html')
        self.assertTrue(campo_formulario.nombre_campo in response.context_data['form'].fields)
        self.assertFalse(self.campo_formulario.nombre_campo in response.context_data['form'].fields)

    @patch('requests.post')
    def test_calificacion_cliente_modificacion_redirecciona_formulario_gestion(self, post):
        url = reverse('calificacion_formulario_update_or_create',
                      kwargs={'pk_campana': self.campana.pk,
                              'pk_contacto': self.contacto.pk})
        post_data = self._obtener_post_data_calificacion_cliente()
        post_data['opcion_calificacion'] = self.opcion_calificacion_gestion.pk
        response = self.client.post(url, post_data, follow=True)
        self.assertTemplateUsed(response, 'formulario/respuesta_formulario_gestion_agente.html')

    @patch('requests.post')
    def test_calificacion_cliente_modificacion_gestion_por_no_accion(self, post):
        contacto_califica = ContactoFactory.create()
        self.campana.bd_contacto.contactos.add(contacto_califica)
        calificacion = CalificacionClienteFactory(
            opcion_calificacion=self.opcion_calificacion_gestion, agente=self.agente_profile,
            contacto=contacto_califica)
        RespuestaFormularioGestionFactory(calificacion=calificacion)
        # Se modifica la calificacion por una de no accion
        url_calificacion = reverse('calificacion_formulario_update_or_create',
                                   kwargs={'pk_campana': self.campana.pk,
                                           'pk_contacto': contacto_califica.pk})
        post_data_calificacion = self._obtener_post_data_calificacion_cliente(
            contacto=contacto_califica)
        post_data_calificacion['opcion_calificacion'] = self.opcion_calificacion_no_accion.pk
        self.client.post(url_calificacion, post_data_calificacion, follow=True)
        self.assertIsNone(
            CalificacionCliente.objects.get(opcion_calificacion__campana=self.campana,
                                            contacto_id=contacto_califica.id).get_venta())

    def test_existe_calificacion_especial_agenda(self):
        self.assertTrue(NombreCalificacion.objects.filter(nombre=settings.CALIFICACION_REAGENDA))

    def _obtener_post_data_calificacion_manual(self):
        post_data = {
            'agente': self.agente_profile.pk,
            'calificacion': '',
            'observaciones': 'test',
            'campana': self.campana.pk,
            'agendado': False,
            'telefono': self.contacto.pk
        }
        return post_data

    @patch('requests.post')
    def test_escoger_calificacion_agenda_redirecciona_formulario_agenda(self, post):
        url = reverse('calificacion_formulario_update_or_create',
                      kwargs={'pk_campana': self.campana.pk,
                              'pk_contacto': self.contacto.pk})
        post_data = self._obtener_post_data_calificacion_cliente()
        post_data['opcion_calificacion'] = self.opcion_calificacion_agenda.pk
        response = self.client.post(url, post_data, follow=True)
        self.assertTemplateUsed(response,
                                'agente/frame/agenda_contacto/create_agenda_contacto.html')

    @patch('requests.post')
    def test_calificacion_agenda_modificacion_redirecciona_update_agenda(self, post):
        self.calificacion_cliente.opcion_calificacion = self.opcion_calificacion_agenda
        self.calificacion_cliente.agendado = False
        self.calificacion_cliente.save()
        AgendaContactoFactory(
            agente=self.agente_profile, contacto=self.contacto, campana=self.campana)
        url = reverse('calificacion_formulario_update_or_create',
                      kwargs={'pk_campana': self.campana.pk,
                              'pk_contacto': self.contacto.pk})
        post_data = self._obtener_post_data_calificacion_cliente()
        post_data['opcion_calificacion'] = self.opcion_calificacion_agenda.pk
        response = self.client.post(url, post_data, follow=True)
        self.assertTemplateUsed(response, 'agenda_contacto/update_agenda_contacto.html')

    @patch('requests.post')
    def test_calificacion_cliente_marcada_agendado_cuando_se_salva_agenda(self, post):
        self.calificacion_cliente.opcion_calificacion = self.opcion_calificacion_agenda
        self.calificacion_cliente.agendado = False
        self.calificacion_cliente.save()
        url = reverse('agenda_contacto_create',
                      kwargs={'pk_campana': self.campana.pk,
                              'pk_contacto': self.contacto.pk})
        post_data = self._obtener_post_data_agenda()
        self.assertFalse(self.calificacion_cliente.agendado)
        self.client.post(url, post_data, follow=True)
        self.calificacion_cliente.refresh_from_db()
        self.assertTrue(self.calificacion_cliente.agendado)

    def _obtener_post_data_agenda(self):
        observaciones = 'test_schedule'
        siguiente_dia = timezone.now() + timezone.timedelta(days=1)
        fecha = str(siguiente_dia.date())
        hora = str(siguiente_dia.time())
        post_data = {'contacto': self.contacto.pk,
                     'campana': self.campana.pk,
                     'agente': self.agente_profile.pk,
                     'fecha': fecha,
                     'telefono': self.contacto.telefono,
                     'hora': hora,
                     'tipo_agenda': AgendaContacto.TYPE_PERSONAL,
                     'observaciones': observaciones}
        return post_data

    @patch('requests.post')
    def test_no_se_programan_en_wombat_agendas_globales_calificaciones_campanas_no_dialer(
            self, post):
        self.campana.type = Campana.TYPE_PREVIEW
        self.campana.save()
        self.calificacion_cliente.opcion_calificacion = self.opcion_calificacion_agenda
        self.calificacion_cliente.save()

        url = reverse('agenda_contacto_create',
                      kwargs={'pk_campana': self.campana.pk,
                              'pk_contacto': self.contacto.pk})
        post_data = self._obtener_post_data_agenda()
        post_data['tipo_agenda'] = AgendaContacto.TYPE_GLOBAL
        self.client.post(url, post_data, follow=True)
        self.assertEqual(post.call_count, 0)

    @patch('requests.post')
    def test_se_programan_en_wombat_agendas_globales_calificaciones_campanas_dialer(
            self, post):
        self.campana.type = Campana.TYPE_DIALER
        self.campana.save()
        self.calificacion_cliente.opcion_calificacion = self.opcion_calificacion_agenda
        self.calificacion_cliente.save()
        url = reverse('agenda_contacto_create',
                      kwargs={'pk_campana': self.campana.pk,
                              'pk_contacto': self.contacto.pk})
        post_data = self._obtener_post_data_agenda()
        post_data['tipo_agenda'] = AgendaContacto.TYPE_GLOBAL
        self.client.post(url, post_data, follow=True)
        self.assertEqual(post.call_count, 1)

    @patch('requests.post')
    def test_creacion_agenda_contacto_adiciona_campo_campana(self, post):
        self.calificacion_cliente.opcion_calificacion_gestion = self.opcion_calificacion_agenda
        url = reverse('agenda_contacto_create',
                      kwargs={'pk_campana': self.campana.pk,
                              'pk_contacto': self.contacto.pk})
        post_data = self._obtener_post_data_agenda()
        self.client.post(url, post_data, follow=True)
        agenda_contacto = AgendaContacto.objects.first()
        self.assertEqual(agenda_contacto.campana.pk, self.campana.pk)

    def test_llamada_manual_telefono_no_contacto_crea_contacto(self):
        # garantizamos un número distinto al existente en la campaña
        contactos_ids = self.campana.bd_contacto.contactos.values_list('id', flat=True)
        contactos_ids = list(contactos_ids)
        telefono = str(self.contacto.telefono) + '11'
        post_data = {
            'opcion_calificacion': self.opcion_calificacion_gestion.pk,
            'contacto_form-telefono': telefono,
            'contacto_form-nombre': 'Nuevo Contacto'
        }

        url = reverse('calificar_por_telefono',
                      kwargs={'pk_campana': self.campana.pk,
                              'telefono': telefono})
        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        nuevo_contacto = self.campana.bd_contacto.contactos.exclude(id__in=contactos_ids)
        self.assertEqual(nuevo_contacto.count(), 1)
        nuevo_contacto = nuevo_contacto[0]
        if self.campana.type != Campana.TYPE_ENTRANTE:
            self.assertEqual(nuevo_contacto.telefono, telefono)
        self.assertIn('Nuevo Contacto', nuevo_contacto.datos)
        self.assertFalse(nuevo_contacto.es_originario)

    def test_llamada_manual_telefono_no_contacto_muestra_formulario_calificacion_blanco(self):
        # garantizamos un número distinto al existente en la campaña
        telefono = str(self.contacto.telefono) + '11'
        url = reverse('calificar_por_telefono',
                      kwargs={'pk_campana': self.campana.pk,
                              'telefono': telefono})
        response = self.client.get(url, follow=True)
        contacto_form = response.context_data['contacto_form']
        datos_contacto_form = set(contacto_form.initial.values())
        self.assertEqual(datos_contacto_form, set([telefono]))

    def test_ocultar_opciones_de_calificacion(self):
        contacto = self.contacto
        telefono = contacto.telefono
        url = reverse('calificar_por_telefono',
                      kwargs={'pk_campana': self.campana.pk, 'telefono': telefono})
        response = self.client.get(url, follow=True)
        opciones_form = response.context_data['form']
        choices = [x for x in opciones_form.fields['opcion_calificacion'].choices]
        # Controlo que estén todas las opciones
        self.assertEqual(len(choices), self.campana.opciones_calificacion.count() + 1)
        opcion = self.opcion_calificacion_no_accion
        self.assertIn((opcion.id, opcion.nombre), choices)

        opcion.oculta = True
        opcion.save()
        response = self.client.get(url, follow=True)
        opciones_form = response.context_data['form']
        choices = [x for x in opciones_form.fields['opcion_calificacion'].choices]
        # Controlo que no este la opción oculta
        self.assertEqual(len(choices), self.campana.opciones_calificacion.count())
        self.assertNotIn((opcion.id, opcion.nombre), choices)

    def test_no_ocultar_opciones_de_calificacion_oculta_si_corresponde_a_la_calificacion(self):
        contacto = self.contacto
        telefono = contacto.telefono
        url = reverse('calificar_por_telefono',
                      kwargs={'pk_campana': self.campana.pk, 'telefono': telefono})
        response = self.client.get(url, follow=True)
        opciones_form = response.context_data['form']
        choices = [x for x in opciones_form.fields['opcion_calificacion'].choices]
        # Controlo que estén todas las opciones
        self.assertEqual(len(choices), self.campana.opciones_calificacion.count() + 1)
        opcion = self.calificacion_cliente.opcion_calificacion
        self.assertIn((opcion.id, opcion.nombre), choices)

        opcion.oculta = True
        opcion.save()
        response = self.client.get(url, follow=True)
        opciones_form = response.context_data['form']
        # Controlo que estén todas las opciones
        choices = [x for x in opciones_form.fields['opcion_calificacion'].choices]
        self.assertEqual(len(choices), self.campana.opciones_calificacion.count() + 1)
        self.assertIn((opcion.id, opcion.nombre), choices)

    def test_llamada_manual_telefono_con_1_contacto_muestra_datos_contacto_formulario(self):
        contacto = self.contacto
        telefono = contacto.telefono
        url = reverse('calificar_por_telefono',
                      kwargs={'pk_campana': self.campana.pk,
                              'telefono': telefono})
        response = self.client.get(url, follow=True)
        contacto_form = response.context_data['contacto_form']
        datos_contacto_form = set(contacto_form.initial.values())
        datos_contacto_model = set(json.loads(contacto.datos) + [str(telefono)])
        datos_contacto_model.add(contacto.id_externo)
        self.assertEqual(datos_contacto_form, datos_contacto_model)

    def test_llamada_manual_telefono_con_n_contactos_redirecciona_vista_escoger_contacto(self):
        contacto = self.contacto
        ContactoFactory(bd_contacto=self.campana.bd_contacto, telefono=contacto.telefono)
        telefono = contacto.telefono
        url = reverse('calificar_por_telefono',
                      kwargs={'pk_campana': self.campana.pk,
                              'telefono': telefono})
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, 'agente/contactos_telefonos_repetidos.html')

    def test_muestra_nombre_campana(self):
        url = reverse('calificar_por_telefono',
                      kwargs={'pk_campana': self.campana.pk,
                              'telefono': '351111111111'})
        response = self.client.get(url, follow=True)
        self.assertContains(response, self.campana.nombre)

    def test_oculta_nombre_campana(self):
        self.campana.mostrar_nombre = False
        self.campana.save()
        url = reverse('calificar_por_telefono',
                      kwargs={'pk_campana': self.campana.pk,
                              'telefono': '351111111111'})
        response = self.client.get(url, follow=True)
        self.assertNotContains(response, self.campana.nombre)

    def get_call_data(self):
        call_data = {"id_campana": self.campana.id,
                     "campana_type": self.campana.type,
                     "telefono": "3512349992",
                     "call_id": '123456789',
                     "call_type": "4",
                     "id_contacto": self.contacto.id,
                     "rec_filename": "",
                     "call_wait_duration": ""}
        return call_data

    def test_muestra_link_sitio_externo(self):
        self.campana.type = Campana.TYPE_PREVIEW
        self.campana.tipo_interaccion = Campana.SITIO_EXTERNO
        sitio_externo = SitioExternoFactory()
        self.campana.sitio_externo = sitio_externo
        self.campana.save()
        parametro1 = ParametrosCrmFactory(campana=self.campana)
        call_data = self.get_call_data()
        url = reverse('calificar_llamada', kwargs={'call_data_json': json.dumps(call_data)})

        response = self.client.get(url)
        self.assertContains(response, sitio_externo.url)
        self.assertContains(response, '"%s": "%s"' % (parametro1.nombre, parametro1.valor))

    def test_redirecciona_a_sitio_externo(self):
        self.campana.type = Campana.TYPE_PREVIEW
        self.campana.tipo_interaccion = Campana.SITIO_EXTERNO
        sitio_externo = SitioExternoFactory(disparador=SitioExterno.AUTOMATICO,
                                            metodo=SitioExterno.GET,
                                            objetivo=SitioExterno.EMBEBIDO)
        self.campana.sitio_externo = sitio_externo
        self.campana.save()
        parametro1 = ParametrosCrmFactory(campana=self.campana)

        call_data = self.get_call_data()
        url = reverse('calificar_llamada', kwargs={'call_data_json': json.dumps(call_data)})

        response = self.client.get(url, follow=False)
        self.assertEqual(response.status_code, 302)
        param_1 = '%s=%s' % (parametro1.nombre, parametro1.valor)
        equal_url = (response.url == '%s?%s' % (sitio_externo.url, param_1))
        self.assertTrue(equal_url)

    @patch('requests.get')
    def test_hace_peticion_sitio_externo_en_servidor(self, request_get):
        self.campana.type = Campana.TYPE_PREVIEW
        self.campana.tipo_interaccion = Campana.SITIO_EXTERNO
        sitio_externo = SitioExternoFactory(disparador=SitioExterno.SERVER,
                                            metodo=SitioExterno.GET,
                                            objetivo=None, formato=None)
        self.campana.sitio_externo = sitio_externo
        self.campana.save()
        ParametrosCrmFactory(campana=self.campana)
        call_data = self.get_call_data()
        url = reverse('calificar_llamada', kwargs={'call_data_json': json.dumps(call_data)})

        self.client.get(url)
        parametros = sitio_externo.get_parametros(self.agente_profile,
                                                  self.campana,
                                                  self.contacto,
                                                  call_data)
        request_get.assert_called_with(
            sitio_externo.url, headers={}, params=parametros, verify=True)

    def test_se_muestra_historico_calificaciones_contacto_llamada_entrante(self):
        self.campana.type = Campana.TYPE_ENTRANTE
        self.campana.save()
        observacion_anterior = self.calificacion_cliente.observaciones
        self.calificacion_cliente.observaciones = "NUEVA OBSERVACION"
        self.calificacion_cliente.save()
        call_data = self.get_call_data()
        call_data["call_type"] = str(self.campana.type)

        url = reverse('calificar_llamada', kwargs={'call_data_json': json.dumps(call_data)})
        response = self.client.get(url)
        self.assertContains(response, observacion_anterior)

    def test_no_se_muestra_historico_calificaciones_contacto_llamada_no_entrante(self):
        self.campana.type = Campana.TYPE_PREVIEW
        self.campana.save()
        observacion_anterior = self.calificacion_cliente.observaciones
        self.calificacion_cliente.observaciones = "NUEVA OBSERVACION"
        self.calificacion_cliente.save()
        call_data = self.get_call_data()
        call_data["call_type"] = str(self.campana.type)

        url = reverse('calificar_llamada', kwargs={'call_data_json': json.dumps(call_data)})
        response = self.client.get(url)
        self.assertNotContains(response, observacion_anterior)

    def test_llamada_entrante_con_numero_privado_inicializa_nuevo_contacto(self):
        self.campana.type = Campana.TYPE_ENTRANTE
        self.campana.save()
        call_id = "123456789.34"
        telefono = "NUMERO PRIVADO"
        call_data = self.get_call_data()
        call_data["telefono"] = str(telefono)
        call_data["call_id"] = call_id
        call_data["call_type"] = str(self.campana.type)

        url = reverse('calificar_llamada', kwargs={'call_data_json': json.dumps(call_data)})
        response = self.client.get(url)
        contacto_form = response.context_data['contacto_form']
        self.assertEqual(contacto_form.instance.pk, None)

    def test_metodo_contactos_no_calificados_devuelve_valores_correctos(self):
        contactos_no_calificados_count = self.campana.obtener_contactos_no_calificados().count()
        self.assertEqual(contactos_no_calificados_count, 0)

    def test_calificacion_cliente_cambio_a_no_agenda_elimina_agendas__globales_existentes(self):
        self.calificacion_cliente.opcion_calificacion = self.opcion_calificacion_agenda
        self.calificacion_cliente.save()
        AgendaContactoFactory(
            agente=self.agente_profile, contacto=self.contacto, campana=self.campana,
            tipo_agenda=AgendaContacto.TYPE_PERSONAL)
        self.assertTrue(AgendaContacto.objects.exists())
        self.calificacion_cliente.opcion_calificacion = self.opcion_calificacion_no_accion
        self.calificacion_cliente.save()
        self.assertFalse(AgendaContacto.objects.exists())

    def test_calificacion_cliente_cambio_a_no_agenda_no_elimina_agendas_personales_existentes(self):
        self.calificacion_cliente.opcion_calificacion = self.opcion_calificacion_agenda
        self.calificacion_cliente.save()
        AgendaContactoFactory(
            agente=self.agente_profile, contacto=self.contacto, campana=self.campana,
            tipo_agenda=AgendaContacto.TYPE_GLOBAL)
        self.assertTrue(AgendaContacto.objects.exists())
        self.calificacion_cliente.opcion_calificacion = self.opcion_calificacion_no_accion
        self.calificacion_cliente.save()
        self.assertTrue(AgendaContacto.objects.exists())

    def test_vista_calificar_contacto_muestra_botones_click2call(self):
        url = reverse('calificacion_formulario_update_or_create',
                      kwargs={'pk_campana': self.campana.pk,
                              'pk_contacto': self.contacto.pk})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'formulario/calificacion_create_update_agente.html')
        click2call = "makeClick2Call('%s', '%s', '%s', '%s', 'agendas')" % \
            (self.campana.id, self.campana.type, self.contacto.id, self.contacto.telefono)
        self.assertContains(response, click2call)
        bd_metadata = self.contacto.bd_contacto.get_metadata()
        campos_telefono = bd_metadata.nombres_de_columnas_de_telefonos
        datos_contacto = self.contacto.obtener_datos()
        for campo_telefono in campos_telefono:
            telefono = datos_contacto[campo_telefono]
            click2call = "makeClick2Call('%s', '%s', '%s', '%s', 'agendas')" % \
                (self.campana.id, self.campana.type, self.contacto.id, telefono)
        self.assertContains(response, click2call)

    def test_no_se_admite_mas_de_una_calificacion_para_un_contacto_en_una_campana_creacion(self):
        opcion_calificacion = self.calificacion_cliente.opcion_calificacion
        contacto = self.contacto
        self.assertRaises(ValidationError, lambda: CalificacionClienteFactory(
            opcion_calificacion=opcion_calificacion, contacto=contacto))

    def test_no_se_admite_mas_de_una_calificacion_para_un_contacto_en_una_campana_modificacion(
            self):
        def modificar_calificacion():
            calificacion = CalificacionClienteFactory(
                opcion_calificacion=self.opcion_calificacion_no_accion)
            calificacion.contacto = self.contacto
            calificacion.save()
        self.assertRaises(ValidationError, modificar_calificacion)

    @patch('api_app.services.calificacion_llamada.CalificacionLLamada.create_family')
    def test_campana_fuerza_calificar_llamada_impacta_en_redis_get(self, create_family):
        self.campana.type = Campana.TYPE_MANUAL
        call_data = self.get_call_data()
        call_data['force_disposition'] = True
        call_data_json = json.dumps(call_data)
        url = reverse('calificar_llamada', kwargs={'call_data_json': call_data_json})
        self.client.get(url)
        create_family.assert_called_with(self.agente_profile, call_data, call_data_json,
                                         calificado=False, gestion=False, id_calificacion=None)

    @patch('api_app.services.calificacion_llamada.CalificacionLLamada.create_family')
    def test_campana_fuerza_calificar_llamada_impacta_en_redis_post(self, create_family):
        self.campana.type = Campana.TYPE_MANUAL
        call_data = self.get_call_data()
        call_data['force_disposition'] = True
        call_data_json = json.dumps(call_data)
        url = reverse('calificar_llamada', kwargs={'call_data_json': call_data_json})
        post_data = self._obtener_post_data_calificacion_cliente()
        post_data['opcion_calificacion'] = self.opcion_calificacion_no_accion.pk
        self.client.post(url, post_data, follow=True)
        # Se hizo seguimiento de "force_disposition" y se cambia el a valor a False
        # TODO investigar como realizar el cambio utilizando:
        # http://docs.python.org/3/library/unittest.mock-examples.html#coping-with-mutable-arguments
        call_data['force_disposition'] = False

        create_family.assert_called_with(self.agente_profile, call_data, call_data_json,
                                         calificado=True, es_agenda=False,
                                         gestion=False, id_calificacion=None)
