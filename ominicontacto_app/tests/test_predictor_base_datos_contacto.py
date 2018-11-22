# -*- coding: utf-8 -*-

"""
    Este modulo testea el servicio PredictoMetadagtaService
"""

from __future__ import unicode_literals

from ominicontacto_app.models import BaseDatosContacto
from ominicontacto_app.services.base_de_datos_contactos import PredictorMetadataService
from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.parser import ParserCsv
from ominicontacto_app.utiles import ValidadorDeNombreDeCampoExtra
import logging as logging_


logger = logging_.getLogger(__name__)


class PredictorBaseDatosContactoTests(OMLBaseTest):
    """Unit tests de PreditorMetadataService"""

    def test_inferir_metadata_correctamente(self):

        planilla = self.copy_test_resource_to_mediaroot("planilla-ejemplo-1.csv")
        nombre_archivo = "planilla-ejemplo-10.csv"
        base_test = BaseDatosContacto.objects.create(
            nombre="test", archivo_importacion=planilla,
            nombre_archivo_importacion=nombre_archivo, metadata="")

        parser = ParserCsv()
        estructura_archivo = parser.previsualiza_archivo(base_test)

        predictor_metadata = PredictorMetadataService()
        metadata = predictor_metadata.inferir_metadata_desde_lineas(estructura_archivo, "utf-8")

        validador_nombre = ValidadorDeNombreDeCampoExtra()
        for nombre_columna in metadata.nombres_de_columnas:
            self.assertTrue(validador_nombre.validar_nombre_de_columna(
                nombre_columna), "el nombre de columna es invalido")
