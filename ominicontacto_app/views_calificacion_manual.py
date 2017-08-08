# -*- coding: utf-8 -*-

"""En este modulo se encuentran las vista de interaccion formularios de calificacion
y gestion con el agente en campañas manuales
"""

from __future__ import unicode_literals

import json

from django.contrib import messages
from django.shortcuts import redirect
from django.http.response import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic.edit import (
    CreateView, UpdateView, DeleteView,
)
from ominicontacto_app.models import CalificacionManual, Campana, AgenteProfile
from ominicontacto_app.forms import CalificacionManualForm, FormularioManualGestionForm
import logging as logging_


logger = logging_.getLogger(__name__)


class CalificacionManualCreateView(CreateView):
    """
    En esta vista se crea la calificacion del contacto de una campana manual
    """
    template_name = 'campana_manual/calificacion_create_update.html'
    model = CalificacionManual
    form_class = CalificacionManualForm

    def get_initial(self):
        initial = super(CalificacionManualCreateView, self).get_initial()
        agente = AgenteProfile.objects.get(pk=self.kwargs['pk_agente'])
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        telefono = self.kwargs['telefono']
        initial.update({'campana': campana,
                        'agente': agente,
                        'telefono': telefono})
        return initial

    def get_form(self):
        self.form_class = self.get_form_class()
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        calificaciones = campana.calificacion_campana.calificacion.all()
        return self.form_class(
            calificacion_choice=calificaciones, gestion=campana.gestion,
            **self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        context = super(CalificacionManualCreateView, self).get_context_data(**kwargs)
        context['pk_campana'] = self.kwargs['pk_campana']
        context['pk_agente'] = self.kwargs['pk_agente']
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        cleaned_data = form.cleaned_data
        calificacion = cleaned_data['calificacion']
        if calificacion is None:
            self.object.es_gestion = True
            self.object.save()
            return HttpResponseRedirect(
                reverse('campana_manual_calificacion_gestion',
                        kwargs={'pk_calificacion': self.object.pk}))
        else:
            self.object.es_gestion = False
            self.object.save()
        message = 'Operación Exitosa!\
                                Se llevó a cabo con éxito la calificacion del cliente'
        messages.success(self.request, message)
        return super(CalificacionManualCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('campana_manual_calificacion_update',
                       kwargs={'pk_calificacion': self.object.pk})


class CalificacionManualUpdateView(UpdateView):
    """
    En esta vista se actualiza la calificacion del contacto de una campana manual
    """
    template_name = 'campana_manual/calificacion_create_update.html'
    model = CalificacionManual
    form_class = CalificacionManualForm

    def get_object(self, queryset=None):
        return CalificacionManual.objects.get(pk=self.kwargs['pk_calificacion'])

    def get_form(self):
        self.form_class = self.get_form_class()
        calificacion = self.get_object()
        campana = calificacion.campana
        calificaciones = campana.calificacion_campana.calificacion.all()
        return self.form_class(
            calificacion_choice=calificaciones, gestion=campana.gestion,
            **self.get_form_kwargs())

    def form_valid(self, form):
        message = 'Operación Exitosa!\
                                Se llevó a cabo con éxito la actualizacion' \
                  'calificacion del cliente'
        messages.success(self.request, message)
        return super(CalificacionManualUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('view_blanco')


class CalificacionManualGestion(UpdateView):
    """
    En esta vista se actualiza la calificacion del contacto de una campana manual
    """
    template_name = 'campana_manual/calificacion_create_update.html'
    model = CalificacionManual
    form_class = FormularioManualGestionForm

    def get_object(self, queryset=None):
        return CalificacionManual.objects.get(pk=self.kwargs['pk_calificacion'])

    def get_form(self):
        self.form_class = self.get_form_class()
        calificacion = self.get_object()
        campana = calificacion.campana
        campos = campana.formulario.campos.all()
        return self.form_class(campos=campos, **self.get_form_kwargs())

    def get_initial(self):
        initial = super(CalificacionManualGestion, self).get_initial()
        self.object = self.get_object()
        if self.object.metadata:
            datos = json.loads(self.object.metadata)
            initial.update(datos)
        return initial

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        del cleaned_data['telefono']
        metadata = json.dumps(cleaned_data)
        self.object = self.get_object()
        self.object.metadata = metadata
        self.object.save()
        message = 'Operación Exitosa!' \
                  'Se llevó a cabo con éxito el llenado del formulario del' \
                  ' cliente'
        messages.success(self.request, message)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('view_blanco')
