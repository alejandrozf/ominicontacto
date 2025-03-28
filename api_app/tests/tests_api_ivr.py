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
from __future__ import unicode_literals
from io import BytesIO

import json
from mock import patch
from django.utils.translation import ugettext as _
from django.urls import reverse
from configuracion_telefonia_app.models import IVR, DestinoEntrante, OpcionDestino
from configuracion_telefonia_app.tests.factories import (
    DestinoPersonalizadoFactory,
    IVRFactory,
    IdentificadorClienteFactory,
    OpcionDestinoFactory,
    RutaEntranteFactory,
    ValidacionFechaHoraFactory,
    DestinoEntranteFactory
)
from ominicontacto_app.tests.factories import (
    ArchivoDeAudioFactory, CampanaFactory, AgenteProfileFactory
)
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.models import Campana, User


class APITest(OMLBaseTest):
    """Tests para los Endpoints del API IVRs"""
    SUCCESS = 'SUCCESS'
    ERROR = 'ERROR'
    # Actions
    CREATE = 1
    UPDATE = 2
    # Audio selected
    MAIN_AUDIO = 1
    TIME_OUT_AUDIO = 2
    INVALID_AUDIO = 3
    # Fixed destinations
    TIME_OUT_DEST = 1
    INVALID_DEST = 2
    # Destination Types
    CAMPAIGN = 1
    VALIDATION_DATE = 2
    IVR = 3
    HANGUP = 5
    ID_CLIENT = 9
    CUSTOM_DST = 7
    INTERNAL_AUDIO = 1
    EXTERNAL_AUDIO = 2

    def _get_local_destination_options(self, nodo_ivr):
        valores_fijos_ivr = (IVR.VALOR_TIME_OUT, IVR.VALOR_DESTINO_INVALIDO)
        return nodo_ivr.destinos_siguientes.exclude(valor__in=valores_fijos_ivr)

    def _set_fixed_destinations(self, nodo_ivr, data=None, option=1):
        if data is not None:
            time_out_destination_new = DestinoEntrante.objects.get(pk=data['time_out_destination'])
            invalid_destination_new = DestinoEntrante.objects.get(pk=data['invalid_destination'])
            if option is self.CREATE:
                OpcionDestino.crear_opcion_destino(
                    nodo_ivr, time_out_destination_new, IVR.VALOR_TIME_OUT)
                OpcionDestino.crear_opcion_destino(
                    nodo_ivr, invalid_destination_new, IVR.VALOR_DESTINO_INVALIDO)
            elif option is self.UPDATE:
                time_out = nodo_ivr.destinos_siguientes.get(valor=IVR.VALOR_TIME_OUT)
                invalid_destination = nodo_ivr.destinos_siguientes.get(
                    valor=IVR.VALOR_DESTINO_INVALIDO)
                time_out.destino_siguiente = time_out_destination_new
                invalid_destination.destino_siguiente = invalid_destination_new
                time_out.save()
                invalid_destination.save()

    def _set_destination_options(self, nodo_ivr, destination_options):
        local_destination_options = self._get_local_destination_options(nodo_ivr)
        actuales_ids = list(local_destination_options.values_list('id', flat=True))
        nuevos_ids = []
        for destination in destination_options:
            dtmf = destination['dtmf']
            opcion_destino_id = destination['id']
            destino_id = destination['destination']
            destino_siguiente = DestinoEntrante.objects.get(pk=destino_id)
            # Update
            if opcion_destino_id is not None:
                nuevos_ids.append(opcion_destino_id)
                opcion_destino = OpcionDestino.objects.get(pk=opcion_destino_id)
                opcion_destino.valor = dtmf
                opcion_destino.destino_siguiente = destino_siguiente
                opcion_destino.destino_anterior = nodo_ivr
                opcion_destino.save()
            # Create
            else:
                OpcionDestino.objects.create(
                    valor=dtmf,
                    destino_siguiente=destino_siguiente,
                    destino_anterior=nodo_ivr
                )
        diference_ids = list(set(actuales_ids) - set(nuevos_ids))
        OpcionDestino.objects.filter(pk__in=diference_ids).delete()

    def _crear_nodos_para_destinos(self):
        self.validacion_fh = ValidacionFechaHoraFactory()
        self.campana = CampanaFactory(type=Campana.TYPE_ENTRANTE, estado=Campana.ESTADO_ACTIVA)
        self.client_id = IdentificadorClienteFactory()
        self.destino_personalizado = DestinoPersonalizadoFactory()
        self.nodo_validacion = DestinoEntrante.crear_nodo_ruta_entrante(self.validacion_fh)
        self.nodo_campana = DestinoEntrante.crear_nodo_ruta_entrante(self.campana)
        self.nodo_client_id = DestinoEntrante.crear_nodo_ruta_entrante(self.client_id)
        self.nodo_destino_personalizado = DestinoEntrante.crear_nodo_ruta_entrante(
            self.destino_personalizado)

    def _crear_ivr(self, nodo_destino):
        ivr = IVRFactory()
        nodo_ivr = DestinoEntrante.crear_nodo_ruta_entrante(ivr)
        nodo_ivr.content_object = ivr
        nodo_ivr.save()
        destination_options = [
            {
                "id": None,
                "dtmf": "1",
                "destination_type": nodo_destino.tipo,
                "destination": nodo_destino.pk
            }
        ]
        fixed_destinations = {
            "time_out_destination": nodo_destino.pk,
            "time_out_destination_type": nodo_destino.tipo,
            "invalid_destination": nodo_destino.pk,
            "invalid_destination_type": nodo_destino.tipo
        }
        self._set_fixed_destinations(nodo_ivr, data=fixed_destinations, option=self.CREATE)
        self._set_destination_options(nodo_ivr, destination_options)
        return ivr

    def _get_ivr_form_data(self):
        return {
            'id': 'null',
            'nombre': 'IVR Create',
            'descripcion': 'IVR Description',
            'time_out': 10,
            'time_out_retries': 5,
            'invalid_retries': 3,
            'main_audio': self.audio_1.pk,
            'time_out_audio': self.audio_2.pk,
            'invalid_audio': self.audio_3.pk,
            'type_main_audio': self.INTERNAL_AUDIO,
            'type_time_out_audio': self.INTERNAL_AUDIO,
            'type_invalid_audio': self.INTERNAL_AUDIO,
            'main_audio_ext': 'null',
            'time_out_audio_ext': 'null',
            'invalid_audio_ext': 'null',
            'time_out_destination': self.nodo_campana.pk,
            'time_out_destination_type': self.nodo_campana.tipo,
            'invalid_destination': self.nodo_validacion.pk,
            'invalid_destination_type': self.nodo_validacion.tipo,
            'destination_options': json.dumps([
                {
                    "id": None,
                    "dtmf": "1",
                    "destination_type": self.nodo_campana.tipo,
                    "destination": self.nodo_campana.pk
                },
                {
                    "id": None,
                    "dtmf": "2",
                    "destination_type": self.nodo_destino_personalizado.tipo,
                    "destination": self.nodo_destino_personalizado.pk
                },
                {
                    "id": None,
                    "dtmf": "3",
                    "destination_type": self.nodo_client_id.tipo,
                    "destination": self.nodo_client_id.pk
                }
            ])
        }

    def setUp(self):
        super(APITest, self).setUp()
        usr_supervisor = self.crear_user_supervisor(username='sup1')
        self.crear_supervisor_profile(user=usr_supervisor, rol=User.SUPERVISOR)
        self.client.login(username=usr_supervisor.username, password=PASSWORD)
        self._crear_nodos_para_destinos()
        self.ivr = self._crear_ivr(self.nodo_campana)
        self.audio_1 = ArchivoDeAudioFactory(audio_asterisk='oml/audio_1')
        self.audio_2 = ArchivoDeAudioFactory(audio_asterisk='oml/audio_2')
        self.audio_3 = ArchivoDeAudioFactory(audio_asterisk='oml/audio_3')
        self.img = BytesIO(b'mybinarydata')
        self.img.name = 'myimage.jpg'
        self.urls_api = {
            'List': 'api_ivrs_list',
            'Create': 'api_ivrs_create',
            'Detail': 'api_ivrs_detail',
            'Update': 'api_ivrs_update',
            'Delete': 'api_ivrs_delete'
        }


