# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.forms.models import (inlineformset_factory, modelformset_factory, BaseInlineFormSet,
                                 BaseModelFormSet)
from django.utils.translation import ugettext as _

from configuracion_telefonia_app.models import (PatronDeDiscado, RutaSaliente, RutaEntrante,
                                                TroncalSIP, OrdenTroncal, DestinoEntrante, IVR,
                                                OpcionDestino, ValidacionTiempo, GrupoHorario)
from ominicontacto_app.models import ArchivoDeAudio
from ominicontacto_app.views_archivo_de_audio import convertir_archivo_audio


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
        }


class PatronDeDiscadoForm(forms.ModelForm):

    class Meta:
        model = PatronDeDiscado
        exclude = ('orden',)
        labels = {
            'match_pattern': _('Patrón de discado'),
            'prefix': _('Prefijo'),
        }


class RutaSalienteForm(forms.ModelForm):

    class Meta:
        model = RutaSaliente
        exclude = ()
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'ring_time': forms.NumberInput(attrs={'class': 'form-control'}),
            'dial_options': forms.TextInput(attrs={'class': 'form-control'}),
        }


class PatronDeDiscadoBaseFormset(BaseInlineFormSet):

        def clean(self):
            """
            Realiza los validaciones relacionadas con los patrones de discado asignados a una ruta
            saliente
            """
            if any(self.errors):
                return
            deleted_forms = self.deleted_forms
            save_candidates_forms = set(self.forms) - set(deleted_forms)
            if len(save_candidates_forms) == 0:
                raise forms.ValidationError(
                    _('Debe ingresar al menos un patrón de discado'), code='invalid')

            patrones_discado = []
            for form in save_candidates_forms:
                prefix = form.cleaned_data.get('prefix', False)
                patron_discado = form.cleaned_data.get('match_pattern', False)
                if (prefix, patron_discado) in patrones_discado:
                    raise forms.ValidationError(
                        _('Los patrones de discado deben ser diferentes'), code='invalid')
                patrones_discado.append((prefix, patron_discado))

        def save(self):
            """
            Salva el formset de los troncales actualizando el orden de acuerdo a los
            cambios realizados en la interfaz
            """
            if not self.instance.patrones_de_discado.exists():
                max_orden = 0
            else:
                max_orden = self.instance.patrones_de_discado.last().orden
            forms = self.forms
            for i, form in enumerate(forms, max_orden + 1):
                # asignamos nuevos ordenes a partir del máximo número de orden para
                # evitar clashes de integridad al salvar los formsets
                form.instance.orden = i
                if (form.instance.pk is not None) and not form.has_changed():
                    # si algun patrón no ha sufrido cambios en una edición se fuerza
                    # el salvado del numero de orden desde la instancia para evitar
                    # problemas de orden
                    form.instance.save()
            super(PatronDeDiscadoBaseFormset, self).save()


class OrdenTroncalBaseFormset(BaseInlineFormSet):

    def clean(self):
        """
        Realiza los validaciones relacionadas con los troncales asignados a
        una ruta saliente
        """
        if any(self.errors):
            return

        deleted_forms = self.deleted_forms
        save_candidates_forms = set(self.forms) - set(deleted_forms)
        if len(save_candidates_forms) == 0:
            raise forms.ValidationError(
                _('Debe ingresar al menos un troncal'), code='invalid')

        troncales = []
        for form in save_candidates_forms:
            troncal = form.cleaned_data.get('troncal', None)
            if troncal in troncales:
                raise forms.ValidationError(_('Los troncales deben ser distintos'), code='invalid')
            troncales.append(troncal)

    def save(self):
        """
        Salva el formset de los troncales actualizando el orden de acuerdo a los
        cambios realizados en la interfaz
        """
        if not self.instance.secuencia_troncales.exists():
            max_orden = 0
        else:
            max_orden = self.instance.secuencia_troncales.last().orden
        forms = self.forms
        for i, form in enumerate(forms, max_orden + 1):
            # asignamos nuevos ordenes a partir del máximo número de orden para
            # evitar clashes de integridad al salvar los formsets
            form.instance.orden = i
            if (form.instance.pk is not None) and not form.has_changed():
                # si alguna asociación con un troncal no ha sufrido cambios en una edición se fuerza
                # el salvado del numero de orden desde la instancia para evitar
                # problemas de orden
                form.instance.save()
        super(OrdenTroncalBaseFormset, self).save()


