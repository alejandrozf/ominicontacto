# -*- coding: utf-8 -*-

"""
Tests relacionados con las campañas
"""
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from ominicontacto_app.models import Campana

from ominicontacto_app.tests.factories import (CampanaFactory, ContactoFactory, UserFactory,
                                               QueueFactory)

from ominicontacto_app.tests.utiles import OMLBaseTest

from ominicontacto_app.utiles import validar_nombres_campanas

from django.forms import ValidationError


class CampanasTests(OMLBaseTest):

    PWD = u'admin123'

    def setUp(self):
        self.usuario_admin_supervisor = UserFactory(is_staff=True, is_supervisor=True)
        self.usuario_admin_supervisor.set_password(self.PWD)
        self.usuario_admin_supervisor.save()

        self.campana = CampanaFactory.create()
        self.campana_activa = CampanaFactory.create(
            estado=Campana.ESTADO_ACTIVA, type=Campana.TYPE_PREVIEW)
        self.campana_borrada = CampanaFactory.create(
            estado=Campana.ESTADO_BORRADA, oculto=False, type=Campana.TYPE_PREVIEW)

        self.contacto = ContactoFactory.create(bd_contacto=self.campana_activa.bd_contacto)

        self.client.login(username=self.usuario_admin_supervisor.username, password=self.PWD)

    def test_campana_contiene_atributo_entero_positivo_llamado_objetivo(self):
        self.assertTrue(self.campana.objetivo >= 0)

    def test_validacion_nombres_de_campana_no_permite_caracteres_no_ASCII(self):
        error_ascii = "el nombre no puede contener tildes ni caracteres no ASCII"
        with self.assertRaisesMessage(ValidationError, error_ascii):
            validar_nombres_campanas("áéíóúñ")

    def test_validacion_nombres_de_campana_no_permite_espacios(self):
        with self.assertRaisesMessage(ValidationError, "el nombre no puede contener espacios"):
            validar_nombres_campanas("nombre con espacios")

    def test_tipo_campanas_preview(self):
        self.assertEqual(Campana.TYPE_PREVIEW, 4)

    def test_tiempo_desconexion_campanas_preview(self):
        self.assertTrue(self.campana.tiempo_desconexion >= 0)

    def test_usuarios_no_logueados_no_acceden_a_vista_lista_campanas_preview(self):
        self.client.logout()
        url = reverse('campana_preview_list')
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, u'registration/login.html')

    def test_usuarios_no_logueados_no_acceden_a_vista_creacion_campanas_preview(self):
        self.client.logout()
        url = reverse('campana_preview_create')
        response = self.client.post(url, follow=True)
        self.assertTemplateUsed(response, u'registration/login.html')

    def test_usuarios_no_logueados_no_acceden_a_vista_modificacion_campanas_preview(self):
        self.client.logout()
        url = reverse('campana_preview_update', args=[self.campana_activa.pk])
        response = self.client.post(url, follow=True)
        self.assertTemplateUsed(response, u'registration/login.html')

    def test_usuarios_no_logueados_no_acceden_a_vista_eliminacion_campanas_preview(self):
        self.client.logout()
        url = reverse('campana_preview_delete', args=[self.campana_borrada.pk])
        response = self.client.post(url, follow=True)
        self.assertTemplateUsed(response, u'registration/login.html')

    def test_usuarios_logueados_pueden_ver_lista_de_campanas_preview_activas(self):
        url = reverse('campana_preview_list')
        response = self.client.get(url, follow=True)
        self.assertContains(response, self.campana_activa.nombre)

    def test_usuarios_logueados_pueden_ver_lista_de_campanas_preview_borras(self):
        url = reverse('campana_preview_list')
        response = self.client.get(url, follow=True)
        self.assertContains(response, self.campana_borrada.nombre)

    def test_usuario_logueado_puede_crear_campana_preview(self):
        url = reverse('campana_preview_create')
        nombre_campana = 'campana_preview_test'
        post_data = {'nombre': nombre_campana,
                     'calificacion_campana': self.campana.calificacion_campana.pk,
                     'bd_contacto': self.campana_activa.bd_contacto.pk,
                     'tipo_interaccion': Campana.FORMULARIO,
                     'formulario': self.campana.formulario.pk,
                     'gestion': 'Venta',
                     'detectar_contestadores': True,
                     'auto_grabacion': True,
                     'objetivo': 1,
                     'tiempo_desconexion': 10}
        self.client.post(url, post_data, follow=True)
        self.assertTrue(Campana.objects.get(nombre=nombre_campana))

    def test_usuario_logueado_puede_modificar_campana_preview(self):
        QueueFactory.create(campana=self.campana_activa)
        url = reverse('campana_preview_update', args=[self.campana_activa.pk])
        nombre_campana = 'campana_preview_actualizada'
        post_data = {'nombre': nombre_campana,
                     'calificacion_campana': self.campana.calificacion_campana.pk,
                     'bd_contacto': self.campana_activa.bd_contacto.pk,
                     'tipo_interaccion': Campana.FORMULARIO,
                     'formulario': self.campana.formulario.pk,
                     'gestion': 'Venta',
                     'detectar_contestadores': True,
                     'auto_grabacion': True,
                     'objetivo': 1,
                     'tiempo_desconexion': 10}
        self.assertNotEqual(Campana.objects.get(pk=self.campana_activa.pk).nombre, nombre_campana)
        self.client.post(url, post_data, follow=True)
        self.assertEqual(Campana.objects.get(pk=self.campana_activa.pk).nombre, nombre_campana)

    def test_usuario_logueado_puede_eliminar_campana_preview(self):
        url = reverse('campana_preview_delete', args=[self.campana_activa.pk])
        self.assertEqual(Campana.objects.get(
            pk=self.campana_activa.pk).estado, Campana.ESTADO_ACTIVA)
        self.client.post(url, follow=True)
        self.assertEqual(Campana.objects.get(
            pk=self.campana_activa.pk).estado, Campana.ESTADO_BORRADA)

    def test_usuario_no_logueado_no_establece_supervisores_campana_preview(self):
        self.client.logout()
        url = reverse('campana_preview_supervisors', args=[self.campana_activa.pk])
        response = self.client.post(url, follow=True)
        self.assertTemplateUsed(response, u'registration/login.html')

    def test_usuario_logueado_establece_supervisores_campana_preview(self):
        url = reverse('campana_preview_supervisors', args=[self.campana_activa.pk])
        self.assertFalse(self.campana_activa.supervisors.all().exists())
        supervisor = UserFactory.create()
        self.campana_activa.supervisors.add(supervisor)
        self.campana_activa.save()
        post_data = {'supervisors': [supervisor.pk]}
        self.client.post(url, post_data, follow=True)
        self.assertTrue(self.campana_activa.supervisors.all().exists())
