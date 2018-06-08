# -*- coding: utf-8 -*-

from django import forms

from configuracion_telefonia_app.models import TroncalSIP


class TroncalSIPForm(forms.ModelForm):

    class Meta:
        model = TroncalSIP
        exclude = ()
        widgets = {
            "nombre": forms.TextInput(attrs={'class': 'form-control'}),
            "canales_maximos": forms.NumberInput(attrs={'class': 'form-control'}),
            "caller_id": forms.TextInput(attrs={'class': 'form-control'}),
            "register_string": forms.TextInput(attrs={'class': 'form-control'}),
            "caller_id": forms.TextInput(attrs={'class': 'form-control'}),
            "text_config": forms.Textarea(attrs={'class': 'form-control'}),
        }
