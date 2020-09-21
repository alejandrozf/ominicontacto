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

from django.contrib import messages
from django.urls import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.generic.edit import (
    CreateView, UpdateView, DeleteView
)
from django.views.generic.list import ListView
from django.views.generic.base import RedirectView
from django.utils.translation import ugettext as _

from ominicontacto_app.errors import (
    OmlParserCsvDelimiterError, OmlParserMinRowError, OmlParserOpenFileError,
    OmlParserMaxRowError, OmlDepuraBaseDatoContactoError, OmlParserRepeatedColumnsError,
    OmlParserCsvImportacionError, OmlArchivoImportacionInvalidoError,
    OmlError)
from ominicontacto_app.forms import (
    BaseDatosContactoForm, PrimerLineaEncabezadoForm, CamposDeBaseDeDatosForm, )
from ominicontacto_app.models import BaseDatosContacto, Campana, AgenteEnContacto
from ominicontacto_app.parser import ParserCsv
from ominicontacto_app.services.base_de_datos_contactos import (
    CreacionBaseDatosService, PredictorMetadataService,
    NoSePuedeInferirMetadataError, NoSePuedeInferirMetadataErrorEncabezado,
    ContactoExistenteError, CreacionBaseDatosServiceIdExternoError)

from api_app.services.base_datos_contacto_service import BaseDatosContactoService

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
        archivo = self.request.FILES['archivo_importacion']
        archivo_nombre = archivo.name
        nombre_base_contactos = form.cleaned_data['nombre']

        base_datos_contacto_service = BaseDatosContactoService()

        try:
            id = base_datos_contacto_service \
                .crear_bd_contactos(archivo, archivo_nombre, nombre_base_contactos)

            return redirect(self.get_success_url(id))

        except OmlError as e:
            message = e.__str__()

        messages.add_message(
            self.request,
            messages.ERROR,
            message,
        )
        return self.form_invalid(form)

    def get_success_url(self, id):
        return reverse(
            'define_base_datos_contacto',
            kwargs={"pk": id})


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

    def dispatch(self, request, *args, **kwargs):
        self.campana = None
        if 'pk_bd_contacto' in kwargs:
            self.bd_contacto = BaseDatosContacto.objects.get(pk=kwargs['pk_bd_contacto'])
        else:
            id_campana = kwargs['pk_campana']
            self.campana = Campana.objects.get(id=id_campana)
            self.bd_contacto = self.campana.bd_contacto

        return super(BaseDatosContactoUpdateView, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.bd_contacto

    def form_valid(self, form):

        self.object = form.save(commit=False)
        self.object.estado = BaseDatosContacto.ESTADO_DEFINIDA_ACTUALIZADA
        # self.object.nombre_archivo_importacion = nombre_archivo_importacion

        try:
            creacion_base_datos = CreacionBaseDatosService()
            creacion_base_datos.genera_base_dato_contacto(self.object)
        except OmlArchivoImportacionInvalidoError:
            message = _('<strong>Operación Errónea!</strong> ') + \
                _('El archivo especificado para realizar la importación de contactos '
                  'no es válido.')

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return self.form_invalid(form)

        return redirect(self.get_success_url())

    def get_success_url(self):
        if self.campana is None:
            return reverse('actualiza_base_datos_contacto',
                           kwargs={"pk": self.object.pk})
        else:
            return reverse('actualiza_base_datos_contacto_de_campana',
                           kwargs={"pk_campana": self.campana.id})


class DefineBaseDatosContactoView(UpdateView):
    """
    Esta vista se obtiene un resumen de la estructura
    del archivo a importar y la presenta al usuario para
    que seleccione en que columnas se encuentran los teléfonos.
    Guarda las posiciónes de la columnas como enteros y llama a
    importar los teléfono del archivo que se guardo.
    Si la importación resulta bien, llama a definir el objeto
    BaseDatosContacto para que esté disponible.
    """

    template_name = 'base_datos_contacto/define_base_datos_contacto.html'
    model = BaseDatosContacto
    context_object_name = 'base_datos_contacto'
    fields = '__all__'
    base_datos_contacto_service = BaseDatosContactoService()
    # @@@@@@@@@@@@@@@@@@@@

    def get_object(self, *args, **kwargs):
        return BaseDatosContacto.objects.obtener_en_actualizada_para_editar(
            self.kwargs['pk'])

    def obtiene_previsualizacion_archivo(self, base_datos_contacto):
        """
        Instancia el servicio ParserCsv e intenta obtener un resumen de las
        primeras 3 lineas del csv.
        """

        # TODO: OML-1012
        #       Estas validaciones deberían realizarse antes de crear la Base de datos
        #       Sino queda una instancia creada inutilizable
        try:
            estructura_archivo = self.base_datos_contacto_service \
                .obtiene_subconjunto_filas_archivo(base_datos_contacto)

        except OmlParserCsvDelimiterError:
            message = _('<strong>Operación Errónea!</strong> ') +\
                _('No se pudo determinar el delimitador a ser utilizado '
                  'en el archivo csv. No se pudo llevar a cabo el procesamiento '
                  'de sus datos.')

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
        except OmlParserMinRowError:
            message = _('<strong>Operación Errónea!</strong> ') +\
                _('El archivo que seleccionó posee menos de 3 filas. '
                  'No se pudo llevar a cabo el procesamiento de sus datos.')

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
        except OmlParserOpenFileError:
            message = _('<strong>Operación Errónea!</strong> ') +\
                _('El archivo que seleccionó no pudo ser abierto para su procesamiento.')

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
        except OmlParserRepeatedColumnsError as e:
            message = _('<strong>Operación Errónea!</strong> ') + e
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
            try:
                error_predictor = False
                error_predictor_encabezado = False
                metadata = self.base_datos_contacto_service.inferir_metadata(estructura_archivo)

            except NoSePuedeInferirMetadataError:
                initial_predecido_datos_extras = {}
                initial_predecido_encabezado = {}
                error_predictor = True
            except NoSePuedeInferirMetadataErrorEncabezado:
                initial_predecido_datos_extras = {}
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
            form_campos_telefonicos = CamposDeBaseDeDatosForm(nombres_campos=estructura_archivo[0])

            return self.render_to_response(self.get_context_data(
                error_predictor_encabezado=error_predictor_encabezado,
                error_predictor=error_predictor,
                estructura_archivo=estructura_archivo,
                form_primer_linea_encabezado=form_primer_linea_encabezado,
                form_campos_telefonicos=form_campos_telefonicos
            ))

        return redirect(reverse('nueva_base_datos_contacto'))

    def form_invalid(self, estructura_archivo,
                     form_primer_linea_encabezado,
                     form_campos_telefonicos):

        message = _('<strong>Operación Errónea!</strong> ') +\
            _('No se pudo efectuar la carga.')

        messages.add_message(
            self.request,
            messages.ERROR,
            message,
        )

        return self.render_to_response(self.get_context_data(
            estructura_archivo=estructura_archivo,
            form_primer_linea_encabezado=form_primer_linea_encabezado,
            form_campos_telefonicos=form_campos_telefonicos))

    def form_valid(self, estructura_archivo,
                   form_primer_linea_encabezado,
                   form_campos_telefonicos):
        # columna_con_telefono = int(form_columna_telefono.cleaned_data.get(
        #                            'telefono', None))
        # cantidad_columnas = len(form_nombre_columnas.fields)
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

        # error = None
        # lista_columnas_encabezado = estructura_archivo[0]
        # if lista_columnas_encabezado[0] != 'telefono':
        #     error = _("El nombre de la primera columna debe ser telefono")
        # if error:
        #     return self.form_invalid(estructura_archivo,
        #                             form_primer_linea_encabezado,
        #                             form_campos_telefonicos, error=error)
        # Detecto el encondig de la base de datoss recientemente subida
        metadata = self.object.get_metadata()
        metadata.cantidad_de_columnas = cantidad_columnas

        # predictor_metadata = PredictorMetadataService()
        # columnas_con_telefonos = predictor_metadata.inferir_columnas_telefono(
        #     estructura_archivo[1:], encoding)
        campos_telefonicos = form_campos_telefonicos.cleaned_data.get('campos_telefonicos')
        columnas_con_telefono = form_campos_telefonicos.columnas_de_telefonos
        metadata.columnas_con_telefono = columnas_con_telefono
        columna_id_externo = form_campos_telefonicos.columna_id_externo
        if columna_id_externo is not None:
            metadata.columna_id_externo = columna_id_externo

        metadata.nombres_de_columnas = estructura_archivo[0]
        es_encabezado = False
        if self.request.POST.get('es_encabezado', False):
            es_encabezado = True
        metadata.primer_fila_es_encabezado = es_encabezado
        metadata.save()

        try:
            self.base_datos_contacto_service.importa_contactos(self.object,
                                                               campos_telefonicos,
                                                               columna_id_externo)
        except CreacionBaseDatosServiceIdExternoError as e:
            message = _('<strong>Operación Errónea!</strong> ') +\
                _('El archivo que seleccionó posee contactos con identificadores externos '
                  'repetidos.<br> '
                  '<u>Línea Inválida:</u> {0}<br> <u>Contenido Línea:</u>'
                  ' {1}<br><u>ID repetido:</u> {2}').format(
                e.numero_fila, e.fila, e.valor_celda)

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return self.render_to_response(self.get_context_data(
                estructura_archivo=estructura_archivo,
                form_primer_linea_encabezado=form_primer_linea_encabezado))

        except OmlParserCsvImportacionError as e:

            message = _('<strong>Operación Errónea!</strong> ') +\
                _('El archivo que seleccionó posee registros inválidos.<br> '
                  '<u>Línea Inválida:</u> {0}<br> <u>Contenido Línea:</u>'
                  '{1}<br><u>Contenido Inválido:</u> {2}').format(
                e.numero_fila, e.fila, e.valor_celda)

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            # FIXME: Ver bien que hacer acá.

        except ContactoExistenteError as e:

            message = _('<strong>Operación Errónea!</strong> ') +\
                _('El archivo que seleccionó posee registros inválidos.<br> '
                  'ERROR: {0}. Vuelva a cargar nuevamente la base de datos '
                  'sin el contacto existente ').format(e)

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )

            return self.render_to_response(self.get_context_data(
                estructura_archivo=estructura_archivo,
                form_primer_linea_encabezado=form_primer_linea_encabezado,
                form_campos_telefonicos=form_campos_telefonicos))

        except OmlParserMaxRowError:
            message = _('<strong>Operación Errónea!</strong> ') +\
                _('El archivo que seleccionó posee más registros de los '
                  'permitidos para ser importados.')

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return redirect(reverse('lista_base_datos_contacto'))
        else:
            message = _('<strong>Operación Exitosa!</strong> ') +\
                _('Se llevó a cabo con éxito la creación de '
                  'la Base de Datos de Contactos.')

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
            form_primer_linea_encabezado = PrimerLineaEncabezadoForm(request.POST)
            form_campos_telefonicos = CamposDeBaseDeDatosForm(data=request.POST,
                                                              nombres_campos=estructura_archivo[0])

            if form_campos_telefonicos.is_valid() and form_primer_linea_encabezado.is_valid():
                return self.form_valid(estructura_archivo,
                                       form_primer_linea_encabezado,
                                       form_campos_telefonicos)
            else:
                return self.form_invalid(estructura_archivo,
                                         form_primer_linea_encabezado,
                                         form_campos_telefonicos)

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
            message = _('<strong>¡Cuidado!</strong> ') +\
                _('La Base Datos Contacto que intenta depurar esta siendo utilizada '
                  'por alguna campaña. No se llevará a cabo la depuración la misma '
                  'mientras esté siendo utilizada.')
            messages.add_message(
                self.request,
                messages.WARNING,
                message,
            )
            return HttpResponseRedirect(success_url)

        try:
            self.object.procesa_depuracion()
        except OmlDepuraBaseDatoContactoError:
            message = _('<strong>¡Operación Errónea!</strong> ') +\
                _('La Base Datos Contacto no se pudo depurar.')
            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return HttpResponseRedirect(success_url)
        else:
            message = _('<strong>Operación Exitosa!</strong> ') +\
                _('Se llevó a cabo con éxito la depuración de la Base de Datos.')

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
        self.campana = None
        if 'pk' in kwargs:
            self.base_datos_contacto = \
                BaseDatosContacto.objects.obtener_en_actualizada_para_editar(
                    self.kwargs['pk'])
        else:
            id_campana = kwargs['pk_campana']
            self.campana = Campana.objects.get(id=id_campana)
            self.base_datos_contacto = self.campana.bd_contacto
            self.id_ultimo_contacto = self.base_datos_contacto.contactos.order_by('id').last().id

        return super(ActualizaBaseDatosContactoView, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.base_datos_contacto

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
            message = _('<strong>Operación Errónea!</strong> ') +\
                _('No se pudo determinar el delimitador a ser utilizado '
                  'en el archivo csv. No se pudo llevar a cabo el procesamiento '
                  'de sus datos.')

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
        except OmlParserMinRowError:
            message = _('<strong>Operación Errónea!</strong> ') +\
                _('El archivo que seleccionó posee menos de 3 filas. '
                  'No se pudo llevar a cabo el procesamiento de sus datos.')

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
        except OmlParserOpenFileError:
            message = _('<strong>Operación Errónea!</strong> ') +\
                _('El archivo que seleccionó no pudo ser abierto para su procesamiento.')

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
        except Exception as e:
            message = _('Error al procesar el archivo de base de contactos: {0}'.format(e))
            logger.error(message)
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
            try:
                error_predictor = False
                error_predictor_encabezado = False

                predictor_metadata = PredictorMetadataService()
                metadata = predictor_metadata.\
                    inferir_metadata_desde_lineas_base_existente(
                        self.object, estructura_archivo)
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

        return redirect(
            reverse('update_base_datos_contacto_de_campana', kwargs={'pk_campana': '9'}))

    def form_invalid(self, estructura_archivo,
                     form_primer_linea_encabezado, error=None):

        message = _('<strong>Operación Errónea!</strong> ') +\
            _('Verifique el archivo cargado. {0}').format(error)

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

        for columna_base, columna_csv in zip(metadata.nombres_de_columnas,
                                             lista_columnas_encabezado):
            if str(columna_base).capitalize() != str(columna_csv).capitalize():
                error = _("El nombre de la columna debe ser {0} en vez de {1}".
                          format(columna_base, columna_csv))

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
            # creacion_base_datos.valida_contactos(self.object)
            bd_metadata = self.object.get_metadata()
            columnas_con_telefono = bd_metadata.nombres_de_columnas_de_telefonos
            columna_id_externo = bd_metadata.columna_id_externo

            creacion_base_datos.importa_contactos(self.object,
                                                  columnas_con_telefono,
                                                  columna_id_externo)
        except CreacionBaseDatosServiceIdExternoError as e:
            message = _('<strong>Operación Errónea!</strong> ') +\
                _('El archivo que seleccionó posee contactos con identificadores externos '
                  'repetidos.<br> '
                  '<u>Línea Inválida:</u> {0}<br> <u>Contenido Línea:</u>'
                  ' {1}<br><u>ID repetido:</u> {2}').format(
                e.numero_fila, e.fila, e.valor_celda)

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return self.render_to_response(self.get_context_data(
                estructura_archivo=estructura_archivo,
                form_primer_linea_encabezado=form_primer_linea_encabezado))

        except OmlParserCsvImportacionError as e:

            message = _('<strong>Operación Errónea!</strong> ') +\
                _('El archivo que seleccionó posee registros inválidos.<br> '
                  '<u>Línea Inválida:</u> {0}<br> <u>Contenido Línea:</u>'
                  '{1}<br><u>Contenido Inválido:</u> {2}').format(
                e.numero_fila, e.fila, e.valor_celda)

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return self.render_to_response(self.get_context_data(
                estructura_archivo=estructura_archivo,
                form_primer_linea_encabezado=form_primer_linea_encabezado))

        except ContactoExistenteError as e:

            message = _('<strong>¡Operación Errónea!</strong> ') +\
                _('El archivo que seleccionó posee registros inválidos.<br> '
                  'ERROR: {0}. Vuelva a cargar nuevamente la base de datos '
                  'sin el contacto existente ').format(e)

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )

            return self.render_to_response(self.get_context_data(
                estructura_archivo=estructura_archivo,
                form_primer_linea_encabezado=form_primer_linea_encabezado))

        except OmlParserMaxRowError:
            message = _('<strong>Operación Errónea!</strong> ') +\
                _('El archivo que seleccionó posee más registros de los '
                  'permitidos para ser importados.')

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return redirect(reverse('lista_base_datos_contacto'))
        else:
            message = _('<strong>Operación Exitosa!</strong> ') +\
                _('Se llevó a cabo con éxito la creación de la Base de Datos de Contactos.')

            messages.add_message(
                self.request,
                messages.SUCCESS,
                message,
            )

            # En caso de que sea agregar a una campaña preview, genero los AgenteEnContacto
            # para los contactos nuevos.
            if self.campana is not None and self.campana.type == Campana.TYPE_PREVIEW:
                self._generar_relaciones_agente_en_contacto()

            return redirect(self.get_success_url())

    def _generar_relaciones_agente_en_contacto(self):
        contactos = self.campana.bd_contacto.contactos.filter(id__gt=self.id_ultimo_contacto)
        agente_en_contacto_list = []
        campos_contacto = self.campana.bd_contacto.get_metadata().nombres_de_columnas_de_datos
        orden = AgenteEnContacto.ultimo_id() + 1
        for contacto in contactos:
            agente_en_contacto = self.campana._crear_agente_en_contacto(
                contacto, -1, campos_contacto, AgenteEnContacto.ESTADO_INICIAL, orden=orden)
            agente_en_contacto_list.append(agente_en_contacto)
            orden += 1
        # insertamos las instancias en la BD
        AgenteEnContacto.objects.bulk_create(agente_en_contacto_list)

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
        if self.campana is None:
            return reverse('lista_base_datos_contacto')
        else:
            url_por_tipo = {
                Campana.TYPE_ENTRANTE: 'campana_list',
                Campana.TYPE_MANUAL: 'campana_manual_list',
                Campana.TYPE_DIALER: 'campana_dialer_list',
                Campana.TYPE_PREVIEW: 'campana_preview_list',
            }
            return reverse(url_por_tipo[self.campana.type])


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
