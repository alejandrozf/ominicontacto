# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic.edit import (
    CreateView
)
from ominicontacto_app.models import SitioExterno
from ominicontacto_app.forms import SitioExternoForm


class SitioExternoCreateView(CreateView):
    model = SitioExterno
    template_name = 'sitio_externo/create_update_form.html'
    form_class = SitioExternoForm

    def get_success_url(self):
        return reverse('view_blanco')