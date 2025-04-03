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

import json
from django import forms
from django.conf import settings

from django.core.validators import URLValidator
from django.forms.models import inlineformset_factory, BaseInlineFormSet, ModelChoiceField
from django.contrib.auth.forms import (
    UserChangeForm,
    UserCreationForm
)
from django.db.models import Count, Q
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, MultiField
from django.contrib.auth.models import Group

from constance import config

from ominicontacto_app.models import (
    User, AgenteProfile, Queue, QueueMember, BaseDatosContacto, ContactoBlacklist,
    Campana, Contacto, CalificacionCliente, Grupo, FieldFormulario,
    RespuestaFormularioGestion, AgendaContacto, ActuacionVigente, Blacklist, SitioExterno,
    SistemaExterno, ReglasIncidencia, ReglaIncidenciaPorCalificacion, SupervisorProfile,
    ArchivoDeAudio, NombreCalificacion, OpcionCalificacion, ParametrosCrm,
    AuditoriaCalificacion, ConfiguracionDeAgentesDeCampana, ListasRapidas, ContactoListaRapida,
    AutenticacionExternaDeUsuario
)
from ominicontacto_app.services.campana_service import CampanaService
from ominicontacto_app.utiles import (convertir_ascii_string, validar_nombres_campanas,
                                      validar_solo_alfanumericos_o_guiones,
                                      contiene_solo_alfanumericos_o_guiones,
                                      validar_longitud_nombre_base_de_contactos)
from configuracion_telefonia_app.models import DestinoEntrante, Playlist, RutaSaliente
from whatsapp_app.models import ConfiguracionWhatsappCampana
from ominicontacto_app.parser import is_valid_length

from ominicontacto_app.utiles import convert_fecha_datetime
from reportes_app.models import LlamadaLog
from ominicontacto_app.services.sistema_externo.interaccion_sistema_externo import (
    InteraccionConSistemaExterno)

import jsonschema

TIEMPO_MINIMO_DESCONEXION = 2
EMPTY_CHOICE = ('', '---------')
ALL_CAMPAIGNS_ACTIVE_CHOICE = ('activas', _('---- Todas las activas ----'))
ALL_CAMPAIGNS_INACTIVE_CHOICE = ('borradas', _('---- Todas las borradas ----'))
ALL_CAMPAIGNS_CHOICE = ('', _('---- Todas ----'))


class CustomUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('username', 'password', 'first_name', 'last_name', 'email', 'is_agente',
                  'is_supervisor')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class CustomUserCreationForm(UserCreationForm):
    rol = forms.ModelChoiceField(queryset=Group.objects.all(), label=_('Rol del usuario'))
    grupo = forms.ModelChoiceField(
        queryset=Grupo.objects.all(), label=_('Grupo de agentes'), required=False)
    autenticacion_externa = forms.BooleanField(
        required=False, disabled=True, widget=forms.CheckboxInput(attrs={'class': 'form-control'}),
        label=_('Autenticación externa'), initial=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'rol', 'password1', 'password2', 'grupo')
        labels = {
        }
        error_messages = {
            'username': {'unique':
                         _('No se puede volver a utilizar dos veces el mismo nombre de usuario')}
        }

    def __init__(self, roles_queryset, grupo_queryset, mostrar_autenticacion_externa,
                 habilitar_autenticacion_externa, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['rol'].widget.attrs['class'] = 'form-control'
        self.fields['rol'].queryset = roles_queryset
        self.fields['rol'].label_from_instance = self.label_para_group

        if grupo_queryset:
            self.fields['grupo'].queryset = grupo_queryset
        self.fields['grupo'].widget.attrs['class'] = 'form-control'
        if mostrar_autenticacion_externa:
            self.fields['autenticacion_externa'].initial = self.instance.autenticar_con_ldap
            if habilitar_autenticacion_externa:
                self.fields['autenticacion_externa'].disabled = False
        else:
            self.fields.pop('autenticacion_externa')

    def clean(self):
        cleaned_data = super().clean()
        rol = cleaned_data.get('rol')
        grupo = cleaned_data.get('grupo')
        if rol and rol.name == User.AGENTE and not cleaned_data.get('email'):
            self.add_error("email", _("Este campo es requerido para un usuario de tipo Agente."))
        if rol and rol.name == User.AGENTE and not grupo:
            self.add_error("grupo", _("Este campo es requerido para un usuario de tipo Agente."))
        return cleaned_data

    @staticmethod
    def label_para_group(obj):
        return User.nombre_rol(obj)


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    password1 = forms.CharField(max_length=128,
                                required=False,
                                # will be overwritten by __init__()
                                help_text=_('Ingrese la nueva contraseña '
                                            '(sólo si desea cambiarla)'),
                                # will be overwritten by __init__()
                                widget=forms.PasswordInput(),
                                label=_('Contraseña'))

    password2 = forms.CharField(
        max_length=128,
        required=False,  # will be overwritten by __init__()
        # will be overwritten by __init__()
        help_text=_('Ingrese la nueva contraseña (sólo si desea cambiarla)'),
        widget=forms.PasswordInput(),
        label=_('Contraseña (otra vez)'))

    autenticacion_externa = forms.BooleanField(
        required=False, disabled=True, widget=forms.CheckboxInput(attrs={'class': 'form-control'}),
        label=_('Autenticación externa'))

    def __init__(self, mostrar_autenticacion_externa,
                 habilitar_autenticacion_externa, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs["instance"].is_agente:
            self.fields["email"].required = True
        if mostrar_autenticacion_externa:
            self.fields['autenticacion_externa'].initial = self.instance.autenticar_con_ldap
            if habilitar_autenticacion_externa:
                self.fields['autenticacion_externa'].disabled = False
        else:
            self.fields.pop('autenticacion_externa')

    def clean(self):
        cleaned_data = super(UserChangeForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 != '':
            validate_password(password1)
        if password1 != password2:
            raise forms.ValidationError(_('Las contraseñas no coinciden'))
        return self.cleaned_data

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        error_messages = {
            'username': {'unique':
                         _('No se puede volver a utilizar dos veces el mismo nombre de usuario')}
        }


class ForcePasswordChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(ForcePasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['password1'].required = True
        self.fields['password2'].required = True
        self.fields['password1'].help_text = _('Ingrese la nueva contraseña')
        self.fields['password2'].help_text = _('Ingrese la nueva contraseña')


class AgenteProfileForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    class Meta:
        model = AgenteProfile
        fields = ('grupo',)

    def __init__(self, grupos_queryset, *args, **kwargs):
        super(AgenteProfileForm, self).__init__(*args, **kwargs)
        self.fields['grupo'].widget.attrs['class'] = 'form-control'
        self.fields['grupo'].queryset = grupos_queryset


class NoValidationMultipleChoiceField(forms.MultipleChoiceField):
    def validate(self, value):
        pass


class CampaingsByTypeForm(forms.Form):
    """
    Formulario para filtrar campañas por tipo
    """
    MANUAL = 1
    DIALER = 2
    ENTRANTE = 3
    PREVIEW = 4
    MANUAL_DISPLAY = _('Manual')
    DIALER_DISPLAY = _('Dialer')
    ENTRANTE_DISPLAY = _('Entrante')
    PREVIEW_DISPLAY = _('Preview')

    CAMPAING_TYPES = (
        ('-------', '-------'),
        (ENTRANTE, ENTRANTE_DISPLAY),
        (DIALER, DIALER_DISPLAY),
        (MANUAL, MANUAL_DISPLAY),
        (PREVIEW, PREVIEW_DISPLAY),
    )

    campaign_type = forms.ChoiceField(
        required=True, choices=CAMPAING_TYPES, label=_('Tipo de campaña'),
        widget=forms.Select(attrs={'class': 'form-control'}))

    campaigns_by_type = NoValidationMultipleChoiceField(
        required=True, label=_('Campañas'), choices=[],
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(CampaingsByTypeForm, self).__init__(*args, **kwargs)


class UpdateAgentPasswordForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    password1 = forms.CharField(max_length=128,
                                required=False,
                                # will be overwritten by __init__()
                                help_text=_('Ingrese la nueva contraseña '
                                            '(sólo si desea cambiarla)'),
                                # will be overwritten by __init__()
                                widget=forms.PasswordInput(),
                                label=_('Contraseña'))

    password2 = forms.CharField(
        max_length=128,
        required=False,  # will be overwritten by __init__()
        # will be overwritten by __init__()
        help_text=_('Ingrese la nueva contraseña (sólo si desea cambiarla)'),
        widget=forms.PasswordInput(),
        label=_('Contraseña (otra vez)'))

    def clean(self):
        cleaned_data = super(UpdateAgentPasswordForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 != '':
            validate_password(password1)
        if password1 != password2:
            raise forms.ValidationError(_('Las contraseñas no coinciden'))
        return self.cleaned_data

    class Meta:
        model = AgenteProfile
        fields = ('password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(UpdateAgentPasswordForm, self).__init__(*args, **kwargs)
        self.fields['password1'].required = True
        self.fields['password2'].required = True
        self.fields['password1'].help_text = _('Ingrese la nueva contraseña')
        self.fields['password2'].help_text = _('Ingrese la nueva contraseña')


class QueueEntranteForm(forms.ModelForm):
    """
    El form de cola para las colas
    """
    tipo_destino = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'tipo_destino'}), required=False
    )
    announce_position = forms.BooleanField(required=False),

    def __init__(self, audios_choices, *args, **kwargs):
        super(QueueEntranteForm, self).__init__(*args, **kwargs)
        self.fields['timeout'].required = True
        self.fields['retry'].required = True
        self.fields['announce_frequency'].required = False
        self.fields['wait_announce_frequency'].required = False
        self.fields['audios'].queryset = ArchivoDeAudio.objects.all()
        self.fields['audio_de_ingreso'].queryset = ArchivoDeAudio.objects.all()
        self.fields['audio_previo_conexion_llamada'].queryset = ArchivoDeAudio.objects.all()
        self.fields['musiconhold'].queryset = Playlist.objects.annotate(
            Count('musicas')).filter(musicas__count__gte=1)
        tipo_destino_choices = [EMPTY_CHOICE]
        tipo_destino = tuple(
            item for item in DestinoEntrante.TIPOS_DESTINOS if item[0] != DestinoEntrante.HANGUP)
        tipo_destino_choices.extend(tipo_destino)
        self.fields['tipo_destino'].choices = tipo_destino_choices
        instance = getattr(self, 'instance', None)
        # inicializa valores de destino failover
        if instance.pk is not None and instance.destino:
            tipo = instance.destino.tipo
            self.initial['tipo_destino'] = tipo
            destinos_qs = DestinoEntrante.get_destinos_por_tipo(tipo)
            destino_entrante_choices = [EMPTY_CHOICE] + [(dest_entr.id, dest_entr.__str__())
                                                         for dest_entr in destinos_qs]
            self.fields['destino'].choices = destino_entrante_choices
        else:
            self.fields['destino'].choices = ()
        # inicializa valores de campo ivr_breakdown
        ivr_breakdown_qs = DestinoEntrante.get_destinos_por_tipo(DestinoEntrante.IVR)
        ivr_breakdown_choices = [EMPTY_CHOICE] + [(dest_entr.id, dest_entr.__str__())
                                                  for dest_entr in ivr_breakdown_qs]
        self.fields['ivr_breakdown'].choices = ivr_breakdown_choices
        if not instance.pk:
            self.initial['wrapuptime'] = 2
            self.initial['auto_grabacion'] = True

    class Meta:
        model = Queue
        fields = ('name', 'timeout', 'retry', 'maxlen', 'wrapuptime', 'servicelevel',
                  'strategy', 'weight', 'wait', 'auto_grabacion', 'campana',
                  'audios', 'announce_frequency', 'audio_de_ingreso', 'campana',
                  'tipo_destino', 'destino', 'ivr_breakdown',
                  'announce_holdtime', 'announce_position', 'musiconhold',
                  'wait_announce_frequency', 'audio_previo_conexion_llamada')

        help_texts = {
            'timeout': _('En segundos'),
            'retry': _('En segundos'),
            'announce_frequency': _('En segundos'),
            'wait': _('En segundos'),
            'wrapuptime': _('En segundos'),
            'wait_announce_frequency': _('En segundos'),
        }
        widgets = {
            'name': forms.HiddenInput(),
            'campana': forms.HiddenInput(),
            'timeout': forms.TextInput(attrs={'class': 'form-control'}),
            'retry': forms.TextInput(attrs={'class': 'form-control'}),
            'maxlen': forms.TextInput(attrs={'class': 'form-control'}),
            'wrapuptime': forms.TextInput(attrs={'class': 'form-control'}),
            'servicelevel': forms.TextInput(attrs={'class': 'form-control'}),
            'strategy': forms.Select(attrs={'class': 'form-control'}),
            'announce_holdtime': forms.Select(attrs={'class': 'form-control'}),
            'weight': forms.TextInput(attrs={'class': 'form-control'}),
            'wait': forms.TextInput(attrs={'class': 'form-control'}),
            'audios': forms.Select(attrs={'class': 'form-control'}),
            'announce_frequency': forms.TextInput(attrs={'class': 'form-control'}),
            'audio_de_ingreso': forms.Select(attrs={'class': 'form-control'}),
            'tipo_destino': forms.Select(attrs={'class': 'form-control'}),
            'destino': forms.Select(attrs={'class': 'form-control', 'id': 'destino'}),
            'ivr_breakdown': forms.Select(attrs={'class': 'form-control'}),
            'musiconhold': forms.Select(attrs={'class': 'form-control'}),
            'wait_announce_frequency': forms.TextInput(attrs={'class': 'form-control'}),
            'audio_previo_conexion_llamada': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_maxlen(self):
        maxlen = self.cleaned_data.get('maxlen')
        if not maxlen > 0:
            raise forms.ValidationError('Cantidad Max de llamadas debe ser'
                                        ' mayor a cero')
        return maxlen

    def clean_announce_frequency(self):
        audio = self.cleaned_data.get('audios', None)
        frequency = self.cleaned_data.get('announce_frequency', None)
        if audio and (frequency is None or not (frequency > 0)):
            raise forms.ValidationError(
                _('Debe definir una frecuencia para el Anuncio Periódico'))
        if audio is None and frequency is not None:
            raise forms.ValidationError(
                _('Debe definir un Anuncio Periódico para esta frecuencia'))
        return frequency

    def clean_destino(self):
        tipo_destino = self.cleaned_data.get('tipo_destino', None)
        destino = self.cleaned_data.get('destino', None)
        if tipo_destino and not destino:
            raise forms.ValidationError(
                _('Debe seleccionar un destino'))
        return destino

    def clean_ivr_breakdown(self):
        ivr_breakdown = self.cleaned_data.get('ivr_breakdown', None)
        anuncio_periodico = self.cleaned_data.get('audios', None)
        if ivr_breakdown and ivr_breakdown.tipo != DestinoEntrante.IVR:
            raise forms.ValidationError(_('Debe seleccionar un destino IVR'))
        if ivr_breakdown and not anuncio_periodico:
            raise forms.ValidationError(_('Debe seleccionar un anuncio periódico'))
        return ivr_breakdown

    def clean_wait_announce_frequency(self):
        announce_position = self.cleaned_data.get('announce_position')
        wait_announce_frequency = self.cleaned_data.get('wait_announce_frequency')
        if announce_position is True and wait_announce_frequency is None:
            raise forms.ValidationError(_('Debe ingresar una frecuencia de '
                                          'anuncios de espera/posición'))
        return wait_announce_frequency


class QueueMemberForm(forms.ModelForm):
    """
    El form de miembro de una cola
    """

    def __init__(self, members, *args, **kwargs):
        super(QueueMemberForm, self).__init__(*args, **kwargs)

        self.fields['member'].queryset = members.prefetch_related('user')
        self.initial['penalty'] = 0

    class Meta:
        model = QueueMember
        fields = ('member', 'penalty')


class BaseDatosContactoForm(forms.ModelForm):

    def clean_nombre(self):
        # controlamos que el nombre no tenga espacios y caracteres no ascii
        nombre = self.cleaned_data.get('nombre')
        validar_solo_alfanumericos_o_guiones(nombre)
        validar_longitud_nombre_base_de_contactos(nombre)
        return nombre

    class Meta:
        model = BaseDatosContacto
        fields = ('nombre', 'archivo_importacion')
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'archivo_importacion': forms.FileInput(attrs={'class': 'form-control'}),
        }


class DefineColumnaTelefonoForm(forms.Form):

    def __init__(self, cantidad_columnas=0, *args, **kwargs):
        super(DefineColumnaTelefonoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        COLUMNAS_TELEFONO = []
        for columna in range(int(cantidad_columnas)):
            COLUMNAS_TELEFONO.append((columna, 'Columna{0}'.format(columna)))

        self.fields['telefono'] = forms.ChoiceField(choices=COLUMNAS_TELEFONO,
                                                    widget=forms.RadioSelect(
                                                        attrs={'class':
                                                               'telefono'}))
        self.helper.layout = Layout(MultiField('telefono'))


class DefineDatosExtrasForm(forms.Form):

    def __init__(self, cantidad_columnas=0, *args, **kwargs):
        super(DefineDatosExtrasForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        crispy_fields = []
        for columna in range(int(cantidad_columnas)):
            value = forms.ChoiceField(choices=BaseDatosContacto.DATOS_EXTRAS,
                                      required=False, label="",
                                      widget=forms.Select(
                                          attrs={'class': 'datos-extras'}))
            self.fields['datos-extras-{0}'.format(columna)] = value

            crispy_fields.append(Field('datos-extras-{0}'.format(columna)))
        self.helper.layout = Layout(crispy_fields)


class DefineNombreColumnaForm(forms.Form):

    def __init__(self, cantidad_columnas=0, *args, **kwargs):
        super(DefineNombreColumnaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        crispy_fields = []
        for columna in range(int(cantidad_columnas)):
            self.fields['nombre-columna-{0}'.format(columna)] = \
                forms.CharField(label="", initial='Columna{0}'.format(columna),
                                error_messages={'required': ''},
                                widget=forms.TextInput(attrs={'class':
                                                              'nombre-columna'}))
            crispy_fields.append(Field('nombre-columna-{0}'.format(columna)))
        self.helper.layout = Layout(crispy_fields)


class PrimerLineaEncabezadoForm(forms.Form):
    es_encabezado = forms.BooleanField(label="Primer fila es encabezado.",
                                       required=False)

    def __init__(self, *args, **kwargs):
        super(PrimerLineaEncabezadoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(Field('es_encabezado'))


class CamposDeBaseDeDatosForm(forms.Form):
    """ Formulario para identificar campos especiales de la base de datos """
    campos_telefonicos = forms.MultipleChoiceField(
        required=True,
        label=_('Campos de teléfono'),
        widget=forms.CheckboxSelectMultiple())
    id_externo = forms.ChoiceField(required=False,
                                   widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, nombres_campos, *args, **kwargs):
        super(CamposDeBaseDeDatosForm, self).__init__(*args, **kwargs)
        self.nombres_campos = nombres_campos
        self.fields['campos_telefonicos'].choices = tuple([(x, x) for x in nombres_campos])
        id_externo_choices = [EMPTY_CHOICE]
        id_externo_choices.extend(tuple([(x, x) for x in nombres_campos]))
        self.fields['id_externo'].choices = id_externo_choices

    def clean(self):
        campos_telefonicos = self.cleaned_data.get('campos_telefonicos', [])
        if len(campos_telefonicos) > 0:
            id_externo = self.cleaned_data.get('id_externo')
            if id_externo in campos_telefonicos:
                msg = _('No se puede elegir un campo telefónico como id_externo')
                raise forms.ValidationError(msg)
        return super(CamposDeBaseDeDatosForm, self).clean()

    @property
    def columnas_de_telefonos(self):
        # Guardo los indices de los nombres de las columnas que tienen telefonos
        seleccionados = self.cleaned_data.get('campos_telefonicos', [])
        return [i for i, x in enumerate(self.nombres_campos) if x in seleccionados]

    @property
    def columna_id_externo(self):
        # Devuelvo el indice del nombre de la columnas del id externo
        seleccionado = self.cleaned_data.get('id_externo', '')
        if seleccionado in self.nombres_campos:
            return self.nombres_campos.index(seleccionado)
        return None


class BusquedaContactoForm(forms.Form):
    buscar = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': _('texto a buscar')}
        )
    )


class ListaRapidaForm(forms.ModelForm):

    def clean_nombre(self):
        # controlamos que el nombre no tenga espacios y caracteres no ascii
        nombre = self.cleaned_data.get('nombre')
        validar_solo_alfanumericos_o_guiones(nombre)
        validar_longitud_nombre_base_de_contactos(nombre)
        return nombre

    class Meta:
        model = ListasRapidas
        fields = ('nombre', 'archivo_importacion')
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'archivo_importacion': forms.FileInput(attrs={'class': 'form-control'}),
        }


class ContactoListaRapidaForm(forms.ModelForm):
    # Campos del formulario
    nombre = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('Nombre de contacto')
            }
        )
    )

    telefono = forms.CharField(
        required=True,
        max_length=25,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('Teléfono de contacto')
            }
        )
    )

    # Fields cleanners
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not telefono.isdigit():
            msg = _("Debe ser en formato '99999999' y numérico.")
            raise forms.ValidationError(msg)
        if not is_valid_length(telefono, 3, 25):
            msg = _("Solo se permiten de 3-25 dígitos.")
            raise forms.ValidationError(msg)
        return telefono

    class Meta:
        model = ContactoListaRapida
        fields = ('nombre', 'telefono')


