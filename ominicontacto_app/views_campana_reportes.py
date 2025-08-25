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

"""Vista de reportes de campana"""

from __future__ import unicode_literals

from django.views.generic import (
    ListView
)
from ominicontacto_app.models import (
    Campana
)

from ominicontacto_app.services.dialer.campana_wombat import CampanaService


import logging as logging_

logger = logging_.getLogger(__name__)


class LlamadasActivasView(ListView):
    """
    Esta vista lista las llamadas activas
    """

    template_name = 'campanas/campana_entrante/llamadas_activas.html'
    context_object_name = 'campanas'
    model = Campana

    def get_context_data(self, **kwargs):
        context = super(LlamadasActivasView, self).get_context_data(
            **kwargs)
        service = CampanaService()  # TODO: Ver si Omnidialer requiere funcinalidad similar
        context['llamadas'] = service.obtener_calls_live()
        return context
