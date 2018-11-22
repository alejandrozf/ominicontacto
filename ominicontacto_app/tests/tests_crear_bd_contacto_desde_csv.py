# -*- coding: utf-8 -*-

"""
Test de integracion de la creación de BD de contactos desde archivos CSV.
"""

from __future__ import unicode_literals

import logging as _logging

from ominicontacto_app.models import BaseDatosContacto, Contacto
from ominicontacto_app.parser import ParserCsv
from ominicontacto_app.services.base_de_datos_contactos import (
    PredictorMetadataService, CreacionBaseDatosService)
from ominicontacto_app.tests.utiles import OMLBaseTest


logger = _logging.getLogger(__name__)


class TestWorkflowCreacionBdContactoDesdeCsv(OMLBaseTest):

    def test_con_planilla_ejemplo_3(self):
        bd_contacto = BaseDatosContacto.objects.create(
            nombre="base-datos-contactos",
            archivo_importacion=self.copy_test_resource_to_mediaroot(
                "planilla-ejemplo-3-headers-con-no-ascii-y-espacios.csv"),
            nombre_archivo_importacion='planilla-ejemplo-3-headers-con-no-ascii-y-espacios.csv')

        parser = ParserCsv()
        estructura_archivo = parser.previsualiza_archivo(bd_contacto)
        predictor_metadata = PredictorMetadataService()
        metadata_inferida = predictor_metadata.inferir_metadata_desde_lineas(
            estructura_archivo, "utf-8")

        metadata = bd_contacto.get_metadata()
        metadata._metadata = metadata_inferida._metadata
        metadata.nombres_de_columnas = ["TELEFONO", "NOMBRE", "FECHA", "HORA"]
        metadata.save()

        creacion_base_datos_service = CreacionBaseDatosService()
        creacion_base_datos_service.importa_contactos(bd_contacto)
        creacion_base_datos_service.define_base_dato_contacto(bd_contacto)

        # ----- checks

        self.assertEquals(BaseDatosContacto.objects.get(pk=bd_contacto.id).estado,
                          BaseDatosContacto.ESTADO_DEFINIDA,
                          "La BD no ha quedado en estado ESTADO_DEFINIDA")

        nros_telefono = [contacto.telefono
                         for contacto in Contacto.objects.filter(bd_contacto=bd_contacto.id)]

        self.assertEquals(len(nros_telefono), 3, "Deberia haber 3 contactos")

        self.assertEquals(set(nros_telefono),
                          set(['354303459865', '111534509230', '283453013491']),
                          "Deberia haber 3 contactos")

    def test_con_demas_planillas_de_ejemplo(self):

        PLANILLAS = (
            "planilla-ejemplo-1.csv",
            "planilla-ejemplo-2.csv",
            "planilla-ejemplo-7-celdas-vacias.csv",
            "planilla-ejemplo-8-ultima-celda-vacia.csv",
        )

        for planilla in PLANILLAS:
            logger.debug("Procesando planilla %s", planilla)
            bd_contacto = BaseDatosContacto.objects.create(
                nombre="base-datos-contactos-{0}".format(planilla),
                archivo_importacion=self.copy_test_resource_to_mediaroot(planilla),
                nombre_archivo_importacion=planilla)

            parser = ParserCsv()
            estructura_archivo = parser.previsualiza_archivo(bd_contacto)
            predictor_metadata = PredictorMetadataService()
            metadata_inferida = predictor_metadata.inferir_metadata_desde_lineas(
                estructura_archivo, "utf-8")

            metadata = bd_contacto.get_metadata()
            metadata._metadata = metadata_inferida._metadata
            metadata.nombres_de_columnas = ["COL{0}".format(num)
                                            for num in range(metadata.cantidad_de_columnas)]
            metadata.save()

            creacion_base_datos_service = CreacionBaseDatosService()
            creacion_base_datos_service.importa_contactos(bd_contacto)
            creacion_base_datos_service.define_base_dato_contacto(bd_contacto)

            # ----- checks

            self.assertEquals(BaseDatosContacto.objects.get(pk=bd_contacto.id).estado,
                              BaseDatosContacto.ESTADO_DEFINIDA,
                              "La BD generada desde '{0}' NO ha quedado en estado ESTADO_DEFINIDA"
                              "".format(planilla))

            self.assertTrue(Contacto.objects.filter(bd_contacto=bd_contacto.id).count() > 0,
                            "La BD generada desde '{0}' NO posee contactos".format(planilla))