class RutaEntranteForm(forms.ModelForm):

    tipo_destino = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'tipo_destino'}),
    )

    field_order = ('nombre', 'telefono', 'prefijo_caller_id', 'idioma', 'tipo_destino',
                   'destino')

    class Meta:
        model = RutaEntrante
        exclude = ()
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'prefijo_caller_id': forms.TextInput(attrs={'class': 'form-control'}),
            'idioma': forms.Select(attrs={'class': 'form-control'}),
            'destino': forms.Select(attrs={'class': 'form-control', 'id': 'destino'}),
        }
        labels = {
            'tipo_destino': _('Tipo de destino'),
            'telefono': _('Número DID')
        }

    def __init__(self, *args, **kwargs):
        super(RutaEntranteForm, self).__init__(*args, **kwargs)
        tipo_destino_choices = [EMPTY_CHOICE]
        tipo_destino_choices.extend(DestinoEntrante.TIPOS_DESTINOS)
        self.fields['tipo_destino'].choices = tipo_destino_choices
        instance = getattr(self, 'instance', None)
        if instance.pk is not None:
            tipo = instance.destino.tipo
            self.initial['tipo_destino'] = tipo
            destinos_qs = DestinoEntrante.get_destinos_por_tipo(tipo)
            destino_entrante_choices = [EMPTY_CHOICE] + [(dest_entr.id, dest_entr.__unicode__())
                                                         for dest_entr in destinos_qs]
            self.fields['destino'].choices = destino_entrante_choices
        else:
            self.fields['destino'].choices = ()


