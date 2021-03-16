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
from django.urls import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.utils.translation import ugettext_lazy as _
from ominicontacto_app.services.audio_conversor import ConversorDeAudioService
from ominicontacto_app.errors import OmlAudioConversionError
from ominicontacto_app.forms import ArchivoDeAudioForm
from ominicontacto_app.models import ArchivoDeAudio
from ominicontacto_app.asterisk_config import AudioConfigFile
import logging as logging_


logger = logging_.getLogger(__name__)


def convertir_archivo_audio(audio):
    """
        Convierte un archivo usando el conversor especificado, actualiza sus rutas
        - audio: Puede ser ArchivoDeAudio o MusicaDeEspera
    """
    conversor_audio = ConversorDeAudioService()
    conversor_audio.convertir_audio_de_archivo_de_audio_globales(audio)
    if audio.audio_asterisk.name:
        audio_file_asterisk = AudioConfigFile(audio)
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
    """
    El model puede ser ArchivoDeAudio o MusicaDeEspera
    """

    def _procesar_archivo_de_audio(self, form):
        try:
            convertir_archivo_audio(form.instance)
        except OmlAudioConversionError:
            form.instance.audio_original = None
            form.instance.save()

            message = _('<strong>Operación Errónea!</strong> ') +\
                _('Hubo un inconveniente en la conversión del audio. Por favor '
                  'verifique que el archivo subido sea el indicado.')
            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return self.form_invalid(form)
        except Exception as e:
            form.instance.audio_original = None
            form.instance.save()

            logger.warn(_("convertir_audio_de_archivo_de_audio_globales(): "
                          "produjo un error inesperado. Detalle: {0}".format(e)))

            message = _('<strong>Operación Errónea!</strong> ') +\
                _('Se produjo un error inesperado en la conversión del audio.')
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

    def get_context_data(self, **kwargs):
        context = super(ArchivoAudioUpdateView, self).get_context_data(
            **kwargs)
        context['base_url'] = "%s://%s" % (self.request.scheme,
                                           self.request.get_host())
        return context

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

    def dispatch(self, request, *args, **kwargs):
        archivo = self.get_object()

        if archivo.usado_en_ivr():
            message = _("No está permitido eliminar un audio en uso por un IVR")
            messages.warning(self.request, message)
            return HttpResponseRedirect(
                reverse('lista_archivo_audio'))
        if archivo.usado_en_queue():
            message = _("No se puede borrar un Archivo de Audio en uso en Campañas")
            messages.warning(self.request, message)
            return HttpResponseRedirect(
                reverse('lista_archivo_audio'))
        return super(ArchivoAudioDeleteView, self).dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.borrar()
        message = _('<strong>Operación Exitosa!</strong> '
                    'Se llevó a cabo con éxito la eliminación del Archivo de Audio.')

        messages.add_message(
            self.request,
            messages.SUCCESS,
            message,
        )
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('lista_archivo_audio')
