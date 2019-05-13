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

from django.utils.translation import ugettext_lazy as _
from django import forms
from django.forms.models import ModelChoiceField

from ominicontacto_app.models import Campana, AgenteProfile, Contacto, AgenteEnSistemaExterno


class Click2CallParametersBaseForm(forms.Form):
    phone = forms.CharField(max_length=128)

    def get_campana(self):
        return self.cleaned_data.get('idCampaign')

    def get_agente(self):
        raise NotImplementedError()

    def get_contacto_id(self):
        raise NotImplementedError()


class Click2CallOMLParametersForm(Click2CallParametersBaseForm):
    idCampaign = ModelChoiceField(queryset=Campana.objects.obtener_activas())
    idAgent = ModelChoiceField(queryset=AgenteProfile.objects.filter(is_inactive=False))
    idContact = ModelChoiceField(queryset=Contacto.objects.all(), required=False)

    def clean_idAgent(self):
        agente = self.cleaned_data.get('idAgent', None)
        campana = self.cleaned_data.get('idCampaign', None)
        if agente and campana:
            if campana.queue_campana.members.filter(id=agente.id).exists():
                return agente
            raise forms.ValidationError(_('El agente no participa en la campaña.'))

    def clean_idContact(self):
        campana = self.cleaned_data.get('idCampaign', None)
        contacto = self.cleaned_data.get('idContact', None)
        if campana and contacto:
            if contacto.bd_contacto == campana.bd_contacto:
                self._contacto = contacto
                return contacto
            raise forms.ValidationError(_('El contacto no corresponde a la campaña.'))

    def get_agente(self):
        return self.cleaned_data.get('idAgent')

    def get_contacto_id(self):
        contacto = self.cleaned_data.get('idContact', '')
        if contacto:
            return contacto.id
        return ''


class Click2CallExternalSiteParametersForm(Click2CallParametersBaseForm):
    idCampaign = ModelChoiceField(queryset=Campana.objects.obtener_activas(),
                                  to_field_name='id_externo')
    # No pueden ser ModelChoiceFields.
    idAgent = forms.CharField(max_length=128)
    idContact = forms.CharField(max_length=128, required=False)

    def __init__(self, sistema_externo, *args, **kwargs):
        super(Click2CallExternalSiteParametersForm, self).__init__(*args, **kwargs)
        self.sistema_externo = sistema_externo
        self.fields['idCampaign'].queryset = Campana.objects.filter(sistema_externo=sistema_externo)
        self._contacto = None

    def clean_idAgent(self):
        idAgent = self.cleaned_data.get('idAgent', None)
        campana = self.cleaned_data.get('idCampaign', None)
        if idAgent and campana:
            try:
                agente_en_sistema = AgenteEnSistemaExterno.objects.get(
                    sistema_externo=self.sistema_externo,
                    id_externo_agente=idAgent)
                if campana.queue_campana.members.filter(id=agente_en_sistema.agente.id).exists():
                    self._agente = agente_en_sistema.agente
                    return idAgent
                raise forms.ValidationError(_('El agente no participa en la campaña.'))
            except AgenteEnSistemaExterno.DoesNotExist:
                raise forms.ValidationError(_('El agente no corresponde al sistema externo.'))

    def clean_idContact(self):
        campana = self.cleaned_data.get('idCampaign', None)
        contacto = self.cleaned_data.get('idContact', None)
        if campana and contacto:
            try:
                contacto = campana.bd_contacto.contactos.get(id_externo=contacto)
                self._contacto = contacto
                return contacto
            except Contacto.DoesNotExist:
                self._contacto = None

    def get_agente(self):
        return self._agente

    def get_contacto_id(self):
        if self._contacto is None:
            return ''
        return self._contacto.id
