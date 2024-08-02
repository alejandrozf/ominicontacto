from ominicontacto_app.models import ArchivoDeAudio
from utiles_globales import validar_extension_archivo_audio


from django import forms
from django.utils.translation import gettext_lazy as _
from ominicontacto_app.services.tts.generador import (
    GTTS_ID, ESPEAK_ID, PICOTTS_ID, GTTS_VOICES, ESPEAK_VOICES, PICOTTS_VOICES)


class ArchivoDeAudioForm(forms.ModelForm):
    usar_tts = forms.BooleanField(required=False, label=_('Utilizar Servicio TTS'))
    tts_service = forms.ChoiceField(
        required=False, widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('Servicio TTS'),
        choices=((GTTS_ID, 'gTTS'),
                 (ESPEAK_ID, 'ESPeak-NG'),
                 (PICOTTS_ID, 'PicoTTS'),
                 ))
    tts_voice = forms.ChoiceField(
        required=False, widget=forms.Select(attrs={'class': 'form-control'}),
        choices=(), label=_('Voz')
    )
    tts_text = forms.CharField(required=False, label=_('Texto'),
                               widget=forms.Textarea(attrs={'class': 'form-control'}))

    class Meta:
        model = ArchivoDeAudio
        fields = ('descripcion', 'audio_original')
        widgets = {
            "descripcion": forms.TextInput(attrs={'class': 'form-control'}),
            "audio_original": forms.FileInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'audio_original': _("Seleccione el archivo de audio que desea para "
                                "la Campaña. Si ya existe uno y guarda otro, el audio será "
                                "reemplazado."),
        }

    def __init__(self, *args, **kwargs):
        super(ArchivoDeAudioForm, self).__init__(*args, **kwargs)
        self.fields['audio_original'].required = False
        self.fields['tts_voice'].choices = self._get_voice_choices()

    def clean(self):
        cleaned_data = super(ArchivoDeAudioForm, self).clean()
        usar_tts = cleaned_data.get('usar_tts', False)
        if not usar_tts:
            audio_original = cleaned_data.get('audio_original', False)
            if audio_original:
                validar_extension_archivo_audio(audio_original)
            else:
                raise forms.ValidationError(_('Debe indicar un archivo'))
        else:
            tts_service = cleaned_data.get('tts_service')
            tts_voice = cleaned_data.get('tts_voice', None)
            if tts_service is None:
                raise forms.ValidationError(_('Debe seleccionar un servicio de TTS'))
            if tts_voice is None:
                raise forms.ValidationError(_('Debe seleccionar una voz'))
            tts_voice = self.get_tts_voice(tts_service, tts_voice)

        return cleaned_data

    def clean_tts_text(self):
        if self.cleaned_data.get('usar_tts'):
            texto = self.cleaned_data.get('tts_text', '').strip()
            if texto == '':
                raise forms.ValidationError(_('Debe indicar un texto'))
            return texto

    def get_tts_voice(self, tts_service, tts_voice):
        # Validar que el prefijo de tts_voice pertenezca al servicio correspondiente
        voice = tts_voice.split('_')
        voice_service = voice.pop(0)
        if not tts_service == voice_service:
            raise forms.ValidationError(_('Voz incorrecta para el servicio seleccionado'))
        if tts_service == ESPEAK_ID or tts_service == PICOTTS_ID:
            return voice[0]
        if tts_service == GTTS_ID:
            return voice

    def _get_voice_choices(self):
        # Agrega el prefijo de cada servicio a cada choice
        choices = tuple(((ESPEAK_ID + '_' + k, v) for k, v in ESPEAK_VOICES.items()))
        choices += tuple(((PICOTTS_ID + '_' + k, v) for k, v in PICOTTS_VOICES.items()))
        # Para gTTS se necesita el par lenguaje + tld (Top Level Domain)
        for lang, voices in GTTS_VOICES.items():
            for tld, voice_description in voices.items():
                choices += ((GTTS_ID + '_' + lang + '_' + tld, voice_description), )
        return choices
