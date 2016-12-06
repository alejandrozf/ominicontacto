# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, FormView
)
from ominicontacto_app.models import Formulario, FieldFormulario
from ominicontacto_app.forms import FormularioForm

import logging as logging_

logger = logging_.getLogger(__name__)


class FormularioCreateView(CreateView):
    model = Formulario
    form_class = FormularioForm
    template_name = 'formulario/formulario_create_update_form.html'

    def get_success_url(self):
        return reverse('formulario_list')


class FormularioListView(ListView):
    template_name = 'formulario/formulario_list.html'
    model = Formulario