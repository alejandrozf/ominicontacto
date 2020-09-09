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

import json

from django.utils.translation import ugettext as _

from ominicontacto_app.services.base_de_datos_contactos import \
    CreacionBaseDatosServiceIdExternoError, PredictorMetadataService
from ominicontacto_app.parser import ParserCsv
from ominicontacto_app.errors import OmlArchivoImportacionInvalidoError, \
    OmlError, OmlParserCsvImportacionError, OmlParserMaxRowError, OmlParserRepeatedColumnsError
from ominicontacto_app.models import BaseDatosContacto, Contacto

from api_app.utils.contactos.base_datos_contacto_archivo_parser \
    import BaseDatosContactoArchivoCSVParser


class BaseDatosContactoService(object):

    def __init__(self) -> None:
        self.parser = None
        self.legacy_parser = ParserCsv()

    def crear_bd_contactos(self, archivo, nombre_archivo, nombre_bd) -> int:
        model_base_contactos = BaseDatosContacto()
        if self._existe_bd_contactos(nombre_bd):
            raise(OmlError(_("Ya existe una base de datos de contactos con ese nombre")))
        self.parser = BaseDatosContactoArchivoCSVParser(nombre_archivo, archivo)

        if not self.parser.es_valida_extension() or not self.parser.es_valido_archivo():
            file_invalid_msg = _("El archivo especificado para realizar la importación de "
                                 "contactos no es válido.")
            raise(OmlArchivoImportacionInvalidoError(file_invalid_msg))

        if not self.parser.headers_no_repetidos():
            raise OmlParserRepeatedColumnsError(_("El archivo a procesar tiene nombres de columnas "
                                                  "repetidos."))

        model_base_contactos.archivo_importacion = archivo
        model_base_contactos.nombre_archivo_importacion = nombre_archivo
        model_base_contactos.nombre = nombre_bd
        model_base_contactos.save()

        return model_base_contactos.id

    def define_base_datos_contactos(self, base_datos_contacto) -> None:
        base_datos_contacto.define()

    def obtiene_subconjunto_filas_archivo(self, base_datos_contacto) -> dict:
        return self.legacy_parser.previsualiza_archivo(base_datos_contacto)

    def inferir_metadata(self, estructura_archivo):
        predictor_metadata = PredictorMetadataService()
        return predictor_metadata.inferir_metadata_desde_lineas(
            estructura_archivo)

    def importa_contactos_desde_api(self, id, campos_telefonicos, columna_id_externo):
        bd_contactos = BaseDatosContacto.objects.obtener_en_actualizada_para_editar(id)
        self.importa_contactos(bd_contactos, campos_telefonicos, columna_id_externo)

    def importa_contactos(self, base_datos_contacto, campos_telefonicos, columna_id_externo):
        """
        Tercer paso de la creación de una BaseDatosContacto.
        Este método se encarga de generar los objectos Contacto por cada linea
        del archivo de importación especificado para la base de datos de
        contactos.
        """

        assert (base_datos_contacto.estado in
                (BaseDatosContacto.ESTADO_EN_DEFINICION,
                 BaseDatosContacto.ESTADO_DEFINIDA_ACTUALIZADA))

        ids_externos = base_datos_contacto.contactos.values_list('id_externo', flat=True)
        ids_externos = set(ids_externos)
        ids_nuevos_contactos = []

        try:
            estructura_archivo = self.legacy_parser.get_estructura_archivo(base_datos_contacto)
            posicion_primer_telefono = estructura_archivo[0].index(campos_telefonicos[0])
            cantidad_contactos = 0
            if base_datos_contacto.cantidad_contactos:
                cantidad_contactos = base_datos_contacto.cantidad_contactos
            numero_fila = 0
            for lista_dato in estructura_archivo[1:]:
                numero_fila += 1
                telefono, datos, id_externo = self._obtener_telefono_y_datos(
                    lista_dato, posicion_primer_telefono, columna_id_externo)
                cantidad_contactos += 1
                if id_externo is not None and id_externo != '':
                    # El id_externo no puede estar repetido
                    if id_externo in ids_externos:
                        base_datos_contacto.contactos.filter(id__in=ids_nuevos_contactos).delete()
                        raise(CreacionBaseDatosServiceIdExternoError(numero_fila,
                                                                     columna_id_externo,
                                                                     lista_dato,
                                                                     id_externo))
                    else:
                        ids_externos.add(id_externo)

                contacto = Contacto.objects.create(
                    telefono=telefono,
                    datos=datos,
                    bd_contacto=base_datos_contacto,
                    id_externo=id_externo
                )
                ids_nuevos_contactos.append(contacto.id)
        except OmlParserMaxRowError:
            base_datos_contacto.contactos.filter(id__in=ids_nuevos_contactos).delete()
            raise OmlError(_("Archivo excede máximo de filas permitidas"))

        except OmlParserCsvImportacionError:
            base_datos_contacto.contactos.filter(id__in=ids_nuevos_contactos).delete()
            raise OmlError(_("Error al parsear el archivo csv"))

        base_datos_contacto.cantidad_contactos = cantidad_contactos

        base_datos_contacto.save()

        self.define_base_datos_contactos(base_datos_contacto)

    def _existe_bd_contactos(self, nombre) -> bool:
        return BaseDatosContacto.objects.filter(nombre=nombre).exists()

    def _obtener_telefono_y_datos(self, lista_dato, posicion_primer_telefono,
                                  columna_id_externo) -> any:
        id_externo = None
        if len(lista_dato) > 1:
            item = []
            for i, valor in enumerate(lista_dato):
                if i == posicion_primer_telefono:
                    telefono = valor
                elif i == columna_id_externo:
                    id_externo = valor
                else:
                    item.append(valor)
        else:
            telefono = lista_dato[0]
            item = ['']

        datos = json.dumps(item)
        return telefono, datos, id_externo

    def remove_db(self, id):
        BaseDatosContacto.objects.filter(id=id).delete()