class CamposListaRapidaForm(forms.Form):
    """ Formulario para identificar campos especiales de la base de datos """
    campos_telefonicos = forms.MultipleChoiceField(
        required=True,
        label=_('Campos de teléfono'),
        widget=forms.CheckboxSelectMultiple())

    def __init__(self, nombres_campos, *args, **kwargs):
        super(CamposListaRapidaForm, self).__init__(*args, **kwargs)
        self.nombres_campos = nombres_campos
        self.fields['campos_telefonicos'].choices = tuple([(x, x) for x in nombres_campos])

    @property
    def columnas_de_telefonos(self):
        # Guardo los indices de los nombres de las columnas que tienen telefonos
        seleccionados = self.cleaned_data.get('campos_telefonicos', [])
        return [i for i, x in enumerate(self.nombres_campos) if x in seleccionados]


class GrabacionBusquedaFormEx(forms.Form):
    fecha = forms.CharField(label=_('Fecha'), required=True)
    tipo_llamada = forms.ChoiceField(label=_('Tipo de llamada'), required=False)
    tel_cliente = forms.CharField(label=_('Teléfono Cliente'), required=False)
    callid = forms.CharField(label=_('Call ID'), required=False)
    agente = forms.ModelChoiceField(
        label=_('Agente'),
        queryset=AgenteProfile.objects.filter(is_inactive=False),
        required=False,
    )
    campana = forms.ChoiceField(label=_('Campaña'), required=False)
    id_contacto_externo = forms.CharField(label=_('ID de contacto externo'), required=False)
    duracion = forms.IntegerField(
        help_text=_('En segundos'),
        initial=0,
        label=_('Duración mínima'),
        min_value=0,
        required=False,
    )
    marcadas = forms.BooleanField(label=_('Marcadas'), required=False)
    gestion = forms.BooleanField(label=_('Calificada como gestión'), required=False)
    grabaciones_x_pagina = forms.ChoiceField(
        choices=((10, 10), (25, 25), (50, 50), (100, 100)),
        label=_('Grabaciones por página'),
        required=True,
    )
    calificacion = forms.ChoiceField(label=_('Calificación'), required=False)
    pagina = forms.IntegerField(initial=1)

    def __init__(self, **kwargs):
        agente_hidden_widget = kwargs.pop("agente_hidden_widget", False)
        campana_choices = kwargs.pop("campana_choices", [])
        super().__init__(**kwargs)
        self.fields['fecha'].widget.attrs.update({'class': 'form-control'})
        self.fields['tipo_llamada'].choices = (EMPTY_CHOICE, *LlamadaLog.TYPE_LLAMADA_CHOICES)
        self.fields['tipo_llamada'].widget.attrs.update({'class': 'form-control'})
        self.fields['tel_cliente'].widget.attrs.update({'class': 'form-control'})
        self.fields['callid'].widget.attrs.update({'class': 'form-control'})
        if agente_hidden_widget:
            self.fields['agente'].widget = self.fields['agente'].hidden_widget()
        else:
            self.fields['agente'].widget.attrs.update({'class': 'form-control'})
        self.fields['id_contacto_externo'].widget.attrs.update({'class': 'form-control'})
        self.fields['campana'].choices = (
            ALL_CAMPAIGNS_CHOICE,
            ALL_CAMPAIGNS_ACTIVE_CHOICE,
            ALL_CAMPAIGNS_INACTIVE_CHOICE,
            *campana_choices,
        )
        self.fields['campana'].widget.attrs.update({'class': 'form-control'})
        self.fields['duracion'].widget.attrs.update({'class': 'form-control'})
        self.fields['grabaciones_x_pagina'].widget.attrs.update({'class': 'form-control'})
        self.fields['calificacion'].choices = (
            EMPTY_CHOICE,
            *[
                (nombre, nombre)
                for nombre in
                OpcionCalificacion.objects.distinct('nombre').values_list('nombre', flat=True)
            ]
        )
        self.fields['calificacion'].widget.attrs.update({'class': 'form-control'})
        self.fields['pagina'].widget = self.fields['pagina'].hidden_widget()

    def clean_agente(self):
        value = self.cleaned_data.get("agente")
        if value:
            return value.id

    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.pop("fecha").split(" - ")
        cleaned_data.update({
            "fecha_desde": fecha[0],
            "fecha_hasta": fecha[1],
        })
        return cleaned_data


