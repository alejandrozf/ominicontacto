# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
#from fts_daemon.audio_conversor import ConversorDeAudioService
from ominicontacto_app.errors import OmlAudioConversionError
#from fts_web.forms import ArchivoAudioForm
from ominicontacto_app.models import ArchivoDeAudio
import logging as logging_


logger = logging_.getLogger(__name__)


class ArchivoAudioListView(ListView):
    """
    Esta vista lista los archivos de audios.
    """

    template_name = 'archivo_audio/lista_archivo_audio.html'
    context_object_name = 'audios'
    model = ArchivoDeAudio
    queryset = ArchivoDeAudio.objects.all()



