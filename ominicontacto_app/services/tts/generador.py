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

""" Wrapper local para servicio de tts """

import os

# # TTS Libs # #
from gtts import gTTS
from espeakng import ESpeakNG
from tts_wrapper import PicoClient, PicoTTS

# # mp3 to wav conversion # #
from pydub import AudioSegment

from django.core.files.storage import default_storage

from ominicontacto_app.models import upload_to_audio_original


def mp3_to_wav(mp3_filename, wav_filename):
    sound = AudioSegment.from_mp3(mp3_filename)
    sound.export(wav_filename, format="wav")


GTTS_ID = 'gtts'
ESPEAK_ID = 'espeak'
PICOTTS_ID = 'picotts'
GTTS_VOICES = {
    'en': {
        'us': 'English (United States)',
        'co.uk': 'English (United Kingdom)',
    },
    'es': {
        'com.mx': 'Spanish (Mexico)',
        'es': 'Spanish (Spain)',
        'us': 'Spanish (United States)',
    },
    'pt': {
        'pt': 'Portuguese (Portugal)',
        'com.br': 'Portuguese (Brazil)',
    },
}
ESPEAK_VOICES = {
    'en-us': 'English_(America)',
    'en-gb': 'English_(Great_Britain)',
    'es-419': 'Spanish_(Latin_America)',
    'es': 'Spanish_(Spain)',
    'pt-br': 'Portuguese_(Brazil)',
    'pt': 'Portuguese_(Portugal)',
}
PICOTTS_VOICES = {
    'en-US': 'English_(America)',
    'en-GB': 'English_(Great_Britain)',
    'es-ES': 'Spanish',
}


class GeneradorTTS(object):
    def generar_archivo(self, servicio, descripcion, texto, voz):
        """ Genera un archivo .wav para ArchivoDeAudio usando servicios de TTS """

        descripcion = descripcion
        # Calculo filename y paths de audio original a partir de descripción
        filename = descripcion + '.wav'
        path_relativo = upload_to_audio_original(None, '') + filename
        abs_output_filename = default_storage.path(path_relativo)

        # Creación de directorio 'audios_reproducción
        directorio = os.path.dirname(abs_output_filename)
        if not os.path.exists(directorio):
            print("Se crearan directorios: {0}".format(directorio))
            os.makedirs(directorio, mode=0o755)

        if servicio == GTTS_ID:
            self._generar_con_gtts(text=texto, lang=voz[0], tld=voz[1],
                                   filename=abs_output_filename)
        if servicio == ESPEAK_ID:
            self._generar_con_espeak(text=texto, voice=voz, filename=abs_output_filename)
        if servicio == PICOTTS_ID:
            self._generar_con_pico_tts(text=texto, voice=voz, filename=abs_output_filename)

        return path_relativo

    def _generar_con_gtts(self, text, lang, tld, filename):
        tts = gTTS(text=text, lang=lang, tld=tld)
        mp3_filename = filename + '.mp3'
        tts.save(mp3_filename)
        mp3_to_wav(mp3_filename, filename)
        os.remove(mp3_filename)

    def _generar_con_espeak(self, text, voice, filename):
        esng = ESpeakNG()
        esng.voice = voice
        # Synthesize speech to WAV format
        wavs = esng.synth_wav(text)
        with open(filename, 'wb') as f:
            f.write(wavs)

    def _generar_con_pico_tts(self, text, voice, filename):
        # Initialize PicoTTS
        pt = PicoTTS(client=PicoClient(), voice=voice)
        # Synthesize speech to WAV format
        pt.synth_to_file(text=text, filename=filename)
