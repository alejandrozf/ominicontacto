# -*- coding: utf-8 -*-

""" Vistas para el reciclados de las campanas"""

from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.views.generic import FormView

import logging as logging_


logger = logging_.getLogger(__name__)


class ReciclarCampanaDialerFormView(FormView):
    """
    Esta vista muestra los distintos tipo de reciclados de las campanas
    dialer
    """

    form_class = None
    template_name = 'nuevo_reciclado.html'

    def get_form(self):

        return self.form_class(**self.get_form_kwargs())

    def form_valid(self, form):
        return super(ReciclarCampanaDialerFormView, self).form_valid(form)

    def get_success_url(self):
        reverse('view_blanco')
