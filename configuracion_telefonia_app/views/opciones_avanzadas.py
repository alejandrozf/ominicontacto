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

import logging


from django.urls import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.views.generic import UpdateView

from configuracion_telefonia_app.models import AmdConf
from configuracion_telefonia_app.forms import AmdConfForm

from configuracion_telefonia_app.regeneracion_configuracion_telefonia import \
    SincronizadorDeConfiguracionAmdConfAsterisk


logger = logging.getLogger(__name__)


class ConfiguracionAMDUpdateView(UpdateView):
    """Vista que permite editar el modulo AMD de Asterisk"""
    model = AmdConf
    form_class = AmdConfForm
    template_name = 'editar_configuracion_amd.html'
    message = _('Se ha modificado la configuración AMD del sistema con éxito')

    def get_success_url(self):
        return reverse('ajustar_configuracion_amd', args=(1,))

    def form_valid(self, form):
        response = super(ConfiguracionAMDUpdateView, self).form_valid(form)
        sincronizador = SincronizadorDeConfiguracionAmdConfAsterisk()
        sincronizador.regenerar_asterisk()
        messages.add_message(self.request, messages.SUCCESS, self.message)
        return response
