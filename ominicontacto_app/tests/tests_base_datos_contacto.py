# -*- coding: utf-8 -*-

"""Unittests del modelo Campana"""

from __future__ import unicode_literals

import json

from ominicontacto_app.models import BaseDatosContacto, MetadataBaseDatosContactoDTO
from ominicontacto_app.tests.utiles import OMLBaseTest


class SetUpForMetadataBaseDatosContactoMixin():
    """Mixin con metodo setUp() que genera una instancia
    basica de MetadataBaseDatosContactoDTO en self.metadata
    """

    def setUp(self):
        metadata = MetadataBaseDatosContactoDTO()
        metadata.cantidad_de_columnas = 5
        metadata.columna_con_telefono = 2
        metadata.columnas_con_fecha = [0, 4]
        metadata.columnas_con_hora = [1]
        metadata.nombres_de_columnas = ["F_ALTA",
                                        "HORA",
                                        "TELEFONO",
                                        "CUIT",
                                        "F_BAJA"
                                        ]
        metadata.primer_fila_es_encabezado = False
        self.metadata = metadata


class TestMetadataBaseDatosContacto(OMLBaseTest):
    """Clase para testear MetadataBaseDatosContacto"""

    def setUp(self):
        self.metadata = {'col_telefono': 6,
                         'cant_col': 9}
        self.metadata_codificada = json.dumps(self.metadata)

    def test_parsea_datos_correctos(self):
        bd = BaseDatosContacto(pk=1, metadata=self.metadata_codificada)

        self.assertEqual(bd.get_metadata().columna_con_telefono, 6)
        self.assertEqual(bd.get_metadata().cantidad_de_columnas, 9)

    def test_guarda_datos_correctos(self):
        bd = BaseDatosContacto(pk=1)
        metadata = bd.get_metadata()
        metadata.cantidad_de_columnas = 2
        metadata.columna_con_telefono = 1
        metadata.nombres_de_columnas = ["A", "B"]
        metadata.primer_fila_es_encabezado = True
        metadata.save()

        self.assertDictEqual(json.loads(bd.metadata),
                             {'col_telefono': 1,
                              'cant_col': 2,
                              'nombres_de_columnas': ["A", "B"],
                              'prim_fila_enc': True,
                              })

    def test_valida_columna_con_telefono(self):
        bd = BaseDatosContacto(pk=1)
        metadata = bd.get_metadata()
        metadata.cantidad_de_columnas = 4
        # metadata.save()

        with self.assertRaises(AssertionError):
            # columna_con_telefono NO puede ser 4
            metadata.columna_con_telefono = 4

    def test_valida_nombres_de_columnas(self):
        bd = BaseDatosContacto(pk=1)
        metadata = bd.get_metadata()
        metadata.cantidad_de_columnas = 4
        metadata.nombres_de_columnas = ["a", "b", "c", "d"]
        # metadata.save()

        with self.assertRaises(AssertionError):
            metadata.nombres_de_columnas = ["a", "b", "c"]
        with self.assertRaises(AssertionError):
            metadata.nombres_de_columnas = ["a", "b", "c", "d", "e"]

    def test_genera_valueerror_sin_datos(self):
        with self.assertRaises(ValueError):
            BaseDatosContacto().get_metadata().columna_con_telefono


class TestMetadataBaseDatosContactoDTO(SetUpForMetadataBaseDatosContactoMixin,
                                       OMLBaseTest):

    def test_valida_metadatos_correcto(self):
        self.metadata.validar_metadatos()

    def test_detecta_col_telefono_incorrecto(self):
        self.metadata._metadata['col_telefono'] = 99
        with self.assertRaises(AssertionError):
            self.metadata.validar_metadatos()

    def test_detecta_cols_fecha_incorrecto(self):
        self.metadata._metadata['cols_fecha'] = [99]
        with self.assertRaises(AssertionError):
            self.metadata.validar_metadatos()

    def test_detecta_cols_hora_incorrecto(self):
        self.metadata._metadata['cols_hora'] = [99]
        with self.assertRaises(AssertionError):
            self.metadata.validar_metadatos()

    def test_detecta_nombres_de_columnas_incorrecto(self):
        # Falta una columna
        self.metadata._metadata['nombres_de_columnas'] = ["F_ALTA",
                                                          "HORA",
                                                          "TELEFONO",
                                                          "CUIT",
                                                          ]
        with self.assertRaises(AssertionError):
            self.metadata.validar_metadatos()

        # Sobra una columna
        self.metadata._metadata['nombres_de_columnas'] = ["F_ALTA",
                                                          "HORA",
                                                          "TELEFONO",
                                                          "CUIT",
                                                          "F_BAJA",
                                                          "EXTRA",
                                                          ]
        with self.assertRaises(AssertionError):
            self.metadata.validar_metadatos()

    def test_detecta_prim_fila_enc_incorrecto(self):
        self.metadata._metadata['prim_fila_enc'] = ''
        with self.assertRaises(AssertionError):
            self.metadata.validar_metadatos()


