# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, FormView
)
from ominicontacto_app.models import Formulario, FieldFormulario
from ominicontacto_app.forms import FormularioForm, FieldFormularioForm

import logging as logging_

logger = logging_.getLogger(__name__)


class FormularioCreateView(CreateView):
    model = Formulario
    form_class = FormularioForm
    template_name = 'formulario/formulario_create_update_form.html'

    def get_success_url(self):
        return reverse('formulario_field',
                       kwargs={"pk_formulario": self.object.pk}
                       )


class FormularioListView(ListView):
    template_name = 'formulario/formulario_list.html'
    model = Formulario


class FieldFormularioCreateView(CreateView):
    model = FieldFormulario
    template_name = 'formulario/formulario_field.html'
    context_object_name = 'fieldformulario'
    form_class = FieldFormularioForm

    def get_initial(self):
        initial = super(FieldFormularioCreateView, self).get_initial()
        formulario = Formulario.objects.get(pk=self.kwargs['pk_formulario'])
        initial.update({'formulario': formulario.id})
        return initial

    def get_context_data(self, **kwargs):
        context = super(
            FieldFormularioCreateView, self).get_context_data(**kwargs)
        formulario = Formulario.objects.get(pk=self.kwargs['pk_formulario'])
        context['formulario'] = formulario
        return context

    def get_success_url(self):
        return reverse('formulario_field',
                       kwargs={"pk_formulario": self.kwargs['pk_formulario']}
                       )
