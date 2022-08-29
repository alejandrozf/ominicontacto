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
from django import forms
from django.forms.models import (modelformset_factory, BaseModelFormSet)
from django.utils.translation import gettext_lazy as _
from configuracion_telefonia_app.models import AmdConf, AudiosAsteriskConf, DestinoEntrante, \
    EsquemaGrabaciones, IdentificadorCliente, MusicaDeEspera, OpcionDestino, \
    Playlist, TroncalSIP
from utiles_globales import validar_extension_archivo_audio

EMPTY_CHOICE = ('', '---------')
TIPOS_DESTINOS_CHOICES = (EMPTY_CHOICE,) + DestinoEntrante.TIPOS_DESTINOS


class TroncalSIPForm(forms.ModelForm):

    class Meta:
        model = TroncalSIP
        exclude = ()
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'canales_maximos': forms.NumberInput(attrs={'class': 'form-control'}),
            'caller_id': forms.TextInput(attrs={'class': 'form-control'}),
            'register_string': forms.TextInput(attrs={'class': 'form-control'}),
            'text_config': forms.Textarea(attrs={'class': 'form-control'}),
            'tecnologia': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'nombre': _('Nombre Troncal'),
            'text_config': _('Parámetros SIP'),
            'register_string': _('Cadena de registración')
        }


class IdentificadorClienteForm(forms.ModelForm):
    class Meta:
        model = IdentificadorCliente
        exclude = ()

    def clean_url(self):
        url = self.cleaned_data.get('url')
        tipo_interaccion = self.cleaned_data.get('tipo_interaccion')
        if not tipo_interaccion == IdentificadorCliente.SIN_INTERACCION_EXTERNA:
            if not url:
                raise forms.ValidationError(_('Debe indicar una url.'))
            return url