class AuditoriaBusquedaForm(forms.Form):
    """Formulario para los aplicar los filtros al buscar calificaciones para auditar
    """

    AUDITORIA_PENDIENTE = 3
    AUDITORIA_PENDIENTE_CHOICE = (AUDITORIA_PENDIENTE, _('Pendiente'))

    fecha = forms.CharField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control'}),
                            label=_('Fecha'))
    agente = forms.ModelChoiceField(queryset=AgenteProfile.objects.none(),
                                    required=False, label=_('Agente'))
    campana = forms.ChoiceField(
        required=False, choices=(), label=_('Campaña'),
        widget=forms.Select(attrs={'class': 'form-control'}))
    pagina = forms.CharField(required=False, widget=forms.HiddenInput(), label=_('Página'))
    grupo_agente = forms.ChoiceField(
        required=False, choices=(), label=_('Grupo de agentes'),
        widget=forms.Select(attrs={'class': 'form-control'}))
    id_contacto_externo = forms.CharField(required=False, label=_('ID de contacto externo'),
                                          widget=forms.TextInput(attrs={'class': 'form-control'}))
    id_contacto = forms.CharField(required=False, label=_('Id del contacto'),
                                  widget=forms.NumberInput(attrs={'class': 'form-control'}))
    telefono = forms.CharField(required=False, label=_('Teléfono Cliente'),
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    callid = forms.CharField(required=False, label=_('Call ID'),
                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    status_auditoria = forms.ChoiceField(
        required=False, choices=(), label=_('Status de auditoría'),
        widget=forms.Select(attrs={'class': 'form-control'}))
    revisadas = forms.BooleanField(
        required=False, widget=forms.CheckboxInput(attrs={'class': 'form-control'}),
        label=_('Únicamente revisadas por Agente'))

    def __init__(self, *args, **kwargs):
        supervisor = kwargs.pop('supervisor')
        super(AuditoriaBusquedaForm, self).__init__(*args, **kwargs)
        # generamos las choices para el filtro de campaña
        campanas = supervisor.campanas_asignadas_actuales().values('pk', 'nombre')
        campanas_ids = [campana['pk'] for campana in campanas]
        campana_choices = [(campana['pk'], campana['nombre'])
                           for campana in campanas]
        campana_choices.insert(0, EMPTY_CHOICE)
        self.fields['campana'].choices = campana_choices
        # generamos las choices para la lista de agentes
        agentes = AgenteProfile.objects.filter(queue__campana__in=campanas_ids).distinct(
        ).select_related('user', 'grupo')
        self.fields['agente'].queryset = agentes
        # generamos las choices para el filtro de grupo de agentes
        grupo_choices = list(set([(agente.grupo.pk, agente.grupo.nombre) for agente in agentes]))
        grupo_choices.insert(0, EMPTY_CHOICE)
        self.fields['grupo_agente'].choices = grupo_choices
        # generamos choices para el filtro por resultado de auditoria
        status_auditoria_choices = AuditoriaCalificacion.RESULTADO_CHOICES
        self.fields['status_auditoria'].choices = (EMPTY_CHOICE,) + \
            (self.AUDITORIA_PENDIENTE_CHOICE,) + status_auditoria_choices


class AuditoriaCalificacionForm(forms.ModelForm):
    class Meta:
        model = AuditoriaCalificacion
        fields = ('resultado', 'revisada', 'observaciones')

    revisada = forms.BooleanField(
        disabled=True, widget=forms.CheckboxInput(attrs={'class': 'form-control'}),
        label=_('Revisada por Agente'), required=False)


class CampanaMixinForm(object):

    INTERACCION_CON_FORMULARIO = (
        (Campana.FORMULARIO, Campana.TIPO_FORMULARIO_DISPLAY),
        (Campana.FORMULARIO_Y_SITIO_EXTERNO, Campana.TIPO_FORMULARIO_Y_SITIO_EXTERNO)
    )
    INTERACCION_SITIO_EXTERNO = (
        (Campana.SITIO_EXTERNO, Campana.TIPO_SITIO_EXTERNO_DISPLAY),
    )

    ERROR_WHATSAPP_DESTINO = _("Debe mantener la canalidad Whatsapp habilitada ya que la "
                               "campaña es destino de las siguientes Lineas de Whatsapp: {0}")

    def __init__(self, *args, **kwargs):
        super(CampanaMixinForm, self).__init__(*args, **kwargs)
        self.fields['bd_contacto'].required = not self.initial.get('es_template', False)
        if self.fields.get('bd_contacto', False):
            self.fields['bd_contacto'].queryset = BaseDatosContacto.objects.obtener_definidas()
        instance = getattr(self, 'instance', None)
        if instance.pk is not None:
            if instance.tipo_interaccion == Campana.SITIO_EXTERNO:
                self.fields['tipo_interaccion'].disabled = True
                self.fields['tipo_interaccion'].required = False
                self.fields['tipo_interaccion'].choices = self.INTERACCION_SITIO_EXTERNO
            else:
                self.fields['tipo_interaccion'].choices = self.INTERACCION_CON_FORMULARIO

    def requiere_bd_contacto(self):
        raise NotImplementedError()

    def clean(self):
        bd_contacto_field = self.fields.get('bd_contacto', False)
        sistema_externo = self.cleaned_data.get('sistema_externo', False)
        bd_contacto = self.cleaned_data.get('bd_contacto', False)
        if sistema_externo and bd_contacto \
                and bd_contacto.get_metadata().columna_id_externo is None:
            message = _("Una campaña asignada a un sistema externo debe usar una"
                        " base de contactos con campo de id externo definido")
            raise forms.ValidationError(message, code='invalid')
        if (bd_contacto_field and not bd_contacto_field.queryset.filter and
                self.requiere_bd_contacto()):
            message = _("Debe cargar una base de datos antes de comenzar a "
                        "configurar una campana")
            self.add_error('bd_contacto', message)
            raise forms.ValidationError(message, code='invalid')
        if self.cleaned_data.get('tipo_interaccion') in \
            [Campana.SITIO_EXTERNO, Campana.FORMULARIO_Y_SITIO_EXTERNO] and \
                not self.cleaned_data.get('sitio_externo'):
            message = _("Debe seleccionar un sitio externo")
            raise forms.ValidationError(message, code='invalid')
        return super(CampanaMixinForm, self).clean()

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        validar_nombres_campanas(nombre)
        return nombre

    def clean_sitio_externo(self):
        sitio_externo = self.cleaned_data.get('sitio_externo')
        tipo_interaccion = self.cleaned_data.get('tipo_interaccion')
        if tipo_interaccion == Campana.FORMULARIO and sitio_externo is not None:
            msg = _('No se puede elegir un URL externo si selecciono un formulario.')
            raise forms.ValidationError(msg)
        if tipo_interaccion == Campana.FORMULARIO_Y_SITIO_EXTERNO and sitio_externo and \
                sitio_externo.objetivo == SitioExterno.EMBEBIDO and \
                sitio_externo.disparador != SitioExterno.CALIFICACION:
            msg = _('Para este tipo de interacción no puede elegir un sitio \
                externo con "Objetivo" embebido')
            raise forms.ValidationError(msg)

        return sitio_externo

    def clean_id_externo(self):
        sistema_externo = self.cleaned_data.get('sistema_externo', None)
        id_externo = self.cleaned_data.get('id_externo', '')
        if sistema_externo and id_externo:
            # Validar que no este repetido
            campana_con_id_externo = sistema_externo.campanas.filter(id_externo=id_externo)
            if self.instance.id:
                campana_con_id_externo = campana_con_id_externo.exclude(id=self.instance.id)
            if campana_con_id_externo.exists():
                msg = _("Ya existe una Campaña con ese id externo para el Sistema Externo elegido")
                raise forms.ValidationError(msg)
        if id_externo and not sistema_externo:
            msg = _("No puede indicar un id externo sin elegir un Sistema Externo")
            raise forms.ValidationError(msg)
        return id_externo

    def clean_outcid(self):
        ruta_saliente = self.cleaned_data.get('outr')
        id_ruta_saliente = self.cleaned_data.get('outcid')
        if ruta_saliente and not id_ruta_saliente:
            msg = _("No se puede indicar una Ruta Saliente sin un CID de Ruta Saliente.")
            raise forms.ValidationError(msg)
        return id_ruta_saliente

    def clean_whatsapp_habilitado(self):
        instance = getattr(self, 'instance', None)
        whatsapp_habilitado = self.cleaned_data.get('whatsapp_habilitado')
        if instance is not None:
            if instance.whatsapp_habilitado and not self.cleaned_data.get('whatsapp_habilitado'):
                lineas_antecesoras = []
                try:
                    nodo = DestinoEntrante.get_nodo_ruta_entrante(instance)
                    lineas_antecesoras = nodo.lineas_whatsapp_antecesoras()
                except Exception:
                    pass
                if lineas_antecesoras:
                    nombres_lineas = lineas_antecesoras.values_list('nombre', flat=True)
                    nombres_lineas = ', '.join(nombres_lineas)
                    msg = self.ERROR_WHATSAPP_DESTINO.format(nombres_lineas)
                    raise forms.ValidationError(msg)
                ConfiguracionWhatsappCampana.objects.filter(
                    is_active=True, campana=instance).update(is_active=False)
        return whatsapp_habilitado


class CampanaEntranteForm(CampanaMixinForm, forms.ModelForm):

    campo_direccion_choice = forms.CharField(
        required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    telefono_habilitado = forms.BooleanField(required=False, disabled=True)
    video_habilitado = forms.BooleanField(required=False, disabled=True)

    def __init__(self, *args, **kwargs):
        super(CampanaEntranteForm, self).__init__(*args, **kwargs)
        self.fields['outr'].queryset = RutaSaliente.objects.all()
        instance = getattr(self, 'instance', None)
        if instance.pk is None:
            self.fields['bd_contacto'].required = False
        else:
            self.fields['nombre'].disabled = True
            self.fields['bd_contacto'].required = True

    def requiere_bd_contacto(self):
        return False

    def clean_bd_contacto(self):
        bd_contacto = self.cleaned_data.get('bd_contacto')
        bd_contacto_field = 'bd_contacto'
        if self.instance.pk and bd_contacto_field in self.changed_data:
            campana_service = CampanaService()
            error = campana_service.validar_modificacion_bd_contacto(
                self.instance, bd_contacto)
            if error:
                raise forms.ValidationError(
                    _("Los nombres de las columnas de la nueva base de datos no coinciden"
                      " con la anterior"),
                    code='invalid')
        return bd_contacto

    class Meta:
        model = Campana
        fields = ('nombre', 'bd_contacto', 'campo_direccion', 'sistema_externo', 'id_externo',
                  'tipo_interaccion', 'sitio_externo', 'objetivo', 'mostrar_nombre',
                  'mostrar_did', 'mostrar_nombre_ruta_entrante', 'outcid', 'outr',
                  'videocall_habilitada', 'whatsapp_habilitado', 'speech', 'control_de_duplicados')
        labels = {
            'bd_contacto': 'Base de Datos de Contactos',
        }

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'bd_contacto': forms.Select(attrs={'class': 'form-control', 'id': 'camp_bd_contactos'}),
            'control_de_duplicados': forms.Select(attrs={'class': 'form-control'}),
            'campo_direccion': forms.Select(attrs={'class': 'form-control'}),
            'sistema_externo': forms.Select(attrs={'class': 'form-control'}),
            'id_externo': forms.TextInput(attrs={'class': 'form-control'}),
            'sitio_externo': forms.Select(attrs={'class': 'form-control'}),
            'objetivo': forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo_interaccion': forms.RadioSelect(),
            'outcid': forms.TextInput(attrs={'class': 'form-control'}),
            'outr': forms.Select(attrs={'class': 'form-control'}),
            'speech': forms.Textarea(attrs={'class': 'form-control'})
        }


class OpcionCalificacionForm(forms.ModelForm):
    nombre_subcalificaciones = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = OpcionCalificacion
        fields = (
            'tipo', 'nombre', 'subcalificaciones', 'formulario', 'campana', 'oculta', 'positiva',
            'interaccion_crm', 'nombre_subcalificaciones')

        widgets = {
            'nombre': forms.Select(),
            'usada_en_calificacion': forms.HiddenInput(),
            'subcalificaciones': forms.TextInput(attrs={'readonly': 'readonly'})
        }

    def __init__(self, *args, **kwargs):
        nombres_calificaciones = kwargs.pop('nombres_calificaciones')
        nombre_subcalificaciones = kwargs.pop('nombre_subcalificaciones')
        con_formulario = kwargs.pop('con_formulario')
        con_crm_calificacion = kwargs.pop('con_crm_calificacion') \
            if 'con_crm_calificacion' in kwargs else None
        super(OpcionCalificacionForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            choices = set(nombres_calificaciones + ((instance.nombre, instance.nombre),))
        else:
            choices = (EMPTY_CHOICE,) + nombres_calificaciones
        self.fields['nombre_subcalificaciones'].initial = nombre_subcalificaciones
        self.fields['nombre'] = forms.ChoiceField(choices=choices)
        if instance and instance.pk and instance.no_editable():
            self.fields['nombre'].disabled = True
            self.fields['tipo'].disabled = True
            self.fields['formulario'].disabled = True
        else:
            self.fields['tipo'].choices = OpcionCalificacion.FORMULARIO_CHOICES_NO_AGENDA

        if not con_formulario:
            self.fields.pop('formulario')

        if not con_crm_calificacion:
            self.fields.pop('interaccion_crm')

    def clean_nombre(self):
        instance = getattr(self, 'instance', None)
        if instance.pk is None and instance.nombre == settings.CALIFICACION_REAGENDA:
            raise forms.ValidationError(
                _("El nombre de la opción de calificación '{0}' está reservado para uso interno"
                  " del sistema, por favor use otro".format(instance.nombre)))
        if instance and instance.pk and instance.no_editable():
            return instance.nombre
        else:
            return self.cleaned_data['nombre']

    def clean_tipo(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk and instance.no_editable():
            return instance.tipo
        else:
            return self.cleaned_data['tipo']

    def clean_formulario(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk and instance.no_editable():
            return instance.formulario
        else:
            tipo = self.cleaned_data.get('tipo', None)
            if tipo == OpcionCalificacion.GESTION:
                # TODO: Solo si se eligio tipo_interaccion Formulario!!!
                formulario = self.cleaned_data.get('formulario', None)
                if not formulario:
                    raise forms.ValidationError(_("Debe elegir un formulario para la gestión."))
                return formulario
            return None


class OpcionCalificacionBaseFormset(BaseInlineFormSet):

    def _construct_form(self, index, **kwargs):
        # adicionamos dinámicamente las nombres de calificaciones existentes en el sistema
        # para que el usuario pueda escoger de ellas al crear las opciones de calificación
        nombres_calificaciones_qs = NombreCalificacion.objects.usuarios().values_list(
            'nombre', 'subcalificaciones')
        kwargs['nombres_calificaciones'] = tuple(
            (nombre, nombre) for nombre, subcalificaciones in nombres_calificaciones_qs)
        kwargs['nombre_subcalificaciones'] = list(
            {nombre: subcalificaciones} for nombre, subcalificaciones in nombres_calificaciones_qs)
        return super(OpcionCalificacionBaseFormset, self)._construct_form(index, **kwargs)

    def _validar_numero_opciones_calificacion(self, save_candidates_forms):

        # en el caso de la modificación vamos a tener un form más que en la creación por la
        # creación automática de la calificación reservada de Agenda
        MIN_NUM_FORMS = int(self.instance.pk is not None) + 1
        if MIN_NUM_FORMS == 1:
            msg = _("Debe ingresar al menos {0} opción de calificación".format(MIN_NUM_FORMS))
        else:
            # MIN_NUM_FORMS == 2
            msg = _("Debe ingresar al menos {0} opciones de calificación".format(MIN_NUM_FORMS))

        if len(save_candidates_forms) < MIN_NUM_FORMS:
            raise forms.ValidationError(msg, code='invalid')

    def clean(self):
        """
        Realiza los validaciones relacionadas con la semántica de las opciones de calificación
        """
        if any(self.errors):
            return
        nombres = []
        tipos_gestion_cont = 0
        deleted_forms = self.deleted_forms
        save_candidates_forms = set(self.forms) - set(deleted_forms)

        self._validar_numero_opciones_calificacion(save_candidates_forms)

        for form in save_candidates_forms:
            nombre = form.cleaned_data.get('nombre', None)
            tipo = form.cleaned_data.get('tipo', None)
            oculta = form.cleaned_data.get('oculta')
            if nombre is None or tipo is None:
                raise forms.ValidationError(_("Rellene los campos en blanco"), code='invalid')
            if nombre in nombres:
                raise forms.ValidationError(
                    _("Los nombres de las opciones de calificación deben ser distintos"),
                    code="invalid")
            if tipo == OpcionCalificacion.GESTION and not oculta:
                tipos_gestion_cont += 1
            nombres.append(nombre)
        if tipos_gestion_cont == 0:
            raise forms.ValidationError(
                _("Debe escoger una opción de calificación de tipo gestión por campaña"),
                code='invalid')

    def save(self):
        """
        Inserta la una opción de calificación interna del sistema para agendar contactos
        """
        campana = self.instance
        if campana.estado != Campana.ESTADO_TEMPLATE_ACTIVO:
            campana.gestionar_opcion_calificacion_agenda()
        super(OpcionCalificacionBaseFormset, self).save()


OpcionCalificacionFormSet = inlineformset_factory(
    Campana, OpcionCalificacion, form=OpcionCalificacionForm,
    formset=OpcionCalificacionBaseFormset, extra=0, min_num=1)


class OpcionCalificacionModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.nombre


class CalificacionClienteForm(forms.ModelForm):
    """
    Formulario para la creacion de Calificaciones de Clientes
    """
    opcion_calificacion = OpcionCalificacionModelChoiceField(
        OpcionCalificacion.objects.all(), empty_label='---------', label=_('Calificación'))
    nombre_subcalificaciones = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = CalificacionCliente
        fields = ('opcion_calificacion', 'subcalificacion',
                  'observaciones', 'nombre_subcalificaciones')
        widgets = {
            'opcion_calificacion': forms.Select(attrs={'class': 'form-control'}),
            'subcalificacion': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'observaciones': _('Observaciones'),
        }

    def __init__(self, campana, es_auditoria, *args, **kwargs):

        historico_calificaciones = kwargs.pop('historico_calificaciones')
        super(CalificacionClienteForm, self).__init__(*args, **kwargs)
        self.campana = campana
        self.es_auditoria = es_auditoria
        self.historico_calificaciones = historico_calificaciones

        filtro = Q(oculta=False)
        if 'opcion_calificacion' in self.data and self.data['opcion_calificacion']:
            subcalificaciones = campana.opciones_calificacion.get(
                id=self.data['opcion_calificacion']).subcalificaciones
            if subcalificaciones:
                choices = (EMPTY_CHOICE,) + tuple((nombre, nombre) for nombre in subcalificaciones)
                self.fields['subcalificacion'] = forms.ChoiceField(
                    choices=choices, required=True,
                    widget=forms.Select(attrs={'class': 'form-control'}))
        elif self.instance.pk:
            if self.instance.opcion_calificacion.oculta:
                filtro = filtro | Q(id=self.instance.opcion_calificacion.id)
            if self.instance.opcion_calificacion.subcalificaciones:
                choices = (EMPTY_CHOICE,) + tuple(
                    (nombre, nombre) for nombre in
                    self.instance.opcion_calificacion.subcalificaciones)
                self.fields['subcalificacion'] = forms.ChoiceField(
                    choices=choices, required=False,
                    widget=forms.Select(attrs={'class': 'form-control'}))
        self.fields['opcion_calificacion'].queryset = campana.opciones_calificacion.filter(filtro)
        self.fields['nombre_subcalificaciones'].initial = list(
            campana.opciones_calificacion.values("id", "subcalificaciones"))

    def clean_opcion_calificacion(self):
        opcion = self.cleaned_data.get('opcion_calificacion')
        if self.es_auditoria:
            if 'opcion_calificacion' in self.changed_data and opcion.es_agenda():
                raise forms.ValidationError(
                    _('Sólo el Agente puede cambiar la calificacion a Agenda.'))
        else:
            if 'opcion_calificacion' in self.changed_data and opcion.oculta:
                raise forms.ValidationError(
                    _('No puede elegir una opción de calificacion oculta.'))
        return opcion


class GrupoAgenteForm(forms.Form):
    grupo = forms.ChoiceField(choices=(), widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(GrupoAgenteForm, self).__init__(*args, **kwargs)
        grupo_choice = [(grupo.id, grupo.nombre)
                        for grupo in Grupo.objects.all()]
        self.fields['grupo'].choices = grupo_choice


class AgendaBusquedaForm(forms.Form):
    """
    El busquedad form poara agente
    """
    fecha = forms.CharField(required=False,
                            widget=forms.TextInput(
                                attrs={'class': 'form-control'}))


class ReporteCampanaForm(forms.Form):
    """
    El form para reporte con fecha
    """
    fecha = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    pagina = forms.CharField(required=False, widget=forms.HiddenInput(), label=_('Página'))
    calificaciones_x_pagina = forms.ChoiceField(
        required=False,
        choices=([(5, 5), (10, 10), (25, 25), (50, 50), (100, 100)]),
        label=_('Calificaciones por página'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class ReporteForm(forms.Form):
    """
    El form para reporte con fecha
    """
    TODOS_RESULTADOS = '-1'
    fecha = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    resultado_auditoria = forms.ChoiceField(
        label=_('Auditoria'), widget=forms.Select(attrs={'class': 'form-control'}),
        choices=((TODOS_RESULTADOS, _('Todas')), ) + AuditoriaCalificacion.RESULTADO_CHOICES)


class FormularioCRMForm(forms.Form):

    def __init__(self, campos, *args, **kwargs):
        super(FormularioCRMForm, self).__init__(*args, **kwargs)

        for campo in campos:
            if campo.tipo is FieldFormulario.TIPO_TEXTO:
                self.fields[campo.nombre_campo] = forms.CharField(
                    label=campo.nombre_campo, widget=forms.TextInput(
                        attrs={'class': 'form-control'}),
                    required=campo.is_required)
            elif campo.tipo is FieldFormulario.TIPO_FECHA:
                self.fields[campo.nombre_campo] = forms.CharField(
                    label=campo.nombre_campo, widget=forms.TextInput(
                        attrs={'class': 'class-fecha form-control'}),
                    required=campo.is_required)
            elif campo.tipo is FieldFormulario.TIPO_LISTA:
                choices = [(option, option)
                           for option in json.loads(campo.values_select)]
                self.fields[campo.nombre_campo] = forms.ChoiceField(
                    choices=choices,
                    label=campo.nombre_campo, widget=forms.Select(
                        attrs={'class': 'form-control'}),
                    required=campo.is_required)
            elif campo.tipo is FieldFormulario.TIPO_TEXTO_AREA:
                self.fields[campo.nombre_campo] = forms.CharField(
                    label=campo.nombre_campo, widget=forms.Textarea(
                        attrs={'class': 'form-control'}),
                    required=campo.is_required)
            elif campo.tipo is FieldFormulario.TIPO_NUMERO:
                self.fields[campo.nombre_campo] = forms.CharField(
                    label=campo.nombre_campo, widget=forms.TextInput(
                        attrs={'class': 'form-control'}),
                    required=campo.is_required)


class SincronizaDialerForm(forms.Form):
    evitar_duplicados = forms.BooleanField(required=False)
    evitar_sin_telefono = forms.BooleanField(required=False)
    prefijo_discador = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'class-fecha form-control'}))


class FormularioNuevoContacto(forms.ModelForm):
    confirmar_duplicado = forms.BooleanField(initial=False, required=False,
                                             widget=forms.HiddenInput)

    class Meta:
        model = Contacto
        fields = ('telefono', 'id_externo', 'confirmar_duplicado')
        widgets = {
            "telefono": forms.TextInput(attrs={'class': 'form-control'}),
            "id_externo": forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, base_datos=None, campos_bloqueados=[], campos_ocultos=[],
                 campos_obligatorios=[],
                 control_de_duplicados=None, *args, **kwargs):
        campos_a_bloquear = []  # Son los campos a bloquear para la edicion.
        campos_a_ocultar = campos_ocultos  # Son los campos a bloquear para la edicion Y creación.
        self.campos_a_bloquear = campos_a_bloquear
        self.campos_a_ocultar = campos_a_ocultar
        self.control_de_duplicados = control_de_duplicados
        self.es_campana_entrante = kwargs.pop('es_campana_entrante', False)

        if 'instance' in kwargs and kwargs['instance'] is not None:
            campos_a_bloquear = campos_bloqueados
            contacto = kwargs['instance']
            self.base_datos = contacto.bd_contacto
            bd_metadata = contacto.bd_contacto.get_metadata()
            datos = json.loads(contacto.datos)
            for nombre, dato in zip(bd_metadata.nombres_de_columnas_de_datos, datos):
                if nombre not in kwargs['initial']:
                    kwargs['initial'].update({self.get_nombre_input(nombre): dato})
        else:
            self.base_datos = base_datos
            bd_metadata = base_datos.get_metadata()

        super(FormularioNuevoContacto, self).__init__(*args, **kwargs)
        if self.es_campana_entrante:
            self.fields['telefono'].required = False
        nombre_campo_telefono = bd_metadata.nombre_campo_telefono
        nombre_campo_id_externo = bd_metadata.nombre_campo_id_externo
        for campo in bd_metadata.nombres_de_columnas:
            bloquear_campo = campo in campos_a_bloquear
            ocultar_campo = campo in campos_a_ocultar
            campo_obligatorio = campo in campos_obligatorios
            if campo == nombre_campo_telefono:
                if ocultar_campo:
                    self.fields.pop('telefono')
                else:
                    nombre_campo = convertir_ascii_string(campo)
                    self.fields['telefono'].label = nombre_campo
                    if bloquear_campo:
                        self.fields['telefono'].disabled = True
            elif campo == nombre_campo_id_externo:
                if ocultar_campo:
                    self.fields.pop('id_externo')
                else:
                    nombre_campo = convertir_ascii_string(campo)
                    self.fields['id_externo'].label = nombre_campo
                    self.fields['id_externo'].required = False
                    if bloquear_campo:
                        self.fields['id_externo'].disabled = True
            elif not ocultar_campo:
                nombre_campo = self.get_nombre_input(campo)
                self.fields[nombre_campo] = forms.CharField(
                    required=False,
                    label=campo, widget=forms.TextInput(
                        attrs={'class': 'form-control'}))
                if bloquear_campo:
                    self.fields[nombre_campo].disabled = True
            if campo_obligatorio:
                self.fields[nombre_campo].required = True

        if nombre_campo_id_externo is None:
            self.fields.pop('id_externo')

        self.bd_metadata = bd_metadata

        self.msg_consfirmacion_duplicado = \
            _('Ya existe un contacto con el mismo teléfono. Desea continuar?')
        if any(e == self.msg_consfirmacion_duplicado for e in self.errors.get('__all__', [])):
            self.fields['confirmar_duplicado'].widget = forms.CheckboxInput()

    @classmethod
    def get_nombre_input(cls, nombre_campo):
        """
        Además del Encode modifico el nombre del input correspondiente a un campo de datos
        de nombre "telefono" para que no se solape con el input 'telefono' correspondiente al campo
        del modelo Contacto
        """
        nombre_input = convertir_ascii_string(nombre_campo)
        if nombre_input == 'telefono':
            # NOTA: Se asume que ninguna base de datos vendra con un campo con el nombre devuelto
            return "input_telefono_en_datos_OML"
        return nombre_input

    def get_datos_json(self):
        """ Devuelve datos en json listos para guardar en el modelo Contacto """
        datos = []
        for nombre in self.bd_metadata.nombres_de_columnas_de_datos:
            campo = self.cleaned_data.get(self.get_nombre_input(nombre), '')
            if campo == '' and nombre in self.campos_a_ocultar and self.instance.pk is not None:
                # los campos a ocultar se guardan mantienen su valor de BD en el
                # caso de que se les quiera ocultar al usuario en edicion
                datos_contacto_dict = self.instance.obtener_datos()
                campo = datos_contacto_dict.get(self.get_nombre_input(nombre), '')
            datos.append(campo)

        return json.dumps(datos)

    def es_campo_telefonico(self, nombre_input):
        """ Devuelve si el nombre del input corresponde a una columna con telefono o no """
        for i in self.bd_metadata.columnas_con_telefono:
            nombre_campo = self.bd_metadata.nombres_de_columnas[i]
            if nombre_input == self.get_nombre_input(nombre_campo):
                return True
        return False

    def clean_telefono(self):
        telefono = str(self.cleaned_data.get('telefono'))
        if telefono and not telefono.isdigit():
            msg = _('Debe ser en formato "999999999" y solo numérico.')
            raise forms.ValidationError(msg)
        if telefono and not 3 <= len(telefono) <= 20:
            msg = _('Solo se permiten de 3-20 dígitos.')
            raise forms.ValidationError(msg)
        return telefono

    def clean_id_externo(self):
        id_externo = self.cleaned_data.get('id_externo')
        # Si el campo no esta vacío
        if not id_externo == '' and id_externo is not None:
            # Validar que no este repetido
            contacto_con_id_externo = self.base_datos.contactos.filter(id_externo=id_externo)
            if self.instance.id:
                contacto_con_id_externo = contacto_con_id_externo.exclude(id=self.instance.id)
            if contacto_con_id_externo.exists():
                msg = _("Ya existe un contacto con ese id externo en la base de datos")
                raise forms.ValidationError(msg)
        return id_externo

    def clean(self):
        if not self.instance.id:
            self.instance.bd_contacto = self.base_datos
        self.validate_phone_fields()
        self.validate_duplicate_phone_field()
        return super(FormularioNuevoContacto, self).clean()

    def validate_duplicate_phone_field(self):
        if all((key in self.cleaned_data for key in ['telefono', 'confirmar_duplicado'])):
            telefono = self.cleaned_data.get('telefono')
            if telefono in self.base_datos.contactos.all().values_list('telefono', flat=True) and \
                    self.instance.telefono != telefono:
                if self.control_de_duplicados == Campana.EVITAR_DUPLICADOS:
                    msg = _('Ya existe un contacto con el mismo teléfono.')
                    raise forms.ValidationError(msg)
                else:
                    # Si el control de duplicados es permitir duplicados,
                    # se debe permitir que se guarde el contacto con el mismo telefono
                    # si se confirma por el usuario.
                    if not self.cleaned_data.get('confirmar_duplicado'):
                        raise forms.ValidationError(self.msg_consfirmacion_duplicado)
            return True
        return False

    def validate_phone_fields(self):
        db_metadata = self.base_datos.get_metadata()
        for field_phone in db_metadata.nombres_de_columnas_de_telefonos[1:]:
            self.validate_field(field_phone)

    def validate_field(self, field_name):
        if field_name in self.campos_a_bloquear:
            return
        if field_name in self.campos_a_ocultar:
            return
        field = str(self.cleaned_data.get(field_name))
        if field:
            if not field.isdigit():
                msg = _('Debe ser en formato "999999999" y solo numérico.')
                self.add_error(field_name, forms.ValidationError(msg))
            if not 3 <= len(field) <= 20:
                msg = _('Solo se permiten de 3-20 dígitos.')
                self.add_error(field_name, forms.ValidationError(msg))


class BloquearCamposParaAgenteForm(forms.Form):

    PREFIJO_BLOQUEAR = 'bloquear_'
    PREFIJO_OCULTAR = 'ocultar_'
    PREFIJO_OBLIGATORIO = 'obligatorio_'

    def __init__(self, campos, campo_telefono, lang, *args, **kwargs):
        super(BloquearCamposParaAgenteForm, self).__init__(*args, **kwargs)
        for campo in campos:
            self.fields['bloquear_' + campo] = forms.BooleanField(
                required=False, label=lang['bloquear'].format(campo),
                widget=forms.CheckboxInput(attrs={'class': 'form-control'}))
            if campo != campo_telefono:
                self.fields['ocultar_' + campo] = forms.BooleanField(
                    required=False, label=lang['ocultar'].format(campo),
                    widget=forms.CheckboxInput(attrs={'class': 'form-control'}))
            if campo != campo_telefono:
                self.fields['obligatorio_' + campo] = forms.BooleanField(
                    required=False, label=lang['obligatorio'].format(campo),
                    widget=forms.CheckboxInput(attrs={'class': 'form-control'}))

    def clean(self):
        bloqueados = set()
        ocultos = set()
        obligatorios = set()
        for nombre, seleccionado in self.cleaned_data.items():
            if nombre.startswith(self.PREFIJO_BLOQUEAR) and seleccionado:
                bloqueados.add(nombre[9:])
            if nombre.startswith(self.PREFIJO_OCULTAR) and seleccionado:
                ocultos.add(nombre[8:])
            if nombre.startswith(self.PREFIJO_OBLIGATORIO) and seleccionado:
                obligatorios.add(nombre[12:])

        if not ocultos.issubset(bloqueados):
            msg = _('Todos los campos ocultos deben marcarse como bloqueados')
            raise forms.ValidationError(msg)
        if obligatorios.intersection(bloqueados):
            msg = _('Los campos obligatorios no pueden estar bloqueados')
            raise forms.ValidationError(msg)

        self.lista_campos_bloqueados = list(bloqueados)
        self.lista_campos_ocultos = list(ocultos)
        self.lista_campos_obligatorios = list(obligatorios)

        if self.lista_campos_bloqueados:
            str_a_persistir = json.dumps(self.lista_campos_bloqueados, separators=(',', ':'))
            # Verifico que no se pase del limite de caracteres del campo
            if len(str_a_persistir) > 2052:
                raise forms.ValidationError(_('Demasiados campos bloqueados seleccionados.'))
        if self.lista_campos_obligatorios:
            str_a_persistir = json.dumps(self.lista_campos_obligatorios, separators=(',', ':'))
            # Verifico que no se pase del limite de caracteres del campo
            if len(str_a_persistir) > 2052:
                raise forms.ValidationError(_('Demasiados campos obligatorios seleccionados.'))
        return super(BloquearCamposParaAgenteForm, self).clean()


class FormularioCampanaContacto(forms.Form):
    campana = forms.ChoiceField(
        choices=(), widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, campana_choice, *args, **kwargs):
        super(FormularioCampanaContacto, self).__init__(*args, **kwargs)
        self.fields['campana'].choices = campana_choice


class UpdateBaseDatosForm(forms.ModelForm):
    evitar_duplicados = forms.BooleanField(required=False)
    evitar_sin_telefono = forms.BooleanField(required=False)
    prefijo_discador = forms.CharField(required=False)
    telefonos = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=(),
    )

    def __init__(self, tts_choices, *args, **kwargs):
        super(UpdateBaseDatosForm, self).__init__(*args, **kwargs)
        self.fields['telefonos'].choices = tts_choices

    class Meta:
        model = Campana
        fields = ('bd_contacto',)
        labels = {
            'bd_contacto': 'Base de Datos de Contactos',
        }
        widgets = {
            'bd_contacto': forms.Select(attrs={'class': 'form-control'}),
        }


FormularioCalificacionFormSet = inlineformset_factory(
    Contacto, CalificacionCliente, form=CalificacionClienteForm,
    can_delete=False, extra=1, max_num=1)


class RespuestaFormularioGestionForm(forms.ModelForm):

    def __init__(self, campos, *args, **kwargs):
        super(RespuestaFormularioGestionForm, self).__init__(*args, **kwargs)

        for campo in campos:
            if campo.tipo is FieldFormulario.TIPO_TEXTO:
                self.fields[campo.nombre_campo] = forms.CharField(
                    label=campo.nombre_campo, widget=forms.TextInput(
                        attrs={'class': 'form-control'}),
                    required=campo.is_required)
            elif campo.tipo is FieldFormulario.TIPO_FECHA:
                self.fields[campo.nombre_campo] = forms.CharField(
                    label=campo.nombre_campo, widget=forms.TextInput(
                        attrs={'class': 'class-fecha form-control'}),
                    required=campo.is_required)
            elif campo.tipo is FieldFormulario.TIPO_LISTA:
                choices = (EMPTY_CHOICE,) + tuple((option, option)
                                                  for option in json.loads(campo.values_select))
                self.fields[campo.nombre_campo] = forms.ChoiceField(
                    choices=choices,
                    label=campo.nombre_campo, widget=forms.Select(
                        attrs={'class': 'form-control'}),
                    required=campo.is_required)
            elif campo.tipo is FieldFormulario.TIPO_TEXTO_AREA:
                self.fields[campo.nombre_campo] = forms.CharField(
                    label=campo.nombre_campo, widget=forms.Textarea(
                        attrs={'class': 'form-control'}),
                    required=campo.is_required)
            elif campo.tipo is FieldFormulario.TIPO_NUMERO and \
                    campo.tipo_numero is FieldFormulario.TIPO_ENTERO:
                self.fields[campo.nombre_campo] = forms.IntegerField(
                    label=campo.nombre_campo, min_value=0,
                    widget=forms.NumberInput(attrs={'class': 'form-control'}),
                    required=campo.is_required)
            elif campo.tipo is FieldFormulario.TIPO_NUMERO and \
                    campo.tipo_numero is FieldFormulario.TIPO_DECIMAL:
                self.fields[campo.nombre_campo] = forms.DecimalField(
                    label=campo.nombre_campo, min_value=0,
                    decimal_places=campo.cifras_significativas,
                    widget=forms.NumberInput(attrs={'class': 'form-control'}),
                    required=campo.is_required)
            elif campo.tipo is FieldFormulario.TIPO_LISTA_DINAMICA:
                servicio = InteraccionConSistemaExterno()
                respuesta_sitio_externo = servicio.obtener_lista_dinamica(campo.sitio_externo)
                choices = (EMPTY_CHOICE,) + tuple((option, option)
                                                  for option in respuesta_sitio_externo)
                self.fields[campo.nombre_campo] = forms.ChoiceField(
                    choices=choices,
                    label=campo.nombre_campo, widget=forms.Select(
                        attrs={'class': 'form-control'}),
                    required=campo.is_required)

    class Meta:
        model = RespuestaFormularioGestion
        fields = ('calificacion', )
        widgets = {
            'calificacion': forms.HiddenInput(),
        }


class AgendaContactoForm(forms.ModelForm):
    telefono = forms.ChoiceField(
        choices=(), widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = AgendaContacto
        fields = ('contacto', 'agente', 'campana', 'fecha', 'hora', 'observaciones',
                  'tipo_agenda', 'telefono')
        widgets = {
            'contacto': forms.HiddenInput(),
            'agente': forms.HiddenInput(),
            'campana': forms.HiddenInput(),
            'tipo_agenda': forms.Select(attrs={'class': 'form-control'}),
            "observaciones": forms.Textarea(attrs={'class': 'form-control'}),
            "fecha": forms.TextInput(attrs={'class': 'form-control'}),
            "hora": forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(AgendaContactoForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            campana = self.instance.campana
            contacto = self.instance.contacto
        else:
            campana = kwargs['initial']['campana']
            contacto = kwargs['initial']['contacto']
        self.fields['telefono'].choices = [
            (x, x) for x in contacto.lista_de_telefonos_de_contacto()]
        if not campana.type == Campana.TYPE_DIALER:
            self.fields['tipo_agenda'].choices = [(AgendaContacto.TYPE_PERSONAL, 'PERSONAL')]

    def clean_tipo_agenda(self):
        campana = self.cleaned_data.get('campana', None)
        if not campana and campana.type == Campana.TYPE_DIALER:
            return AgendaContacto.TYPE_PERSONAL
        return self.cleaned_data['tipo_agenda']


class CampanaDialerForm(CampanaMixinForm, forms.ModelForm):

    campo_direccion_choice = forms.CharField(
        required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    telefono_habilitado = forms.BooleanField(required=False, disabled=True)
    video_habilitado = forms.BooleanField(required=False, disabled=True)

    def __init__(self, *args, **kwargs):
        super(CampanaDialerForm, self).__init__(*args, **kwargs)

        es_template = self.initial.get('es_template', False)

        self.fields['fecha_inicio'].help_text = 'Ejemplo: 10/04/2014'
        self.fields['fecha_fin'].help_text = 'Ejemplo: 20/04/2014'
        self.fields['fecha_inicio'].required = not es_template
        self.fields['fecha_fin'].required = not es_template
        self.fields['outr'].queryset = RutaSaliente.objects.all()
        if self.instance.pk:
            self.fields['nombre'].disabled = not es_template
            self.fields['bd_contacto'].disabled = True

    def requiere_bd_contacto(self):
        return True

    def clean_bd_contacto(self):
        bd_contacto = self.cleaned_data['bd_contacto']
        instance = getattr(self, 'instance', None)
        es_template = self.initial.get('es_template', False)
        # Si uno desea modificar una campaña dialer, con instance no se permitira cambiar la BD
        if instance and instance.pk:
            return instance.bd_contacto
        if not es_template and not bd_contacto.contactos.exists():
            raise forms.ValidationError(_('No puede seleccionar una BD vacia'))
        return self.cleaned_data['bd_contacto']

    class Meta:
        model = Campana
        fields = ('nombre', 'fecha_inicio', 'fecha_fin', 'control_de_duplicados',
                  'bd_contacto', 'campo_direccion', 'sistema_externo', 'id_externo',
                  'tipo_interaccion', 'sitio_externo', 'objetivo', 'mostrar_nombre',
                  'outcid', 'outr', 'speech', 'prioridad', 'whatsapp_habilitado')
        labels = {
            'bd_contacto': 'Base de Datos de Contactos',
        }

        help_texts = {
            'prioridad': _('Valor entre 1 y 100'),
        }

        widgets = {
            'bd_contacto': forms.Select(attrs={'class': 'form-control', 'id': 'camp_bd_contactos'}),
            'control_de_duplicados': forms.Select(attrs={'class': 'form-control'}),
            'campo_direccion': forms.Select(attrs={'class': 'form-control'}),
            'sistema_externo': forms.Select(attrs={'class': 'form-control'}),
            'id_externo': forms.TextInput(attrs={'class': 'form-control'}),
            'sitio_externo': forms.Select(attrs={'class': 'form-control'}),
            'tipo_interaccion': forms.RadioSelect(),
            'objetivo': forms.NumberInput(attrs={'class': 'form-control'}),
            'outcid': forms.TextInput(attrs={'class': 'form-control'}),
            'outr': forms.Select(attrs={'class': 'form-control'}),
            'speech': forms.Textarea(attrs={'class': 'form-control'}),
            'prioridad': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ActuacionVigenteForm(forms.ModelForm):
    """
    El form de miembro de una cola
    """

    def clean(self):
        domingo = self.cleaned_data.get('domingo')
        lunes = self.cleaned_data.get('lunes')
        martes = self.cleaned_data.get('martes')
        miercoles = self.cleaned_data.get('miercoles')
        jueves = self.cleaned_data.get('jueves')
        viernes = self.cleaned_data.get('viernes')
        sabado = self.cleaned_data.get('sabado')
        if domingo == lunes == martes == miercoles == jueves == viernes == sabado is False:
            raise forms.ValidationError(_('Debe seleccionar algun día'))

        return self.cleaned_data

    class Meta:
        model = ActuacionVigente
        fields = ('domingo', 'lunes', 'martes', 'miercoles', 'jueves',
                  'viernes', 'sabado', 'hora_desde', 'hora_hasta')
        widgets = {
            'dia_semanal': forms.Select(attrs={'class': 'form-control'}),
            "hora_desde": forms.TextInput(attrs={'class': 'form-control'}),
            "hora_hasta": forms.TextInput(attrs={'class': 'form-control'}),
        }


class BlacklistForm(forms.ModelForm):

    class Meta:
        model = Blacklist
        fields = ('nombre', 'archivo_importacion')
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'archivo_importacion': forms.FileInput(attrs={'class': 'form-control'}),
        }


class ContactoBlacklistForm(forms.ModelForm):
    # Campos del formulario
    telefono = forms.CharField(
        required=True,
        max_length=25,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('Teléfono de contacto')
            }
        )
    )

    # Fields cleanners
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not telefono.isdigit():
            msg = _("Debe ser en formato '99999999' y numérico.")
            raise forms.ValidationError(msg)
        if not is_valid_length(telefono, 3, 25):
            msg = _("Solo se permiten de 3-25 dígitos.")
            raise forms.ValidationError(msg)
        return telefono

    class Meta:
        model = ContactoBlacklist
        fields = ('telefono',)


class SistemaExternoForm(forms.ModelForm):

    class Meta:
        model = SistemaExterno
        fields = ('nombre', )


class ReglasIncidenciaForm(forms.ModelForm):

    class Meta:
        model = ReglasIncidencia
        fields = ('estado', 'intento_max', 'reintentar_tarde', 'en_modo')

        widgets = {
            'estado': forms.Select(attrs={'class': 'form-control'}),
            "intento_max": forms.TextInput(attrs={'class': 'form-control'}),
            "reintentar_tarde": forms.TextInput(attrs={'class': 'form-control'}),
            'en_modo': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.campana = None
        if 'campana' in kwargs:
            self.campana = kwargs.pop('campana')
        super(ReglasIncidenciaForm, self).__init__(*args, **kwargs)

    def clean_estado(self):
        """
        Realiza la  validación de que no existan reglas de incidencia de un mismo tipo repetidas
        """
        estado = self.cleaned_data.get('estado')
        if estado and self.campana and \
            estado in list(
                set(self.campana.reglas_incidencia.exclude(id=self.instance.id).
                    values_list('estado', flat=True))):
            raise forms.ValidationError(
                _("Los nombres de los estados de las reglas deben ser distintos"))
        return estado

    def save(self, commit=True):
        regla = super(ReglasIncidenciaForm, self).save(commit=False)
        if regla.estado == ReglasIncidencia.TERMINATED:
            regla.estado_personalizado = ReglasIncidencia.ESTADO_PERSONALIZADO_CONTESTADOR
        else:
            regla.estado_personalizado = ""
        if commit:
            regla.save()
        return regla


class ReglasIncidenciaBaseFomset(BaseInlineFormSet):

    def clean(self):
        """
        Realiza la  validación de que no existan reglas de incidencia de un mismo tipo repetidas
        """
        if any(self.errors):
            return
        estados_reglas = []
        for form in self.forms:
            estado = form.cleaned_data.get('estado')
            if estado in estados_reglas:
                raise forms.ValidationError(
                    _("Los nombres de los estados de las reglas deben ser distintos"))
            estados_reglas.append(estado)


ReglasIncidenciaFormSet = inlineformset_factory(
    Campana, ReglasIncidencia, form=ReglasIncidenciaForm, formset=ReglasIncidenciaBaseFomset,
    extra=1, min_num=0)


class OpcionCalificacionChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.nombre


class ReglaIncidenciaPorCalificacionForm(forms.ModelForm):
    opcion_calificacion = OpcionCalificacionChoiceField(
        queryset=OpcionCalificacion.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = ReglaIncidenciaPorCalificacion
        fields = ('opcion_calificacion', 'intento_max', 'reintentar_tarde', 'en_modo')
        widgets = {
            "intento_max": forms.NumberInput(attrs={'class': 'form-control'}),
            "reintentar_tarde": forms.NumberInput(attrs={'class': 'form-control'}),
            'en_modo': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, campana, *args, **kwargs):
        super(ReglaIncidenciaPorCalificacionForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            campana = self.instance.opcion_calificacion.campana
        self.fields['opcion_calificacion'].queryset = campana.opciones_calificacion.all()


class QueueDialerForm(forms.ModelForm):
    """
    El form de cola para las llamadas
    """
    tipo_destino = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'tipo_destino'}), required=False
    )

    class Meta:
        model = Queue
        fields = ('name', 'maxlen', 'wrapuptime', 'servicelevel', 'strategy', 'weight',
                  'wait', 'auto_grabacion', 'campana', 'detectar_contestadores', 'musiconhold',
                  'audio_para_contestadores', 'initial_predictive_model', 'initial_boost_factor',
                  'dial_timeout', 'tipo_destino', 'destino', 'audio_previo_conexion_llamada')

        widgets = {
            'campana': forms.HiddenInput(),
            'name': forms.HiddenInput(),
            "maxlen": forms.TextInput(attrs={'class': 'form-control'}),
            "wrapuptime": forms.TextInput(attrs={'class': 'form-control'}),
            "servicelevel": forms.TextInput(attrs={'class': 'form-control'}),
            'strategy': forms.Select(attrs={'class': 'form-control'}),
            "weight": forms.TextInput(attrs={'class': 'form-control'}),
            "wait": forms.TextInput(attrs={'class': 'form-control'}),
            "audio_para_contestadores": forms.Select(attrs={'class': 'form-control'}),
            "initial_boost_factor": forms.NumberInput(
                attrs={'class': 'form-control', 'min': 0.1, 'max': 5}),
            "dial_timeout": forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo_destino': forms.Select(attrs={'class': 'form-control'}),
            'destino': forms.Select(attrs={'class': 'form-control', 'id': 'destino'}),
            'musiconhold': forms.Select(attrs={'class': 'form-control'}),
            'audio_previo_conexion_llamada': forms.Select(attrs={'class': 'form-control'}),
        }

        help_texts = {
            'dial_timeout': _(""" Es recomendable que este valor sea menor al dial timeout
            definido en la ruta saliente. En segundos"""),
            'wrapuptime': _('En segundos'),
            'wait': _('En segundos'),
        }

    def clean(self):
        initial_boost_factor = self.cleaned_data.get('initial_boost_factor')
        if initial_boost_factor and initial_boost_factor < 0.1:
            raise forms.ValidationError('El factor boost inicial no debe ser'
                                        ' menor a 0.1')
        if initial_boost_factor and initial_boost_factor > 5.0:
            raise forms.ValidationError('El factor boost inicial no debe ser'
                                        ' mayor a 5.0')

        initial_predictive_model = self.cleaned_data.get('initial_predictive_model')
        if initial_predictive_model and not initial_boost_factor:
            raise forms.ValidationError('El factor boost inicial no deber ser'
                                        ' none si la predicitvidad está activa')

        dial_timeout = self.cleaned_data.get('dial_timeout')
        if dial_timeout < 10 or dial_timeout > 90:
            raise forms.ValidationError(_('El valor de dial timeout deberá estar comprendido entre'
                                          ' 10 y 90 segundos'))

        return self.cleaned_data

    def clean_destino(self):
        tipo_destino = self.cleaned_data.get('tipo_destino', None)
        destino = self.cleaned_data.get('destino', None)
        if tipo_destino and not destino:
            raise forms.ValidationError(
                _('Debe seleccionar un destino'))
        return destino

    def __init__(self, *args, **kwargs):
        super(QueueDialerForm, self).__init__(*args, **kwargs)
        self.fields['audio_para_contestadores'].queryset = ArchivoDeAudio.objects.all()
        tipo_destino_choices = [EMPTY_CHOICE]
        tipo_destino = tuple(
            item for item in DestinoEntrante.TIPOS_DESTINOS if item[0] != DestinoEntrante.HANGUP)
        tipo_destino_choices.extend(tipo_destino)
        self.fields['tipo_destino'].choices = tipo_destino_choices
        self.fields['audio_previo_conexion_llamada'].queryset = ArchivoDeAudio.objects.all()
        self.fields['musiconhold'].queryset = Playlist.objects.annotate(
            Count('musicas')).filter(musicas__count__gte=1)
        instance = getattr(self, 'instance', None)
        if instance.pk is not None and instance.destino:
            tipo = instance.destino.tipo
            self.initial['tipo_destino'] = tipo
            destinos_qs = DestinoEntrante.get_destinos_por_tipo(tipo)
            destino_entrante_choices = [EMPTY_CHOICE] + [(dest_entr.id, str(dest_entr))
                                                         for dest_entr in destinos_qs]
            self.fields['destino'].choices = destino_entrante_choices
        else:
            self.fields['destino'].choices = ()

        if not instance.pk:
            self.initial['wrapuptime'] = 2
            self.initial['auto_grabacion'] = True


ROL_CHOICES = ((SupervisorProfile.ROL_GERENTE, _('Supervisor Gerente')),
               (SupervisorProfile.ROL_ADMINISTRADOR, _('Administrador')),
               (SupervisorProfile.ROL_CLIENTE, _('Cliente')))


class SupervisorProfileForm(forms.Form):
    """Form para elegir el rol de un supervisor"""
    rol = forms.ModelChoiceField(queryset=Group.objects.all(),
                                 label=_('Rol del usuario'),
                                 widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, rol, roles_de_supervisores_queryset, *args, **kwargs):
        super(SupervisorProfileForm, self).__init__(*args, **kwargs)
        self.fields['rol'].queryset = roles_de_supervisores_queryset
        self.fields['rol'].initial = rol


class CampanaSupervisorUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        supervisors_choices = kwargs.pop('supervisors_choices', [])
        supervisors_required = kwargs.pop('supervisors_required', False)
        super(CampanaSupervisorUpdateForm, self).__init__(*args, **kwargs)
        self.fields['supervisors'].choices = supervisors_choices
        self.fields['supervisors'].required = supervisors_required

    class Meta:
        model = Campana
        fields = ('supervisors',)

        widgets = {
            'supervisors': forms.CheckboxSelectMultiple(),
        }


class CampanaManualForm(CampanaMixinForm, forms.ModelForm):
    auto_grabacion = forms.BooleanField(required=False, initial=True)
    detectar_contestadores = forms.BooleanField(required=False)
    campo_direccion_choice = forms.CharField(
        required=False, widget=forms.Select(attrs={'class': 'form-control'}))

    telefono_habilitado = forms.BooleanField(required=False, disabled=True)
    video_habilitado = forms.BooleanField(required=False, disabled=True)

    def __init__(self, *args, **kwargs):
        super(CampanaManualForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.fields['outr'].queryset = RutaSaliente.objects.all()
        if instance.pk is None:
            self.fields['bd_contacto'].required = False
        else:
            self.fields['nombre'].disabled = True
            self.fields['bd_contacto'].required = True
            # self.fields['tipo_interaccion'].required = False

    class Meta:
        model = Campana
        fields = ('nombre', 'bd_contacto', 'control_de_duplicados', 'campo_direccion',
                  'sistema_externo', 'id_externo', 'tipo_interaccion', 'sitio_externo',
                  'objetivo', 'outcid', 'outr', 'speech', 'whatsapp_habilitado')

        widgets = {
            'sistema_externo': forms.Select(attrs={'class': 'form-control'}),
            'id_externo': forms.TextInput(attrs={'class': 'form-control'}),
            'sitio_externo': forms.Select(attrs={'class': 'form-control'}),
            'tipo_interaccion': forms.RadioSelect(),
            'objetivo': forms.NumberInput(attrs={'class': 'form-control'}),
            'bd_contacto': forms.Select(attrs={'class': 'form-control', 'id': 'camp_bd_contactos'}),
            'control_de_duplicados': forms.Select(attrs={'class': 'form-control'}),
            'outcid': forms.TextInput(attrs={'class': 'form-control'}),
            'outr': forms.Select(attrs={'class': 'form-control'}),
            'speech': forms.Textarea(attrs={'class': 'form-control'})
        }

    def requiere_bd_contacto(self):
        return False


class CampanaPreviewForm(CampanaMixinForm, forms.ModelForm):
    auto_grabacion = forms.BooleanField(required=False, initial=True)
    campo_direccion_choice = forms.CharField(
        required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    telefono_habilitado = forms.BooleanField(required=False, disabled=True)
    video_habilitado = forms.BooleanField(required=False, disabled=True)

    def __init__(self, *args, **kwargs):
        super(CampanaPreviewForm, self).__init__(*args, **kwargs)
        self.fields['outr'].queryset = RutaSaliente.objects.all()
        instance = getattr(self, 'instance', None)
        if instance and instance.pk and not self.initial.get('es_template', False):
            self.fields['nombre'].disabled = True
            self.fields['bd_contacto'].disabled = True
            self.fields['tiempo_desconexion'].disabled = True
            # self.fields['tipo_interaccion'].required = False

    class Meta:
        model = Campana
        fields = ('nombre', 'sistema_externo', 'id_externo', 'control_de_duplicados',
                  'tipo_interaccion', 'sitio_externo', 'objetivo', 'bd_contacto',
                  'campo_direccion', 'tiempo_desconexion', 'outr', 'outcid', 'speech',
                  'whatsapp_habilitado')

        widgets = {
            'bd_contacto': forms.Select(attrs={'class': 'form-control', 'id': 'camp_bd_contactos'}),
            'control_de_duplicados': forms.Select(attrs={'class': 'form-control'}),
            'campo_direccion': forms.Select(attrs={'class': 'form-control'}),
            'sistema_externo': forms.Select(attrs={'class': 'form-control'}),
            'id_externo': forms.TextInput(attrs={'class': 'form-control'}),
            'sitio_externo': forms.Select(attrs={'class': 'form-control'}),
            'tipo_interaccion': forms.RadioSelect(),
            'objetivo': forms.NumberInput(attrs={'class': 'form-control'}),
            'tiempo_desconexion': forms.NumberInput(attrs={'class': 'form-control'}),
            'outcid': forms.TextInput(attrs={'class': 'form-control'}),
            'outr': forms.Select(attrs={'class': 'form-control'}),
            'speech': forms.Textarea(attrs={'class': 'form-control'})
        }

    def requiere_bd_contacto(self):
        return True

    def clean_tiempo_desconexion(self):
        tiempo_desconexion = self.cleaned_data['tiempo_desconexion']
        if tiempo_desconexion < TIEMPO_MINIMO_DESCONEXION:
            msg = 'Debe ingresar un minimo de {0} minutos'.format(TIEMPO_MINIMO_DESCONEXION)
            raise forms.ValidationError(msg)
        return tiempo_desconexion

    def clean_bd_contacto(self):
        bd_contacto = self.cleaned_data['bd_contacto']
        es_template = self.initial.get('es_template', False)
        if not es_template and not bd_contacto.contactos.exists():
            raise forms.ValidationError(_('No puede seleccionar una BD vacia'))
        return bd_contacto


class EscogerCampanaForm(forms.Form):
    campana = forms.ChoiceField(
        label=_("Escoja una campaña"), choices=(),
        widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        campanas = kwargs.pop('campanas', None)
        super(EscogerCampanaForm, self).__init__(*args, **kwargs)
        choices = [(pk, nombre) for pk, nombre in campanas]
        self.fields['campana'].choices = choices


class GrupoForm(forms.ModelForm):

    class Meta:
        model = Grupo
        fields = ('nombre', 'auto_unpause', 'auto_attend_inbound',
                  'auto_attend_dialer', 'obligar_calificacion', 'call_off_camp',
                  'acceso_grabaciones_agente', 'acceso_dashboard_agente',
                  'on_hold', 'limitar_agendas_personales', 'cantidad_agendas_personales',
                  'limitar_agendas_personales_en_dias', 'tiempo_maximo_para_agendar',
                  'show_console_timers', 'acceso_contactos_agente',
                  'acceso_agendas_agente', 'acceso_calificaciones_agente',
                  'acceso_campanas_preview_agente', 'conjunto_de_pausa',
                  'obligar_despausa', 'whatsapp_habilitado',
                  'restringir_tipo_llamadas_manuales', 'permitir_llamadas_manuales_a_manuales',
                  'permitir_llamadas_manuales_a_dialer', 'permitir_llamadas_manuales_a_entrante',
                  'permitir_llamadas_manuales_a_preview')
        widgets = {
            'auto_unpause': forms.NumberInput(attrs={'class': 'form-control'}),
            'cantidad_agendas_personales': forms.NumberInput(attrs={
                'class': 'form-control', 'style': 'display:inline; width:8ch'}),
            'tiempo_maximo_para_agendar': forms.NumberInput(attrs={
                'class': 'form-control', 'style': 'display:inline; width:8ch'}),
            'conjunto_de_pausa': forms.Select(attrs={'class': 'form-control'})
        }
        help_texts = {
            'auto_unpause': _('En segundos'),
            'cantidad_agendas_personales': _('Cantidad máxima de agendas'),
            'tiempo_maximo_para_agendar': _('Cantidad máxima de días para agendar'),
            'obligar_despausa': _('Forzar Despausa'),
            'conjunto_de_pausa': _('Conjunto de Pausas'),
        }
        labels = {
            'acceso_grabaciones_agente': _('Permitir el acceso a las grabaciones'),
            'acceso_dashboard_agente': _('Permitir el acceso al dashboard'),
            'on_hold': _('Permitir la activación de On-Hold')
        }

    def __init__(self, *args, **kwargs):
        super(GrupoForm, self).__init__(*args, **kwargs)
        self.fields['auto_unpause'].required = False

    def validate_required_field(self, cleaned_data, field_name,
                                message=_('Este campo es requerido')):
        if (field_name in cleaned_data and
                cleaned_data[field_name] is None):
            self._errors[field_name] = self.error_class([message])
            del cleaned_data[field_name]

    def clean(self):
        cleaned_data = super(GrupoForm, self).clean()
        if cleaned_data.get('limitar_agendas_personales', None):
            self.validate_required_field(cleaned_data, 'cantidad_agendas_personales')
        if cleaned_data.get('limitar_agendas_personales_en_dias', None):
            self.validate_required_field(cleaned_data, 'tiempo_maximo_para_agendar')

    def clean_tiempo_maximo_para_agendar(self):
        data = self.cleaned_data['tiempo_maximo_para_agendar']
        if data and data > 30:
            raise forms.ValidationError(_('Permitir agendar a no más de 30 días'))
        return data


class ParametrosCrmForm(forms.ModelForm):

    def __init__(self, columnas_bd, *args, **kwargs):
        self.con_crm_calificacion = kwargs.pop('con_crm_calificacion') \
            if 'con_crm_calificacion' in kwargs else None
        super(ParametrosCrmForm, self).__init__(*args, **kwargs)
        self.columnas_bd = columnas_bd
        self.columnas_bd_keys = [x[0] for x in columnas_bd]
        if not self.con_crm_calificacion:
            tipo_choices = [(choice[0], choice[1]) for choice in self.fields['tipo'].choices
                            if choice[0] != ParametrosCrm.DATO_CALIFICACION]
            self.fields['tipo'] = forms.ChoiceField(choices=tipo_choices)

    class Meta:
        model = ParametrosCrm
        fields = ('tipo', 'valor', 'nombre')

        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'valor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _(u'Valor')}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _(u'Nombre')}),
        }

    def clean_valor(self):
        tipo = int(self.cleaned_data.get('tipo')) if self.cleaned_data.get('tipo') else None
        valor = self.cleaned_data.get('valor')
        if tipo == ParametrosCrm.DATO_CONTACTO and valor not in self.columnas_bd_keys:
            raise forms.ValidationError(
                _('El valor debe corresponder a un campo de la base de datos de contactos'))
        if tipo == ParametrosCrm.DATO_CAMPANA and valor not in ParametrosCrm.OPCIONES_CAMPANA_KEYS:
            raise forms.ValidationError(
                _('El valor debe corresponder a un campo válido de la campaña'))
        if tipo == ParametrosCrm.DATO_LLAMADA and valor not in ParametrosCrm.OPCIONES_LLAMADA_KEYS:
            raise forms.ValidationError(
                _('El valor debe corresponder a un dato válido de la llamada'))
        if tipo == ParametrosCrm.DIALPLAN:
            if not valor.startswith(ParametrosCrm.PREFIJO_DIALPLAN):
                raise (forms.ValidationError(
                    _('El valor debe tener el prefijo {0}'.format(ParametrosCrm.PREFIJO_DIALPLAN))))
            else:
                return valor.capitalize()
        if tipo == ParametrosCrm.DATO_CALIFICACION and \
                valor not in ParametrosCrm.OPCIONES_DATO_CALIFICACION_KEYS:
            raise forms.ValidationError(
                _('El valor debe corresponder a un campo válido de datos de calificación'))
        # Si es tipo ParametrosCrm.CUSTOM puede ir cualquier valor.
        return valor

    def es_placeholder(self, nombre):
        return nombre[0] == '{' and nombre[-1] == '}' and nombre[1:-1].isdigit()

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '')
        if not nombre:
            raise forms.ValidationError(_('Debe definir un nombre para el parámetro'))
        if contiene_solo_alfanumericos_o_guiones(nombre):
            return nombre
        if self.es_placeholder(nombre):
            return nombre
        raise forms.ValidationError(
            _('Sólo se permiten caracteres alfanuméricos o ser de tipo placeholder. Ej: "{1}"'))


class QueueMemberBaseFomset(BaseInlineFormSet):

    def clean(self):
        """Realiza la  validación de que no existan miembros de cola repetidas para una misma
        cola de campaña
        """
        if any(self.errors):
            return
        members = []
        for form in self.forms:
            member = form.cleaned_data.get('member')
            if member in members:
                raise forms.ValidationError(
                    _("Los agentes deben ser distintos"))
            members.append(member)


ParametrosCrmFormSet = inlineformset_factory(
    Campana, ParametrosCrm, form=ParametrosCrmForm, extra=1, can_delete=True)

QueueMemberFormset = inlineformset_factory(
    Queue, QueueMember, formset=QueueMemberBaseFomset, form=QueueMemberForm, extra=1,
    can_delete=True, min_num=0)


class RegistroForm(forms.Form):
    nombre = forms.CharField(label=_("Inserte su nombre o empresa"),
                             widget=forms.TextInput(attrs={'class': 'form-control'}),
                             required=True)
    password = forms.CharField(label=_("Inserte su contraseña de acceso"),
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                               required=True)
    email = forms.EmailField(label=_("Inserte su correo electrónico"),
                             widget=forms.TextInput(attrs={'class': 'form-control'}),
                             required=True)
    telefono = forms.CharField(label=_("Inserte su teléfono"),
                               widget=forms.TextInput(attrs={'class': 'form-control'}),
                               required=False)

    def __init__(self, *args, **kwargs):
        super(RegistroForm, self).__init__(*args, **kwargs)
        self.initial = {
            'nombre': config.CLIENT_NAME,
            'email': config.CLIENT_EMAIL,
            'telefono': config.CLIENT_PHONE,
        }


class AsignacionContactosForm(forms.Form):

    proporcionalmente = forms.BooleanField(label=_('Asignar proporcionalmente'),
                                           required=False, initial=False)
    aleatorio = forms.BooleanField(label=_('En orden aleatorio'),
                                   required=False, initial=False)

    def clean(self):
        # no tiene sentido q se seleccione aleatoriamente si no se seleccionó
        # la asignación proporcional
        cleaned_data = super(AsignacionContactosForm, self).clean()
        proporcionalmente = cleaned_data.get('proporcionalmente', False)
        aleatorio = cleaned_data.get('aleatorio', False)
        if aleatorio and not proporcionalmente:
            raise forms.ValidationError(
                _('Debe seleccionar la asignación proporcional si quiere escoger'
                  'la asignación en orden aleatorio'))
        return cleaned_data


class OrdenarAsignacionContactosForm(forms.Form):
    """Formulario para importar el orden realizado sobre los
    Agentes en Contactos en un archivo .csv
    """
    agentes_en_contactos_ordenados = forms.FileField()
    campo_desactivacion = forms.CharField(
        required=False, widget=forms.HiddenInput(
            attrs={'id': 'campoDesactivacionImport'}))


class CampanaPreviewCampoDesactivacion(forms.ModelForm):

    campo_desactivacion = forms.ChoiceField(
        required=False, widget=forms.Select(
            attrs={'class': 'form-control', 'id': 'campoDesactivacion'}))

    def __init__(self, *args, **kwargs):
        super(CampanaPreviewCampoDesactivacion, self).__init__(*args, **kwargs)
        campana = self.instance
        nombres_columnas_datos = campana.bd_contacto.get_metadata().nombres_de_columnas_de_datos
        nombres_columnas_datos_choices = [(i, i) for i in nombres_columnas_datos]
        choices = [EMPTY_CHOICE] + nombres_columnas_datos_choices
        self.fields['campo_desactivacion'].choices = choices
        self.fields['campo_desactivacion'].label = _('Campo desactivación')

    class Meta:
        model = Campana
        fields = ('campo_desactivacion',)


class FiltroUsuarioFechaForm(forms.Form):
    fecha = forms.CharField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control'}),
                            label=_('Fecha'))
    usuario = forms.ModelChoiceField(
        queryset=User.objects.all(), label=_('Agente'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False)

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        fecha_desde, fecha_hasta = fecha.split('-')
        fecha_desde = convert_fecha_datetime(fecha_desde)
        fecha_hasta = convert_fecha_datetime(fecha_hasta)
        if fecha_hasta < fecha_desde:
            raise forms.ValidationError(_('La fecha inicial debe ser anterior a la final'))
        self.fecha_desde = fecha_desde
        self.fecha_hasta = fecha_hasta

    def __init__(self, users_choices, *args, **kwargs):
        super(FiltroUsuarioFechaForm, self).__init__(*args, **kwargs)
        self.fields['usuario'].queryset = users_choices


class FiltroAgendasForm(forms.Form):
    fecha = forms.CharField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control'}),
                            label=_('Fecha'))
    agente = forms.ModelChoiceField(
        queryset=AgenteProfile.objects.all(), label=_('Agente'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False)

    campana = forms.ModelMultipleChoiceField(
        queryset=Campana.objects.filter(
            estado__in=[Campana.ESTADO_ACTIVA, Campana.ESTADO_INACTIVA, Campana.ESTADO_PAUSADA]),
        label=_('Campana'),
        required=False)

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        fecha_desde, fecha_hasta = fecha.split('-')
        fecha_desde = convert_fecha_datetime(fecha_desde)
        fecha_hasta = convert_fecha_datetime(fecha_hasta, final_dia=True)
        if fecha_hasta < fecha_desde:
            raise forms.ValidationError(_('La fecha inicial debe ser anterior a la final'))
        self.fecha_desde = fecha_desde
        self.fecha_hasta = fecha_hasta


class ConfiguracionDeAgentesDeCampanaForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionDeAgentesDeCampana
        exclude = ('campana',)

    def __init__(self, campana_type, *args, **kwargs):
        super(ConfiguracionDeAgentesDeCampanaForm, self).__init__(*args, **kwargs)
        self.fields['set_auto_attend_inbound'].widget.attrs['class'] = 'form-control'
        self.fields['auto_attend_inbound'].widget.attrs['class'] = 'form-control'
        self.fields['set_auto_attend_dialer'].widget.attrs['class'] = 'form-control'
        self.fields['auto_attend_dialer'].widget.attrs['class'] = 'form-control'
        self.fields['set_auto_unpause'].widget.attrs['class'] = 'form-control'
        self.fields['auto_unpause'].widget.attrs['class'] = 'form-control'
        self.fields['set_obligar_calificacion'].widget.attrs['class'] = 'form-control'
        self.fields['obligar_calificacion'].widget.attrs['class'] = 'form-control'
        if not campana_type == Campana.TYPE_ENTRANTE:
            del self.fields['set_auto_attend_inbound']
            del self.fields['auto_attend_inbound']
        if not campana_type == Campana.TYPE_DIALER:
            del self.fields['set_auto_attend_dialer']
            del self.fields['auto_attend_dialer']


class AutenticacionExternaForm(forms.Form):
    tipo = forms.ChoiceField(
        required=True, widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('Tipo'),
        choices=(('0', '--------'), ('LDAP', _('LDAP Server'))))
    servidor = forms.CharField(
        max_length=255, required=False, validators=[URLValidator],
        label=_('Servidor'),
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    base_dn = forms.CharField(
        max_length=255, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    activacion = forms.ChoiceField(
        required=False, widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('Activación'),
        choices=((AutenticacionExternaDeUsuario.TODOS, _('Todos')),
                 (AutenticacionExternaDeUsuario.TODOS_NO_ADMIN, _('Todos menos Admin')),
                 (AutenticacionExternaDeUsuario.MANUAL_ACTIVO, _('Manual (default activo)')),
                 (AutenticacionExternaDeUsuario.MANUAL_INACTIVO, _('Manual (default inactivo)'))
                 ))
    ms_simple_auth = forms.BooleanField(
        required=False, label=_('MicroSoft AD DS Simple Authentication'))

    def clean(self):
        # no tiene sentido q se seleccione aleatoriamente si no se seleccionó
        # la asignación proporcional
        cleaned_data = super(AutenticacionExternaForm, self).clean()
        if cleaned_data.get('tipo') == 'LDAP':
            if len(self.cleaned_data.get('servidor', '')) < 4:
                self.add_error('servidor',
                               _('Ingrese una url de servidor válida.'))
            if len(self.cleaned_data.get('base_dn', '')) < 4:
                self.add_error('base_dn',
                               _('Ingrese una base DN válida.'))
            activacion = self.cleaned_data.get('activacion', '')
            if activacion not in AutenticacionExternaDeUsuario.CHOICES_ACTIVACION:
                self.add_error('activacion',
                               _('Seleccione un tipo de activación válido.'))
        return cleaned_data


class CampanaConfiguracionWhatsappForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionWhatsappCampana
        fields = ('linea', 'grupo_plantilla_whatsapp', 'nivel_servicio',)
        widgets = {
            'linea': forms.Select(attrs={'class': 'form-control'}),
            'grupo_plantilla_whatsapp': forms.Select(attrs={'class': 'form-control'}),
            'nivel_servicio': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class CustomBaseDatosContactoForm(forms.ModelForm):

    metadata_schema = {
        "$id": "custom-basedatoscontacto.metadata",
        "type": "object",
        "properties": {
            "prim_fila_enc": {
                "const": False,
            },
            "cant_col": {
                "type": "integer",
                "minimum": 0,
            },
            "nombres_de_columnas": {
                "type": "array",
                "items": {
                    "type": "string",
                },
            },
            "cols_telefono": {
                "type": "array",
                "items": {
                    "type": "integer",
                    "minimum": 0,
                },
            },
            "col_id_externo": {
                "type": ["integer", "null"],
            },
        },
        "required": [
            "prim_fila_enc",
            "cant_col",
            "nombres_de_columnas",
            "cols_telefono",
            "col_id_externo",
        ],
    }

    class Meta:
        model = BaseDatosContacto
        fields = [
            "nombre",
            "metadata",
        ]
        widgets = {
            "metadata": forms.HiddenInput,
        }

    def clean_metadata(self):
        value = self.cleaned_data["metadata"]
        metadata = json.loads(value)
        try:
            jsonschema.validate(metadata, self.metadata_schema)
        except jsonschema.ValidationError as error:
            raise forms.ValidationError(error.message)
        if metadata["cant_col"] != len(metadata["nombres_de_columnas"]):
            raise forms.ValidationError(_("El valor de {0} es incorrecto".format('cant_col')))
        if any(col >= metadata["cant_col"] for col in metadata["cols_telefono"]):
            raise forms.ValidationError(_("El valor de {0} es incorrecto".format('cols_telefono')))
        if metadata["col_id_externo"] and metadata["col_id_externo"] >= metadata["cant_col"]:
            raise forms.ValidationError(_("El valor de {0} es incorrecto".format('col_id_externo')))
        return value
