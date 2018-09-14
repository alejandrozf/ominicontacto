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

import json
from django import forms
from django.conf import settings
from django.forms.models import inlineformset_factory, BaseInlineFormSet, ModelChoiceField
from django.contrib.auth.forms import (
    UserChangeForm,
    UserCreationForm
)
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, MultiField

from ominicontacto_app.models import (
    User, AgenteProfile, Queue, QueueMember, BaseDatosContacto, Grabacion,
    Campana, Contacto, CalificacionCliente, Grupo, Formulario, FieldFormulario, Pausa,
    MetadataCliente, AgendaContacto, ActuacionVigente, Backlist, SitioExterno,
    ReglasIncidencia, UserApiCrm, SupervisorProfile, ArchivoDeAudio,
    NombreCalificacion, OpcionCalificacion, ParametroExtraParaWebform
)
from ominicontacto_app.services.campana_service import CampanaService
from ominicontacto_app.utiles import (convertir_ascii_string, validar_nombres_campanas,
                                      validar_solo_ascii_y_sin_espacios)

from utiles_globales import validar_extension_archivo_audio

TIEMPO_MINIMO_DESCONEXION = 2
EMPTY_CHOICE = ('', '---------')


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
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'is_agente',
            'is_supervisor')
        labels = {
            'is_agente': 'Es un agente',
            'is_supervisor': 'Es un supervisor',
        }

    def clean(self):
        is_agente = self.cleaned_data.get('is_agente', None)
        is_supervisor = self.cleaned_data.get('is_supervisor', None)
        if is_agente and is_supervisor:
            raise forms.ValidationError(
                _('Un usuario no puede ser Agente y Supervisor al mismo tiempo'))
        return self.cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username', None)
        existe_user = User.objects.filter(username=username).exists()
        if existe_user:
            raise forms.ValidationError(
                _('No se puede volver a utilizar dos veces el mismo nombre de usuario,'
                  ' por favor seleccione un nombre de usuario diferente'))
        return username


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    password1 = forms.CharField(max_length=20,
                                required=False,
                                # will be overwritten by __init__()
                                help_text=_('Ingrese la nueva contraseña '
                                            '(sólo si desea cambiarla)'),
                                # will be overwritten by __init__()
                                widget=forms.PasswordInput(),
                                label=_('Contrasena'))

    password2 = forms.CharField(
        max_length=20,
        required=False,  # will be overwritten by __init__()
        # will be overwritten by __init__()
        help_text=_('Ingrese la nueva contraseña (sólo si desea cambiarla)'),
        widget=forms.PasswordInput(),
        label=_('Contrasena (otra vez)'))

    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        validate_password(password1)
        if password1 != password2:
            raise forms.ValidationError(_('Los passwords no concuerdan'))

        return self.cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username', None)
        existe_user = User.objects.filter(username=username).exists()
        if existe_user:
            raise forms.ValidationError(
                _('No se puede volver a utilizar dos veces el mismo nombre de usuario,'
                  ' por favor seleccione un nombre de usuario diferente'))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


class AgenteProfileForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    # def __init__(self, *args, **kwargs):
    #     super(AgenteProfileForm, self).__init__(*args, **kwargs)
    #
    #     self.fields['user'].widget.attrs['disabled'] = True
    #
    # def clean_user(self):
    #     if self.instance.is_disabled:
    #         return self.instance.user
    #     else:
    #         return self.cleaned_data.get('user')

    # def clean_sip_extension(self):
    #     sip_extension = self.cleaned_data['sip_extension']
    #     if settings.OL_SIP_LIMITE_INFERIOR > sip_extension or\
    #             sip_extension > settings.OL_SIP_LIMITE_SUPERIOR:
    #         raise forms.ValidationError("El sip_extension es incorrecto debe "
    #                                     "ingresar un numero entre {0} y {1}".
    #                                     format(settings.OL_SIP_LIMITE_INFERIOR,
    #                                            settings.OL_SIP_LIMITE_SUPERIOR))
    #     return sip_extension

    class Meta:
        model = AgenteProfile
        fields = ('modulos', 'grupo')


