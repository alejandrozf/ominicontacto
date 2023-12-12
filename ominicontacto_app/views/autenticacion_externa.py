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

from constance import config as config_constance

from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import FormView

from ominicontacto_app.forms.base import AutenticacionExternaForm
from ominicontacto_app.models import AutenticacionExternaDeUsuario


class ConfigurarAutenticacionExternaView(FormView):
    template_name = 'autenticacion_externa.html'
    form_class = AutenticacionExternaForm
    success_url = reverse_lazy('security_external_authentication')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        initial = {}
        initial['tipo'] = config_constance.EXTERNAL_AUTH_TYPE
        initial['servidor'] = config_constance.EXTERNAL_AUTH_SERVER
        initial['base_dn'] = config_constance.EXTERNAL_AUTH_DN
        initial['activacion'] = config_constance.EXTERNAL_AUTH_ACTIVATION
        initial['ms_simple_auth'] = config_constance.EXTERNAL_AUTH_MS_SIMPLE_AUTH
        kwargs['initial'] = initial
        return kwargs

    def form_valid(self, form):
        tipo = form.cleaned_data.get('tipo')
        config_constance.EXTERNAL_AUTH_TYPE = tipo
        config_constance.EXTERNAL_AUTH_SERVER = form.cleaned_data.get('servidor')
        config_constance.EXTERNAL_AUTH_DN = form.cleaned_data.get('base_dn')
        activacion = form.cleaned_data.get('activacion')
        config_constance.EXTERNAL_AUTH_ACTIVATION = activacion
        ms_simple_auth = form.cleaned_data.get('ms_simple_auth')
        config_constance.EXTERNAL_AUTH_MS_SIMPLE_AUTH = ms_simple_auth

        if tipo == 'LDAP':
            if activacion == AutenticacionExternaDeUsuario.MANUAL_ACTIVO:
                AutenticacionExternaDeUsuario.establecer_manual_defaults(True)
            if activacion == AutenticacionExternaDeUsuario.MANUAL_INACTIVO:
                AutenticacionExternaDeUsuario.establecer_manual_defaults(False)

        messages.add_message(
            self.request,
            messages.SUCCESS,
            _('Configuración de autenticación actualizada'),
        )
        self.request
        return super().form_valid(form)
