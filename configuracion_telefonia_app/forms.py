# -*- coding: utf-8 -*-

from django import forms

from django.forms.models import inlineformset_factory

from configuracion_telefonia_app.models import (PatronDeDiscado, RutaSaliente,
                                                TroncalSIP, OrdenTroncal)


class TroncalSIPForm(forms.ModelForm):

    class Meta:
        model = TroncalSIP
        exclude = ()
        widgets = {
            "nombre": forms.TextInput(attrs={'class': 'form-control'}),
            "canales_maximos": forms.NumberInput(attrs={'class': 'form-control'}),
            "caller_id": forms.TextInput(attrs={'class': 'form-control'}),
            "register_string": forms.TextInput(attrs={'class': 'form-control'}),
            "text_config": forms.Textarea(attrs={'class': 'form-control'}),
        }


class PatronDeDiscadoForm(forms.ModelForm):

    class Meta:
        model = PatronDeDiscado
        exclude = ()


class RutaSalienteForm(forms.ModelForm):

    class Meta:
        model = RutaSaliente
        exclude = ()


PatronDeDiscadoFormset = inlineformset_factory(
    RutaSaliente, PatronDeDiscado, form=PatronDeDiscadoForm, can_delete=True, extra=0, min_num=1)

OrdenTroncalFormset = inlineformset_factory(
    RutaSaliente, OrdenTroncal, fields=('troncal',), can_delete=True, extra=0, min_num=1)
