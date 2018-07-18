# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from configuracion_telefonia_app.models import RutaEntrante, DestinoEntrante
from configuracion_telefonia_app.tests.factories import RutaEntranteFactory

from ominicontacto_app.models import Campana
from ominicontacto_app.tests.factories import CampanaFactory
from ominicontacto_app.tests.utiles import OMLBaseTest


class TestsRutasEntrantes(OMLBaseTest):
    PWD = u'admin123'

    def setUp(self, *args, **kwargs):
        super(TestsRutasEntrantes, self).setUp(*args, **kwargs)

        self.admin = self.crear_administrador()
        self.admin.set_password(self.PWD)

        self.usr_sup = self.crear_user_supervisor()
        self.crear_supervisor_profile(self.usr_sup)

        self.campana_entrante = CampanaFactory(type=Campana.TYPE_ENTRANTE)
        self.destino_campana_entrante = DestinoEntrante.crear_nodo_ruta_entrante(
            self.campana_entrante)

        self.ruta_entrante = RutaEntranteFactory(destino=self.destino_campana_entrante)

    def _obtener_post_data_ruta_entrante(self):
        return {
            'nombre': 'test_ruta_entrante',
            'telefono': '123456',
            'prefijo': '351',
            'idioma': RutaEntrante.ES,
            'tipo_destino': self.destino_campana_entrante.tipo,
            'destino': self.destino_campana_entrante.pk
        }

    def test_usuario_sin_administracion_no_puede_crear_ruta_entrante(self):
        url = reverse('crear_ruta_entrante')
        self.client.login(username=self.usr_sup.username, password=self.PWD)
        post_data = self._obtener_post_data_ruta_entrante()
        n_rutas_entrantes = RutaEntrante.objects.count()
        self.client.post(url, post_data, follow=True)
        self.assertEqual(RutaEntrante.objects.count(), n_rutas_entrantes)

    def test_usuario_administrador_puede_crear_ruta_entrante(self):
        url = reverse('crear_ruta_entrante')
        self.client.login(username=self.admin.username, password=self.PWD)
        post_data = self._obtener_post_data_ruta_entrante()
        n_rutas_entrantes = RutaEntrante.objects.count()
        self.client.post(url, post_data, follow=True)
        self.assertEqual(RutaEntrante.objects.count(), n_rutas_entrantes + 1)

    def test_usuario_sin_administracion_no_puede_modificar_ruta_entrante(self):
        url = reverse('editar_ruta_entrante', args=[self.ruta_entrante.pk])
        self.client.login(username=self.usr_sup.username, password=self.PWD)
        post_data = self._obtener_post_data_ruta_entrante()
        post_data['id'] = self.ruta_entrante.pk
        n_rutas_entrantes = RutaEntrante.objects.count()
        self.client.post(url, post_data, follow=True)
        self.assertEqual(RutaEntrante.objects.count(), n_rutas_entrantes)

    def test_usuario_administrador_puede_modificar_ruta_entrante(self):
        nuevo_nombre = 'ruta_entrante_modificada'
        url = reverse('editar_ruta_entrante', args=[self.ruta_entrante.pk])
        self.client.login(username=self.admin.username, password=self.PWD)
        post_data = self._obtener_post_data_ruta_entrante()
        post_data['id'] = self.ruta_entrante.pk
        post_data['nombre'] = nuevo_nombre
        response = self.client.post(url, post_data, follow=True)
        self.ruta_entrante.refresh_from_db()
        self.assertEqual(self.ruta_entrante.nombre, nuevo_nombre)

    def test_usuario_sin_administracion_no_puede_eliminar_ruta_entrante(self):
        pass

    def test_usuario_administrador_puede_eliminar_ruta_entrante(self):
        pass

    def test_usuario_sin_administracion_no_puede_crear_ivr(self):
        pass

    def test_usuario_administrador_puede_crear_ivr(self):
        pass

    def test_usuario_sin_administracion_no_puede_modificar_ivr(self):
        pass

    def test_usuario_administrar_puede_modificar_ivr(self):
        pass

    def test_creacion_ivr_crea_nodo_generico_correspondiente(self):
        pass

    def test_usuario_sin_administracion_no_puede_crear_grupo_horario(self):
        pass

    def test_usuario_administrador_puede_crear_grupo_horario(self):
        pass

    def test_usuario_sin_administracion_no_puede_modificar_grupo_horario(self):
        pass

    def test_usuario_administrar_puede_modificar_grupo_horario(self):
        pass

    def test_usuario_sin_administracion_no_puede_crear_validacion_fecha_hora(self):
        pass

    def test_usuario_administrador_puede_crear_validacion_fecha_hora(self):
        pass

    def test_usuario_sin_administracion_no_puede_modificar_validacion_fecha_hora(self):
        pass

    def test_usuario_administrar_puede_modificar_validacion_fecha_hora(self):
        pass

    def test_creacion_validacion_entrante_crea_nodo_generico_correspondiente(self):
        pass

    def test_form_ivr_escoger_audio_ppal_sistema_coincide_tipo_audio_es_valido(self):
        pass

    def test_form_ivr_escoger_audio_ppal_sistema_no_coincide_tipo_audio_es_invalido(self):
        pass

    def test_form_ivr_escoger_audio_ppal_externo_coincide_tipo_audio_es_valido(self):
        pass

    def test_form_ivr_escoger_audio_ppal_externo_no_coincide_tipo_audio_es_invalido(self):
        pass

    def test_form_ivr_escoger_audio_time_out_sistema_coincide_tipo_audio_es_valido(self):
        pass

    def test_form_ivr_escoger_audio_time_out_sistema_no_coincide_tipo_audio_es_invalido(self):
        pass

    def test_form_ivr_escoger_audio_time_out_externo_coincide_tipo_audio_es_valido(self):
        pass

    def test_form_ivr_escoger_audio_time_out_externo_no_coincide_tipo_audio_es_invalido(self):
        pass

    def test_form_ivr_escoger_audio_destino_invalido_sistema_coincide_tipo_audio_es_valido(self):
        pass

    def test_form_ivr_escoger_audio_destino_invalido_sistema_no_coincide_tipo_audio_es_invalido(
            self):
        pass

    def test_form_ivr_escoger_audio_destino_invalido_externo_coincide_tipo_audio_es_valido(self):
        pass

    def test_form_ivr_escoger_audio_destino_invalido_externo_no_coincide_tipo_audio_es_invalido(
            self):
        pass

    def test_form_validacion_fecha_hora_destinos_distintos_es_valido(self):
        pass

    def test_form_validacion_fecha_hora_destinos_iguales_es_invalido(self):
        pass
