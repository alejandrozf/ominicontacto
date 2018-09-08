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

"""Views para generar una nueva base de datos de contactos"""

from __future__ import unicode_literals

import json

from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic.edit import (
    CreateView, UpdateView, DeleteView
)
from django.views.generic.list import ListView
from django.views.generic.base import RedirectView
from ominicontacto_app.errors import (
    OmlParserCsvDelimiterError, OmlParserMinRowError, OmlParserOpenFileError,
    OmlParserMaxRowError, OmlDepuraBaseDatoContactoError,
    OmlParserCsvImportacionError, OmlArchivoImportacionInvalidoError)
from ominicontacto_app.forms import (
    BaseDatosContactoForm, DefineNombreColumnaForm, DefineColumnaTelefonoForm,
    DefineDatosExtrasForm, PrimerLineaEncabezadoForm)
from ominicontacto_app.models import BaseDatosContacto, UserApiCrm
from ominicontacto_app.parser import ParserCsv
from ominicontacto_app.services.base_de_datos_contactos import (
    CreacionBaseDatosService, PredictorMetadataService,
    NoSePuedeInferirMetadataError, NoSePuedeInferirMetadataErrorEncabezado,
    ContactoExistenteError, CreacionBaseDatosApiService)
from django.views.decorators.csrf import csrf_exempt
import logging as logging_


logger = logging_.getLogger(__name__)

# =============================================================================
# Base Datos Contacto
# =============================================================================


class BaseDatosContactoListView(ListView):
    """
    Esta vista es para generar el listado de
    Lista de Contactos.
    """

    template_name = 'base_datos_contacto/lista_base_datos_contacto.html'
    context_object_name = 'bases_datos_contacto'
    model = BaseDatosContacto

    def get_queryset(self):
        queryset = BaseDatosContacto.objects.obtener_definidas()
        return queryset


class BaseDatosContactoCreateView(CreateView):
    """
    Esta vista crea una instancia de BaseDatosContacto
    sin definir, lo que implica que no esta disponible
    hasta que se procese su definición.
    """

    template_name = 'base_datos_contacto/nueva_edita_base_datos_contacto.html'
    model = BaseDatosContacto
    context_object_name = 'base_datos_contacto'
    form_class = BaseDatosContactoForm

    def form_valid(self, form):
        nombre_archivo_importacion = \
            self.request.FILES['archivo_importacion'].name

        self.object = form.save(commit=False)
        self.object.nombre_archivo_importacion = nombre_archivo_importacion

        try:
            creacion_base_datos = CreacionBaseDatosService()
            creacion_base_datos.genera_base_dato_contacto(self.object)
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

        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            'define_base_datos_contacto',
            kwargs={"pk": self.object.pk})


class BaseDatosContactoUpdateView(UpdateView):
    """
    Esta vista crea una instancia de BaseDatosContacto
    sin definir, lo que implica que no esta disponible
    hasta que se procese su definición.
    """

    template_name = 'base_datos_contacto/nueva_edita_base_datos_contacto.html'
    model = BaseDatosContacto
    context_object_name = 'base_datos_contacto'
    form_class = BaseDatosContactoForm

    def get_object(self, queryset=None):
        return BaseDatosContacto.objects.get(pk=self.kwargs['pk_bd_contacto'])

    def form_valid(self, form):

        self.object = form.save(commit=False)
        self.object.estado = BaseDatosContacto.ESTADO_DEFINIDA_ACTUALIZADA
        # self.object.nombre_archivo_importacion = nombre_archivo_importacion

        try:
            creacion_base_datos = CreacionBaseDatosService()
            creacion_base_datos.genera_base_dato_contacto(self.object)
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

        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            'actualiza_base_datos_contacto',
            kwargs={"pk": self.object.pk})


