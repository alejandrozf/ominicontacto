# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3, as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

from __future__ import unicode_literals
from django.utils.translation import gettext as _

from mock import patch

from django.urls import reverse

from configuracion_telefonia_app.models import (RutaEntrante, DestinoEntrante, IVR,
                                                ValidacionFechaHora)
from configuracion_telefonia_app.tests.factories import (
    RutaEntranteFactory, IVRFactory, OpcionDestinoFactory, ValidacionTiempoFactory,
    ValidacionFechaHoraFactory)

from ominicontacto_app.models import Campana, User
from ominicontacto_app.tests.factories import CampanaFactory, ArchivoDeAudioFactory
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD


class TestsRutasEntrantes(OMLBaseTest):

    def setUp(self, *args, **kwargs):
        super(TestsRutasEntrantes, self).setUp(*args, **kwargs)

        self.admin = self.crear_administrador()

        # Creo un Supervisor Normal
        self.supervisor = self.crear_supervisor_profile(rol=User.SUPERVISOR)
        self.usr_sup = self.supervisor.user

        # Creo un Supervisor Customer
        self.referente = self.crear_supervisor_profile(rol=User.REFERENTE)
        self.usr_referente = self.referente.user

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
        self.actualizar_permisos()
        url = reverse('crear_validacion_fecha_hora')
        self.client.login(username=self.usr_referente.username, password=PASSWORD)
        post_data = self._obtener_post_data_validacion_fecha_hora()
        n_validaciones_fecha_hora = ValidacionFechaHora.objects.count()
        self.client.post(url, post_data, follow=True)
        self.assertEqual(ValidacionFechaHora.objects.count(), n_validaciones_fecha_hora)

    @patch('configuracion_telefonia_app.views.base.escribir_nodo_entrante_config')
    def test_usuario_supervisor_puede_crear_validacion_fecha_hora(
            self, escribir_nodo_entrante_config):
        self.actualizar_permisos()
        url = reverse('crear_validacion_fecha_hora')
        self.client.login(username=self.usr_sup.username, password=PASSWORD)
        post_data = self._obtener_post_data_validacion_fecha_hora()
        n_validaciones_fecha_hora = ValidacionFechaHora.objects.count()
        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ValidacionFechaHora.objects.count(), n_validaciones_fecha_hora + 1)

    @patch('configuracion_telefonia_app.views.base.escribir_nodo_entrante_config')
    def test_usuario_administrador_puede_crear_validacion_fecha_hora(
            self, escribir_nodo_entrante_config):
        self.actualizar_permisos()
        url = reverse('crear_validacion_fecha_hora')
        self.client.login(username=self.admin.username, password=PASSWORD)
        post_data = self._obtener_post_data_validacion_fecha_hora()
        n_validaciones_fecha_hora = ValidacionFechaHora.objects.count()
        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ValidacionFechaHora.objects.count(), n_validaciones_fecha_hora + 1)

    def test_usuario_customer_no_puede_modificar_validacion_fecha_hora(self):
        self.actualizar_permisos()
        nuevo_nombre = 'validacion_fecha_hora_modificada'
        url = reverse('editar_validacion_fecha_hora', args=[self.validacion_fecha_hora.pk])
        self.client.login(username=self.usr_referente.username, password=PASSWORD)
        post_data = self._obtener_post_data_validacion_fecha_hora()
        post_data['nombre'] = nuevo_nombre
        post_data['validacion_fecha_hora-0-id'] = self.opc_dest_val_fecha_hora_true.pk
        post_data['validacion_fecha_hora-1-id'] = self.opc_dest_val_fecha_hora_false.pk
        self.client.post(url, post_data, follow=True)
        self.validacion_fecha_hora.refresh_from_db()
        self.assertNotEqual(self.validacion_fecha_hora.nombre, nuevo_nombre)

    @patch('configuracion_telefonia_app.views.base.escribir_nodo_entrante_config')
    def test_usuario_supervisor_puede_modificar_validacion_fecha_hora(
            self, escribir_nodo_entrante_config):
        self.actualizar_permisos()
        nuevo_nombre = 'validacion_fecha_hora_modificada'
        url = reverse('editar_validacion_fecha_hora', args=[self.validacion_fecha_hora.pk])
        self.client.login(username=self.usr_sup.username, password=PASSWORD)
        post_data = self._obtener_post_data_validacion_fecha_hora()
        post_data['nombre'] = nuevo_nombre
        post_data['validacion_fecha_hora-0-id'] = self.opc_dest_val_fecha_hora_true.pk
        post_data['validacion_fecha_hora-1-id'] = self.opc_dest_val_fecha_hora_false.pk
        post_data['validacion_fecha_hora-INITIAL_FORMS'] = 2
        self.client.post(url, post_data, follow=True)
        self.validacion_fecha_hora.refresh_from_db()
        self.assertEqual(self.validacion_fecha_hora.nombre, nuevo_nombre)

    @patch('configuracion_telefonia_app.views.base.escribir_nodo_entrante_config')
    def test_usuario_administrar_puede_modificar_validacion_fecha_hora(
            self, escribir_nodo_entrante_config):
        self.actualizar_permisos()
        nuevo_nombre = 'validacion_fecha_hora_modificada'
        url = reverse('editar_validacion_fecha_hora', args=[self.validacion_fecha_hora.pk])
        self.client.login(username=self.admin.username, password=PASSWORD)
        post_data = self._obtener_post_data_validacion_fecha_hora()
        post_data['nombre'] = nuevo_nombre
        post_data['validacion_fecha_hora-0-id'] = self.opc_dest_val_fecha_hora_true.pk
        post_data['validacion_fecha_hora-1-id'] = self.opc_dest_val_fecha_hora_false.pk
        post_data['validacion_fecha_hora-INITIAL_FORMS'] = 2
        self.client.post(url, post_data, follow=True)
        self.validacion_fecha_hora.refresh_from_db()
        self.assertEqual(self.validacion_fecha_hora.nombre, nuevo_nombre)

    @patch('configuracion_telefonia_app.views.base.escribir_nodo_entrante_config')
    def test_creacion_validacion_fecha_hora_crea_nodo_generico_correspondiente(
            self, escribir_nodo_entrante_config):
        url = reverse('crear_validacion_fecha_hora')
        self.client.login(username=self.admin.username, password=PASSWORD)
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
        self.client.login(username=self.admin.username, password=PASSWORD)
        post_data = self._obtener_post_data_validacion_fecha_hora()
        post_data['validacion_fecha_hora-0-destino_siguiente'] = self.destino_campana_entrante.pk,
        post_data['validacion_fecha_hora-1-destino_siguiente'] = self.destino_campana_entrante.pk,
        response = self.client.post(url, post_data, follow=True)
        self.assertFalse(response.context['validacion_fecha_hora_formset'].is_valid())

    def test_no_se_permite_crear_destino_nombre_no_alfanumerico(self):
        url = reverse('crear_destino_personalizado')
        self.client.login(username=self.admin.username, password=PASSWORD)
        post_data = {
            'nombre': 'aaa bb',
            'custom_destination': 'bbb',
            'failover_form-valor': 'failover',
            'failover_form-tipo_destino': 1,
            'failover_form-destino_siguiente': 1}
        response = self.client.post(url, post_data, follow=True)
        self.assertFalse(response.context['form'].is_valid())
        self.assertEqual(response.context['form'].errors['nombre'],
                         [_('Introduzca un valor válido.')])

    def test_no_se_permite_crear_destino_custom_destino_no_alfanumerico(self):
        url = reverse('crear_destino_personalizado')
        self.client.login(username=self.admin.username, password=PASSWORD)
        post_data = {
            'nombre': 'aaabb',
            'custom_destination': 'bbb aaa',
            'failover_form-valor': 'failover',
            'failover_form-tipo_destino': 1,
            'failover_form-destino_siguiente': 1}
        response = self.client.post(url, post_data, follow=True)
        self.assertFalse(response.context['form'].is_valid())
        self.assertEqual(response.context['form'].errors['custom_destination'],
                         [_('Introduzca un valor válido.')])

    def test_no_se_permite_crear_destino_custom_sin_failover(self):
        url = reverse('crear_destino_personalizado')
        self.client.login(username=self.admin.username, password=PASSWORD)
        post_data = {
            'nombre': 'aaabb',
            'custom_destination': 'bbbaaa'}
        response = self.client.post(url, post_data, follow=True)
        self.assertFalse(response.context['opcion_destino_failover_form'].is_valid())
        error = response.context['opcion_destino_failover_form'].errors['destino_siguiente']
        self.assertEqual(error, [_('Este campo es requerido.')])
