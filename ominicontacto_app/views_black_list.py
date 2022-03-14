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

"""Vista Blacklist para crear una nueva Blacklist o llamada listas negras de telefonos"""

from __future__ import unicode_literals

from django.utils.translation import ugettext as _
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect
from django.views.generic.edit import (
    CreateView, UpdateView, DeleteView
)
from django.views.generic.list import ListView
from ominicontacto_app.errors import (
    OmlParserCsvDelimiterError, OmlParserMinRowError, OmlParserOpenFileError,
    OmlArchivoImportacionInvalidoError)
from ominicontacto_app.forms import BlacklistForm, ContactoBlacklistForm
from ominicontacto_app.models import Blacklist, ContactoBlacklist
from ominicontacto_app.parser import ParserCsv
from ominicontacto_app.services.black_list import (
    CreacionBlacklistService, ValidaDataService, NoSePuedeInferirMetadataError,
    NoSePuedeInferirMetadataErrorEncabezado, NoSePuedeInferirMetadataErrorFormatoFilas)
from ominicontacto_app.services.asterisk.redis_database import BlacklistFamily

import logging as logging_


logger = logging_.getLogger(__name__)


class BlacklistView(ListView):
    """
    Vista de las blacklist
    """
    template_name = 'black_list/black_list.html'
    context_object_name = 'black_lists'
    model = Blacklist

    def get_queryset(self):
        return Blacklist.objects.all().order_by('-fecha_alta')


class BlacklistCreateView(CreateView):
    """
    Esta vista crea una instancia de Blacklist
    sin definir, lo que implica que no esta disponible
    hasta que se procese su definición.
    """

    template_name = 'black_list/nueva_edita_black_list.html'
    model = Blacklist
    context_object_name = 'blacklist'
    form_class = BlacklistForm
    blacklist_service = CreacionBlacklistService()

    def obtiene_previsualizacion_archivo(self, black_list):
        """
        Instancia el servicio ParserCsv e intenta obtener un resumen de las
        primeras 3 lineas del csv.
        """

        try:
            parser = ParserCsv()
            estructura_archivo = parser.previsualiza_archivo(
                black_list)

        except OmlParserCsvDelimiterError:
            message = _('<strong>Operación Errónea!</strong> '
                        'No se pudo determinar el delimitador a ser utilizado '
                        'en el archivo csv. No se pudo llevar a cabo el procesamiento '
                        'de sus datos.')

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
        except OmlParserMinRowError:
            message = _('<strong>Operación Errónea!</strong> '
                        'El archivo que seleccionó posee menos de 3 filas. '
                        'No se pudo llevar a cabo el procesamiento de sus datos.')

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
        except OmlParserOpenFileError:
            message = _('<strong>Operación Errónea!</strong> '
                        'El archivo que seleccionó no pudo ser abierto para su procesamiento.')

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
        else:
            return estructura_archivo

    def _eliminar_blacklist_anterior(self):
        blacklist_antiguos = Blacklist.objects.all()
        blacklist_antiguos.delete()

    def form_valid(self, form):
        nombre_archivo_importacion = \
            self.request.FILES['archivo_importacion'].name
        self.object = form.save(commit=False)
        self.object.nombre_archivo_importacion = nombre_archivo_importacion
        try:
            self.blacklist_service.genera_black_list(self.object)
        except OmlArchivoImportacionInvalidoError:
            message = _('<strong>Operación Errónea!</strong> ') +\
                _('El archivo especificado para realizar la importación de contactos '
                  'no es válido.')

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
        except NoSePuedeInferirMetadataErrorFormatoFilas:
            message = '<strong>Operación Errónea!</strong> \
                        Las filas del archivo no tienen el formato adecuado'

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return self.form_invalid(form)
        except NoSePuedeInferirMetadataError:
            message = '<strong>Operación Errónea!</strong> \
                        No se pueden interferir los datos de la blacklist y \
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

        self._eliminar_blacklist_anterior()
        self.object.save()
        self.blacklist_service.importa_contactos(self.object)
        blacklist_family = BlacklistFamily()
        blacklist_family.regenerar_families(self.object)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            'black_list_list')