class QueueEntranteForm(forms.ModelForm):
    """
    El form de cola para las colas
    """

    def __init__(self, audios_choices, *args, **kwargs):
        super(QueueEntranteForm, self).__init__(*args, **kwargs)
        self.fields['timeout'].required = True
        self.fields['retry'].required = True
        self.fields['announce_frequency'].required = False
        self.fields['audios'].queryset = ArchivoDeAudio.objects.all()
        self.fields['audio_de_ingreso'].queryset = ArchivoDeAudio.objects.all()

    class Meta:
        model = Queue
        fields = ('name', 'timeout', 'retry', 'maxlen', 'servicelevel',
                  'strategy', 'weight', 'wait', 'auto_grabacion', 'campana',
                  'audios', 'announce_frequency', 'audio_de_ingreso', 'campana')

        help_texts = {
            'timeout': """En segundos """,
        }
        widgets = {
            'name': forms.HiddenInput(),
            'campana': forms.HiddenInput(),
            'timeout': forms.TextInput(attrs={'class': 'form-control'}),
            'retry': forms.TextInput(attrs={'class': 'form-control'}),
            'maxlen': forms.TextInput(attrs={'class': 'form-control'}),
            'servicelevel': forms.TextInput(attrs={'class': 'form-control'}),
            'strategy': forms.Select(attrs={'class': 'form-control'}),
            'weight': forms.TextInput(attrs={'class': 'form-control'}),
            'wait': forms.TextInput(attrs={'class': 'form-control'}),
            'audios': forms.Select(attrs={'class': 'form-control'}),
            'announce_frequency': forms.TextInput(attrs={'class': 'form-control'}),
            'audio_de_ingreso': forms.Select(attrs={'class': 'form-control'}),
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
        if audio and not (frequency > 0):
            raise forms.ValidationError(
                _('Debe definir una frecuencia para el Anuncio Periódico'))
        return frequency


class QueueMemberForm(forms.ModelForm):
    """
    El form de miembro de una cola
    """

    def __init__(self, members, *args, **kwargs):
        super(QueueMemberForm, self).__init__(*args, **kwargs)

        self.fields['member'].queryset = members

    class Meta:
        model = QueueMember
        fields = ('member', 'penalty')


class BaseDatosContactoForm(forms.ModelForm):

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


class BusquedaContactoForm(forms.Form):
    buscar = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'search pattern'}
        )
    )


class GrabacionBusquedaForm(forms.Form):
    """
    El form para la busqueda de grabaciones
    """
    fecha = forms.CharField(required=False,
                            widget=forms.TextInput(attrs={'class': 'form-control'}))
    tipo_llamada_choice = list(Grabacion.TYPE_LLAMADA_CHOICES)
    tipo_llamada_choice.insert(0, EMPTY_CHOICE)
    tipo_llamada = forms.ChoiceField(required=False,
                                     choices=tipo_llamada_choice)
    tel_cliente = forms.CharField(required=False)
    agente = forms.ModelChoiceField(queryset=AgenteProfile.objects.filter(is_inactive=False),
                                    required=False, label='Agente')
    campana = forms.ChoiceField(required=False, choices=())
    pagina = forms.CharField(required=False, widget=forms.HiddenInput())
    marcadas = forms.BooleanField(required=False)
    duracion = forms.IntegerField(required=False, min_value=0, initial=0,
                                  label=_(u'Duración mínima'),
                                  widget=forms.NumberInput(attrs={'class': 'form-control'}))

    def __init__(self, campana_choice, *args, **kwargs):
        super(GrabacionBusquedaForm, self).__init__(*args, **kwargs)
        campana_choice.insert(0, EMPTY_CHOICE)
        self.fields['campana'].choices = campana_choice


