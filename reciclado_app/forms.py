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

from django import forms
from django.utils.translation import gettext_lazy as _


class RecicladoForm(forms.Form):
    CHOICES = [('nueva_campaña', 'Reciclar y crear una nueva campaña'),
               ('misma_campana', 'Reciclar y utilizar la campaña actual')]

    reciclado_radio = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect())
    retomar_contactacion = forms.BooleanField(
        required=False, widget=forms.CheckboxInput(attrs={'class': 'form-control'}),
        label=_('Retomar contactación'), initial=False)

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
