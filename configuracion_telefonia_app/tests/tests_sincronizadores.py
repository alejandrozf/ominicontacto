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

from mock import patch

from configuracion_telefonia_app.tests.factories import (
    IdentificadorClienteFactory, DestinoPersonalizadoFactory, PlaylistFactory)

from configuracion_telefonia_app.models import (OpcionDestino, IdentificadorCliente,
                                                DestinoEntrante)
from configuracion_telefonia_app.regeneracion_configuracion_telefonia import (
    SincronizadorDeConfiguracionIdentificadorClienteAsterisk,
    SincronizadorDeConfiguracionDestinoPersonalizadoAsterisk,
    SincronizadorDeConfiguracionAmdConfAsterisk
)
from ominicontacto_app.models import Campana
from ominicontacto_app.tests.factories import CampanaFactory
from configuracion_telefonia_app.models import AmdConf
from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.utiles import convert_audio_asterisk_path_astdb
from ominicontacto_app.asterisk_config import PlaylistsConfigCreator


class TestsSincronizadores(OMLBaseTest):

    def test_identificador_cliente_sin_interaccion_externa_envia_datos_correctos_creacion_astdb(
            self):
        campana_entrante_1 = CampanaFactory(type=Campana.TYPE_ENTRANTE)
        campana_entrante_2 = CampanaFactory(type=Campana.TYPE_ENTRANTE)
        ident_cliente = IdentificadorClienteFactory(
            tipo_interaccion=IdentificadorCliente.SIN_INTERACCION_EXTERNA, url=None)
        dest_entrante_1 = DestinoEntrante.crear_nodo_ruta_entrante(campana_entrante_1)
        dest_entrante_2 = DestinoEntrante.crear_nodo_ruta_entrante(campana_entrante_2)
        dest_entrante_ident_client = DestinoEntrante.crear_nodo_ruta_entrante(ident_cliente)
        OpcionDestino.crear_opcion_destino(
            dest_entrante_ident_client, dest_entrante_1, IdentificadorCliente.DESTINO_MATCH)
        OpcionDestino.crear_opcion_destino(
            dest_entrante_ident_client, dest_entrante_2, IdentificadorCliente.DESTINO_NO_MATCH)
        sync_ident_cliente = SincronizadorDeConfiguracionIdentificadorClienteAsterisk()
        gen_family = sync_ident_cliente._obtener_generador_family()
        dict_astdb = gen_family._create_dict(ident_cliente)
        self.assertEqual(dict_astdb['NAME'], ident_cliente.nombre)
        self.assertEqual(dict_astdb['TYPE'], ident_cliente.tipo_interaccion)
        self.assertFalse(dict_astdb.get('URL', False))
        audio_path = convert_audio_asterisk_path_astdb(ident_cliente.audio.audio_asterisk)
        self.assertEqual(dict_astdb['AUDIO'], audio_path)
        self.assertEqual(dict_astdb['LENGTH'], ident_cliente.longitud_id_esperado)
        self.assertEqual(dict_astdb['TIMEOUT'], ident_cliente.timeout)
        self.assertEqual(dict_astdb['RETRIES'], ident_cliente.intentos)
        self.assertEqual(dict_astdb['TRUEDST'], "{0},{1}".format(
            dest_entrante_1.tipo, dest_entrante_1.object_id))
        self.assertEqual(dict_astdb['FALSEDST'], "{0},{1}".format(
            dest_entrante_2.tipo, dest_entrante_2.object_id))

    def test_identificador_cliente_interaccion_externa_tipo1_envia_datos_correctos_creacion_astdb(
            self):
        campana_entrante_1 = CampanaFactory(type=Campana.TYPE_ENTRANTE)
        campana_entrante_2 = CampanaFactory(type=Campana.TYPE_ENTRANTE)
        ident_cliente = IdentificadorClienteFactory(
            tipo_interaccion=IdentificadorCliente.INTERACCION_EXTERNA_1)
        dest_entrante_1 = DestinoEntrante.crear_nodo_ruta_entrante(campana_entrante_1)
        dest_entrante_2 = DestinoEntrante.crear_nodo_ruta_entrante(campana_entrante_2)
        dest_entrante_ident_client = DestinoEntrante.crear_nodo_ruta_entrante(ident_cliente)
        OpcionDestino.crear_opcion_destino(
            dest_entrante_ident_client, dest_entrante_1, IdentificadorCliente.DESTINO_MATCH)
        OpcionDestino.crear_opcion_destino(
            dest_entrante_ident_client, dest_entrante_2, IdentificadorCliente.DESTINO_NO_MATCH)
        sync_ident_cliente = SincronizadorDeConfiguracionIdentificadorClienteAsterisk()
        gen_family = sync_ident_cliente._obtener_generador_family()
        dict_astdb = gen_family._create_dict(ident_cliente)
        self.assertEqual(dict_astdb['NAME'], ident_cliente.nombre)
        self.assertEqual(dict_astdb['TYPE'], ident_cliente.tipo_interaccion)
        self.assertEqual(dict_astdb['EXTERNALURL'], ident_cliente.url)
        audio_path = convert_audio_asterisk_path_astdb(ident_cliente.audio.audio_asterisk)
        self.assertEqual(dict_astdb['AUDIO'], audio_path)
        self.assertEqual(dict_astdb['LENGTH'], ident_cliente.longitud_id_esperado)
        self.assertEqual(dict_astdb['TIMEOUT'], ident_cliente.timeout)
        self.assertEqual(dict_astdb['RETRIES'], ident_cliente.intentos)
        self.assertEqual(dict_astdb['TRUEDST'], "{0},{1}".format(
            dest_entrante_1.tipo, dest_entrante_1.object_id))
        self.assertEqual(dict_astdb['FALSEDST'], "{0},{1}".format(
            dest_entrante_2.tipo, dest_entrante_2.object_id))

    def test_identificador_cliente_interaccion_externa_tipo2_envia_datos_correctos_creacion_astdb(
            self):
        ident_cliente = IdentificadorClienteFactory(
            tipo_interaccion=IdentificadorCliente.INTERACCION_EXTERNA_2)
        DestinoEntrante.crear_nodo_ruta_entrante(ident_cliente)
        sync_ident_cliente = SincronizadorDeConfiguracionIdentificadorClienteAsterisk()
        gen_family = sync_ident_cliente._obtener_generador_family()
        dict_astdb = gen_family._create_dict(ident_cliente)
        self.assertEqual(dict_astdb['NAME'], ident_cliente.nombre)
        self.assertEqual(dict_astdb['TYPE'], ident_cliente.tipo_interaccion)
        self.assertEqual(dict_astdb['EXTERNALURL'], ident_cliente.url)
        audio_path = convert_audio_asterisk_path_astdb(ident_cliente.audio.audio_asterisk)
        self.assertEqual(dict_astdb['AUDIO'], audio_path)
        self.assertEqual(dict_astdb['LENGTH'], ident_cliente.longitud_id_esperado)
        self.assertEqual(dict_astdb['TIMEOUT'], ident_cliente.timeout)
        self.assertFalse(dict_astdb.get('TRUEDST', False))
        self.assertFalse(dict_astdb.get('FALSEDST', False))

    def test_creacion_sincronizador_destino_personalizado_envia_datos_correctos_asterisk(self):
        campana_entrante_1 = CampanaFactory(type=Campana.TYPE_ENTRANTE)
        dest_entrante_1 = DestinoEntrante.crear_nodo_ruta_entrante(campana_entrante_1)
        dest_personalizado = DestinoPersonalizadoFactory()
        nodo_dest_personalizado = DestinoEntrante.crear_nodo_ruta_entrante(dest_personalizado)
        OpcionDestino.crear_opcion_destino(
            nodo_dest_personalizado, dest_entrante_1, 'failover')
        sync_dest_personalizado = SincronizadorDeConfiguracionDestinoPersonalizadoAsterisk()
        gen_family = sync_dest_personalizado._obtener_generador_family()
        dict_astdb = gen_family._create_dict(dest_personalizado)
        self.assertEqual(dict_astdb['NAME'], dest_personalizado.nombre)
        self.assertEqual(dict_astdb['DST'], dest_personalizado.custom_destination)
        self.assertEqual(dict_astdb['FAILOVER'], "{0},{1}".format(
            dest_entrante_1.tipo, dest_entrante_1.object_id))

    def test_creacion_sincronizador_amd_envia_datos_correctos_redis(self):
        amd_conf = AmdConf.objects.first()
        sync_amd_conf = SincronizadorDeConfiguracionAmdConfAsterisk()
        gen_family = sync_amd_conf._obtener_generador_family()
        dict_astdb = gen_family._create_dict(amd_conf)
        self.assertEqual(dict_astdb['NAME'], 'GLOBAL_AMD')
        self.assertEqual(dict_astdb['INITIAL_SILENCE'], amd_conf.initial_silence)
        self.assertEqual(dict_astdb['GREETING'], amd_conf.greeting)


class TestConfigCreators(OMLBaseTest):

    @patch('ominicontacto_app.asterisk_config.ConfigFile.write')
    def test_playlist_config_creator(self, write):
        playlist = PlaylistFactory()
        template = """
        [{oml_nombre_playlist}]
        mode=files
        directory=sounds/moh/{oml_nombre_playlist}
        """
        template = "\n".join(t.strip() for t in template.splitlines())
        config = template.format(**{'oml_nombre_playlist': playlist.nombre})
        creator = PlaylistsConfigCreator()
        creator.create_config_asterisk()
        write.assert_called_with([config])
