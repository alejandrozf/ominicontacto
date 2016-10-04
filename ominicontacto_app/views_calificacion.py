# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView,
)
from ominicontacto_app.models import (
    Calificacion, CalificacionCampana
)


class CalificacionCreateView(CreateView):
    model = Calificacion
    template_name = 'base_create_update_form.html'
    fields = ('nombre',)

    def get_success_url(self):
        return reverse('calificacion_list')


class CalificacionUpdateView(UpdateView):
    model = Calificacion
    template_name = 'base_create_update_form.html'
    fields = ('nombre',)

    def get_success_url(self):
        return reverse('calificacion_list')


class CalificacionDeleteView(DeleteView):
    """
    Esta vista se encarga de la eliminación del
    objeto grupo
    """
    model = Calificacion
    template_name = 'calificacion/delete_calificacion.html'

    def get_success_url(self):
        return reverse('calificacion_list')


class CalificacionListView(ListView):
    model = Calificacion
    template_name = 'calificacion/calificacion_list.html'


class CalificacionCampanaCreateView(CreateView):
    model = CalificacionCampana
    template_name = 'base_create_update_form.html'
    fields = ('nombre', 'calificacion')

    def dispatch(self, request, *args, **kwargs):
        calfificacion = Calificacion.objects.all()
        if not calfificacion:
            message = ("Debe cargar una calificacion antes de cargar una "
                       "calificacion de campana")
            messages.warning(self.request, message)

        return super(CalificacionCampanaCreateView, self).dispatch(request,
            *args, **kwargs)

    def get_success_url(self):
        return reverse('calificacion_campana_list')


class CalificacionCampanaUpdateView(UpdateView):
    model = CalificacionCampana
    template_name = 'base_create_update_form.html'
    fields = ('nombre', 'calificacion')

    def dispatch(self, request, *args, **kwargs):
        calfificacion = Calificacion.objects.all()
        if not calfificacion:
            message = ("Debe cargar una calificacion antes de cargar una "
                       "calificacion de campana")
            messages.warning(self.request, message)

        return super(CalificacionCampanaUpdateView, self).dispatch(request,
            *args, **kwargs)

    def get_success_url(self):
        return reverse('calificacion_campana_list')


class CalificacionCampanaDeleteView(DeleteView):
    """
    Esta vista se encarga de la eliminación del
    objeto grupo
    """
    model = CalificacionCampana
    template_name = 'calificacion/delete_calificacion_campana.html'

    def get_success_url(self):
        return reverse('calificacion_campana_list')


class CalificacionCampanaListView(ListView):
    model = CalificacionCampana
    template_name = 'calificacion/calificacion_campana_list.html'