class IVRForm(forms.ModelForm):

    AUDIO_OML = 1
    AUDIO_EXTERNO = 2
    AUDIO_TIPO_CHOICES = ((AUDIO_OML, _('Archivo de OML')), (AUDIO_EXTERNO, _('Archivo externo')))

    audio_ppal_escoger = forms.ChoiceField(
        choices=AUDIO_TIPO_CHOICES, widget=forms.RadioSelect(
            attrs={'class': 'form-control escogerAudioPpal'}))
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
        exclude = ()

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'audio_principal': forms.Select(attrs={'class': 'form-control'}),
            'time_out': forms.NumberInput(attrs={'class': 'form-control'}),
            'time_out_retries': forms.NumberInput(attrs={'class': 'form-control'}),
            'time_out_audio': forms.Select(attrs={'class': 'form-control'}),
            'invalid_retries': forms.NumberInput(attrs={'class': 'form-control'}),
            'invalid_audio': forms.Select(attrs={'class': 'form-control'}),
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
            destinos_choices = [EMPTY_CHOICE] + [(dest_entr.id, dest_entr.__unicode__())
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

    def _validar_escoger_audio(self, valor_escoger_audio, valor_audio_oml, valor_audio_externo):
        # valida que el audio escogido concuerde con el valor del selector del tipo de audio
        valor_escoger_audio = int(valor_escoger_audio)
        if valor_escoger_audio == self.AUDIO_EXTERNO and valor_audio_externo is None:
            raise forms.ValidationError(
                _('Debe escoger un audio como archivo externo'), code='invalid')

    def _validar_extension_audio(self, valor):
        if (valor is not None and not valor.name.endswith('.wav') and
                not valor.name.endswith('.mp3')):
            raise forms.ValidationError(_('Archivos permitidos: .mp3, .wav'), code='invalid')

    def clean(self):
        cleaned_data = super(IVRForm, self).clean()
        audio_ppal_escoger = cleaned_data['audio_ppal_escoger']
        audio_principal = cleaned_data['audio_principal']
        audio_ppal_ext_audio = cleaned_data['audio_ppal_ext_audio']
        time_out_audio_escoger = cleaned_data['time_out_audio_escoger']
        time_out_audio = cleaned_data['time_out_audio']
        time_out_ext_audio = cleaned_data['time_out_ext_audio']
        invalid_destination_audio_escoger = cleaned_data['invalid_destination_audio_escoger']
        invalid_audio = cleaned_data['invalid_audio']
        invalid_destination_ext_audio = cleaned_data['invalid_destination_ext_audio']
        self._validar_escoger_audio(audio_ppal_escoger, audio_principal, audio_ppal_ext_audio)
        self._validar_escoger_audio(time_out_audio_escoger, time_out_audio, time_out_ext_audio)
        self._validar_escoger_audio(
            invalid_destination_audio_escoger, invalid_audio, invalid_destination_ext_audio)
        self._validar_extension_audio(audio_ppal_ext_audio)
        self._validar_extension_audio(time_out_ext_audio)
        self._validar_extension_audio(invalid_destination_ext_audio)
        return cleaned_data

    def _asignar_audio_externo(self, escoger_audio, audio_externo, tipo_audio):
        if escoger_audio == str(self.AUDIO_EXTERNO):
            kwargs = {
                'descripcion': audio_externo.name,
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
                    _('Los valores de DMT deben ser distintos'), code='invalid')
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
            'valor': _('DMTF'),
            'destino_siguiente': _('Destino'),
        }

    def __init__(self, *args, **kwargs):
        super(OpcionDestinoIVRForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance.pk is not None:
            tipo_destino = instance.destino_siguiente.tipo
            self.initial['tipo_destino'] = tipo_destino
            destinos_qs = DestinoEntrante.get_destinos_por_tipo(tipo_destino)
            destino_entrante_choices = [EMPTY_CHOICE] + [(dest_entr.id, dest_entr.__unicode__())
                                                         for dest_entr in destinos_qs]
            self.fields['destino_siguiente'].choices = destino_entrante_choices

    def clean_valor(self):
        valor = self.cleaned_data['valor']
        compiled_regex = re.compile(self.DMFT_REGEX)
        if compiled_regex.match(valor) is None:
            raise forms.ValidationError(
                _('El valor del DMTF debe ser un dígito o alguno de: #, -, *'))
        return valor


class ValidacionTiempoForm(forms.ModelForm):

    class Meta:
        model = ValidacionTiempo
        exclude = ()


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
            destino_entrante_choices = [EMPTY_CHOICE] + [(dest_entr.id, dest_entr.__unicode__())
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


PatronDeDiscadoFormset = inlineformset_factory(
    RutaSaliente, PatronDeDiscado, form=PatronDeDiscadoForm,
    formset=PatronDeDiscadoBaseFormset, can_delete=True, extra=0, min_num=1)

OrdenTroncalFormset = inlineformset_factory(
    RutaSaliente, OrdenTroncal, fields=('troncal',), formset=OrdenTroncalBaseFormset,
    can_delete=True, extra=0, min_num=1)

OpcionDestinoIVRFormset = modelformset_factory(
    OpcionDestino, form=OpcionDestinoIVRForm, formset=OpcionDestinoIVRBaseFormset, can_delete=True,
    extra=1, min_num=0)

OpcionDestinoValidacionFechaHoraFormset = modelformset_factory(
    OpcionDestino, form=OpcionDestinoValidacionFechaHoraForm,
    formset=OpcionDestinoValidacionFechaHoraFormSet, can_delete=False, extra=0, min_num=2,
    max_num=2)

ValidacionTiempoFormset = inlineformset_factory(
    GrupoHorario, ValidacionTiempo, form=ValidacionTiempoForm, can_delete=True, extra=0, min_num=1)
