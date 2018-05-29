# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from ominicontacto_app.models import (
    AgenteProfile, Grupo
)


EMPTY_CHOICE = ('', '---------')


class ReporteAgentesForm(forms.Form):
    """
    El form para reporte con fecha
    """
    fecha = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    agente = forms.MultipleChoiceField(required=False, choices=())
    grupo_agente = forms.ChoiceField(required=False, choices=(), widget=forms.Select(
        attrs={'class': 'form-control'}))
    todos_agentes = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(ReporteAgentesForm, self).__init__(*args, **kwargs)

        agente_choice = [(agente.pk, agente.user.get_full_name())
                         for agente in AgenteProfile.objects.filter(is_inactive=False)]
        self.fields['agente'].choices = agente_choice
        grupo_choice = [(grupo.id, grupo.nombre)
                        for grupo in Grupo.objects.all()]
        grupo_choice.insert(0, EMPTY_CHOICE)
        self.fields['grupo_agente'].choices = grupo_choice
