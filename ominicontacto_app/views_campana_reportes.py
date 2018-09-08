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

"""Vista de reportes de campana"""

from __future__ import unicode_literals

from django.views.generic import (
    ListView
)
from ominicontacto_app.models import (
    Campana
)

from ominicontacto_app.services.campana_service import CampanaService


import logging as logging_

logger = logging_.getLogger(__name__)


class LlamadasActivasView(ListView):
    """
    Esta vista lista las llamadas activas
    """

    template_name = 'campana/llamadas_activas.html'
    context_object_name = 'campanas'
    model = Campana

    def get_context_data(self, **kwargs):
        context = super(LlamadasActivasView, self).get_context_data(
            **kwargs)
        service = CampanaService()
        context['llamadas'] = service.obtener_calls_live()
        return context
