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

"""Aca se encuentran las vistas con la creacion de los formularios dinamico en la
caso de que califica como gestion(que generalmente vulgarmente llamada venta)"""

from __future__ import unicode_literals
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect
from django.views.generic import (
    FormView, TemplateView
)
from django.utils.translation import ugettext as _
from ominicontacto_app.models import Formulario
from ominicontacto_app.forms import (FormularioCRMForm)
import logging as logging_

logger = logging_.getLogger(__name__)


class FormularioListView(TemplateView):
    """Vista para listar los formularios"""
    template_name = 'formulario/formulario_list.html'


class FormularioPreviewFormView(FormView):
    """Vista para ver el formulario una vez finalizado"""
    form_class = FormularioCRMForm
    template_name = 'formulario/formulario_preview.html'

    def dispatch(self, *args, **kwargs):
        formulario = Formulario.objects.get(pk=self.kwargs['pk_formulario'])
        campos = formulario.campos.all()

        if not campos.exists():
            message = _("No está permitido crear un formulario vacio.")
            messages.error(self.request, message)
            return redirect(reverse('formulario_field',
                                    kwargs={"pk_formulario": self.kwargs['pk_formulario']}))
        return super(FormularioPreviewFormView, self).dispatch(*args, **kwargs)

    def get_form(self):
        self.form_class = self.get_form_class()
        formulario = Formulario.objects.get(pk=self.kwargs['pk_formulario'])
        campos = formulario.campos.all()
        return self.form_class(campos=campos, **self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        context = super(
            FormularioPreviewFormView, self).get_context_data(**kwargs)
        context['pk_formulario'] = self.kwargs['pk_formulario']
        return context