class DefineBaseDatosContactoView(UpdateView):
    """
    Esta vista se obtiene un resumen de la estructura
    del archivo a importar y la presenta al usuario para
    que seleccione en que columna se encuentra el teléfono.
    Guarda la posición de la columna como entero y llama a
    importar los teléfono del archivo que se guardo.
    Si la importación resulta bien, llama a definir el objeto
    BaseDatosContacto para que esté disponible.
    """

    template_name = 'base_datos_contacto/define_base_datos_contacto.html'
    model = BaseDatosContacto
    context_object_name = 'base_datos_contacto'
    fields = '__all__'

    # @@@@@@@@@@@@@@@@@@@@

    def dispatch(self, request, *args, **kwargs):
        self.base_datos_contacto = \
            BaseDatosContacto.objects.obtener_en_actualizada_para_editar(
                self.kwargs['pk'])
        return super(DefineBaseDatosContactoView, self).dispatch(request,
                                                                 *args,
                                                                 **kwargs)

    def obtiene_previsualizacion_archivo(self, base_datos_contacto):
        """
        Instancia el servicio ParserCsv e intenta obtener un resumen de las
        primeras 3 lineas del csv.
        """

        try:
            parser = ParserCsv()
            estructura_archivo = parser.previsualiza_archivo(
                base_datos_contacto)

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

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        estructura_archivo = self.obtiene_previsualizacion_archivo(self.object)

        if estructura_archivo:
            cantidad_de_columnas = len(estructura_archivo[0])
            parser = ParserCsv()
            encoding = parser.detectar_encoding_csv(estructura_archivo)
            estructura_archivo_transformada = parser.visualizar_estructura_template(
                estructura_archivo, encoding
            )
            try:
                error_predictor = False
                error_predictor_encabezado = False

                predictor_metadata = PredictorMetadataService()
                metadata = predictor_metadata.inferir_metadata_desde_lineas(
                    estructura_archivo, encoding)
            except NoSePuedeInferirMetadataError:
                initial_predecido_columna_telefono = {}
                initial_predecido_datos_extras = {}
                initial_predecido_nombre_columnas = {}
                initial_predecido_encabezado = {}

                error_predictor = True
            except NoSePuedeInferirMetadataErrorEncabezado:
                initial_predecido_columna_telefono = {}
                initial_predecido_datos_extras = {}
                initial_predecido_nombre_columnas = {}
                initial_predecido_encabezado = {}

                error_predictor_encabezado = True
            else:

                initial_predecido_columna_telefono = \
                    {'telefono': metadata.columna_con_telefono}

                initial_predecido_datos_extras = dict(
                    [('datos-extras-{0}'.format(col),
                        BaseDatosContacto.DATO_EXTRA_FECHA)
                        for col in metadata.columnas_con_fecha])

                initial_predecido_datos_extras.update(dict(
                    [('datos-extras-{0}'.format(col),
                        BaseDatosContacto.DATO_EXTRA_HORA)
                        for col in metadata.columnas_con_hora]))

                initial_predecido_nombre_columnas = dict(
                    [('nombre-columna-{0}'.format(i), nombre)
                        for i, nombre in enumerate(
                            metadata.nombres_de_columnas)])

                initial_predecido_encabezado = {
                    'es_encabezado': metadata.primer_fila_es_encabezado}

            form_columna_telefono = DefineColumnaTelefonoForm(
                cantidad_columnas=cantidad_de_columnas,
                initial=initial_predecido_columna_telefono)

            form_datos_extras = DefineDatosExtrasForm(
                cantidad_columnas=cantidad_de_columnas,
                initial=initial_predecido_datos_extras)

            form_nombre_columnas = DefineNombreColumnaForm(
                cantidad_columnas=cantidad_de_columnas,
                initial=initial_predecido_nombre_columnas)

            form_primer_linea_encabezado = PrimerLineaEncabezadoForm(
                initial=initial_predecido_encabezado)

            return self.render_to_response(self.get_context_data(
                error_predictor_encabezado=error_predictor_encabezado,
                error_predictor=error_predictor,
                estructura_archivo=estructura_archivo_transformada,
                #form_columna_telefono=form_columna_telefono,
                #form_datos_extras=form_datos_extras,
                #form_nombre_columnas=form_nombre_columnas,
                form_primer_linea_encabezado=form_primer_linea_encabezado
            ))

        return redirect(reverse('nueva_base_datos_contacto'))

    def form_invalid(self, estructura_archivo,
                     form_primer_linea_encabezado, error=None):

        message = '<strong>Operación Errónea!</strong> \
                  Verifique el archivo cargado. {0}'.format(error)

        messages.add_message(
            self.request,
            messages.ERROR,
            message,
        )

        return self.render_to_response(self.get_context_data(
            estructura_archivo=estructura_archivo,
            #form_columna_telefono=form_columna_telefono,
            #form_datos_extras=form_datos_extras,
            #form_nombre_columnas=form_nombre_columnas,
            form_primer_linea_encabezado=form_primer_linea_encabezado))

    def form_valid(self, estructura_archivo,
                   form_primer_linea_encabezado):
        # columna_con_telefono = int(form_columna_telefono.cleaned_data.get(
        #                            'telefono', None))
        lista_columnas_fechas = []
        lista_columnas_horas = []
        lista_nombre_columnas = []

        #cantidad_columnas = len(form_nombre_columnas.fields)
        cantidad_columnas = len(estructura_archivo[0])

        # for numero_columna in range(cantidad_columnas):
        #     dato_extra = form_datos_extras.cleaned_data.get(
        #         'datos-extras-{0}'.format(numero_columna), None)
        #     if dato_extra == BaseDatosContacto.DATO_EXTRA_FECHA:
        #         lista_columnas_fechas.append(numero_columna)
        #     elif dato_extra == BaseDatosContacto.DATO_EXTRA_HORA:
        #         lista_columnas_horas.append(numero_columna)
        #
        #     nombre_columna = form_nombre_columnas.cleaned_data.get(
        #         'nombre-columna-{0}'.format(numero_columna), None)
        #
        #     validador_nombre = ValidadorDeNombreDeCampoExtra()
        #     if not validador_nombre.validar_nombre_de_columna(nombre_columna):
        #         error = 'El nombre de la Columna{0} no es válido. Debe estar \
        #                  en mayúscula y sin espacios. Por ejemplo: \
        #                  TELEFONO_FIJO'.format(numero_columna)
        #
        #         return self.form_invalid(estructura_archivo,
        #                                  #form_columna_telefono,
        #                                  #form_datos_extras,
        #                                  #form_nombre_columnas,
        #                                  form_primer_linea_encabezado,
        #                                  error=error)
        #
        #     lista_nombre_columnas.append(nombre_columna)

        lista_columnas_encabezado = estructura_archivo[0]

        error = None

        if lista_columnas_encabezado[0] != 'telefono':
            error = "El nombre de la primera columna debe ser telefono"

        if error:
            return self.form_invalid(estructura_archivo,
                                     form_primer_linea_encabezado, error=error)

        parser = ParserCsv()
        # Detecto el encondig de la base de datoss recientemente subida
        encoding = parser.detectar_encoding_csv(estructura_archivo)
        metadata = self.object.get_metadata()
        metadata.cantidad_de_columnas = cantidad_columnas
        predictor_metadata = PredictorMetadataService()
        columnas_con_telefonos = predictor_metadata.inferir_columnas_telefono(
            estructura_archivo[1:], encoding)
        metadata.columnas_con_telefono = columnas_con_telefonos
        #metadata.columnas_con_fecha = lista_columnas_fechas
        #metadata.columnas_con_hora = lista_columnas_horas
        metadata.nombres_de_columnas = [value.decode(encoding)
                                        for value in estructura_archivo[0]]

        es_encabezado = False
        if self.request.POST.get('es_encabezado', False):
            es_encabezado = True
        metadata.primer_fila_es_encabezado = es_encabezado
        metadata.save()

        creacion_base_datos = CreacionBaseDatosService()

        try:
            #creacion_base_datos.valida_contactos(self.object)
            creacion_base_datos.importa_contactos(self.object)
        except OmlParserCsvImportacionError as e:

            message = '<strong>Operación Errónea!</strong>\
                      El archivo que seleccionó posee registros inválidos.<br>\
                      <u>Línea Inválida:</u> {0}<br> <u>Contenido Línea:</u>\
                      {1}<br><u>Contenido Inválido:</u> {2}'.format(
                      e.numero_fila, e.fila, e.valor_celda)

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            # FIXME: Ver bien que hacer acá.

        except ContactoExistenteError as e:

            message = '<strong>Operación Errónea!</strong>\
                          El archivo que seleccionó posee registros inválidos.<br>\
                           ERROR: {0}. Vuelva cargar nuevamente la base de datos ' \
                      ' sin el contacto existente '.format(e)

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )


            return self.render_to_response(self.get_context_data(
                estructura_archivo=estructura_archivo,
                #form_columna_telefono=form_columna_telefono,
                #form_datos_extras=form_datos_extras,
                #form_nombre_columnas=form_nombre_columnas,
                form_primer_linea_encabezado=form_primer_linea_encabezado))

        except OmlParserMaxRowError:
            message = '<strong>Operación Errónea!</strong> \
                      El archivo que seleccionó posee mas registros de los\
                      permitidos para ser importados.'

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return redirect(reverse('lista_base_datos_contacto'))
        else:
            creacion_base_datos.define_base_dato_contacto(self.object)

            message = '<strong>Operación Exitosa!</strong>\
                      Se llevó a cabo con éxito la creación de\
                      la Base de Datos de Contactos.'

            messages.add_message(
                self.request,
                messages.SUCCESS,
                message,
            )
            return redirect(self.get_success_url())

    def post(self, request, *args, **kwargs):

        self.object = self.get_object()

        estructura_archivo = self.obtiene_previsualizacion_archivo(self.object)
        if estructura_archivo:
            cantidad_columnas = len(estructura_archivo[0])

            #form_columna_telefono = DefineColumnaTelefonoForm(
            #    cantidad_columnas, request.POST)
            #form_datos_extras = DefineDatosExtrasForm(
            #    cantidad_columnas, request.POST)
            #form_nombre_columnas = DefineNombreColumnaForm(
            #    cantidad_columnas, request.POST)
            form_primer_linea_encabezado = PrimerLineaEncabezadoForm(
                request.POST)

            if form_primer_linea_encabezado.is_valid():

                return self.form_valid(estructura_archivo,
                                       #form_columna_telefono,
                                       #form_datos_extras,
                                       #form_nombre_columnas,
                                       form_primer_linea_encabezado)
            else:
                return self.form_invalid(estructura_archivo,
                                         #form_columna_telefono,
                                         #form_datos_extras,
                                         #form_nombre_columnas,
                                         form_primer_linea_encabezado)
        return redirect(reverse('nueva_base_datos_contacto'))

    def get_success_url(self):
        return reverse('lista_base_datos_contacto')


