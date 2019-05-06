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

from django.views.generic import ListView, CreateView, UpdateView
from django.core.urlresolvers import reverse

from ominicontacto_app.models import SistemaExterno


class SistemaExternoCreateView(CreateView):
    """Vista para crear un SistemaExterno"""
    model = SistemaExterno
    template_name = 'base_create_update_form.html'
    fields = ('nombre',)

    def get_success_url(self):
        return reverse('sistema_externo_list')


class SistemaExternoUpdateView(UpdateView):
    """Vista para modificar un SistemaExterno"""
    model = SistemaExterno
    template_name = 'base_create_update_form.html'
    fields = ('nombre',)

    def get_success_url(self):
        return reverse('sistema_externo_list')


class SistemaExternoListView(ListView):
    """Vista para listar los modulos"""
    model = SistemaExterno
    template_name = 'sistema_externo/sistema_externo_list.html'