class CampanaMixinForm(object):
    def __init__(self, *args, **kwargs):
        super(CampanaMixinForm, self).__init__(*args, **kwargs)
        self.fields['bd_contacto'].required = not self.initial.get('es_template', False)
        if self.fields.get('bd_contacto', False):
            self.fields['bd_contacto'].queryset = BaseDatosContacto.objects.obtener_definidas()

    def requiere_bd_contacto(self):
        raise NotImplemented

    def clean(self):
        bd_contacto_field = self.fields.get('bd_contacto', False)
        if (bd_contacto_field and not bd_contacto_field.queryset.filter and
                self.requiere_bd_contacto()):
            message = _("Debe cargar una base de datos antes de comenzar a "
                        "configurar una campana")
            self.add_error('bd_contacto', message)
            raise forms.ValidationError(message, code='invalid')
        if self.cleaned_data.get('tipo_interaccion') is Campana.FORMULARIO and \
                not self.cleaned_data.get('formulario'):
            message = _("Debe seleccionar un formulario")
            self.add_error('formulario', message)
            raise forms.ValidationError(message, code='invalid')
        elif self.cleaned_data.get('tipo_interaccion') is Campana.SITIO_EXTERNO and \
                not self.cleaned_data.get('sitio_externo'):
            message = _("Debe seleccionar un sitio externo")
            self.add_error('formulario', message)
            raise forms.ValidationError(message, code='invalid')
        return super(CampanaMixinForm, self).clean()

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        validar_nombres_campanas(nombre)
        return nombre


class CampanaForm(CampanaMixinForm, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CampanaForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance.pk is None:
            self.fields['bd_contacto'].required = False
        else:
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
        fields = ('nombre', 'bd_contacto', 'formulario',
                  'sitio_externo', 'tipo_interaccion', 'objetivo')
        labels = {
            'bd_contacto': 'Base de Datos de Contactos',
        }

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'bd_contacto': forms.Select(attrs={'class': 'form-control'}),
            'formulario': forms.Select(attrs={'class': 'form-control'}),
            'sitio_externo': forms.Select(attrs={'class': 'form-control'}),
            'objetivo': forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo_interaccion': forms.RadioSelect(),
        }


class OpcionCalificacionForm(forms.ModelForm):
    class Meta:
        model = OpcionCalificacion
        fields = ('tipo', 'nombre', 'campana')

        widgets = {
            'nombre': forms.Select(),
            'usada_en_calificacion': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        nombres_calificaciones = kwargs.pop('nombres_calificaciones')
        super(OpcionCalificacionForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            # al modificar, en caso de que el valor del campo 'nombre' no esté entre las
            # calificaciones creadas se agrega
            choices = set(nombres_calificaciones + ((instance.nombre, instance.nombre),))
        else:
            # al crear se muestra en primer lugar una opción vacía
            choices = (EMPTY_CHOICE,) + nombres_calificaciones
        self.fields['nombre'] = forms.ChoiceField(choices=choices)

        if instance and instance.pk and instance.no_editable():
            self.fields['nombre'].disabled = True
            self.fields['tipo'].disabled = True
        else:
            self.fields['tipo'].choices = OpcionCalificacion.FORMULARIO_CHOICES_NO_AGENDA

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


class OpcionCalificacionBaseFormset(BaseInlineFormSet):

    def _construct_form(self, index, **kwargs):
        # adicionamos dinámicamente las nombres de calificaciones existentes en el sistema
        # para que el usuario pueda escoger de ellas al crear las opciones de calificación
        nombres_calificaciones_qs = NombreCalificacion.objects.usuarios().values_list(
            'nombre', flat=True)
        kwargs['nombres_calificaciones'] = tuple((nombre, nombre)
                                                 for nombre in nombres_calificaciones_qs)
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
            if nombre is None or tipo is None:
                raise forms.ValidationError(_("Rellene los campos en blanco"), code='invalid')
            if nombre in nombres:
                raise forms.ValidationError(
                    _("Los nombres de las opciones de calificación deben ser distintos"),
                    code="invalid")
            if tipo == OpcionCalificacion.GESTION:
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


class ContactoForm(forms.ModelForm):
    datos = forms.CharField(
        widget=forms.Textarea(attrs={'readonly': 'readonly'})
    )

    class Meta:
        model = Contacto
        fields = ('telefono', 'datos', 'bd_contacto')
        widgets = {
            'bd_contacto': forms.HiddenInput(),
        }


class OpcionCalificacionModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.nombre


class CalificacionClienteForm(forms.ModelForm):
    """
    Formulario para la creacion de Calificaciones de Clientes
    """

    opcion_calificacion = OpcionCalificacionModelChoiceField(
        OpcionCalificacion.objects.all(), empty_label='---------')

    def __init__(self, campana, *args, **kwargs):
        super(CalificacionClienteForm, self).__init__(*args, **kwargs)
        self.campana = campana
        self.fields['opcion_calificacion'].queryset = campana.opciones_calificacion.all()

    class Meta:
        model = CalificacionCliente
        fields = ('opcion_calificacion', 'observaciones')
        widgets = {
            'opcion_calificacion': forms.Select(attrs={'class': 'form-control'}),
        }


class GrupoAgenteForm(forms.Form):
    grupo = forms.ChoiceField(choices=())

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


class ReporteForm(forms.Form):
    """
    El form para reporte con fecha
    """
    fecha = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))


