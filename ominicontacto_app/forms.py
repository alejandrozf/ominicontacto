# -*- coding: utf-8 -*-


from django.conf import settings
from django import forms
from django.contrib.auth.forms import (
    UserChangeForm,
    UserCreationForm
)
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from ominicontacto_app.models import (User, AgenteProfile, Queue, QueueMember)


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

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_agente',
                  'is_customer', 'is_supervisor')


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
                  'servicelevel', 'strategy', 'weight')

        help_texts = {
            'timeout': """En segundos """,
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
                  'servicelevel', 'strategy', 'weight')

        help_texts = {
            'timeout': """En segundos """,
        }
