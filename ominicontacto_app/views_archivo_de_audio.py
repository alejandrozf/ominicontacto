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

from __future__ import unicode_literals

import os

from django.contrib import messages
from django.urls import reverse
from django.forms import ValidationError
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.utils.translation import gettext_lazy as _
from api_app.services.storage_service import StorageService
from ominicontacto_app.services.audio_conversor import ConversorDeAudioService
from ominicontacto_app.errors import OmlAudioConversionError
from ominicontacto_app.forms.audio import ArchivoDeAudioForm
from ominicontacto_app.models import ArchivoDeAudio
from ominicontacto_app.asterisk_config import AudioConfigFile
from ominicontacto_app.services.tts.generador import GeneradorTTS
import logging as logging_


logger = logging_.getLogger(__name__)


def convertir_archivo_audio(audio):
    """
        Convierte un archivo usando el conversor especificado, actualiza sus rutas
        - audio: Puede ser ArchivoDeAudio o MusicaDeEspera
    """
    conversor_audio = ConversorDeAudioService()
    conversor_audio.convertir_audio_de_archivo_de_audio_globales(audio)
    copiar_archivo_en_asterisk(audio)
    copiar_archivo_en_storage(audio)


def copiar_archivo_en_asterisk(audio):
    if audio.audio_asterisk.name:
        audio_file_asterisk = AudioConfigFile(audio)
        audio_file_asterisk.copy_asterisk()


def copiar_archivo_en_storage(audio):
    if audio.audio_asterisk.name:
        if os.getenv('S3_STORAGE_ENABLED'):
            s3_handler = StorageService()
            s3_handler.upload_file(audio.audio_asterisk.name,
                                   audio.audio_asterisk.path,
                                   'media_root')


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
        cleaned_data = form.cleaned_data
        if cleaned_data.get('usar_tts'):
            servicio = cleaned_data.get('tts_service')
            voz = form.get_tts_voice(servicio, cleaned_data.get('tts_voice'))
            generador = GeneradorTTS()
            try:
                filename = generador.generar_archivo(
                    servicio=servicio,
                    descripcion=cleaned_data.get('descripcion'),
                    texto=cleaned_data.get('tts_text'),
                    voz=voz,
                )
            except Exception as e:
                logger.error('TTS Service Error: {0}'.format(e))
                form.add_error(field=None, error=ValidationError(_('Error creando archivo TTS')))
                return super(ArchivoAudioCreateView, self).form_invalid(form)
            form.save(commit=False)
            form.instance.audio_original = filename
        else:
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

        if self.object.audio_original:
            if os.getenv('S3_STORAGE_ENABLED'):
                s3_handler = StorageService()
                audio_url = s3_handler \
                    .get_file_url(f'/media_root/{self.object.audio_asterisk.name}')

            else:
                audio_url = "%s://%s%s" % (self.request.scheme,
                                           self.request.get_host(),
                                           self.object.audio_original.url)

            context['audio_url'] = audio_url
        return context

    template_name = 'archivo_audio/nuevo_edita_archivo_audio.html'
    model = ArchivoDeAudio
    form_class = ArchivoDeAudioForm

    def form_valid(self, form):
        form.save()
        cleaned_data = form.cleaned_data
        # Si se modificó el audio original... Ver si debo llamar al servicio de TTS
        if 'audio_original' in form.changed_data:
            self._procesar_archivo_de_audio(form)
        elif cleaned_data.get('usar_tts'):
            servicio = cleaned_data.get('tts_service')
            voz = form.get_tts_voice(servicio, cleaned_data.get('tts_voice'))
            generador = GeneradorTTS()
            try:
                filename = generador.generar_archivo(
                    servicio=servicio,
                    descripcion=cleaned_data.get('descripcion'),
                    texto=cleaned_data.get('tts_text'),
                    voz=voz,
                )
            except Exception as e:
                logger.error('TTS Service Error: {0}'.format(e))
                form.add_error(field=None, error=ValidationError(_('Error creando archivo TTS')))
                return super(ArchivoAudioUpdateView, self).form_invalid(form)
            form.instance.audio_original = filename
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
        audio_file_asterisk = AudioConfigFile(self.object)
        audio_file_asterisk.delete_asterisk()
        if os.getenv('S3_STORAGE_ENABLED'):
            s3_handler = StorageService()
            s3_handler.delete_file(self.object.audio_asterisk.name, 'media_root')
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
