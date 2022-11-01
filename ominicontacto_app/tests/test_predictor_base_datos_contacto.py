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
        metadata = predictor_metadata.inferir_metadata_desde_lineas(estructura_archivo)

        validador_nombre = ValidadorDeNombreDeCampoExtra()
        for nombre_columna in metadata.nombres_de_columnas:
            self.assertTrue(validador_nombre.validar_nombre_de_columna(
                nombre_columna), "el nombre de columna es invalido")
