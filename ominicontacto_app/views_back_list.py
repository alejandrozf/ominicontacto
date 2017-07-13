# -*- coding: utf-8 -*-

"""Vista Backlist para crear una nueva Backlist o llamada listas negras de telefonos"""

from __future__ import unicode_literals

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic.edit import (
    CreateView
)
from django.views.generic.list import ListView
from ominicontacto_app.errors import (
    OmlParserCsvDelimiterError, OmlParserMinRowError, OmlParserOpenFileError,
    OmlArchivoImportacionInvalidoError)
from ominicontacto_app.forms import BacklistForm
from ominicontacto_app.models import Backlist
from ominicontacto_app.parser import ParserCsv
from ominicontacto_app.services.back_list import (
    CreacionBacklistService, ValidaDataService, NoSePuedeInferirMetadataError,
    NoSePuedeInferirMetadataErrorEncabezado)

import logging as logging_


logger = logging_.getLogger(__name__)


class BackListView(ListView):
    """
    Esta vista es para generar el listado de
    Lista de Contactos.
    """

    template_name = 'back_list/lista_back_list.html'
    context_object_name = 'back_lists'
    model = Backlist


class BacklistCreateView(CreateView):
    """
    Esta vista crea una instancia de Backlist
    sin definir, lo que implica que no esta disponible
    hasta que se procese su definición.
    """

    def obtiene_previsualizacion_archivo(self, back_list):
        """
        Instancia el servicio ParserCsv e intenta obtener un resumen de las
        primeras 3 lineas del csv.
        """

        try:
            parser = ParserCsv()
            estructura_archivo = parser.previsualiza_archivo(
                back_list)

        except OmlParserCsvDelimiterError:
            message = '<strong>Operación Errónea!</strong> \
            No se pudo determinar el delimitador a ser utilizado \
            en el archivo csv. No se pudo llevar a cabo el procesamiento \
            de sus datos.'

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
        except OmlParserMinRowError:
            message = '<strong>Operación Errónea!</strong> \
            El archivo que seleccionó posee menos de 3 filas.\
            No se pudo llevar a cabo el procesamiento de sus datos.'

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
        except OmlParserOpenFileError:
            message = '<strong>Operación Errónea!</strong> \
            El archivo que seleccionó no pudo ser abierto para su \
            para su procesamiento.'

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
        else:
            return estructura_archivo

    template_name = 'back_list/nueva_edita_back_list.html'
    model = Backlist
    context_object_name = 'backlist'
    form_class = BacklistForm

    def form_valid(self, form):
        nombre_archivo_importacion = \
            self.request.FILES['archivo_importacion'].name

        self.object = form.save(commit=False)
        self.object.nombre_archivo_importacion = nombre_archivo_importacion

        try:
            creacion_back_list = CreacionBacklistService()
            creacion_back_list.genera_back_list(self.object)
        except OmlArchivoImportacionInvalidoError:
            message = '<strong>Operación Errónea!</strong> \
            El archivo especificado para realizar la importación de contactos \
            no es válido.'

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return self.form_invalid(form)
        estructura_archivo = self.obtiene_previsualizacion_archivo(self.object)
        try:
            validata_data = ValidaDataService()
            validata_data.valida_datos_desde_lineas(estructura_archivo)
        except NoSePuedeInferirMetadataError:
            message = '<strong>Operación Errónea!</strong> \
                        No se puede interferir lo datos de la backlist y \
                        no es válido.'

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return self.form_invalid(form)
        except NoSePuedeInferirMetadataErrorEncabezado:
            message = '<strong>Operación Errónea!</strong> \
                      El encabezado del archivo es erroneo el nombre de la primera  \
                      columna debe ser telefono.'

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return self.form_invalid(form)
        self.object.save()
        creacion_back_list = CreacionBacklistService()
        creacion_back_list.importa_contactos(self.object)
        creacion_back_list.crear_archivo_backlist(self.object)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            'back_list_list')
