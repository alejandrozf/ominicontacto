# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from ominicontacto_app.models import (
    CampanaDialer
)
from django.views.generic import (
    ListView
)

import logging as logging_

logger = logging_.getLogger(__name__)


class CampanaDialerListView(ListView):
    """
    Esta vista lista los objetos CampanaDialer
    """

    template_name = 'campana_dialer/campana_list.html'
    context_object_name = 'campanas'
    model = CampanaDialer

    def get_context_data(self, **kwargs):
        context = super(CampanaDialerListView, self).get_context_data(
           **kwargs)
        context['inactivas'] = CampanaDialer.objects.obtener_inactivas()
        context['pausadas'] = CampanaDialer.objects.obtener_pausadas()
        context['activas'] = CampanaDialer.objects.obtener_activas()
        context['borradas'] = CampanaDialer.objects.obtener_borradas().filter(
            oculto=False)
        return context