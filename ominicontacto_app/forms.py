# -*- coding: utf-8 -*-


import json
from django import forms
from django.forms.models import inlineformset_factory
from django.contrib.auth.forms import (
    UserChangeForm,
    UserCreationForm
)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Div, MultiField, HTML
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from ominicontacto_app.models import (
    User, AgenteProfile, Queue, QueueMember, BaseDatosContacto, Grabacion,
    Campana, Contacto, CalificacionCliente, Grupo, Formulario, FieldFormulario, Pausa,
    MetadataCliente, AgendaContacto, CampanaDialer, CampanaMember, ActuacionVigente,
    Backlist, SitioExterno, ReglasIncidencia
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


class QueueForm(forms.ModelForm):
    """
    El form de cola para las llamadas
    """

    def __init__(self, *args, **kwargs):
        super(QueueForm, self).__init__(*args, **kwargs)
        self.fields['timeout'].required = True
        self.fields['retry'].required = True

    class Meta:
        model = Queue
        fields = ('name', 'timeout', 'retry', 'maxlen', 'wrapuptime',
                  'servicelevel', 'strategy', 'weight', 'wait',
                  'auto_grabacion', 'campana')

        help_texts = {
            'timeout': """En segundos """,
        }
        widgets = {
            'campana': forms.HiddenInput(),
            'name': forms.HiddenInput(),
        }


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


class QueueUpdateForm(forms.ModelForm):
    """
    El form para actualizar la cola para las llamadas
    """

    def __init__(self, *args, **kwargs):
        super(QueueUpdateForm, self).__init__(*args, **kwargs)
        self.fields['timeout'].required = True
        self.fields['retry'].required = True

    class Meta:
        model = Queue
        fields = ('timeout', 'retry', 'maxlen', 'wrapuptime',
                  'servicelevel', 'strategy', 'weight', 'wait',
                  'auto_grabacion')

        help_texts = {
            'timeout': """En segundos """,
        }

    def clean(self):
        maxlen = self.cleaned_data.get('maxlen')
        if not maxlen > 0:
            raise forms.ValidationError('Cantidad Max de llamadas debe ser'
                                        ' mayor a cero')

        return self.cleaned_data


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


class GrabacionBusquedaForm(forms.Form):
    """
    El form para la busqueda de grabaciones
    """
    fecha = forms.CharField(required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    tipo_llamada_choice = list(Grabacion.TYPE_LLAMADA_CHOICES)
    tipo_llamada_choice.insert(0, ('', '---------'))
    tipo_llamada = forms.ChoiceField(required=False,
                                     choices=tipo_llamada_choice)
    tel_cliente = forms.CharField(required=False)
    sip_agente = forms.ChoiceField(required=False, label='Agente', choices=())
    campana = forms.ChoiceField(required=False, choices=())
    pagina = forms.CharField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(GrabacionBusquedaForm, self).__init__(*args, **kwargs)
        agente_choice = [(agente.sip_extension, agente.user.get_full_name())
                        for agente in AgenteProfile.objects.all()]
        agente_choice.insert(0, ('', '---------'))
        self.fields['sip_agente'].choices = agente_choice
        campana_choice = [(campana.pk, campana.nombre)
                         for campana in Campana.objects.all()]
        campana_choice.insert(0, ('', '---------'))
        self.fields['campana'].choices = campana_choice


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
        fields = ('nombre', 'fecha_inicio', 'fecha_fin', 'calificacion_campana',
                  'bd_contacto', 'formulario', 'gestion', 'sitio_externo', 'tipo_interaccion')
        labels = {
            'bd_contacto': 'Base de Datos de Contactos',
        }

        widgets = {
            'calificacion_campana': forms.Select(attrs={'class': 'form-control'}),
            'bd_contacto': forms.Select(attrs={'class': 'form-control'}),
            'formulario': forms.Select(attrs={'class': 'form-control'}),
            "gestion": forms.TextInput(attrs={'class': 'form-control'}),
            'sitio_externo': forms.Select(attrs={'class': 'form-control'}),
            "tipo_interaccion": forms.RadioSelect(),
        }


class CampanaUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CampanaUpdateForm, self).__init__(*args, **kwargs)

        self.fields['bd_contacto'].queryset = \
            BaseDatosContacto.objects.obtener_definidas()

        self.fields['fecha_inicio'].help_text = 'Ejemplo: 10/04/2014'
        self.fields['fecha_inicio'].required = True

        self.fields['fecha_fin'].help_text = 'Ejemplo: 20/04/2014'
        self.fields['fecha_fin'].required = True

    class Meta:
        model = Campana
        fields = ('nombre', 'fecha_inicio', 'fecha_fin', 'calificacion_campana',
                  'bd_contacto', 'gestion')
        labels = {
            'bd_contacto': 'Base de Datos de Contactos',
        }
        widgets = {
            'calificacion_campana': forms.Select(attrs={'class': 'form-control'}),
            'bd_contacto': forms.Select(attrs={'class': 'form-control'}),
            "nombre": forms.TextInput(attrs={'class': 'form-control'}),
            "gestion": forms.TextInput(attrs={'class': 'form-control'}),
        }


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


class ExportaDialerForm(forms.Form):
    campana = forms.ChoiceField(choices=())
    usa_contestador = forms.BooleanField(required=False)
    evitar_duplicados = forms.BooleanField(required=False)
    evitar_sin_telefono = forms.BooleanField(required=False)
    prefijo_discador = forms.CharField(required=False)
    telefonos = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=(),
    )

    def __init__(self, campana_choice, tts_choices, *args, **kwargs):
        super(ExportaDialerForm, self).__init__(*args, **kwargs)
        self.fields['campana'].choices = campana_choice
        self.fields['telefonos'].choices = tts_choices


