# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test.utils import override_settings
from ominicontacto_app.errors import OmlParserMinRowError, OmlParserCsvDelimiterError
from ominicontacto_app.parser import ParserCsv, validate_telefono, sanitize_number, \
    validate_fechas, validate_horas
from ominicontacto_app.tests.utiles import OMLBaseTest


class GetDialectTest(OMLBaseTest):

    def test_cantidad_minima_de_filas(self):
        planilla = self.get_test_resource("planilla-ejemplo-4.csv")
        parser = ParserCsv()
        with self.assertRaises(OmlParserMinRowError):
            parser._get_dialect(open(planilla, 'r'))

    def test_delimiter_incorrecto(self):
        parser = ParserCsv()

        with self.assertRaises(OmlParserCsvDelimiterError):
            planilla = self.get_test_resource("planilla-ejemplo-5.csv")
            parser._get_dialect(open(planilla, 'r'))


class ValidateTelefonoTest(OMLBaseTest):
    def test_validate_number_validos(self):

        datos = ['35430098657', '(11)153450923', '28301734914', '356-01273413']

        for dato in datos:
            self.assertTrue(validate_telefono(dato))

    def test_validate_number_invalidos(self):

        datos = ['355', '(11)blablabla', '5', 'test']

        for dato in datos:
            self.assertFalse(validate_telefono(dato),
                             "ERROR: el nro telefonico INVALIDO '{0}' ha sido "
                             "detectado como VALIDO.".format(dato))

    def test_validate_validacion_muy_relajada(self):

        datos = ['12345',
                 '12345678901234567890',
                 '(12) 34-5678-9012-3456-789-0',
                 ]

        # With STRICT values FAILS
        with override_settings(OL_NRO_TELEFONO_LARGO_MIN=11,
                               OL_NRO_TELEFONO_LARGO_MAX=13):
            for dato in datos:
                self.assertFalse(validate_telefono(dato),
                                 "ERROR: el nro telefonico INVALIDO '{0}' ha "
                                 "sido detectado como VALIDO.".format(dato))

        # With RELAXED values PASS
        with override_settings(OL_NRO_TELEFONO_LARGO_MIN=5,
                               OL_NRO_TELEFONO_LARGO_MAX=25):
            for dato in datos:
                self.assertTrue(validate_telefono(dato))


class SanitizeNumberTest(OMLBaseTest):
    def test_sanitize_number(self):
        self.assertEqual(sanitize_number('(0351)15-3368309'), '0351153368309')


class ValidateFechasTest(OMLBaseTest):
    def test_validate_fechas_validos(self):
        datos = ['01/01/2014', '01/01/14', '16/07/16', '31/07/16']

        self.assertTrue(validate_fechas(datos))

    def test_validate_fechas_formato_invalidos(self):
        datos = ['1/1/2014']

        self.assertFalse(validate_fechas(datos))

    def test_validate_fechas_no_fecha(self):
        datos = ['test']

        self.assertFalse(validate_fechas(datos))

    def test_validate_fechas_vacias(self):
        datos = []

        self.assertFalse(validate_fechas(datos))


class ValidateHorasTest(OMLBaseTest):
    def test_validate_horas_validos(self):
        datos = ['16:00', '16:00:00', '01:00', '00:00']

        self.assertTrue(validate_horas(datos))

    def test_validate_horas_formato_invalido1(self):
        datos = ['10:00pm']

        self.assertFalse(validate_horas(datos))

    def test_validate_horas_formato_invalido2(self):
        datos = ['1:00']

        self.assertFalse(validate_horas(datos))

    def test_validate_horas_formato_invalido3(self):
        datos = ['24:00']

        self.assertFalse(validate_horas(datos))

    def test_validate_horas_no_hora(self):
        datos = ['test']

        self.assertFalse(validate_horas(datos))

    def test_validate_horas_vacias(self):
        datos = []

        self.assertFalse(validate_horas(datos))
