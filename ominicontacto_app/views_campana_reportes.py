# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import datetime
from django.contrib import messages

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