class CalificacionClienteForm(forms.ModelForm):

    def __init__(self, calificacion_choice, gestion, *args, **kwargs):
        super(CalificacionClienteForm, self).__init__(*args, **kwargs)
        self.fields['calificacion'].queryset = calificacion_choice
        self.fields['calificacion'].empty_label = None
        self.fields['calificacion'].empty_label = gestion

    class Meta:
        model = CalificacionCliente
        fields = ('campana', 'contacto', 'es_venta', 'calificacion', 'agente',
                  'observaciones', 'agendado')
        widgets = {
            'campana': forms.HiddenInput(),
            'contacto': forms.HiddenInput(),
            'es_venta': forms.HiddenInput(),
            'agente': forms.HiddenInput(),
            'agendado': forms.HiddenInput(),
        }


class GrupoAgenteForm(forms.Form):
    grupo = forms.ChoiceField(choices=())

    def __init__(self, *args, **kwargs):
        super(GrupoAgenteForm, self).__init__(*args, **kwargs)
        grupo_choice = [(grupo.id, grupo.nombre)
                        for grupo in Grupo.objects.all()]
        self.fields['grupo'].choices = grupo_choice


class GrabacionReporteForm(forms.Form):
    """
    El form para reporte de grabaciones
    """
    fecha = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))


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
    usa_contestador = forms.BooleanField(required=False)
    evitar_duplicados = forms.BooleanField(required=False)
    evitar_sin_telefono = forms.BooleanField(required=False)
    prefijo_discador = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'class-fecha form-control'}))
    telefonos = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=(),
    )

    def __init__(self, tts_choices, *args, **kwargs):
        super(SincronizaDialerForm, self).__init__(*args, **kwargs)
        self.fields['telefonos'].choices = tts_choices


