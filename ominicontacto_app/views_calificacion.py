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

"""Vista relacionada con la creacion de una calificacion en el sentido no llamar,
no interesado,etc y luego la agrupacion de la misma en un grupo lo cual se va utilizar
 para la creacion de una campana en el momento de ser calificada"""

from __future__ import unicode_literals

from django.conf import settings
# from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView,
)
from ominicontacto_app.models import NombreCalificacion
from ominicontacto_app.forms import CalificacionForm


class CalificacionCreateView(CreateView):
    """Vista para crear una calificacion
    DT: remover fields de la vista y crear un formulario"""
    model = NombreCalificacion
    form_class = CalificacionForm
    template_name = 'base_create_update_form.html'

    def get_success_url(self):
        return reverse('calificacion_list')


class CalificacionUpdateView(UpdateView):
    """Vista para modificar una calificacion
    DT: remover fields de la vista y crear un formulario"""
    model = NombreCalificacion
    template_name = 'base_create_update_form.html'
    form_class = CalificacionForm

    def get_success_url(self):
        return reverse('calificacion_list')


class CalificacionDeleteView(DeleteView):
    """
    Esta vista se encarga de la eliminación del
    objeto calificacion
    """
    model = NombreCalificacion
    template_name = 'calificacion/delete_calificacion.html'

    def get_success_url(self):
        return reverse('calificacion_list')


class CalificacionListView(ListView):
    """Lista las calificaciones"""
    model = NombreCalificacion
    template_name = 'calificacion/calificacion_list.html'
    queryset = NombreCalificacion.objects.exclude(nombre=settings.CALIFICACION_REAGENDA)
