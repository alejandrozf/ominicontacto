# -*- coding: utf-8 -*-


from django.conf import settings
from django import forms
from django.contrib.auth.forms import (
    UserChangeForm,
    UserCreationForm
)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Div, MultiField, HTML
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from ominicontacto_app.models import (
    User, AgenteProfile, Queue, QueueMember, BaseDatosContacto, Grabacion,
    Campana
)


class CustomUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('username', 'password', 'first_name', 'last_name', 'email', 'is_agente',
                  'is_customer', 'is_supervisor')

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
        'is_customer', 'is_supervisor')


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    password1 = forms.CharField(max_length=20,
                                required=False,
                                # will be overwritten by __init__()
                                help_text='Ingrese la nueva contraseña (sólo si desea cambiarla)',
                                # will be overwritten by __init__()
                                widget=forms.PasswordInput(),
                                label='Contrasena')

    password2 = forms.CharField(max_length=20,
                            required=False,  # will be overwritten by __init__()
                            help_text='Ingrese la nueva contraseña (sólo si desea cambiarla)',  # will be overwritten by __init__()
                            widget=forms.PasswordInput(),
                            label='Contrasena (otra vez)')

    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError('Los passwords no concuerdan')

        return self.cleaned_data

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_agente',
                  'is_customer', 'is_supervisor', 'password1', 'password2')


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

    def clean_sip_extension(self):
        sip_extension = self.cleaned_data['sip_extension']
        if settings.OL_SIP_LIMITE_INFERIOR > sip_extension or\
                sip_extension > settings.OL_SIP_LIMITE_SUPERIOR:
            raise forms.ValidationError("El sip_extension es incorrecto debe "
                                        "ingresar un numero entre {0} y {1}".
                                        format(settings.OL_SIP_LIMITE_INFERIOR,
                                               settings.OL_SIP_LIMITE_SUPERIOR))
        return sip_extension

    class Meta:
        model = AgenteProfile
        fields = ('sip_extension', 'sip_password', 'modulos', 'grupo')


class QueueForm(forms.ModelForm):
    """
    El form de cola para las llamadas
    """

    class Meta:
        model = Queue
        fields = ('name', 'timeout', 'retry', 'maxlen', 'wrapuptime',
                  'servicelevel', 'strategy', 'weight', 'type', 'wait',
                  'auto_grabacion', 'campana')

        help_texts = {
            'timeout': """En segundos """,
        }
        widgets = {
            'campana': forms.HiddenInput()
        }


class QueueMemberForm(forms.ModelForm):
    """
    El form de miembro de una cola
    """

    class Meta:
        model = QueueMember
        fields = ('member', 'penalty')


class QueueUpdateForm(forms.ModelForm):
    """
    El form para actualizar la cola para las llamadas
    """

    class Meta:
        model = Queue
        fields = ('timeout', 'retry', 'maxlen', 'wrapuptime',
                  'servicelevel', 'strategy', 'weight', 'type', 'wait',
                  'auto_grabacion')

        help_texts = {
            'timeout': """En segundos """,
        }


class BaseDatosContactoForm(forms.ModelForm):

    class Meta:
        model = BaseDatosContacto
        fields = ('nombre', 'archivo_importacion')


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
    buscar = forms.CharField(required=False,  widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'search pattern'}))


class GrabacionBusquedaForm(forms.ModelForm):
    """
    El form para la busqueda de grabaciones
    """
    fecha = forms.DateTimeField(required=False)
    tipo_llamada_choice = list(Grabacion.TYPE_LLAMADA_CHOICES)
    tipo_llamada_choice.insert(0, ('', '---------'))
    tipo_llamada = forms.ChoiceField(required=False,
                                     choices=tipo_llamada_choice)
    id_cliente = forms.CharField(required=False)
    tel_cliente = forms.CharField(required=False)
    sip_agente = forms.IntegerField(required=False)

    class Meta:
        model = Grabacion
        fields = ('fecha', 'tipo_llamada', 'id_cliente', 'tel_cliente',
                  'sip_agente')


class CampanaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CampanaForm, self).__init__(*args, **kwargs)

        self.fields['bd_contacto'].queryset =\
            BaseDatosContacto.objects.obtener_definidas()

        self.fields['fecha_inicio'].help_text = 'Ejemplo: 10/04/2014'
        self.fields['fecha_inicio'].required = True

        self.fields['fecha_fin'].help_text = 'Ejemplo: 20/04/2014'
        self.fields['fecha_fin'].required = True

    class Meta:
        model = Campana
        fields = ('nombre', 'fecha_inicio', 'fecha_fin', 'bd_contacto')
        labels = {
            'bd_contacto': 'Base de Datos de Contactos',
        }
