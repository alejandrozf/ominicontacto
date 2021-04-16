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

"""Views para generar listas rapidas"""
from __future__ import unicode_literals

from django.utils.translation import ugettext as _
from django.urls import reverse
from django.views.generic.edit import (
    CreateView, UpdateView, DeleteView
)
from django.shortcuts import redirect
from ominicontacto_app.errors import (OmlArchivoImportacionInvalidoError, OmlError,
                                      OmlParserCsvImportacionError)
from django.contrib import messages
from django.views.generic.list import ListView


from ominicontacto_app.models import ListasRapidas
from ominicontacto_app.forms import (ListaRapidaForm, PrimerLineaEncabezadoForm,
                                     CamposListaRapidaForm)

from ominicontacto_app.services.lista_rapida import (ListaRapidaService, ValidaListaRapidaService,
                                                     NoSePuedeInferirMetadataError,
                                                     NoSePuedeInferirMetadataErrorEncabezado,
                                                     ContactoExistenteError)


class ListaRapidaListView(ListView):
    template_name = 'lista_rapida/listas_rapidas.html'
    model = ListasRapidas
    context_object_name = 'lista_rapida'

    def get_queryset(self):
        queryset = ListasRapidas.objects.all()
        return queryset


class ListaRapidaCreateView(CreateView):
    template_name = 'lista_rapida/nueva_edita_lista_rapida.html'
    model = ListasRapidas
    form_class = ListaRapidaForm
    context_object_name = 'lista_rapida'

    def form_valid(self, form):
        archivo = self.request.FILES['archivo_importacion']
        archivo_nombre = archivo.name
        nombre_base_contactos = form.cleaned_data['nombre']
        self.object = form.save(commit=False)

        lista_rapida_service = ListaRapidaService()

        valida_data = ValidaListaRapidaService()

        try:
            valida_data.valida_datos_desde_lineas(self.object)
            valida_data.valida_lista_rapida(archivo, archivo_nombre, nombre_base_contactos)
        except OmlError as e:
            message = e.__str__()
            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return self.form_invalid(form)

        try:
            id = lista_rapida_service \
                .crea_lista_rapida(archivo, archivo_nombre, nombre_base_contactos)

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
            'define_lista_rapida',
            kwargs={"pk": id})


class DefineListaRapidaView(UpdateView):
    template_name = 'lista_rapida/define_lista_rapida.html'
    model = ListasRapidas
    context_object_name = 'lista_rapida'
    fields = '__all__'
    valida_lista_rapida = ValidaListaRapidaService()
    lista_rapida_service = ListaRapidaService()

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        estructura_archivo = self.valida_lista_rapida._obtiene_previsualizacion_archivo(self.object)
        if estructura_archivo:
            try:
                error_predictor = False
                error_predictor_encabezado = False
                metadata = self.lista_rapida_service.inferir_metadata(estructura_archivo)

            except NoSePuedeInferirMetadataError:
                initial_predecido_encabezado = {}
                error_predictor = True
            except NoSePuedeInferirMetadataErrorEncabezado:
                initial_predecido_encabezado = {}
                error_predictor_encabezado = True
            else:
                initial_predecido_encabezado = {
                    'es_encabezado': metadata.primer_fila_es_encabezado}

            form_primer_linea_encabezado = PrimerLineaEncabezadoForm(
                initial=initial_predecido_encabezado)
            form_campos_telefonicos = CamposListaRapidaForm(nombres_campos=estructura_archivo[0])

            return self.render_to_response(self.get_context_data(
                error_predictor_encabezado=error_predictor_encabezado,
                error_predictor=error_predictor,
                estructura_archivo=estructura_archivo,
                form_primer_linea_encabezado=form_primer_linea_encabezado,
                form_campos_telefonicos=form_campos_telefonicos
            ))

        return redirect(reverse('nueva_base_datos_contacto'))

    def form_valid(self, estructura_archivo,
                   form_primer_linea_encabezado,
                   form_campos_telefonicos):
        cantidad_columnas = len(estructura_archivo[0])
        metadata = self.object.get_metadata()
        metadata.cantidad_de_columnas = cantidad_columnas
        columnas_con_telefono = form_campos_telefonicos.columnas_de_telefonos
        metadata.columnas_con_telefono = columnas_con_telefono
        metadata.nombres_de_columnas = estructura_archivo[0]
        es_encabezado = False
        if self.request.POST.get('es_encabezado', False):
            es_encabezado = True
        metadata.primer_fila_es_encabezado = es_encabezado
        metadata.save()

        try:
            self.lista_rapida_service.importa_contactos(self.object)

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

        except OmlError as e:

            message = _('<strong>Operación Errónea!</strong> ') +\
                _('El archivo que seleccionó posee registros inválidos.<br> '
                  'ERROR: {0}.').format(e)

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )

            return self.render_to_response(self.get_context_data(
                estructura_archivo=estructura_archivo,
                form_primer_linea_encabezado=form_primer_linea_encabezado,
                form_campos_telefonicos=form_campos_telefonicos))
        else:
            message = _('<strong>Operación Exitosa!</strong> ') +\
                _('Se llevó a cabo con éxito la creación de '
                  'la lista rapida.')

            messages.add_message(
                self.request,
                messages.SUCCESS,
                message,
            )
            return redirect(self.get_success_url())

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

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        estructura_archivo = self.valida_lista_rapida._obtiene_previsualizacion_archivo(self.object)
        if estructura_archivo:
            form_primer_linea_encabezado = PrimerLineaEncabezadoForm(request.POST)
            form_campos_telefonicos = CamposListaRapidaForm(data=request.POST,
                                                            nombres_campos=estructura_archivo[0])

            if form_campos_telefonicos.is_valid() and form_primer_linea_encabezado.is_valid():
                return self.form_valid(estructura_archivo, form_primer_linea_encabezado,
                                       form_campos_telefonicos)
            else:
                return self.form_invalid(estructura_archivo,
                                         form_primer_linea_encabezado,
                                         form_campos_telefonicos)

        return redirect(reverse('nueva_lista_rapida'))

    def get_success_url(self):
        return reverse('listas_rapidas')


class ListaRapidaUpdateView(UpdateView):
    template_name = 'lista_rapida/nueva_edita_lista_rapida.html'
    model = ListasRapidas
    form_class = ListaRapidaForm
    context_object_name = 'lista_rapida'

    def get_object(self, queryset=None):
        return ListasRapidas.objects.get(pk=self.kwargs.get("pk_lista_rapida"))

    def form_valid(self, form):
        self.object = form.save(commit=False)
        try:
            creacion_lista_rapida = ListaRapidaService()
            creacion_lista_rapida.genera_lista_rapida(self.object)
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
        self.object.save()

        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('define_lista_rapida',
                       kwargs={"pk": self.object.pk})


class ListaRapidaDeleteView(DeleteView):
    model = ListasRapidas
    template_name = 'lista_rapida/delete_lista_rapida.html'
    context_object_name = 'lista_rapida'

    def get_object(self, queryset=None):
        return ListasRapidas.objects.get(pk=self.kwargs.get("pk_lista_rapida"))

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        message = _("Operación Exitosa:\
                    se llevó a cabo con éxito la eliminación de la lista rápida.")

        messages.add_message(
            self.request,
            messages.SUCCESS,
            message,
        )
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('listas_rapidas')
