# -*- coding: utf-8 -*-

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
