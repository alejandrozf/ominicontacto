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

import re

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.forms.models import (inlineformset_factory, modelformset_factory, BaseModelFormSet)
from django.utils.translation import ugettext_lazy as _

from configuracion_telefonia_app.models import AmdConf, AudiosAsteriskConf, DestinoEntrante, \
    EsquemaGrabaciones, GrupoHorario, IVR, IdentificadorCliente, MusicaDeEspera, OpcionDestino, \
    Playlist, TroncalSIP, ValidacionTiempo
from ominicontacto_app.models import ArchivoDeAudio
from ominicontacto_app.views_archivo_de_audio import convertir_archivo_audio

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


class IVRForm(forms.ModelForm):

    AUDIO_OML = '1'
    AUDIO_EXTERNO = '2'
    AUDIO_TIPO_CHOICES = ((AUDIO_OML, _('Archivo interno')), (AUDIO_EXTERNO, _('Archivo externo')))

    audio_ppal_escoger = forms.ChoiceField(
        choices=AUDIO_TIPO_CHOICES, widget=forms.RadioSelect(
            attrs={'class': 'form-control escogerAudioPpal'}))
    audio_principal = forms.ModelChoiceField(
        required=False, queryset=ArchivoDeAudio.objects.filter(borrado=False),
        widget=forms.Select(attrs={'class': 'form-control'}))
    audio_ppal_ext_audio = forms.FileField(required=False)
    time_out_destination = forms.ModelChoiceField(
        queryset=DestinoEntrante.objects.all(), label=_('Destino time out:'), widget=forms.Select(
            attrs={'class': 'form-control', 'id': 'destinoTimeOut'}))
    time_out_destination_type = forms.ChoiceField(
        label=_('Tipo de destino para time out:'), choices=TIPOS_DESTINOS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'destinoTimeOutTipo'}))
    time_out_audio_escoger = forms.ChoiceField(
        choices=AUDIO_TIPO_CHOICES, widget=forms.RadioSelect(
            attrs={'class': 'form-control escogerAudioTimeOut'}))
    time_out_ext_audio = forms.FileField(required=False)
    invalid_destination = forms.ModelChoiceField(
        queryset=DestinoEntrante.objects.all(), label=_('Destino inválido:'), widget=forms.Select(
            attrs={'class': 'form-control', 'id': 'destinoInvalido'}))
    invalid_destination_type = forms.ChoiceField(
        label=_('Tipo de destino para destino inválido:'), choices=TIPOS_DESTINOS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'destinoInvalidoTipo'}))
    invalid_destination_audio_escoger = forms.ChoiceField(
        choices=AUDIO_TIPO_CHOICES, widget=forms.RadioSelect(
            attrs={'class': 'form-control escogerAudioDestInvalido'}))
    invalid_destination_ext_audio = forms.FileField(required=False)

    class Meta:
        model = IVR
        fields = (
            'nombre', 'descripcion', 'time_out', 'time_out_retries', 'invalid_retries',
            'audio_ppal_escoger', 'audio_principal', 'audio_ppal_ext_audio',
            'time_out_destination', 'time_out_destination_type', 'time_out_audio_escoger',
            'time_out_ext_audio', 'time_out_audio', 'invalid_destination',
            'invalid_destination_type', 'invalid_destination_audio_escoger',
            'invalid_destination_ext_audio', 'invalid_audio')
        exclude = ()

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'time_out': forms.NumberInput(attrs={'class': 'form-control'}),
            'time_out_retries': forms.NumberInput(attrs={'class': 'form-control'}),
            'time_out_audio': forms.Select(attrs={'class': 'form-control'}),
            'invalid_retries': forms.NumberInput(attrs={'class': 'form-control'}),
            'invalid_audio': forms.Select(attrs={'class': 'form-control'}),
        }

        help_texts = {
            'time_out': _('En segundos'),
        }

        labels = {
            'nombre': _('Nombre'),
            'descripcion': _('Descripción')
        }

    def _inicializar_ivr_a_modificar(self, *args, **kwargs):
        valores_fijos_ivr = (IVR.VALOR_TIME_OUT, IVR.VALOR_DESTINO_INVALIDO)
        valor_opcion_field = {
            IVR.VALOR_TIME_OUT: 'time_out_destination',
            IVR.VALOR_DESTINO_INVALIDO: 'invalid_destination'
        }
        ivr = self.instance
        nodo_ivr = DestinoEntrante.objects.get(
            object_id=ivr.pk, content_type=ContentType.objects.get_for_model(ivr))
        opciones_destino_fijas_ivr = nodo_ivr.destinos_siguientes.filter(
            valor__in=valores_fijos_ivr)
        for opcion_destino in opciones_destino_fijas_ivr:
            destino = opcion_destino.destino_siguiente
            destino_valor = opcion_destino.valor
            destino_field = valor_opcion_field[destino_valor]
            destino_field_tipo = valor_opcion_field[destino_valor] + '_type'
            self.initial[destino_field] = destino.pk
            self.initial[destino_field_tipo] = destino.tipo
            destinos_qs = DestinoEntrante.get_destinos_por_tipo(destino.tipo)
            destinos_choices = [EMPTY_CHOICE] + [(dest_entr.id, str(dest_entr))
                                                 for dest_entr in destinos_qs]
            self.fields[destino_field].choices = destinos_choices

    def __init__(self, *args, **kwargs):
        super(IVRForm, self).__init__(*args, **kwargs)
        # se marcan las opciones de selección de audio por defecto
        # a cargar un audio de OML
        self.initial['audio_ppal_escoger'] = self.AUDIO_OML
        self.initial['time_out_audio_escoger'] = self.AUDIO_OML
        self.initial['invalid_destination_audio_escoger'] = self.AUDIO_OML

        destinos_qs = DestinoEntrante.objects.all()
        self.fields['time_out_destination'].queryset = destinos_qs
        self.fields['invalid_destination'].queryset = destinos_qs

        # TODO: revisar por qué si el queryset por defecto de ArchivoDeAudio está modificado
        # para no mostrar los audios marcados como eliminados, dichos audios se muestran como
        # opciones para los campos listados a continuación
        audios_queryset = ArchivoDeAudio.objects.all()
        self.fields['audio_principal'].queryset = audios_queryset
        self.fields['time_out_audio'].queryset = audios_queryset
        self.fields['invalid_audio'].queryset = audios_queryset
        self.fields['invalid_audio'].queryset = audios_queryset
        instance = getattr(self, 'instance', None)
        if instance.pk is not None:
            self._inicializar_ivr_a_modificar(self, *args, **kwargs)

    def _validar_escoger_audio(self, valor_escoger_audio, valor_audio_oml, valor_audio_externo,
                               obligatorio=False):
        # valida que el audio escogido concuerde con el valor del selector del tipo de audio
        if valor_escoger_audio == self.AUDIO_EXTERNO and valor_audio_externo is None:
            raise forms.ValidationError(
                _('Debe escoger un audio como archivo externo'), code='invalid')
        if valor_escoger_audio != self.AUDIO_EXTERNO and valor_audio_externo is not None:
            raise forms.ValidationError(
                _('Seleccione Archivo Externo si desea subir un Archivo de audio nuevo'),
                code='invalid')
        if obligatorio and valor_escoger_audio == self.AUDIO_OML and valor_audio_oml is None:
            raise forms.ValidationError(
                _('Debe escoger un archivo'), code='invalid')

    def clean_audio_principal(self):
        audio_ppal_escoger = self.cleaned_data['audio_ppal_escoger']
        if audio_ppal_escoger == self.AUDIO_OML:
            audio_principal = self.cleaned_data.get('audio_principal', None)
            if audio_principal is None:
                raise forms.ValidationError(
                    _('Debe escoger un archivo'))
            return audio_principal
        return None

    def clean(self):
        cleaned_data = super(IVRForm, self).clean()
        audio_ppal_escoger = cleaned_data['audio_ppal_escoger']
        audio_principal = cleaned_data.get('audio_principal', None)
        audio_ppal_ext_audio = cleaned_data.get('audio_ppal_ext_audio', None)
        time_out_audio_escoger = cleaned_data['time_out_audio_escoger']
        time_out_audio = cleaned_data.get('time_out_audio', None)
        time_out_ext_audio = cleaned_data.get('time_out_ext_audio', None)
        invalid_destination_audio_escoger = cleaned_data['invalid_destination_audio_escoger']
        invalid_audio = cleaned_data.get('invalid_audio', None)
        invalid_destination_ext_audio = cleaned_data.get('invalid_destination_ext_audio', None)
        self._validar_escoger_audio(audio_ppal_escoger, audio_principal, audio_ppal_ext_audio,
                                    obligatorio=True)
        self._validar_escoger_audio(time_out_audio_escoger, time_out_audio, time_out_ext_audio)
        self._validar_escoger_audio(
            invalid_destination_audio_escoger, invalid_audio, invalid_destination_ext_audio)
        validar_extension_archivo_audio(audio_ppal_ext_audio)
        validar_extension_archivo_audio(time_out_ext_audio)
        validar_extension_archivo_audio(invalid_destination_ext_audio)
        return cleaned_data

    def _asignar_audio_externo(self, escoger_audio, audio_externo, tipo_audio):
        """ En caso que se haya elegido audio externo, lo asigna al IVR """
        if escoger_audio == str(self.AUDIO_EXTERNO):
            # Primero saco la extension .wav
            descripcion = ''.join(audio_externo.name.rsplit('.wav', 1))
            descripcion = ArchivoDeAudio.calcular_descripcion(descripcion)
            kwargs = {
                'descripcion': descripcion,
                'audio_original': audio_externo
            }
            archivo_de_audio = ArchivoDeAudio.crear_archivo(**kwargs)
            convertir_archivo_audio(archivo_de_audio)
            if tipo_audio == 'audio_principal':
                self.instance.audio_principal = archivo_de_audio
            elif tipo_audio == 'time_out_audio':
                self.instance.time_out_audio = archivo_de_audio
            elif tipo_audio == 'invalid_audio':
                self.instance.invalid_audio = archivo_de_audio

    def save(self, *args, **kwargs):
        audio_ppal_escoger = self.cleaned_data['audio_ppal_escoger']
        audio_ppal_ext_audio = self.cleaned_data['audio_ppal_ext_audio']
        time_out_audio_escoger = self.cleaned_data['time_out_audio_escoger']
        time_out_ext_audio = self.cleaned_data['time_out_ext_audio']
        invalid_destination_audio_escoger = self.cleaned_data['invalid_destination_audio_escoger']
        invalid_destination_ext_audio = self.cleaned_data['invalid_destination_ext_audio']
        self._asignar_audio_externo(audio_ppal_escoger, audio_ppal_ext_audio, 'audio_principal')
        self._asignar_audio_externo(time_out_audio_escoger, time_out_ext_audio, 'time_out_audio')
        self._asignar_audio_externo(
            invalid_destination_audio_escoger, invalid_destination_ext_audio, 'invalid_audio')
        return super(IVRForm, self).save(*args, **kwargs)