class FormularioForm(forms.ModelForm):

    class Meta:
        model = Formulario
        fields = ('nombre', 'descripcion')
        widgets = {
            "nombre": forms.TextInput(attrs={'class': 'form-control'}),
            "descripcion": forms.Textarea(attrs={'class': 'form-control'}),
        }


class FieldFormularioForm(forms.ModelForm):
    list_values = forms.MultipleChoiceField(widget=forms.SelectMultiple(
        attrs={'class': 'form-control', 'style': 'width:100%;',
               'disabled': 'disabled'}), required=False)
    value_item = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'disabled': 'disabled',
               'placeholder': 'agregar item a la lista'}), required=False)

    class Meta:
        model = FieldFormulario
        fields = ('formulario', 'nombre_campo', 'tipo', 'values_select',
                  'is_required')
        widgets = {
            'formulario': forms.HiddenInput(),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            "nombre_campo": forms.TextInput(attrs={'class': 'form-control'}),
            'values_select': forms.HiddenInput(),
        }


class OrdenCamposForm(forms.Form):
    sentido_orden = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(OrdenCamposForm, self).__init__(*args, **kwargs)
        self.fields['sentido_orden'].widget = forms.HiddenInput()


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


class SincronizaDialerForm(forms.Form):
    evitar_duplicados = forms.BooleanField(required=False)
    evitar_sin_telefono = forms.BooleanField(required=False)
    prefijo_discador = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'class-fecha form-control'}))
    columnas = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=(),
    )

    def __init__(self, tts_choices, *args, **kwargs):
        super(SincronizaDialerForm, self).__init__(*args, **kwargs)
        self.fields['columnas'].choices = tts_choices


class FormularioNuevoContacto(forms.ModelForm):

    def __init__(self, campos, *args, **kwargs):
        super(FormularioNuevoContacto, self).__init__(*args, **kwargs)
        for campo in campos:
            self.fields[convertir_ascii_string(campo)] = forms.CharField(
                label=campo, widget=forms.TextInput(
                    attrs={'class': 'form-control'}))

    class Meta:
        model = Contacto
        fields = ('telefono',)
        widgets = {
            "telefono": forms.TextInput(attrs={'class': 'form-control'}),
        }


class FormularioContactoCalificacion(forms.ModelForm):

    def __init__(self, campos, *args, **kwargs):
        super(FormularioContactoCalificacion, self).__init__(*args, **kwargs)
        for campo in campos:
            self.fields[convertir_ascii_string(campo)] = forms.CharField(
                required=False,
                label=campo, widget=forms.TextInput(
                    attrs={'class': 'form-control'}))

    class Meta:
        model = Contacto
        fields = ('telefono',)
        widgets = {
            "telefono": forms.TextInput(attrs={'class': 'form-control'}),
        }


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