class IVRTest(APITest):
    def test_listar_ivrs(self):
        URL = reverse(self.urls_api['List'])
        response = self.client.get(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], self.SUCCESS)
        self.assertEqual(
            response_json['message'],
            _('Se obtuvieron los IVRs de forma exitosa'))

    def test_detalle_ivr(self):
        URL = reverse(
            self.urls_api['Detail'],
            args=[self.ivr.pk, ])
        response = self.client.get(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], self.SUCCESS)
        self.assertEqual(
            response_json['data']['id'], self.ivr.pk)
        self.assertEqual(
            response_json['data']['name'], self.ivr.nombre)
        self.assertEqual(
            response_json['data']['description'], self.ivr.descripcion)
        self.assertEqual(
            response_json['message'],
            _('Se obtuvo la informacion del '
              'IVR de forma exitosa'))

    @patch('configuracion_telefonia_app.regeneracion_configuracion_telefonia'
           '.SincronizadorDeConfiguracionIVRAsterisk'
           '.regenerar_asterisk')
    def test_crear_ivr(self, regenerar_asterisk):
        URL = reverse(self.urls_api['Create'])
        numBefore = IVR.objects.all().count()
        dataForm = self._get_ivr_form_data()
        response = self.client.post(URL, data=dataForm)
        numAfter = IVR.objects.all().count()
        response_json = json.loads(response.content)
        ivr = IVR.objects.last()
        regenerar_asterisk.assert_called_with(ivr)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(numAfter, numBefore + 1)
        self.assertEqual(response_json['status'], self.SUCCESS)
        self.assertEqual(
            response_json['message'],
            _('Se creo el IVR de forma exitosa'))

    @patch('configuracion_telefonia_app.regeneracion_configuracion_telefonia'
           '.SincronizadorDeConfiguracionIVRAsterisk'
           '.regenerar_asterisk')
    def test_creacion_ivr_crea_destino_entrante_correspondiente(self, regenerar_asterisk):
        URL = reverse(self.urls_api['Create'])
        numBefore = DestinoEntrante.objects.filter(tipo=DestinoEntrante.IVR).count()
        dataForm = self._get_ivr_form_data()
        response = self.client.post(URL, data=dataForm)
        numAfter = DestinoEntrante.objects.filter(tipo=DestinoEntrante.IVR).count()
        response_json = json.loads(response.content)
        ivr = IVR.objects.last()
        regenerar_asterisk.assert_called_with(ivr)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(numAfter, numBefore + 1)
        self.assertEqual(response_json['status'], self.SUCCESS)

    @patch('configuracion_telefonia_app.regeneracion_configuracion_telefonia'
           '.SincronizadorDeConfiguracionIVRAsterisk'
           '.eliminar_y_regenerar_asterisk')
    def test_eliminar_ivr(self, eliminar_y_regenerar_asterisks):
        pk = self.ivr.pk
        URL = reverse(self.urls_api['Delete'], args=[pk, ])
        numBefore = IVR.objects.all().count()
        response = self.client.delete(URL, follow=True)
        numAfter = IVR.objects.all().count()
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(numAfter, numBefore - 1)
        self.assertEqual(response_json['status'], self.SUCCESS)
        self.assertEqual(
            response_json['message'],
            _('Se elimino el IVR de forma exitosa'))

    def test_eliminar_ivr_con_ruta_entrante(self):
        RutaEntranteFactory(destino=DestinoEntrante.get_nodo_ruta_entrante(self.ivr))
        pk = self.ivr.pk
        URL = reverse(self.urls_api['Delete'], args=[pk, ])
        response = self.client.delete(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], self.ERROR)
        self.assertEqual(
            response_json['errors'],
            _('No se puede eliminar un objeto que es '
              'destino en un flujo de llamada.'))

    def test_no_elimina_ivr_destino_de_otro_nodo(self):
        ivr = IVRFactory()
        nodo_ivr = DestinoEntrante.crear_nodo_ruta_entrante(ivr)
        OpcionDestinoFactory(valor='True',
                             destino_anterior=self.nodo_validacion,
                             destino_siguiente=nodo_ivr)
        OpcionDestinoFactory(valor='False',
                             destino_anterior=self.nodo_validacion,
                             destino_siguiente=self.nodo_campana)
        pk = ivr.pk
        URL = reverse(self.urls_api['Delete'], args=[pk, ])
        response = self.client.delete(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], self.ERROR)
        self.assertEqual(
            response_json['errors'],
            _('No se puede eliminar un objeto que es '
              'destino en un flujo de llamada.'))

    def test_validar_nombre_repetido_ivr(self):
        dataForm = self._get_ivr_form_data()
        dataForm['nombre'] = self.ivr.nombre
        URL = reverse(self.urls_api['Create'])
        response = self.client.post(URL, data=dataForm)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], self.ERROR)
        self.assertEqual(
            response_json['errors']['nombre'], ['Ya existe ivr con este nombre.'])

    def test_validar_dtmfs_repetidos(self):
        dataForm = self._get_ivr_form_data()
        dataForm['destination_options'] = json.dumps([
            {
                "id": None,
                "dtmf": "1",
                "destination_type": self.nodo_campana.tipo,
                "destination": self.nodo_campana.pk
            },
            {
                "id": None,
                "dtmf": "1",
                "destination_type": self.nodo_destino_personalizado.tipo,
                "destination": self.nodo_destino_personalizado.pk
            }
        ])
        URL = reverse(self.urls_api['Create'])
        response = self.client.post(URL, data=dataForm)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], self.ERROR)
        self.assertEqual(
            response_json['errors']['destination_options_json'],
            ["Hay DTMF's repetidos en las opciones de destino del IVR"])

    def test_validar_audio_principal_externo(self):
        dataForm = self._get_ivr_form_data()
        dataForm['type_main_audio'] = self.EXTERNAL_AUDIO
        URL = reverse(self.urls_api['Create'])
        response = self.client.post(URL, data=dataForm)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], self.ERROR)
        self.assertEqual(
            response_json['errors']['main_audio'],
            ['Debe escoger un audio como archivo externo'])

    def test_validar_audio_time_out_externo(self):
        dataForm = self._get_ivr_form_data()
        dataForm['type_time_out_audio'] = self.EXTERNAL_AUDIO
        URL = reverse(self.urls_api['Create'])
        response = self.client.post(URL, data=dataForm)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], self.ERROR)
        self.assertEqual(
            response_json['errors']['time_out_audio'],
            ['Debe escoger un audio como archivo externo'])

    def test_validar_audio_invalido_externo(self):
        dataForm = self._get_ivr_form_data()
        dataForm['type_invalid_audio'] = self.EXTERNAL_AUDIO
        URL = reverse(self.urls_api['Create'])
        response = self.client.post(URL, data=dataForm)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], self.ERROR)
        self.assertEqual(
            response_json['errors']['invalid_audio'],
            ['Debe escoger un audio como archivo externo'])

    def test_validar_audio_principal_interno(self):
        dataForm = self._get_ivr_form_data()
        dataForm['main_audio'] = 'null'
        URL = reverse(self.urls_api['Create'])
        response = self.client.post(URL, data=dataForm)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], self.ERROR)
        self.assertEqual(
            response_json['errors']['main_audio'],
            ['Debe escoger un audio interno del sistema'])

    def test_validar_audio_time_out_interno(self):
        dataForm = self._get_ivr_form_data()
        dataForm['time_out_audio'] = 'null'
        URL = reverse(self.urls_api['Create'])
        response = self.client.post(URL, data=dataForm)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], self.ERROR)
        self.assertEqual(
            response_json['errors']['time_out_audio'],
            ['Debe escoger un audio interno del sistema'])

    def test_validar_audio_invalido_interno(self):
        dataForm = self._get_ivr_form_data()
        dataForm['invalid_audio'] = 'null'
        URL = reverse(self.urls_api['Create'])
        response = self.client.post(URL, data=dataForm)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], self.ERROR)
        self.assertEqual(
            response_json['errors']['invalid_audio'],
            ['Debe escoger un audio interno del sistema'])

    def test_validar_tipo_extension_de_archivo_audio_principal_externo(self):
        dataForm = self._get_ivr_form_data()
        dataForm['type_main_audio'] = self.EXTERNAL_AUDIO
        dataForm['main_audio_ext'] = self.img
        URL = reverse(self.urls_api['Create'])
        response = self.client.post(URL, data=dataForm)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], self.ERROR)
        self.assertEqual(
            response_json['errors']['main_audio'],
            ['El archivo no tiene extension .wav'])

    def test_validar_tipo_extension_de_archivo_audio_time_out_externo(self):
        dataForm = self._get_ivr_form_data()
        dataForm['type_time_out_audio'] = self.EXTERNAL_AUDIO
        dataForm['time_out_audio_ext'] = self.img
        URL = reverse(self.urls_api['Create'])
        response = self.client.post(URL, data=dataForm)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], self.ERROR)
        self.assertEqual(
            response_json['errors']['time_out_audio'],
            ['El archivo no tiene extension .wav'])

    def test_validar_tipo_extension_de_archivo_audio_invalido_externo(self):
        dataForm = self._get_ivr_form_data()
        dataForm['type_invalid_audio'] = self.EXTERNAL_AUDIO
        dataForm['invalid_audio_ext'] = self.img
        URL = reverse(self.urls_api['Create'])
        response = self.client.post(URL, data=dataForm)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], self.ERROR)
        self.assertEqual(
            response_json['errors']['invalid_audio'],
            ['El archivo no tiene extension .wav'])

    @patch('configuracion_telefonia_app.regeneracion_configuracion_telefonia'
           '.SincronizadorDeConfiguracionIVRAsterisk.regenerar_asterisk')
    def test_ivr_destino_agente(self, regenerar_asterisk):
        URL = reverse(self.urls_api['Create'])
        self.agente = AgenteProfileFactory()
        self.agente_destino_entrante = DestinoEntranteFactory.create(
            tipo=DestinoEntrante.AGENTE, content_object=self.agente)
        destination_options = json.dumps([
            {
                "dtmf": "1111",
                "destination_type": DestinoEntrante.AGENTE,
                "destination": self.agente_destino_entrante.id,
                "id": None
            }
        ])
        post_data = self._get_ivr_form_data()
        post_data.update({'destination_options': destination_options})
        response = self.client.post(URL, post_data, follow=True)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.agente.is_ivr_destino(), True)
