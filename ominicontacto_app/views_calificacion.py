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


# class CalificacionCampanaMixin(object):

#      def form_valid(self, form):
#          form.cleaned_data['calificacion'] |= NombreCalificacion.objects.filter(
#              nombre=settings.CALIFICACION_REAGENDA)
#          return super(CalificacionCampanaMixin, self).form_valid(form)


# class CalificacionCampanaCreateView(CalificacionCampanaMixin, CreateView):
#     """Vista para crear un un grupo de calificacion
#     DT: remover fields de la vista y crear un formulario"""
#     model = CalificacionCampana
#     form_class = CalificacionCampanaForm
#     template_name = 'base_create_update_form.html'

#    def dispatch(self, request, *args, **kwargs):
#        calfificacion = NombreCalificacion.objects.all()
#        if not califificacion:
#            message = ("Debe cargar una calificacion antes de cargar una "
#                       "calificacion de campana")
#            messages.warning(self.request, message)

#         return super(CalificacionCampanaCreateView, self).dispatch(
#             request, *args, **kwargs)

#     def get_success_url(self):
#         return reverse('calificacion_campana_list')


# class CalificacionCampanaUpdateView(CalificacionCampanaMixin, UpdateView):
#     """Vista para crear un grupo de calificacion
#     DT: remover fields de la vista y crear un formulario"""
#     model = CalificacionCampana
#     form_class = CalificacionCampanaForm
#     template_name = 'base_create_update_form.html'

#     def dispatch(self, request, *args, **kwargs):
#         calfificacion = NombreCalificacion.objects.all()
#         if not calfificacion:
#             message = ("Debe cargar una calificacion antes de cargar una "
#                        "calificacion de campana")
#             messages.warning(self.request, message)

#         return super(CalificacionCampanaUpdateView, self).dispatch(
#             request, *args, **kwargs)

#     def get_success_url(self):
#         return reverse('calificacion_campana_list')


# class CalificacionCampanaDeleteView(DeleteView):
#     """
#     Esta vista se encarga de la eliminación del
#     objeto CalificacionCampana
#     """
#     model = CalificacionCampana
#     template_name = 'calificacion/delete_calificacion_campana.html'

#     def get_success_url(self):
#         return reverse('calificacion_campana_list')


# class CalificacionCampanaListView(ListView):
#     model = CalificacionCampana
#     template_name = 'calificacion/calificacion_campana_list.html'
