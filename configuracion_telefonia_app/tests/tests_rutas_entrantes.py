# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from configuracion_telefonia_app.models import RutaEntrante, DestinoEntrante, IVR
from configuracion_telefonia_app.tests.factories import (RutaEntranteFactory, IVRFactory,
                                                         OpcionDestinoFactory)

from ominicontacto_app.models import Campana
from ominicontacto_app.tests.factories import CampanaFactory, ArchivoDeAudioFactory
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

        self.ivr = IVRFactory()
        self.destino_ivr = DestinoEntrante.crear_nodo_ruta_entrante(self.ivr)

        self.opc_dest_ivr_time_out = OpcionDestinoFactory(
            valor=IVR.VALOR_TIME_OUT, destino_anterior=self.destino_ivr,
            destino_siguiente=self.destino_campana_entrante)
        self.opc_dest_ivr_invalid = OpcionDestinoFactory(
            valor=IVR.VALOR_DESTINO_INVALIDO, destino_anterior=self.destino_ivr,
            destino_siguiente=self.destino_ivr)
        self.opc_dest_ivr_camp_entrante_1 = OpcionDestinoFactory(
            valor='1', destino_anterior=self.destino_ivr,
            destino_siguiente=self.destino_campana_entrante)
        self.opc_dest_ivr_ivr_2 = OpcionDestinoFactory(
            valor='2', destino_anterior=self.destino_ivr, destino_siguiente=self.destino_ivr)

        self.archivo_audio = ArchivoDeAudioFactory()

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
        url = reverse('eliminar_ruta_entrante', args=[self.ruta_entrante.pk])
        self.client.login(username=self.usr_sup.username, password=self.PWD)
        n_rutas_entrantes = RutaEntrante.objects.count()
        self.client.post(url, follow=True)
        self.assertEqual(RutaEntrante.objects.count(), n_rutas_entrantes)

    def test_usuario_administrador_puede_eliminar_ruta_entrante(self):
        url = reverse('eliminar_ruta_entrante', args=[self.ruta_entrante.pk])
        self.client.login(username=self.admin.username, password=self.PWD)
        n_rutas_entrantes = RutaEntrante.objects.count()
        self.client.post(url, follow=True)
        self.assertEqual(RutaEntrante.objects.count(), n_rutas_entrantes - 1)

    def _obtener_post_data_ivr(self):
        return {
            'nombre': 'nombre',
            'descripcion': 'descripcion',
            'audio_ppal_escoger': 1,
            'audio_principal': self.archivo_audio.pk,
            'audio_ppal_ext_audio': '',
            'time_out': 1,
            'time_out_retries': 1,
            'time_out_audio_escoger': 1,
            'time_out_audio': self.archivo_audio.pk,
            'time_out_ext_audio': '',
            'time_out_destination_type': self.destino_campana_entrante.tipo,
            'time_out_destination': self.destino_campana_entrante.pk,
            'invalid_retries': 1,
            'invalid_destination_audio_escoger': 1,
            'invalid_audio': self.archivo_audio.pk,
            'invalid_destination_ext_audio': '',
            'invalid_destination_type': self.destino_ivr.tipo,
            'invalid_destination': self.destino_ivr.pk,
            'ivr-0-valor': 1,
            'ivr-0-tipo_destino': self.destino_campana_entrante.tipo,
            'ivr-0-destino_siguiente': self.destino_campana_entrante.pk,
            'ivr-0-id': '',
            'ivr-1-valor': 2,
            'ivr-1-tipo_destino': self.destino_ivr.tipo,
            'ivr-1-destino_siguiente': self.destino_ivr.pk,
            'ivr-1-id': '',
            'ivr-TOTAL_FORMS': 2,
            'ivr-INITIAL_FORMS': 0,
            'ivr-MIN_NUM_FORMS': 0,
            'ivr-MAX_NUM_FORMS': 1000
        }

    def test_usuario_sin_administracion_no_puede_crear_ivr(self):
        url = reverse('crear_ivr')
        self.client.login(username=self.usr_sup.username, password=self.PWD)
        post_data = self._obtener_post_data_ivr()
        n_ivrs = IVR.objects.count()
        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(IVR.objects.count(), n_ivrs)

    def test_usuario_administrador_puede_crear_ivr(self):
        url = reverse('crear_ivr')
        self.client.login(username=self.admin.username, password=self.PWD)
        post_data = self._obtener_post_data_ivr()
        n_ivrs = IVR.objects.count()
        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(IVR.objects.count(), n_ivrs + 1)

    def test_usuario_sin_administracion_no_puede_modificar_ivr(self):
        url = reverse('editar_ivr', args=[self.ivr.pk])
        self.client.login(username=self.usr_sup.username, password=self.PWD)
        post_data = self._obtener_post_data_ivr()
        n_ivrs = IVR.objects.count()
        self.client.post(url, post_data, follow=True)
        self.assertEqual(IVR.objects.count(), n_ivrs)

    def test_usuario_administrar_puede_modificar_ivr(self):
        url = reverse('editar_ivr', args=[self.ivr.pk])
        nuevo_nombre = 'ivr_modificado'
        self.client.login(username=self.admin.username, password=self.PWD)
        post_data = self._obtener_post_data_ivr()
        post_data['nombre'] = nuevo_nombre
        post_data['ivr-0-id'] = self.opc_dest_ivr_camp_entrante_1.pk
        post_data['ivr-1-id'] = self.opc_dest_ivr_ivr_2.pk
        post_data['ivr-INITIAL_FORMS'] = 2
        self.client.post(url, post_data, follow=True)
        self.ivr.refresh_from_db()
        self.assertEqual(self.ivr.nombre, nuevo_nombre)

    def test_creacion_ivr_crea_nodo_generico_correspondiente(self):
        url = reverse('crear_ivr')
        self.client.login(username=self.admin.username, password=self.PWD)
        post_data = self._obtener_post_data_ivr()
        n_dests_ivrs = DestinoEntrante.objects.filter(tipo=DestinoEntrante.IVR).count()
        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(
            DestinoEntrante.objects.filter(tipo=DestinoEntrante.IVR).count(), n_dests_ivrs + 1)

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
