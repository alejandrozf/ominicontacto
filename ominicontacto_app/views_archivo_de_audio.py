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

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from ominicontacto_app.services.audio_conversor import ConversorDeAudioService
from ominicontacto_app.errors import OmlAudioConversionError
from ominicontacto_app.forms import ArchivoDeAudioForm
from ominicontacto_app.models import ArchivoDeAudio
from ominicontacto_app.asterisk_config import AudioConfigFile
import logging as logging_


logger = logging_.getLogger(__name__)


def convertir_archivo_audio(archivo_de_audio):
    """Convierte un archivo usando el conversor especificado, actualiza sus rutas"""
    conversor_audio = ConversorDeAudioService()
    conversor_audio.convertir_audio_de_archivo_de_audio_globales(archivo_de_audio)
    audio_asterisk = archivo_de_audio.audio_asterisk.name
    if audio_asterisk:
        audio_file_asterisk = AudioConfigFile(audio_asterisk)
        audio_file_asterisk.copy_asterisk()


class ArchivoAudioListView(ListView):
    """
    Esta vista lista los archivos de audios.
    """

    template_name = 'archivo_audio/lista_archivo_audio.html'
    context_object_name = 'audios'
    model = ArchivoDeAudio
    queryset = ArchivoDeAudio.objects.all()


class ArchivoDeAudioMixin(object):

    def _procesar_archivo_de_audio(self, form):
        try:
            convertir_archivo_audio(form.instance)
        except OmlAudioConversionError:
            form.instance.audio_original = None
            form.instance.save()

            message = '<strong>Operación Errónea!</strong> \
            Hubo un inconveniente en la conversión del audio. Por favor \
            verifique que el archivo subido sea el indicado.'
            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return self.form_invalid(form)
        except Exception as e:
            form.instance.audio_original = None
            form.instance.save()

            logger.warn("convertir_audio_de_archivo_de_audio_globales(): "
                        "produjo un error inesperado. Detalle: %s", e)

            message = '<strong>Operación Errónea!</strong> \
            Se produjo un error inesperado en la conversión del audio.'
            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return self.form_invalid(form)


class ArchivoAudioCreateView(ArchivoDeAudioMixin, CreateView):
    """
    Esta vista crea un objeto ArchivoDeAudio.
    """

    template_name = 'archivo_audio/nuevo_edita_archivo_audio.html'
    model = ArchivoDeAudio
    form_class = ArchivoDeAudioForm

    def form_valid(self, form):
        form.save()
        self._procesar_archivo_de_audio(form)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('lista_archivo_audio')


class ArchivoAudioUpdateView(ArchivoDeAudioMixin, UpdateView):
    """
    Esta vista edita un objeto ArchivoDeAudio.
    """

    template_name = 'archivo_audio/nuevo_edita_archivo_audio.html'
    model = ArchivoDeAudio
    form_class = ArchivoDeAudioForm

    def form_valid(self, form):
        form.save()
        if 'audio_original' in form.changed_data:
            self._procesar_archivo_de_audio(form)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('lista_archivo_audio')


class ArchivoAudioDeleteView(DeleteView):
    """
    Esta vista se encarga de la eliminación del
    objeto ArchivoDeAudio seleccionado.
    """

    model = ArchivoDeAudio
    template_name = 'archivo_audio/elimina_archivo_audio.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.borrar()

        message = '<strong>Operación Exitosa!</strong>\
        Se llevó a cabo con éxito la eliminación del Archivo de Audio.'

        messages.add_message(
            self.request,
            messages.SUCCESS,
            message,
        )
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('lista_archivo_audio')
