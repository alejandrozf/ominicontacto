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

from django.utils.translation import ugettext as _
from django import forms

from ominicontacto_app.utiles import convert_fecha_datetime
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


class ReporteLlamadasForm(forms.Form):
    """
    El form para reporte de llamadas
    """
    fecha = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    finalizadas = forms.BooleanField(required=False, label=_(u'Incluir campañas finalizadas'))

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        try:
            fecha_desde, fecha_hasta = fecha.split('-')
            fecha_desde = convert_fecha_datetime(fecha_desde)
            fecha_hasta = convert_fecha_datetime(fecha_hasta, final_dia=True)
        except ValueError:
            raise forms.ValidationError(_('Formato inválido'))
        self.desde = fecha_desde
        self.hasta = fecha_hasta
        return fecha


class EstadisticasJSONForm(forms.Form):
    estadisticas = forms.CharField()

    def clean_estadisticas(self):
        estadisticas = self.cleaned_data.get('estadisticas')
        try:
            json_data = json.loads(estadisticas)
        except ValueError:
            raise forms.ValidationError(_(u'Formato JSON invalido'))
        return json_data


TIPO_REPORTE_CHOICES = (
    ('llamadas_por_tipo', ''),
    ('llamadas_por_campana', ''),
    ('tipos_de_llamada_manual', ''),
    ('tipos_de_llamada_dialer', ''),
    ('tipos_de_llamada_entrante', ''),
    ('tipos_de_llamada_preview', ''),
)


class ExportarReporteLlamadasForm(EstadisticasJSONForm):
    tipo_reporte = forms.ChoiceField(choices=TIPO_REPORTE_CHOICES, required=True)