class FormularioNuevoContacto(forms.ModelForm):

    def __init__(self, campos, *args, **kwargs):
        super(FormularioNuevoContacto, self).__init__(*args, **kwargs)
        for campo in campos:
            self.fields[campo] = forms.CharField(
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
            self.fields[campo] = forms.CharField(required=False,
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
    usa_contestador = forms.BooleanField(required=False)
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


class PausaForm(forms.ModelForm):

    class Meta:
        model = Pausa
        fields = ('nombre', )

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if ' ' in nombre:
            raise forms.ValidationError('el nombre no puede contener espacios')
        return nombre


FormularioCalificacionFormSet = inlineformset_factory(
    Contacto, CalificacionCliente, form=CalificacionClienteForm,
    can_delete=False)


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
        fields = ('contacto', 'agente', 'tipo_agenda', 'fecha', 'hora', 'observaciones')
        widgets = {
            'contacto': forms.HiddenInput(),
            'agente': forms.HiddenInput(),
            'tipo_agenda': forms.Select(attrs={'class': 'form-control'}),
            "observaciones": forms.Textarea(attrs={'class': 'form-control'}),
            "fecha": forms.TextInput(attrs={'class': 'form-control'}),
            "hora": forms.TextInput(attrs={'class': 'form-control'}),
        }


class CampanaDialerForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CampanaDialerForm, self).__init__(*args, **kwargs)

        self.fields['bd_contacto'].queryset =\
            BaseDatosContacto.objects.obtener_definidas()

        self.fields['fecha_inicio'].help_text = 'Ejemplo: 10/04/2014'
        self.fields['fecha_inicio'].required = True

        self.fields['fecha_fin'].help_text = 'Ejemplo: 20/04/2014'
        self.fields['fecha_fin'].required = True

    class Meta:
        model = CampanaDialer
        fields = ('nombre', 'fecha_inicio', 'fecha_fin', 'calificacion_campana',
                  'bd_contacto', 'formulario', 'gestion', 'maxlen', 'wrapuptime',
                  'servicelevel', 'strategy', 'weight', 'wait', 'auto_grabacion',
                  'sitio_externo', 'tipo_interaccion')
        labels = {
            'bd_contacto': 'Base de Datos de Contactos',
        }
        widgets = {
            'calificacion_campana': forms.Select(attrs={'class': 'form-control'}),
            'bd_contacto': forms.Select(attrs={'class': 'form-control'}),
            'formulario': forms.Select(attrs={'class': 'form-control'}),
            'sitio_externo': forms.Select(attrs={'class': 'form-control'}),
            "gestion": forms.TextInput(attrs={'class': 'form-control'}),
            "maxlen": forms.TextInput(attrs={'class': 'form-control'}),
            "wrapuptime": forms.TextInput(attrs={'class': 'form-control'}),
            "servicelevel": forms.TextInput(attrs={'class': 'form-control'}),
            'strategy': forms.Select(attrs={'class': 'form-control'}),
            "weight": forms.TextInput(attrs={'class': 'form-control'}),
            "wait": forms.TextInput(attrs={'class': 'form-control'}),
            "tipo_interaccion": forms.RadioSelect(),
        }


class CampanaDialerUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CampanaDialerUpdateForm, self).__init__(*args, **kwargs)

        self.fields['fecha_inicio'].help_text = 'Ejemplo: 10/04/2014'
        self.fields['fecha_inicio'].required = True

        self.fields['fecha_fin'].help_text = 'Ejemplo: 20/04/2014'
        self.fields['fecha_fin'].required = True

    class Meta:
        model = Campana
        fields = ('nombre', 'fecha_inicio', 'fecha_fin', 'calificacion_campana',
                  'gestion')

        widgets = {
            'calificacion_campana': forms.Select(attrs={'class': 'form-control'}),
            "nombre": forms.TextInput(attrs={'class': 'form-control'}),
            "gestion": forms.TextInput(attrs={'class': 'form-control'}),
        }