class TestMetodosDatoExtraEs(SetUpForMetadataBaseDatosContactoMixin,
                             OMLBaseTest):

    def test_dato_extra_es_fecha(self):

        self.assertTrue(self.metadata.dato_extra_es_fecha("F_ALTA"))
        self.assertTrue(self.metadata.dato_extra_es_fecha("F_BAJA"))

        self.assertFalse(self.metadata.dato_extra_es_fecha("TELEFONO"))
        self.assertFalse(self.metadata.dato_extra_es_fecha("CUIT"))
        self.assertFalse(self.metadata.dato_extra_es_fecha("HORA"))

        with self.assertRaises(ValueError):
            self.metadata.dato_extra_es_fecha("X")

    def test_dato_extra_es_hora(self):

        self.assertTrue(self.metadata.dato_extra_es_hora("HORA"))

        self.assertFalse(self.metadata.dato_extra_es_hora("F_ALTA"))
        self.assertFalse(self.metadata.dato_extra_es_hora("F_BAJA"))
        self.assertFalse(self.metadata.dato_extra_es_hora("TELEFONO"))
        self.assertFalse(self.metadata.dato_extra_es_hora("CUIT"))

        with self.assertRaises(ValueError):
            self.metadata.dato_extra_es_hora("X")

    def test_dato_extra_es_telefono(self):

        self.assertTrue(self.metadata.dato_extra_es_telefono("TELEFONO"))

        self.assertFalse(self.metadata.dato_extra_es_telefono("HORA"))
        self.assertFalse(self.metadata.dato_extra_es_telefono("F_ALTA"))
        self.assertFalse(self.metadata.dato_extra_es_telefono("F_BAJA"))
        self.assertFalse(self.metadata.dato_extra_es_telefono("CUIT"))

        with self.assertRaises(ValueError):
            self.metadata.dato_extra_es_telefono("X")

    def test_dato_extra_es_generico(self):

        self.assertTrue(self.metadata.dato_extra_es_generico("CUIT"))

        self.assertFalse(self.metadata.dato_extra_es_generico("HORA"))
        self.assertFalse(self.metadata.dato_extra_es_generico("F_ALTA"))
        self.assertFalse(self.metadata.dato_extra_es_generico("F_BAJA"))
        self.assertFalse(self.metadata.dato_extra_es_generico("TELEFONO"))

        with self.assertRaises(ValueError):
            self.metadata.dato_extra_es_generico("X")


class TestMetadataBaseDatosContactoParseoDeDatos(OMLBaseTest):

    def setUp(self):
        metadata = MetadataBaseDatosContactoDTO()
        metadata.cantidad_de_columnas = 5
        metadata.columna_con_telefono = 2
        metadata.columnas_con_fecha = [0, 4]
        metadata.columnas_con_hora = [1]
        metadata.nombres_de_columnas = ["F_ALTA",
                                        "HORA",
                                        "TELEFONO",
                                        "CUIT",
                                        "F_BAJA"
                                        ]
        metadata.primer_fila_es_encabezado = False
        self.metadata = metadata

        self.datos_json_ok = json.dumps(["xxx",
                                         "xxx",
                                         "01145679999",
                                         "xxx",
                                         "xxx"])

        self.datos_json_con_sobrante = json.dumps(["xxx",
                                                   "xxx",
                                                   "01145679999",
                                                   "xxx",
                                                   "xxx",
                                                   "dato-sobrante",
                                                   ])

        self.datos_json_con_faltantes = json.dumps(["xxx",
                                                    "xxx",
                                                    "01145679999",
                                                    "xxx",
                                                    ])

    def test_obtener_telefono_de_dato_de_contacto(self):
        telefono = self.metadata.obtener_telefono_de_dato_de_contacto(
            self.datos_json_ok)
        self.assertEquals(telefono, "01145679999")

    def test_obtener_telefono__reporta_error_si_sobran_datos(self):
        with self.assertRaises(AssertionError):
            self.metadata.obtener_telefono_de_dato_de_contacto(
                self.datos_json_con_sobrante)

    def test_obtener_telefono__reporta_error_si_faltan_datos(self):
        with self.assertRaises(AssertionError):
            self.metadata.obtener_telefono_de_dato_de_contacto(
                self.datos_json_con_faltantes)