class OpcionDestinoIVRBaseFormset(BaseModelFormSet):

    def clean(self):
        """
        Realiza los validaciones relacionadas con los troncales asignados a una
        ruta saliente
        """
        if any(self.errors):
            return

        deleted_forms = self.deleted_forms
        save_candidates_forms = set(self.forms) - set(deleted_forms)
        dmtfs = []
        for form in save_candidates_forms:
            dmtf = form.cleaned_data.get('valor', None)
            if dmtf in dmtfs:
                raise forms.ValidationError(
                    _('Los valores de DTMF deben ser distintos'), code='invalid')
            dmtfs.append(dmtf)


class OpcionDestinoIVRForm(forms.ModelForm):

    DMFT_REGEX = r'^[0-9|\-|#|\*]$'

    tipo_destino = forms.ChoiceField(
        label=_('Tipo de destino'), choices=TIPOS_DESTINOS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = OpcionDestino
        fields = ('valor', 'destino_siguiente',)
        labels = {
            'valor': _('DTMF'),
            'destino_siguiente': _('Destino'),
        }

    def __init__(self, *args, **kwargs):
        super(OpcionDestinoIVRForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance.pk is not None:
            tipo_destino = instance.destino_siguiente.tipo
            self.initial['tipo_destino'] = tipo_destino
            destinos_qs = DestinoEntrante.get_destinos_por_tipo(tipo_destino)
            destino_entrante_choices = [EMPTY_CHOICE] + [(dest_entr.id, str(dest_entr))
                                                         for dest_entr in destinos_qs]
            self.fields['destino_siguiente'].choices = destino_entrante_choices

    def clean_valor(self):
        valor = self.cleaned_data['valor']
        compiled_regex = re.compile(self.DMFT_REGEX)
        if compiled_regex.match(valor) is None:
            raise forms.ValidationError(
                _('El valor del DTMF debe ser un dígito o alguno de: #, -, *'))
        return valor


class ValidacionTiempoForm(forms.ModelForm):

    class Meta:
        model = ValidacionTiempo
        exclude = ()


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


OpcionDestinoIVRFormset = modelformset_factory(
    OpcionDestino, form=OpcionDestinoIVRForm, formset=OpcionDestinoIVRBaseFormset, can_delete=True,
    extra=1, min_num=0)

OpcionDestinoValidacionFechaHoraFormset = modelformset_factory(
    OpcionDestino, form=OpcionDestinoValidacionFechaHoraForm,
    formset=OpcionDestinoValidacionFechaHoraFormSet, can_delete=False, extra=0, min_num=2,
    max_num=2)

ValidacionTiempoFormset = inlineformset_factory(
    GrupoHorario, ValidacionTiempo, form=ValidacionTiempoForm, can_delete=True, extra=0, min_num=1)
