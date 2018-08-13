# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.utils.translation import ugettext as _

from io import BytesIO
from mock import patch

from django.core.urlresolvers import reverse

from configuracion_telefonia_app.forms import IVRForm
from configuracion_telefonia_app.models import (RutaEntrante, DestinoEntrante, IVR, GrupoHorario,
                                                ValidacionFechaHora)
from configuracion_telefonia_app.tests.factories import (
    RutaEntranteFactory, IVRFactory, OpcionDestinoFactory, ValidacionTiempoFactory,
    ValidacionFechaHoraFactory)

from ominicontacto_app.models import Campana
from ominicontacto_app.tests.factories import CampanaFactory, ArchivoDeAudioFactory
from ominicontacto_app.tests.utiles import OMLBaseTest


class TestsRutasEntrantes(OMLBaseTest):
    PWD = u'admin123'

    def setUp(self, *args, **kwargs):
        super(TestsRutasEntrantes, self).setUp(*args, **kwargs)

        self.admin = self.crear_administrador()
        self.admin.set_password(self.PWD)

        # Creo un Supervisor Normal
        self.usr_sup = self.crear_user_supervisor()
        self.crear_supervisor_profile(self.usr_sup)

        # Creo un Supervisor Customer
        self.usr_customer = self.crear_user_supervisor()
        self.crear_supervisor_profile(self.usr_customer, is_customer=True)

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

        self.validacion_tiempo = ValidacionTiempoFactory()
        self.grupo_horario = self.validacion_tiempo.grupo_horario

        self.validacion_fecha_hora = ValidacionFechaHoraFactory(grupo_horario=self.grupo_horario)
        self.destino_val_fecha_hora = DestinoEntrante.crear_nodo_ruta_entrante(
            self.validacion_fecha_hora)
        self.opc_dest_val_fecha_hora_true = OpcionDestinoFactory(
            valor=ValidacionFechaHora.DESTINO_MATCH, destino_anterior=self.destino_val_fecha_hora,
            destino_siguiente=self.destino_campana_entrante)
        self.opc_dest_val_fecha_hora_false = OpcionDestinoFactory(
            valor=ValidacionFechaHora.DESTINO_NO_MATCH,
            destino_anterior=self.destino_val_fecha_hora,
            destino_siguiente=self.destino_ivr)

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

    @patch('configuracion_telefonia_app.views.escribir_ruta_entrante_config')
    def test_usuario_administrador_puede_crear_ruta_entrante(self, escribir_ruta_entrante_config):
        url = reverse('crear_ruta_entrante')
        self.client.login(username=self.admin.username, password=self.PWD)
        post_data = self._obtener_post_data_ruta_entrante()
        n_rutas_entrantes = RutaEntrante.objects.count()
        self.client.post(url, post_data, follow=True)
        self.assertEqual(RutaEntrante.objects.count(), n_rutas_entrantes + 1)

    def test_usuario_sin_administracion_no_puede_modificar_ruta_entrante(self):
        nuevo_nombre = 'ruta_entrante_modificada'
        url = reverse('editar_ruta_entrante', args=[self.ruta_entrante.pk])
        self.client.login(username=self.usr_sup.username, password=self.PWD)
        post_data = self._obtener_post_data_ruta_entrante()
        post_data['id'] = self.ruta_entrante.pk
        post_data['nombre'] = nuevo_nombre
        self.client.post(url, post_data, follow=True)
        self.ruta_entrante.refresh_from_db()
        self.assertNotEqual(self.ruta_entrante.nombre, nuevo_nombre)

    @patch('configuracion_telefonia_app.views.escribir_ruta_entrante_config')
    def test_usuario_administrador_puede_modificar_ruta_entrante(
            self, escribir_ruta_entrante_config):
        nuevo_nombre = 'ruta_entrante_modificada'
        url = reverse('editar_ruta_entrante', args=[self.ruta_entrante.pk])
        self.client.login(username=self.admin.username, password=self.PWD)
        post_data = self._obtener_post_data_ruta_entrante()
        post_data['id'] = self.ruta_entrante.pk
        post_data['nombre'] = nuevo_nombre
        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.ruta_entrante.refresh_from_db()
        self.assertEqual(self.ruta_entrante.nombre, nuevo_nombre)

    def test_usuario_sin_administracion_no_puede_eliminar_ruta_entrante(self):
        url = reverse('eliminar_ruta_entrante', args=[self.ruta_entrante.pk])
        self.client.login(username=self.usr_sup.username, password=self.PWD)
        n_rutas_entrantes = RutaEntrante.objects.count()
        self.client.post(url, follow=True)
        self.assertEqual(RutaEntrante.objects.count(), n_rutas_entrantes)

    @patch('ominicontacto_app.services.asterisk_database.RutaEntranteFamily.delete_family')
    def test_usuario_administrador_puede_eliminar_ruta_entrante(
            self, eliminar_ruta_entrante_config):
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
        self.assertEqual(response.status_code, 403)
        self.assertEqual(IVR.objects.count(), n_ivrs)

    @patch('configuracion_telefonia_app.views.escribir_nodo_entrante_config')
    def test_usuario_administrador_puede_crear_ivr(self, escribir_nodo_entrante_config):
        url = reverse('crear_ivr')
        self.client.login(username=self.admin.username, password=self.PWD)
        post_data = self._obtener_post_data_ivr()
        n_ivrs = IVR.objects.count()
        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(IVR.objects.count(), n_ivrs + 1)

    def test_usuario_sin_administracion_no_puede_modificar_ivr(self):
        url = reverse('editar_ivr', args=[self.ivr.pk])
        nuevo_nombre = 'ivr_modificado'
        self.client.login(username=self.usr_sup.username, password=self.PWD)
        post_data = self._obtener_post_data_ivr()
        post_data['nombre'] = nuevo_nombre
        post_data['ivr-0-id'] = self.opc_dest_ivr_camp_entrante_1.pk
        post_data['ivr-1-id'] = self.opc_dest_ivr_ivr_2.pk
        post_data['ivr-INITIAL_FORMS'] = 2
        self.client.post(url, post_data, follow=True)
        self.ivr.refresh_from_db()
        self.assertNotEqual(self.ivr.nombre, nuevo_nombre)

    @patch('configuracion_telefonia_app.views.escribir_nodo_entrante_config')
    def test_usuario_administrar_puede_modificar_ivr(self, escribir_nodo_entrante_config):
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

    @patch('configuracion_telefonia_app.views.escribir_nodo_entrante_config')
    def test_creacion_ivr_crea_nodo_generico_correspondiente(self, escribir_nodo_entrante_config):
        url = reverse('crear_ivr')
        self.client.login(username=self.admin.username, password=self.PWD)
        post_data = self._obtener_post_data_ivr()
        n_dests_ivrs = DestinoEntrante.objects.filter(tipo=DestinoEntrante.IVR).count()
        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            DestinoEntrante.objects.filter(tipo=DestinoEntrante.IVR).count(), n_dests_ivrs + 1)

    def _obtener_post_data_grupo_horario(self):
        return {
            'nombre': 'grupo_horario',
            'validacion_tiempo-0-tiempo_inicial': '15:45',
            'validacion_tiempo-0-tiempo_final': '15:45',
            'validacion_tiempo-0-dia_semana_inicial': '1',
            'validacion_tiempo-0-dia_semana_final': '0',
            'validacion_tiempo-0-dia_mes_inicio': '14',
            'validacion_tiempo-0-dia_mes_final': '17',
            'validacion_tiempo-0-mes_inicio': '10',
            'validacion_tiempo-0-mes_final': '12',
            'validacion_tiempo-0-id': '',
            'validacion_tiempo-TOTAL_FORMS': '1',
            'validacion_tiempo-INITIAL_FORMS': '0',
            'validacion_tiempo-MIN_NUM_FORMS': '1',
            'validacion_tiempo-MAX_NUM_FORMS': '1000',
        }

    def test_usuario_customer_no_puede_crear_grupo_horario(self):
        url = reverse('crear_grupo_horario')
        self.client.login(username=self.usr_customer.username, password=self.PWD)
        post_data = self._obtener_post_data_grupo_horario()
        n_grupos_horarios = GrupoHorario.objects.count()
        self.client.post(url, post_data, follow=True)
        self.assertEqual(GrupoHorario.objects.count(), n_grupos_horarios)

    @patch('ominicontacto_app.services.asterisk_database.GrupoHorarioFamily.regenerar_family')
    def test_usuario_supervisor_puede_crear_grupo_horario(self, regenerar_family):
        url = reverse('crear_grupo_horario')
        self.client.login(username=self.usr_sup.username, password=self.PWD)
        post_data = self._obtener_post_data_grupo_horario()
        n_grupos_horarios = GrupoHorario.objects.count()
        self.client.post(url, post_data, follow=True)
        self.assertEqual(GrupoHorario.objects.count(), n_grupos_horarios + 1)

    @patch('ominicontacto_app.services.asterisk_database.GrupoHorarioFamily.regenerar_family')
    def test_usuario_administrador_puede_crear_grupo_horario(self, regenerar_family):
        url = reverse('crear_grupo_horario')
        self.client.login(username=self.admin.username, password=self.PWD)
        post_data = self._obtener_post_data_grupo_horario()
        n_grupos_horarios = GrupoHorario.objects.count()
        self.client.post(url, post_data, follow=True)
        self.assertEqual(GrupoHorario.objects.count(), n_grupos_horarios + 1)

    @patch('ominicontacto_app.services.asterisk_database.GrupoHorarioFamily.regenerar_family')
    def test_usuario_customer_no_puede_modificar_grupo_horario(self, regenerar_family):
        url = reverse('editar_grupo_horario', args=[self.grupo_horario.pk])
        nuevo_nombre = 'grupo_horario_modificado'
        self.client.login(username=self.usr_customer.username, password=self.PWD)
        post_data = self._obtener_post_data_grupo_horario()
        post_data['nombre'] = nuevo_nombre
        post_data['validacion_tiempo-0-id'] = self.validacion_tiempo.pk
        post_data['validacion_tiempo-INITIAL_FORMS'] = 1
        self.client.post(url, post_data, follow=True)
        self.grupo_horario.refresh_from_db()
        self.assertNotEqual(self.grupo_horario.nombre, nuevo_nombre)

    @patch('ominicontacto_app.services.asterisk_database.GrupoHorarioFamily.regenerar_family')
    def test_usuario_supervisor_puede_modificar_grupo_horario(self, regenerar_family):
        url = reverse('editar_grupo_horario', args=[self.grupo_horario.pk])
        nuevo_nombre = 'grupo_horario_modificado'
        self.client.login(username=self.usr_sup.username, password=self.PWD)
        post_data = self._obtener_post_data_grupo_horario()
        post_data['nombre'] = nuevo_nombre
        post_data['validacion_tiempo-0-id'] = self.validacion_tiempo.pk
        post_data['validacion_tiempo-INITIAL_FORMS'] = 1
        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.grupo_horario.refresh_from_db()
        self.assertEqual(self.grupo_horario.nombre, nuevo_nombre)

    @patch('ominicontacto_app.services.asterisk_database.GrupoHorarioFamily.regenerar_family')
    def test_usuario_administrador_puede_modificar_grupo_horario(self, regenerar_family):
        url = reverse('editar_grupo_horario', args=[self.grupo_horario.pk])
        nuevo_nombre = 'grupo_horario_modificado'
        self.client.login(username=self.admin.username, password=self.PWD)
        post_data = self._obtener_post_data_grupo_horario()
        post_data['nombre'] = nuevo_nombre
        post_data['validacion_tiempo-0-id'] = self.validacion_tiempo.pk
        post_data['validacion_tiempo-INITIAL_FORMS'] = 1
        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.grupo_horario.refresh_from_db()
        self.assertEqual(self.grupo_horario.nombre, nuevo_nombre)

    def _obtener_post_data_validacion_fecha_hora(self):
        return {
            'nombre': 'val1',
            'grupo_horario': self.grupo_horario.pk,
            'validacion_fecha_hora-0-valor': 'True',
            'validacion_fecha_hora-0-id': '',
            'validacion_fecha_hora-0-tipo_destino': self.destino_campana_entrante.tipo,
            'validacion_fecha_hora-0-destino_siguiente': self.destino_campana_entrante.pk,
            'validacion_fecha_hora-1-valor': 'False',
            'validacion_fecha_hora-1-id': '',
            'validacion_fecha_hora-1-tipo_destino': self.destino_ivr.tipo,
            'validacion_fecha_hora-1-destino_siguiente': self.destino_ivr.pk,
            'validacion_fecha_hora-TOTAL_FORMS': '2',
            'validacion_fecha_hora-INITIAL_FORMS': '0',
            'validacion_fecha_hora-MIN_NUM_FORMS': '2',
            'validacion_fecha_hora-MAX_NUM_FORMS': '2',
        }

    def test_usuario_customer_no_puede_crear_validacion_fecha_hora(self):
        url = reverse('crear_validacion_fecha_hora')
        self.client.login(username=self.usr_customer.username, password=self.PWD)
        post_data = self._obtener_post_data_validacion_fecha_hora()
        n_validaciones_fecha_hora = ValidacionFechaHora.objects.count()
        self.client.post(url, post_data, follow=True)
        self.assertEqual(ValidacionFechaHora.objects.count(), n_validaciones_fecha_hora)

    @patch('configuracion_telefonia_app.views.escribir_nodo_entrante_config')
    def test_usuario_supervisor_puede_crear_validacion_fecha_hora(
            self, escribir_nodo_entrante_config):
        url = reverse('crear_validacion_fecha_hora')
        self.client.login(username=self.usr_sup.username, password=self.PWD)
        post_data = self._obtener_post_data_validacion_fecha_hora()
        n_validaciones_fecha_hora = ValidacionFechaHora.objects.count()
        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ValidacionFechaHora.objects.count(), n_validaciones_fecha_hora + 1)

    @patch('configuracion_telefonia_app.views.escribir_nodo_entrante_config')
    def test_usuario_administrador_puede_crear_validacion_fecha_hora(
            self, escribir_nodo_entrante_config):
        url = reverse('crear_validacion_fecha_hora')
        self.client.login(username=self.admin.username, password=self.PWD)
        post_data = self._obtener_post_data_validacion_fecha_hora()
        n_validaciones_fecha_hora = ValidacionFechaHora.objects.count()
        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ValidacionFechaHora.objects.count(), n_validaciones_fecha_hora + 1)

    def test_usuario_customer_no_puede_modificar_validacion_fecha_hora(self):
        nuevo_nombre = 'validacion_fecha_hora_modificada'
        url = reverse('editar_validacion_fecha_hora', args=[self.validacion_fecha_hora.pk])
        self.client.login(username=self.usr_customer.username, password=self.PWD)
        post_data = self._obtener_post_data_validacion_fecha_hora()
        post_data['nombre'] = nuevo_nombre
        post_data['validacion_fecha_hora-0-id'] = self.opc_dest_val_fecha_hora_true.pk
        post_data['validacion_fecha_hora-1-id'] = self.opc_dest_val_fecha_hora_false.pk
        self.client.post(url, post_data, follow=True)
        self.validacion_fecha_hora.refresh_from_db()
        self.assertNotEqual(self.validacion_fecha_hora.nombre, nuevo_nombre)

    @patch('configuracion_telefonia_app.views.escribir_nodo_entrante_config')
    def test_usuario_supervisor_puede_modificar_validacion_fecha_hora(
            self, escribir_nodo_entrante_config):
        nuevo_nombre = 'validacion_fecha_hora_modificada'
        url = reverse('editar_validacion_fecha_hora', args=[self.validacion_fecha_hora.pk])
        self.client.login(username=self.usr_sup.username, password=self.PWD)
        post_data = self._obtener_post_data_validacion_fecha_hora()
        post_data['nombre'] = nuevo_nombre
        post_data['validacion_fecha_hora-0-id'] = self.opc_dest_val_fecha_hora_true.pk
        post_data['validacion_fecha_hora-1-id'] = self.opc_dest_val_fecha_hora_false.pk
        post_data['validacion_fecha_hora-INITIAL_FORMS'] = 2
        self.client.post(url, post_data, follow=True)
        self.validacion_fecha_hora.refresh_from_db()
        self.assertEqual(self.validacion_fecha_hora.nombre, nuevo_nombre)

    @patch('configuracion_telefonia_app.views.escribir_nodo_entrante_config')
    def test_usuario_administrar_puede_modificar_validacion_fecha_hora(
            self, escribir_nodo_entrante_config):
        nuevo_nombre = 'validacion_fecha_hora_modificada'
        url = reverse('editar_validacion_fecha_hora', args=[self.validacion_fecha_hora.pk])
        self.client.login(username=self.admin.username, password=self.PWD)
        post_data = self._obtener_post_data_validacion_fecha_hora()
        post_data['nombre'] = nuevo_nombre
        post_data['validacion_fecha_hora-0-id'] = self.opc_dest_val_fecha_hora_true.pk
        post_data['validacion_fecha_hora-1-id'] = self.opc_dest_val_fecha_hora_false.pk
        post_data['validacion_fecha_hora-INITIAL_FORMS'] = 2
        self.client.post(url, post_data, follow=True)
        self.validacion_fecha_hora.refresh_from_db()
        self.assertEqual(self.validacion_fecha_hora.nombre, nuevo_nombre)

    @patch('configuracion_telefonia_app.views.escribir_nodo_entrante_config')
    def test_creacion_validacion_fecha_hora_crea_nodo_generico_correspondiente(
            self, escribir_nodo_entrante_config):
        url = reverse('crear_validacion_fecha_hora')
        self.client.login(username=self.admin.username, password=self.PWD)
        post_data = self._obtener_post_data_validacion_fecha_hora()
        n_dests_validaciones_fecha_hora = DestinoEntrante.objects.filter(
            tipo=DestinoEntrante.VALIDACION_FECHA_HORA).count()
        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            DestinoEntrante.objects.filter(tipo=DestinoEntrante.VALIDACION_FECHA_HORA).count(),
            n_dests_validaciones_fecha_hora + 1)

    def test_form_validacion_fecha_hora_destinos_iguales_es_invalido(self):
        url = reverse('crear_validacion_fecha_hora')
        self.client.login(username=self.admin.username, password=self.PWD)
        post_data = self._obtener_post_data_validacion_fecha_hora()
        post_data['validacion_fecha_hora-0-destino_siguiente'] = self.destino_campana_entrante.pk,
        post_data['validacion_fecha_hora-1-destino_siguiente'] = self.destino_campana_entrante.pk,
        response = self.client.post(url, post_data, follow=True)
        self.assertFalse(response.context['validacion_fecha_hora_formset'].is_valid())

    def test_form_ivr_escoger_audio_ppal_externo_no_coincide_tipo_audio_es_invalido(self):
        url = reverse('crear_ivr')
        self.client.login(username=self.admin.username, password=self.PWD)
        post_data = self._obtener_post_data_ivr()
        post_data['audio_ppal_escoger'] = IVRForm.AUDIO_EXTERNO
        img = BytesIO(b'mybinarydata')
        img.name = 'myimage.jpg'
        post_data['audio_ppal_ext_audio'] = img
        response = self.client.post(url, post_data, follow=True)
        self.assertFalse(response.context['form'].is_valid())
        self.assertContains(response, _('Archivos permitidos: .wav'))

    def test_form_ivr_escoger_audio_time_out_externo_no_coincide_tipo_audio_es_invalido(self):
        url = reverse('crear_ivr')
        self.client.login(username=self.admin.username, password=self.PWD)
        post_data = self._obtener_post_data_ivr()
        post_data['time_out_audio_escoger'] = IVRForm.AUDIO_EXTERNO
        img = BytesIO(b'mybinarydata')
        img.name = 'myimage.jpg'
        post_data['time_out_ext_audio'] = img
        response = self.client.post(url, post_data, follow=True)
        self.assertFalse(response.context['form'].is_valid())
        self.assertContains(response, _('Archivos permitidos: .wav'))

    def test_form_ivr_escoger_audio_destino_invalido_externo_no_coincide_tipo_audio_es_invalido(
            self):
        url = reverse('crear_ivr')
        self.client.login(username=self.admin.username, password=self.PWD)
        post_data = self._obtener_post_data_ivr()
        post_data['invalid_destination_audio_escoger'] = IVRForm.AUDIO_EXTERNO
        img = BytesIO(b'mybinarydata')
        img.name = 'myimage.jpg'
        post_data['invalid_destination_ext_audio'] = img
        response = self.client.post(url, post_data, follow=True)
        self.assertFalse(response.context['form'].is_valid())
        self.assertContains(response, _('Archivos permitidos: .wav'))