class DepuraBaseDatosContactoView(DeleteView):
    """
    Esta vista se encarga de la depuración del
    objeto Base de Datos seleccionado.
    """

    model = BaseDatosContacto
    template_name = 'base_datos_contacto/depura_base_datos_contacto.html'

    def dispatch(self, request, *args, **kwargs):
        self.base_datos_contacto = \
            BaseDatosContacto.objects.obtener_definida_para_depurar(
                self.kwargs['pk'])
        return super(DepuraBaseDatosContactoView, self).dispatch(request,
                                                                 *args,
                                                                 **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()

        if self.object.verifica_en_uso():
            message = """<strong>¡Cuidado!</strong>
            La Base Datos Contacto que intenta depurar esta siendo utilizada
            por alguna campaña. No se llevará a cabo la depuración la misma
            mientras esté siendo utilizada."""
            messages.add_message(
                self.request,
                messages.WARNING,
                message,
            )
            return HttpResponseRedirect(success_url)

        try:
            self.object.procesa_depuracion()
        except OmlDepuraBaseDatoContactoError:
            message = """<strong>¡Operación Errónea!</strong>
            La Base Datos Contacto no se pudo depurar."""
            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return HttpResponseRedirect(success_url)
        else:
            message = '<strong>Operación Exitosa!</strong>\
            Se llevó a cabo con éxito la depuración de la Base de Datos.'

            messages.add_message(
                self.request,
                messages.SUCCESS,
                message,
            )
            return HttpResponseRedirect(success_url)

    def get_success_url(self):
        return reverse(
            'lista_base_datos_contacto',
        )


class ActualizaBaseDatosContactoView(UpdateView):
    """
    Esta vista se obtiene un resumen de la estructura
    del archivo a importar y la presenta al usuario para
    que seleccione en que columna se encuentra el teléfono.
    Guarda la posición de la columna como entero y llama a
    importar los teléfono del archivo que se guardo.
    Si la importación resulta bien, llama a definir el objeto
    BaseDatosContacto para que esté disponible.
    """

    template_name = 'base_datos_contacto/define_base_datos_contacto.html'
    model = BaseDatosContacto
    context_object_name = 'base_datos_contacto'
    fields = '__all__'

    # @@@@@@@@@@@@@@@@@@@@

    def dispatch(self, request, *args, **kwargs):
        self.base_datos_contacto = \
            BaseDatosContacto.objects.obtener_en_actualizada_para_editar(
                self.kwargs['pk'])
        return super(ActualizaBaseDatosContactoView, self).dispatch(request,
                                                                 *args,
                                                                 **kwargs)

    def obtiene_previsualizacion_archivo(self, base_datos_contacto):
        """
        Instancia el servicio ParserCsv e intenta obtener un resumen de las
        primeras 3 lineas del csv.
        """

        try:
            parser = ParserCsv()
            estructura_archivo = parser.previsualiza_archivo(
                base_datos_contacto)

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

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        estructura_archivo = self.obtiene_previsualizacion_archivo(self.object)
        if estructura_archivo:
            cantidad_de_columnas = len(estructura_archivo[0])

            try:
                error_predictor = False
                error_predictor_encabezado = False

                predictor_metadata = PredictorMetadataService()
                metadata = predictor_metadata.\
                    inferir_metadata_desde_lineas_base_existente(self.object,
                    estructura_archivo)
            except NoSePuedeInferirMetadataError:
                initial_predecido_encabezado = {}

                error_predictor = True
            except NoSePuedeInferirMetadataErrorEncabezado:
                initial_predecido_encabezado = {}

                error_predictor_encabezado = True
            else:
                initial_predecido_datos_extras = dict(
                    [('datos-extras-{0}'.format(col),
                        BaseDatosContacto.DATO_EXTRA_FECHA)
                        for col in metadata.columnas_con_fecha])

                initial_predecido_datos_extras.update(dict(
                    [('datos-extras-{0}'.format(col),
                        BaseDatosContacto.DATO_EXTRA_HORA)
                        for col in metadata.columnas_con_hora]))

                initial_predecido_encabezado = {
                    'es_encabezado': metadata.primer_fila_es_encabezado}

            form_primer_linea_encabezado = PrimerLineaEncabezadoForm(
                initial=initial_predecido_encabezado)

            return self.render_to_response(self.get_context_data(
                error_predictor_encabezado=error_predictor_encabezado,
                error_predictor=error_predictor,
                estructura_archivo=estructura_archivo,
                form_primer_linea_encabezado=form_primer_linea_encabezado
            ))

        return redirect(reverse('nueva_base_datos_contacto'))

    def form_invalid(self, estructura_archivo,
                     form_primer_linea_encabezado, error=None):

        message = '<strong>Operación Errónea!</strong> \
                  Verifique el archivo cargado. {0}'.format(error)

        messages.add_message(
            self.request,
            messages.ERROR,
            message,
        )

        return self.render_to_response(self.get_context_data(
            estructura_archivo=estructura_archivo,
            form_primer_linea_encabezado=form_primer_linea_encabezado))

    def form_valid(self, estructura_archivo,
                   form_primer_linea_encabezado):

        cantidad_columnas = len(estructura_archivo[0])

        lista_columnas_encabezado = estructura_archivo[0]

        error = None

        metadata = self.object.get_metadata()
        metadata.cantidad_de_columnas = cantidad_columnas

        for columna_base, columna_csv in zip(metadata.nombres_de_columnas, lista_columnas_encabezado):
            if columna_base != columna_csv:
                error = "El nombre de la columna debe ser {0} en vez de {1}".\
                    format(columna_base, columna_csv)

        if error:
            return self.form_invalid(estructura_archivo,
                                     form_primer_linea_encabezado, error=error)

        es_encabezado = False
        if self.request.POST.get('es_encabezado', False):
            es_encabezado = True
        metadata.primer_fila_es_encabezado = es_encabezado
        metadata.save()

        creacion_base_datos = CreacionBaseDatosService()

        try:
            #creacion_base_datos.valida_contactos(self.object)
            creacion_base_datos.importa_contactos(self.object)
        except OmlParserCsvImportacionError as e:

            message = '<strong>Operación Errónea!</strong>\
                      El archivo que seleccionó posee registros inválidos.<br>\
                      <u>Línea Inválida:</u> {0}<br> <u>Contenido Línea:</u>\
                      {1}<br><u>Contenido Inválido:</u> {2}'.format(
                      e.numero_fila, e.fila, e.valor_celda)

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            # FIXME: Ver bien que hacer acá.

        except ContactoExistenteError as e:

            message = '<strong>Operación Errónea!</strong>\
                          El archivo que seleccionó posee registros inválidos.<br>\
                           ERROR: {0}. Vuelva cargar nuevamente la base de datos ' \
                      ' sin el contacto existente '.format(e)

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )

            return self.render_to_response(self.get_context_data(
                estructura_archivo=estructura_archivo,
                form_primer_linea_encabezado=form_primer_linea_encabezado))

        except OmlParserMaxRowError:
            message = '<strong>Operación Errónea!</strong> \
                      El archivo que seleccionó posee mas registros de los\
                      permitidos para ser importados.'

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return redirect(reverse('lista_base_datos_contacto'))
        else:
            creacion_base_datos.define_base_dato_contacto(self.object)

            message = '<strong>Operación Exitosa!</strong>\
                      Se llevó a cabo con éxito la creación de\
                      la Base de Datos de Contactos.'

            messages.add_message(
                self.request,
                messages.SUCCESS,
                message,
            )
            return redirect(self.get_success_url())

    def post(self, request, *args, **kwargs):

        self.object = self.get_object()

        estructura_archivo = self.obtiene_previsualizacion_archivo(self.object)
        if estructura_archivo:
            form_primer_linea_encabezado = PrimerLineaEncabezadoForm(
                request.POST)
            if form_primer_linea_encabezado.is_valid():

                return self.form_valid(estructura_archivo,
                                       form_primer_linea_encabezado)
            else:
                return self.form_invalid(estructura_archivo,
                                         form_primer_linea_encabezado)
        return redirect(reverse('nueva_base_datos_contacto'))

    def get_success_url(self):
        return reverse('lista_base_datos_contacto')


