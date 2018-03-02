# -*- coding: utf-8 -*-

""" Vistas para el reciclados de las campanas"""

from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.views.generic import FormView
from ominicontacto_app.models import Campana
from reciclado_app.forms import RecicladoForm

import logging as logging_


logger = logging_.getLogger(__name__)


class ReciclarCampanaDialerFormView(FormView):
    """
    Esta vista muestra los distintos tipo de reciclados de las campanas
    dialer
    """

    form_class = RecicladoForm
    template_name = 'nuevo_reciclado.html'

    def get_form_kwargs(self):
        kwargs = super(ReciclarCampanaDialerFormView, self).get_form_kwargs()
        reciclado_choice = None
        kwargs['reciclado_choice'] = reciclado_choice
        return kwargs

    def form_valid(self, form):
        return super(ReciclarCampanaDialerFormView, self).form_valid(form)

    def get_success_url(self):
        reverse('view_blanco')
