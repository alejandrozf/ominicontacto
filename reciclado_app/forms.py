# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms


class RecicladoForm(forms.Form):
    CHOICES = [('nueva_campaña', 'Reciclar y crear una nueva campaña'),
               ('misma_campana', 'Reciclar y utilizar la campaña actual')]

    reciclado_radio = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect())

    def __init__(self, *args, **kwargs):
        reciclado_choice = kwargs.pop('reciclado_choice', None)
        no_contactados_choice = kwargs.pop('no_contactados_choice', None)

        super(RecicladoForm, self).__init__(*args, **kwargs)
        self.fields['reciclado_calificacion'] = forms.MultipleChoiceField(
            required=False,
            choices=reciclado_choice,
            widget=forms.CheckboxSelectMultiple(
                attrs={'class': 'form-control'}),)
        self.fields['reciclado_no_contactacion'] = forms.MultipleChoiceField(
            required=False,
            choices=no_contactados_choice,
            widget=forms.CheckboxSelectMultiple(
                attrs={'class': 'form-control'}), )