class OcultarBaseView(RedirectView):
    """
    Esta vista actualiza la base de datos ocultandola.
    """

    pattern_name = 'lista_base_datos_contacto'

    def get(self, request, *args, **kwargs):
        base = BaseDatosContacto.objects.get(pk=self.kwargs['bd_contacto'])
        base.ocultar()
        return HttpResponseRedirect(reverse('lista_base_datos_contacto'))


class DesOcultarBaseView(RedirectView):
    """
    Esta vista actualiza la base haciendola visible.
    """

    pattern_name = 'lista_base_datos_contacto'

    def get(self, request, *args, **kwargs):
        base = BaseDatosContacto.objects.get(pk=self.kwargs['bd_contacto'])
        base.desocultar()
        return HttpResponseRedirect(reverse('lista_base_datos_contacto'))


def mostrar_bases_datos_borradas_ocultas_view(request):
    """Esta vista muestra la base de datos ocultas"""
    bases_datos_contacto = BaseDatosContacto.objects.obtener_definidas_ocultas()
    data = {
        'bases_datos_contacto': bases_datos_contacto,
    }
    return render(request, 'base_datos_contacto/base_datos_ocultas.html', data)


@csrf_exempt
def cargar_base_datos_view(request):
    """Servicio externo para cargar una base de datos via post"""
    if request.method == 'POST':
        received_json_data = json.loads(request.body)
        # tener en cuenta que se espera json con estas claves
        data_esperada = ['nombre', 'datos', 'columnas', 'user_api',
                         'password_api']
        for data in data_esperada:
            if data not in received_json_data.keys():
                return JsonResponse({'status': 'Error en falta {0}'.format(data)
                                     })

        try:
            usuario = UserApiCrm.objects.get(
                usuario=received_json_data['user_api'])
            received_password = received_json_data['password_api']
            if check_password(received_password,usuario.password):
               service = CreacionBaseDatosApiService()
               base_datos = service.crear_base_datos_api(
                   received_json_data['nombre'])

               predictor = service.inferir_metadata_desde_lineas(
                   received_json_data['columnas'], received_json_data['datos'])

               metadata = base_datos.get_metadata()
               metadata.cantidad_de_columnas = predictor.cantidad_de_columnas

               columnas_con_telefonos = service.inferir_columnas_telefono(
                   received_json_data['datos'])
               metadata.columnas_con_telefono = columnas_con_telefonos
               metadata.nombres_de_columnas = received_json_data['columnas']

               es_encabezado = False

               metadata.primer_fila_es_encabezado = es_encabezado
               metadata.save()
               base_datos.save()

               try:
                   service.importa_contactos(base_datos,
                                             received_json_data['datos'])
                   base_datos.define()
               except OmlParserCsvImportacionError as e:

                   message = '<strong>Operación Errónea!</strong>\
                             El archivo que seleccionó posee registros inválidos.<br>\
                             <u>Línea Inválida:</u> {0}<br> <u>Contenido Línea:</u>\
                             {1}<br><u>Contenido Inválido:</u> {2}'.format(
                       e.numero_fila, e.fila, e.valor_celda)

                   logger.error(message)
            else:
                return JsonResponse({'status': 'no coinciden usuario y/o password'})
        except UserApiCrm.DoesNotExist:
            return JsonResponse({'status': 'no existe este usuario {0}'.format(
                received_json_data['user_api'])})
        return JsonResponse({'status': 'OK'})
    else:
        return JsonResponse({'status': 'este es un metodo post'})
