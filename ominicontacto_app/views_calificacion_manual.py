# -*- coding: utf-8 -*-

"""En este modulo se encuentran las vista de interaccion formularios de calificacion
y gestion con el agente en campañas manuales
"""

from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.views.generic.edit import (
    CreateView, UpdateView, DeleteView,
)
from ominicontacto_app.models import CalificacionManual, Campana, AgenteProfile
from ominicontacto_app.forms import CalificacionManualForm
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

    def get_success_url(self):
        return reverse('view_blanco')
