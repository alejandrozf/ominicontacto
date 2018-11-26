# -*- coding: utf-8 -*-

"""Unittests del servicio base_de_datos_contacto"""

from __future__ import unicode_literals

from mock import Mock

from django.core.files import File

from ominicontacto_app.errors import OmlArchivoImportacionInvalidoError
from ominicontacto_app.models import BaseDatosContacto, Contacto
from ominicontacto_app.services.base_de_datos_contactos import \
    CreacionBaseDatosService, PredictorMetadataService, \
    NoSePuedeInferirMetadataError
from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.utiles import ValidadorDeNombreDeCampoExtra


class TestGeneraBaseDatosContacto(OMLBaseTest):

    def test_genera_base_datos_falla_archivo_xls(self):
        bd = BaseDatosContacto(id=1)
        bd.nombre_archivo_importacion = "planilla-ejemplo-0.xls"
        bd.save = Mock()

        # -----
        creacion_base_de_datos_service = CreacionBaseDatosService()
        with self.assertRaises(OmlArchivoImportacionInvalidoError):
            creacion_base_de_datos_service.genera_base_dato_contacto(bd)

    def test_genera_base_datos_archivo_valido(self):
        bd = BaseDatosContacto(id=1)
        bd.archivo_importacion = self.copy_test_resource_to_mediaroot("planilla-ejemplo-0.csv")
        bd.nombre_archivo_importacion = "planilla-ejemplo-0.csv"
        bd.save = Mock()

        creacion_base_de_datos_service = CreacionBaseDatosService()
        creacion_base_de_datos_service.genera_base_dato_contacto(bd)

    def test_importa_contacto(self):
        # 3543009865,lkasdjlfkaf,0351156219387
        # 111534509230,dkasjflkja,0351156982639
        # 2830173491,alsdkjfieasdf,3516983419
        # 3560127341,kahvuahdsfasdfa,2954638961

        bd = BaseDatosContacto(id=1)
        bd.archivo_importacion = File(open(self.get_test_resource(
            "planilla-ejemplo-1.csv"), 'r'))
        bd.nombre_archivo_importacion = "planilla-ejemplo-1.csv"
        bd.save = Mock()

        metadata = bd.get_metadata()
        metadata.cantidad_de_columnas = 3
        metadata.columna_con_telefono = 0
        metadata.nombres_de_columnas = ["TELEFONO_FIJO",
                                        "NOMBRE",
                                        "CELULAR"]
        metadata.save()

        # -----

        creacion_base_de_datos_service = CreacionBaseDatosService()
        creacion_base_de_datos_service.importa_contactos(bd)

        self.assertEqual(bd.contactos.count(), 4)

    def test_define_base_dato_contacto(self):
        bd = BaseDatosContacto(id=1)
        bd.save = Mock()

        # -----

        creacion_base_de_datos_service = CreacionBaseDatosService()
        creacion_base_de_datos_service.define_base_dato_contacto(bd)

        self.assertEqual(bd.estado, BaseDatosContacto.ESTADO_DEFINIDA)


TELEFONO_OK = "5493572444444"
FECHA_OK = "28/02/2014"
HORA_OK = "23:59:59"


class TestInfiereMetadata(OMLBaseTest):

    def test_detecta_pocas_lineas(self):
        service = PredictorMetadataService()

        # Ninguna linea
        with self.assertRaises(NoSePuedeInferirMetadataError):
            service.inferir_metadata_desde_lineas([], "utf-8")

        # Una linea
        with self.assertRaises(NoSePuedeInferirMetadataError):
            service.inferir_metadata_desde_lineas([[TELEFONO_OK], ], "utf-8")

        # Por las dudas chequeamos q' funcione con 2 linas
        service.inferir_metadata_desde_lineas([['telefono'], [TELEFONO_OK], ], "utf-8")

    def test_infiere_ok_con_todos_los_datos(self):
        ENCABEZADO_ORIGINAL = ["telefono", "Apellido", "Nombre",
                               "Fecha Alta", "Hora Alta", ]

        ENCABEZADO_AJUSTADO = [u'TELEFONO', u'APELLIDO', u'NOMBRE',
                               u'FECHA_ALTA', u'HORA_ALTA']

        lineas = [
            ENCABEZADO_ORIGINAL,
            [TELEFONO_OK, "Napoli", "Chizo", FECHA_OK, HORA_OK, ],
            [TELEFONO_OK, "Napoli", "Chizo", FECHA_OK, HORA_OK, ],
            [TELEFONO_OK, "Napoli", "Chizo", FECHA_OK, HORA_OK, ],
            [TELEFONO_OK, "Napoli", "Chizo", FECHA_OK, HORA_OK, ],
        ]

        service = PredictorMetadataService()
        metadata = service.inferir_metadata_desde_lineas(lineas, "utf-8")

        self.assertEquals(metadata.cantidad_de_columnas, 5)
        self.assertEquals(metadata.columna_con_telefono, 0)
        self.assertEquals(metadata.columnas_con_fecha, [3])
        self.assertEquals(metadata.columnas_con_hora, [4])

        self.assertEquals(metadata.primer_fila_es_encabezado, True)
        self.assertEquals(metadata.nombres_de_columnas, ENCABEZADO_AJUSTADO)

    def test_no_infiere_nada_sin_datos(self):
        lineas = [
            ["telefono", "Apellido", "Nombre", "Fecha Alta", "Hora Alta"],
            ["Chizo", "Napoli", "", "", ""],
            ["Chizo", "Napoli", "", "", ""],
        ]

        service = PredictorMetadataService()
        with self.assertRaises(NoSePuedeInferirMetadataError):
            service.inferir_metadata_desde_lineas(lineas, "utf-8")