class OpcionDestinoValidacionFechaHoraForm(forms.ModelForm):

    tipo_destino = forms.ChoiceField(
        label=_('Tipo de destino'), choices=TIPOS_DESTINOS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = OpcionDestino
        fields = ('valor', 'destino_siguiente',)
        labels = {
            'destino_siguiente': _('Destino'),
        }
        widgets = {
            'valor': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super(OpcionDestinoValidacionFechaHoraForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance.pk is not None:
            tipo_destino = instance.destino_siguiente.tipo
            self.initial['tipo_destino'] = tipo_destino
            destinos_qs = DestinoEntrante.get_destinos_por_tipo(tipo_destino)
            destino_entrante_choices = [EMPTY_CHOICE] + [(dest_entr.id, str(dest_entr))
                                                         for dest_entr in destinos_qs]
            self.fields['destino_siguiente'].choices = destino_entrante_choices


class OpcionDestinoValidacionFechaHoraFormSet(BaseModelFormSet):

    def clean(self):
        """
        Realiza los validaciones relacionadas con los destinos especificados
        para un nodo de ruta entrante de tipo validación fecha/hora
        """
        if any(self.errors):
            return

        deleted_forms = self.deleted_forms
        save_candidates_forms = set(self.forms) - set(deleted_forms)
        destinos = []
        for form in save_candidates_forms:
            destino = form.cleaned_data.get('destino_siguiente', None)
            if destino in destinos:
                raise forms.ValidationError(
                    _('Los destinos deben ser distintos'), code='invalid')
            destinos.append(destino)


class OpcionDestinoPersonalizadoForm(OpcionDestinoValidacionFechaHoraForm):

    FAILOVER = 'failover'

    def __init__(self, *args, **kwargs):
        super(OpcionDestinoPersonalizadoForm, self).__init__(*args, **kwargs)
        self.initial['valor'] = self.FAILOVER


class AudiosAsteriskForm(forms.Form):

    AUDIO_IDIOMA_CHOICES_DICT = {
        AudiosAsteriskConf.ES: _('Español'),
        AudiosAsteriskConf.EN: _('Inglés'),
        AudiosAsteriskConf.FR: _('Francés'),
        AudiosAsteriskConf.IT: _('Italiano'),
        AudiosAsteriskConf.JA: _('Japonés'),
        AudiosAsteriskConf.RU: _('Ruso'),
        AudiosAsteriskConf.SV: _('Sueco'),
    }

    idiomas_instalados = [EMPTY_CHOICE]

    audio_idioma = forms.ChoiceField(
        label=_('Escoger idioma del paquete de audios a instalar'),
        widget=forms.Select(
            attrs={'class': 'form-control escogerAudioIdioma'}))

    def __init__(self, *args, **kwargs):
        super(AudiosAsteriskForm, self).__init__(*args, **kwargs)
        self.initial = {
            'audio_idioma': ''
        }
        self.idiomas_instalados, self.idiomas_no_instalados = self._obtener_idiomas_instalados()

        self.fields['audio_idioma'].choices = [EMPTY_CHOICE] + self.idiomas_no_instalados

    def _obtener_idiomas_instalados(self):
        instalados_list = AudiosAsteriskConf \
            .objects \
            .all() \
            .filter(esta_instalado=True)

        idiomas_instalados = [(valor.paquete_idioma,
                               self.AUDIO_IDIOMA_CHOICES_DICT[valor.paquete_idioma])
                              for valor in instalados_list]
        idiomas_no_instalados = list(
            set(AudiosAsteriskConf.AUDIO_IDIOMA_CHOICES) - set(idiomas_instalados))
        idiomas_instalados_mostrar = [str(choice) for valor, choice in idiomas_instalados]
        return (idiomas_instalados_mostrar, idiomas_no_instalados)


class PlaylistForm(forms.ModelForm):

    class Meta:
        model = Playlist
        exclude = ()


class AmdConfForm(forms.ModelForm):

    class Meta:
        model = AmdConf
        exclude = ()
        widgets = {
            'initial_silence': forms.NumberInput(attrs={'class': 'form-control'}),
            'greeting': forms.NumberInput(attrs={'class': 'form-control'}),
            'after_greeting_silence': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_analysis_time': forms.NumberInput(attrs={'class': 'form-control'}),
            'min_word_length': forms.NumberInput(attrs={'class': 'form-control'}),
            'between_words_silence': forms.NumberInput(attrs={'class': 'form-control'}),
            'maximum_number_of_words': forms.NumberInput(attrs={'class': 'form-control'}),
            'maximum_word_length': forms.NumberInput(attrs={'class': 'form-control'}),
            'silence_threshold': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'initial_silence': _('Silencio inicial (ms)'),
            'greeting': _('Saludo (ms)'),
            'after_greeting_silence': _('Silencio post saludo (ms)'),
            'total_analysis_time': _('Tiempo de análisis (ms)'),
            'min_word_length': _('Duración mínima de cada palabra (ms)'),
            'between_words_silence': _('Silencio entre palabras (ms)'),
            'maximum_number_of_words': _('Número máximo de palabras'),
            'maximum_word_length': _('Largo máximo de cada palabra (ms)'),
            'silence_threshold': _('Nivel de ruido'),
        }


class EsquemaGrabacionesForm(forms.ModelForm):

    class Meta:
        model = EsquemaGrabaciones
        exclude = ()
        widgets = {
            'id_contacto': forms.CheckboxInput(attrs={'class': 'form-control'}),
            'fecha': forms.CheckboxInput(attrs={'class': 'form-control'}),
            'telefono_contacto': forms.CheckboxInput(attrs={'class': 'form-control'}),
            'id_campana': forms.CheckboxInput(attrs={'class': 'form-control'}),
            'id_externo_contacto': forms.CheckboxInput(attrs={'class': 'form-control'}),
            'id_externo_campana': forms.CheckboxInput(attrs={'class': 'form-control'}),
            'id_agente': forms.CheckboxInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'id_contacto': _('Id contacto'),
            'fecha': _('Fecha'),
            'telefono_contacto': _('Teléfono contacto'),
            'id_campana': _('Id Campana'),
            'id_externo_contacto': _('Id externo contacto'),
            'id_externo_campana': _('Id externo campana'),
            'id_agente': _('Id agente'),
        }


class MusicaDeEsperaForm(forms.ModelForm):

    class Meta:
        model = MusicaDeEspera
        fields = ('nombre', 'audio_original', 'playlist')
        widgets = {
            "nombre": forms.TextInput(attrs={'class': 'form-control'}),
            "audio_original": forms.FileInput(attrs={'class': 'form-control'}),
            "playlist": forms.HiddenInput(),
        }
        help_texts = {
            'audio_original': _("Seleccione el archivo .wav que desea para la Musica de Espera."),
        }

    def __init__(self, *args, **kwargs):
        super(MusicaDeEsperaForm, self).__init__(*args, **kwargs)
        self.initial['playlist'] = kwargs['initial']['playlist']
        self.fields['audio_original'].required = True

    def clean_archivo(self):
        audio_original = self.cleaned_data.get('audio_original', False)
        if audio_original:
            validar_extension_archivo_audio(audio_original)
        return audio_original


OpcionDestinoValidacionFechaHoraFormset = modelformset_factory(
    OpcionDestino, form=OpcionDestinoValidacionFechaHoraForm,
    formset=OpcionDestinoValidacionFechaHoraFormSet, can_delete=False, extra=0, min_num=2,
    max_num=2)