class BlacklistUpdateView(UpdateView):
    template_name = 'black_list/nueva_edita_black_list.html'
    model = Blacklist
    form_class = BlacklistForm
    context_object_name = 'black_list'
    blacklist_service = CreacionBlacklistService()
    validata_data_service = ValidaDataService()

    def obtiene_previsualizacion_archivo(self, black_list):
        """
        Instancia el servicio ParserCsv e intenta obtener un resumen de las
        primeras 3 lineas del csv.
        """

        try:
            parser = ParserCsv()
            estructura_archivo = parser.previsualiza_archivo(
                black_list)

        except OmlParserCsvDelimiterError:
            message = _('<strong>Operación Errónea!</strong> '
                        'No se pudo determinar el delimitador a ser utilizado '
                        'en el archivo csv. No se pudo llevar a cabo el procesamiento '
                        'de sus datos.')

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
        except OmlParserMinRowError:
            message = _('<strong>Operación Errónea!</strong> '
                        'El archivo que seleccionó posee menos de 3 filas. '
                        'No se pudo llevar a cabo el procesamiento de sus datos.')

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
        except OmlParserOpenFileError:
            message = _('<strong>Operación Errónea!</strong> '
                        'El archivo que seleccionó no pudo ser abierto para su procesamiento.')

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
        else:
            return estructura_archivo

    def get_object(self, queryset=None):
        return Blacklist.objects.get(pk=self.kwargs.get("pk_blacklist"))

    def form_valid(self, form):
        nombre_archivo_importacion = \
            self.request.FILES['archivo_importacion'].name
        self.object = form.save(commit=False)
        self.object.nombre_archivo_importacion = nombre_archivo_importacion

        try:
            self.blacklist_service.genera_black_list(self.object)
        except OmlArchivoImportacionInvalidoError:
            message = _('<strong>Operación Errónea!</strong> ') +\
                _('El archivo especificado para realizar la importación de contactos '
                  'no es válido.')
            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return self.form_invalid(form)
        estructura_archivo = self.obtiene_previsualizacion_archivo(self.object)
        try:
            self.validata_data_service.valida_datos_desde_lineas(estructura_archivo)
        except NoSePuedeInferirMetadataErrorFormatoFilas:
            message = '<strong>Operación Errónea!</strong> \
                        Las filas del archivo no tienen el formato adecuado'

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return self.form_invalid(form)
        except NoSePuedeInferirMetadataError:
            message = '<strong>Operación Errónea!</strong> \
                        No se pueden interferir los datos de la blacklist y \
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
        contactos_repetidos = self.blacklist_service.importa_contactos(self.object)
        blacklist_family = BlacklistFamily()
        blacklist_family.regenerar_families(self.object)

        if not contactos_repetidos:
            message = '<strong>Operación Exitosa:<strong> \
                      Se llevó a cabo con éxito la importacion de todos los contactos.'
            messages.add_message(
                self.request,
                messages.SUCCESS,
                message,
            )
        else:
            message = '<strong>¡Contactos repetidos!</strong> \
                      El archivo contenia contactos que ya estaban en la blacklist por lo tanto \
                      no fueron agregados.'
            messages.add_message(
                self.request,
                messages.WARNING,
                message,
            )
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('black_list_list')


class BlacklistDeleteView(DeleteView):
    model = Blacklist
    template_name = 'black_list/delete_black_list.html'
    context_object_name = 'black_list'

    def get_object(self, queryset=None):
        return Blacklist.objects.get(pk=self.kwargs.get("pk_blacklist"))

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        blacklist_family = BlacklistFamily()
        blacklist_family.delete_family()
        message = _("<strong>Operación Exitosa:</strong> \
                    Se llevó a cabo con éxito la eliminación de la blacklist.")

        messages.add_message(
            self.request,
            messages.SUCCESS,
            message,
        )
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('black_list_list')


class BlacklistNuevoContactoView(CreateView):
    """
        Vista para crear un contacto de una blacklist
    """
    model = ContactoBlacklist
    form_class = ContactoBlacklistForm
    template_name = 'black_list/contactos/new.html'

    def get_context_data(self, **kwargs):
        context = super(
            BlacklistNuevoContactoView,
            self
        ).get_context_data(**kwargs)
        context['blacklist'] = Blacklist.objects.get(
            pk=self.kwargs['pk_blacklist']
        )
        return context

    def existe_contacto(self, blacklist, telefono):
        existencias = blacklist.contactosblacklist.filter(
            telefono=telefono).count()
        return True if existencias > 0 else False

    def form_valid(self, form):
        blacklist = Blacklist.objects.get(pk=self.kwargs['pk_blacklist'])
        self.object = form.save(commit=False)
        self.object.black_list = blacklist
        self.object.save()
        blacklist.cantidad_contactos += 1
        blacklist.save()
        blacklist_family = BlacklistFamily()
        blacklist_family.regenerar_families(blacklist)
        message = _("<strong>Operación Exitosa:</strong> "
                    "Se llevó a cabo con éxito la creación del contacto.")
        messages.add_message(
            self.request,
            messages.SUCCESS,
            message,
        )
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('black_list_list')
