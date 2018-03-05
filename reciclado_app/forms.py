# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms


class RecicladoForm(forms.Form):

    def __init__(self, *args, **kwargs):
        reciclado_choice = kwargs.pop('reciclado_choice', None)

        super(RecicladoForm, self).__init__(*args, **kwargs)
        self.fields['reciclado_tipos'] = forms.MultipleChoiceField(
            choices=reciclado_choice,
            widget=forms.CheckboxSelectMultiple(
                attrs={'class': 'form-control'}),)