class TestValidadorNombreDeCampo(OMLBaseTest):

    def test_valida_nombres_validos(self):
        service = ValidadorDeNombreDeCampoExtra()
        NOMBRES_VALIDOS = ["NOMBRE", "EMAIL_PERSONA", "EMAIL_2", "X", ]
        for nombre_columna in NOMBRES_VALIDOS:
            self.assertTrue(service.validar_nombre_de_columna(nombre_columna),
                            "validar_nombre_de_columna() ha reportado como "
                            "invalido el nombre de columna '{0}', que en "
                            "realidad es VALIDO".format(nombre_columna))

    def test_detecta_nombres_invalidos(self):
        service = ValidadorDeNombreDeCampoExtra()
        NOMBRES_INVALIDOS = [
            "NOMBRE ",
            " NOMBRE",
            " NOMBRE ",
            "EMAIL PERSONA",
            "FACTURA_EN_$",
            "FACTURA_ÑOÑA",
            "",
        ]
        for nombre_columna in NOMBRES_INVALIDOS:
            self.assertFalse(service.validar_nombre_de_columna(nombre_columna),
                             "validar_nombre_de_columna() ha reportado como "
                             "VALIDO el nombre de columna '{0}', que en "
                             "realidad es INVALIDO".format(nombre_columna))


class TestSaneadorNombreDeCampo(OMLBaseTest):

    def test_sanea_correctamente(self):
        service = PredictorMetadataService()
        NOMBRES = [
            ["NOMBRE", "NOMBRE"],
            ["EMAIL_PERSONA", "EMAIL_PERSONA"],
            ["EMAIL_2", "EMAIL_2"],
            ["X", "X"],
            ["NOMBRE ", "NOMBRE"],
            [" NOMBRE", "NOMBRE"],
            [" NOMBRE ", "NOMBRE"],
            ["EMAIL PERSONA", "EMAIL_PERSONA"],
            ["EMAIL    PERSONA", "EMAIL_PERSONA"],
            ["FACTURA EN $", "FACTURA_EN_$"],
            ["", ""],
        ]

        for nombre_original, nombre_saneado_esperado in NOMBRES:
            resultado = service.sanear_nombre_de_columna(nombre_original)
            self.assertEquals(resultado,
                              nombre_saneado_esperado,
                              "sanear_nombre_de_columna() ha devuelto un "
                              "valor inesperado al sanear '{0}'. "
                              "Devolvio: '{1}', se esperaba '{2}'"
                              "".format(nombre_original,
                                        resultado,
                                        nombre_saneado_esperado))


class TestImportarDesdeCsvNoAscii(OMLBaseTest):

    def test_importa_archivo_utf8_correctamente(self):
        bd = BaseDatosContacto(id=1)
        bd.archivo_importacion = self.copy_test_resource_to_mediaroot(
            "bd-contactos-utf8.csv")
        bd.nombre_archivo_importacion = "bd-contactos-utf8.csv"
        bd.save = Mock()

        # -----
        service = CreacionBaseDatosService()
        service.genera_base_dato_contacto(bd)

        metadata = bd.get_metadata()
        metadata.cantidad_de_columnas = 2
        metadata.columna_con_telefono = 0
        metadata.nombres_de_columnas = ["TELEFONO", "NOMBRE"]
        metadata.primer_fila_es_encabezado = True
        metadata.save()

        service.importa_contactos(bd)

        self.assertEquals(Contacto.objects.count(), 2)
        contactos = list(Contacto.objects.all())
        contactos_dict = dict([(c.telefono, c.datos) for c in contactos])

        self.assertIn('375849371648', contactos_dict)
        self.assertIn('957327493493', contactos_dict)