class UpdateBaseDatosDialerForm(forms.ModelForm):
    usa_contestador = forms.BooleanField(required=False)
    evitar_duplicados = forms.BooleanField(required=False)
    evitar_sin_telefono = forms.BooleanField(required=False)
    prefijo_discador = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'class-fecha form-control'}))
    telefonos = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=(),
    )

    def __init__(self, tts_choices, *args, **kwargs):
        super(UpdateBaseDatosDialerForm, self).__init__(*args, **kwargs)
        self.fields['telefonos'].choices = tts_choices

    class Meta:
        model = CampanaDialer
        fields = ('bd_contacto',)
        labels = {
            'bd_contacto': 'Base de Datos de Contactos',
        }
        widgets = {
            'bd_contacto': forms.Select(attrs={'class': 'form-control'}),
        }


class CampanaMemberForm(forms.ModelForm):
    """
    El form de miembro de una cola
    """

    class Meta:
        model = CampanaMember
        fields = ('member', 'penalty')


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
        if domingo==lunes==martes==miercoles==jueves==viernes==sabado==False:
            raise forms.ValidationError('debe seleccionar algun día')

        return self.cleaned_data

    class Meta:
        model = ActuacionVigente
        fields = ('campana', 'domingo', 'lunes', 'martes', 'miercoles', 'jueves',
                  'viernes', 'sabado', 'hora_desde', 'hora_hasta')
        widgets = {
            'campana': forms.HiddenInput(),
            'dia_semanal': forms.Select(attrs={'class': 'form-control'}),
            "hora_desde": forms.TextInput(attrs={'class': 'form-control'}),
            "hora_hasta": forms.TextInput(attrs={'class': 'form-control'}),
        }


class BacklistForm(forms.ModelForm):

    class Meta:
        model = Backlist
        fields = ('nombre', 'archivo_importacion')


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
        fields = ('campana', 'estado', 'intento_max', 'reintentar_tarde')

        widgets = {
            'campana': forms.HiddenInput(),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            "intento_max": forms.TextInput(attrs={'class': 'form-control'}),
            "reintentar_tarde": forms.TextInput(attrs={'class': 'form-control'}),
        }


class QueueDialerForm(forms.ModelForm):
    """
    El form de cola para las llamadas
    """

    class Meta:
        model = Queue
        fields = ('name', 'maxlen', 'wrapuptime', 'servicelevel', 'strategy', 'weight',
                  'wait', 'auto_grabacion', 'campana')

        widgets = {
            'campana': forms.HiddenInput(),
            'name': forms.HiddenInput(),
            "maxlen": forms.TextInput(attrs={'class': 'form-control'}),
            "wrapuptime": forms.TextInput(attrs={'class': 'form-control'}),
            "servicelevel": forms.TextInput(attrs={'class': 'form-control'}),
            'strategy': forms.Select(attrs={'class': 'form-control'}),
            "weight": forms.TextInput(attrs={'class': 'form-control'}),
            "wait": forms.TextInput(attrs={'class': 'form-control'}),
        }


class QueueDialerUpdateForm(forms.ModelForm):
    """
    El form para actualizar la cola para las llamadas
    """

    class Meta:
        model = Queue
        fields = ('maxlen', 'wrapuptime', 'servicelevel', 'strategy', 'weight', 'wait',
                  'auto_grabacion')
        widgets = {
            "maxlen": forms.TextInput(attrs={'class': 'form-control'}),
            "wrapuptime": forms.TextInput(attrs={'class': 'form-control'}),
            "servicelevel": forms.TextInput(attrs={'class': 'form-control'}),
            'strategy': forms.Select(attrs={'class': 'form-control'}),
            "weight": forms.TextInput(attrs={'class': 'form-control'}),
            "wait": forms.TextInput(attrs={'class': 'form-control'}),
        }


    def clean(self):
        maxlen = self.cleaned_data.get('maxlen')
        if not maxlen > 0:
            raise forms.ValidationError('Cantidad Max de llamadas debe ser'
                                        ' mayor a cero')

        return self.cleaned_data