class PausaForm(forms.ModelForm):

    class Meta:
        model = Pausa
        fields = ('nombre', 'tipo')
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        validar_nombres_campanas(nombre)
        return nombre


FormularioCalificacionFormSet = inlineformset_factory(
    Contacto, CalificacionCliente, form=CalificacionClienteForm,
    can_delete=False, extra=1, max_num=1)

OpcionCalificacionFormSet = inlineformset_factory(
    Campana, OpcionCalificacion, form=OpcionCalificacionForm,
    formset=OpcionCalificacionBaseFormset, extra=0, min_num=1)


class FormularioVentaForm(forms.ModelForm):

    def __init__(self, campos, *args, **kwargs):
        super(FormularioVentaForm, self).__init__(*args, **kwargs)

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

    class Meta:
        model = MetadataCliente
        fields = ('campana', 'contacto', 'agente')
        widgets = {
            'campana': forms.HiddenInput(),
            'contacto': forms.HiddenInput(),
            'agente': forms.HiddenInput(),
        }


FormularioVentaFormSet = inlineformset_factory(
    Contacto, MetadataCliente, form=FormularioVentaForm,
    can_delete=False, extra=1, max_num=1)


class AgendaContactoForm(forms.ModelForm):

    class Meta:
        model = AgendaContacto
        fields = ('contacto', 'agente', 'campana', 'tipo_agenda', 'fecha', 'hora', 'observaciones')
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
        if not kwargs['initial']['campana'].type == Campana.TYPE_DIALER:
            self.fields['tipo_agenda'].choices = [(AgendaContacto.TYPE_PERSONAL, 'PERSONAL')]

    def clean_tipo_agenda(self):
        campana = self.cleaned_data.get('campana', None)
        if not campana and campana.type == Campana.TYPE_DIALER:
            return AgendaContacto.TYPE_PERSONAL
        return self.cleaned_data['tipo_agenda']


class CampanaDialerForm(CampanaMixinForm, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CampanaDialerForm, self).__init__(*args, **kwargs)

        es_template = self.initial.get('es_template', False)

        self.fields['fecha_inicio'].help_text = 'Ejemplo: 10/04/2014'
        self.fields['fecha_fin'].help_text = 'Ejemplo: 20/04/2014'
        self.fields['fecha_inicio'].required = not es_template
        self.fields['fecha_fin'].required = not es_template

        if self.instance.pk:
            self.fields['bd_contacto'].disabled = True
            self.fields['formulario'].disabled = True
            self.fields['tipo_interaccion'].required = False

    def requiere_bd_contacto(self):
        return True

    def clean_bd_contacto(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            return instance.bd_contacto
        else:
            return self.cleaned_data['bd_contacto']

    def clean_formulario(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            return instance.formulario
        else:
            return self.cleaned_data['formulario']

    class Meta:
        model = Campana
        fields = ('nombre', 'fecha_inicio', 'fecha_fin',
                  'bd_contacto', 'formulario', 'sitio_externo',
                  'tipo_interaccion', 'objetivo')
        labels = {
            'bd_contacto': 'Base de Datos de Contactos',
        }

        widgets = {
            'bd_contacto': forms.Select(attrs={'class': 'form-control'}),
            'formulario': forms.Select(attrs={'class': 'form-control'}),
            'sitio_externo': forms.Select(attrs={'class': 'form-control'}),
            'tipo_interaccion': forms.RadioSelect(),
            'objetivo': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ParametroExtraParaWebformForm(forms.ModelForm):
    class Meta:
        model = ParametroExtraParaWebform
        fields = ('campana', 'parametro', 'columna')

    def clean_parametro(self):
        parametro = self.cleaned_data['parametro']
        validar_solo_ascii_y_sin_espacios(parametro)
        return parametro

    def clean_columna(self):
        columna = self.cleaned_data['columna']
        validar_solo_ascii_y_sin_espacios(columna)
        return columna


ParametroExtraParaWebformFormSet = inlineformset_factory(
    Campana, ParametroExtraParaWebform,
    form=ParametroExtraParaWebformForm, can_delete=True, extra=1)


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
            raise forms.ValidationError('debe seleccionar algun día')

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


class BacklistForm(forms.ModelForm):

    class Meta:
        model = Backlist
        fields = ('nombre', 'archivo_importacion')
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'archivo_importacion': forms.FileInput(attrs={'class': 'form-control'}),
        }


class SitioExternoForm(forms.ModelForm):

    class Meta:
        model = SitioExterno
        fields = ('nombre', 'url')

        widgets = {
            "nombre": forms.TextInput(attrs={'class': 'form-control'}),
            "url": forms.TextInput(attrs={'class': 'form-control'}),
        }


class ReglasIncidenciaForm(forms.ModelForm):

    class Meta:
        model = ReglasIncidencia
        fields = ('estado', 'intento_max', 'reintentar_tarde')

        widgets = {
            'estado': forms.Select(attrs={'class': 'form-control'}),
            "intento_max": forms.TextInput(attrs={'class': 'form-control'}),
            "reintentar_tarde": forms.TextInput(attrs={'class': 'form-control'}),
        }


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


class QueueDialerForm(forms.ModelForm):
    """
    El form de cola para las llamadas
    """

    class Meta:
        model = Queue
        fields = ('name', 'maxlen', 'wrapuptime', 'servicelevel', 'strategy', 'weight',
                  'wait', 'auto_grabacion', 'campana', 'detectar_contestadores',
                  'audio_para_contestadores', 'initial_predictive_model', 'initial_boost_factor')

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
            "initial_boost_factor": forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        initial_boost_factor = self.cleaned_data.get('initial_boost_factor')
        if initial_boost_factor and initial_boost_factor < 1.0:
            raise forms.ValidationError('El factor boost inicial no debe ser'
                                        ' menor a 1.0')

        initial_predictive_model = self.cleaned_data.get('initial_predictive_model')
        if initial_predictive_model and not initial_boost_factor:
            raise forms.ValidationError('El factor boost inicial no deber ser'
                                        ' none si la predicitvidad está activa')

        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        super(QueueDialerForm, self).__init__(*args, **kwargs)
        self.fields['audio_para_contestadores'].queryset = ArchivoDeAudio.objects.all()


class UserApiCrmForm(forms.ModelForm):

    class Meta:
        model = UserApiCrm
        fields = ('usuario', 'password')

        widgets = {
            "usuario": forms.TextInput(attrs={'class': 'form-control'}),
            "password": forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def clean_usuario(self):
        usuario = self.cleaned_data['usuario']
        if ' ' in usuario:
            raise forms.ValidationError(_('El usuario no puede contener espacios'))
        return usuario


ROL_CHOICES = ((SupervisorProfile.ROL_GERENTE, _(u'Supervisor Gerente')),
               (SupervisorProfile.ROL_ADMINISTRADOR, _(u'Administrador')),
               (SupervisorProfile.ROL_CLIENTE, _(u'Cliente')))


class SupervisorProfileForm(forms.ModelForm):
    rol = forms.ChoiceField(choices=ROL_CHOICES, label=_(u'Rol del usuario'),
                            initial=SupervisorProfile.ROL_GERENTE,
                            widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = SupervisorProfile
        fields = ('rol', )

    def __init__(self, rol, *args, **kwargs):
        super(SupervisorProfileForm, self).__init__(*args, **kwargs)
        self.fields['rol'].initial = rol


class CampanaSupervisorUpdateForm(forms.ModelForm):

    def __init__(self, supervisors_choices, *args, **kwargs):
        super(CampanaSupervisorUpdateForm, self).__init__(*args, **kwargs)
        self.fields['supervisors'].choices = supervisors_choices

    class Meta:
        model = Campana
        fields = ('supervisors',)


class CampanaManualForm(CampanaMixinForm, forms.ModelForm):
    auto_grabacion = forms.BooleanField(required=False)
    detectar_contestadores = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(CampanaManualForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance.pk is None:
            self.fields['bd_contacto'].required = False
        else:
            self.fields['bd_contacto'].required = True

    class Meta:
        model = Campana
        fields = ('nombre', 'formulario', 'bd_contacto',
                  'sitio_externo', 'tipo_interaccion', 'objetivo')

        widgets = {
            'formulario': forms.Select(attrs={'class': 'form-control'}),
            'sitio_externo': forms.Select(attrs={'class': 'form-control'}),
            'tipo_interaccion': forms.RadioSelect(),
            'objetivo': forms.NumberInput(attrs={'class': 'form-control'}),
            'bd_contacto': forms.Select(attrs={'class': 'form-control'}),
        }

    def requiere_bd_contacto(self):
        return False


class CampanaPreviewForm(CampanaMixinForm, forms.ModelForm):
    auto_grabacion = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(CampanaPreviewForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk and not self.initial.get('es_template', False):
            self.fields['bd_contacto'].disabled = True
            self.fields['tiempo_desconexion'].disabled = True

    class Meta:
        model = Campana
        fields = ('nombre', 'formulario',
                  'sitio_externo', 'tipo_interaccion', 'objetivo', 'bd_contacto',
                  'tiempo_desconexion')

        widgets = {
            'bd_contacto': forms.Select(attrs={'class': 'form-control'}),
            'formulario': forms.Select(attrs={'class': 'form-control'}),
            'sitio_externo': forms.Select(attrs={'class': 'form-control'}),
            'tipo_interaccion': forms.RadioSelect(),
            'objetivo': forms.NumberInput(attrs={'class': 'form-control'}),
            'tiempo_desconexion': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def requiere_bd_contacto(self):
        return True

    def clean_tiempo_desconexion(self):
        tiempo_desconexion = self.cleaned_data['tiempo_desconexion']
        if tiempo_desconexion < TIEMPO_MINIMO_DESCONEXION:
            msg = 'Debe ingresar un minimo de {0} minutos'.format(TIEMPO_MINIMO_DESCONEXION)
            raise forms.ValidationError(msg)
        return tiempo_desconexion


class CalificacionForm(forms.ModelForm):
    class Meta:
        model = NombreCalificacion
        fields = ('nombre',)

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if nombre == settings.CALIFICACION_REAGENDA:
            message = _('Esta calificación está reservada para el sistema')
            raise forms.ValidationError(message, code='invalid')
        return nombre


class ArchivoDeAudioForm(forms.ModelForm):

    class Meta:
        model = ArchivoDeAudio
        fields = ('descripcion', 'audio_original')
        widgets = {
            "descripcion": forms.TextInput(attrs={'class': 'form-control'}),
            "audio_original": forms.FileInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'audio_original': """Seleccione el archivo de audio que desea para
            la Campaña. Si ya existe uno y guarda otro, el audio será
            reemplazado.""",
        }

    def __init__(self, *args, **kwargs):
        super(ArchivoDeAudioForm, self).__init__(*args, **kwargs)
        self.fields['audio_original'].required = True

    def clean(self):
        cleaned_data = super(ArchivoDeAudioForm, self).clean()
        audio_original = cleaned_data.get('audio_original', False)
        if audio_original:
            validar_extension_archivo_audio(audio_original)
        return cleaned_data


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
        fields = ('nombre', 'auto_unpause', 'auto_attend_ics', 'auto_attend_inbound',
                  'auto_attend_dialer')
        widgets = {
            'auto_unpause': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(GrupoForm, self).__init__(*args, **kwargs)
        self.fields['auto_unpause'].required = False
