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

"""Vista para generar templates de campana"""

from __future__ import unicode_literals

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DeleteView
from django.views.generic.detail import DetailView

from ominicontacto_app.views_campana_creacion import CampanaTemplateCreateMixin
from django.shortcuts import get_object_or_404

from ominicontacto_app.forms import ReglasIncidenciaFormSet
from ominicontacto_app.models import Campana

from ominicontacto_app.views_campana_creacion import CampanaTemplateCreateCampanaMixin
from ominicontacto_app.views_campana_dialer_creacion import CampanaDialerCreateView


import logging as logging_

logger = logging_.getLogger(__name__)


class TemplateListView(ListView):
    """
    Esta vista lista los objetos Capanas-->Templates activos.
    """

    template_name = 'template/lista_template.html'
    context_object_name = 'campanas'
    model = Campana

    def get_context_data(self, **kwargs):
        context = super(TemplateListView, self).get_context_data(**kwargs)
        context['templates_activos'] = \
            Campana.objects.obtener_templates_activos_dialer()
        return context


class CampanaDialerTemplateCreateView(CampanaTemplateCreateMixin, CampanaDialerCreateView):
    """
    Crea una campaña sin acción en el sistema, sólo con el objetivo de servir de
    template base para agilizar la creación de las campañas dialer
    """

    # FIXME: esto debería hacerse de forma más elegante usando herencia,
    # pero necesita un refactor
    FORMS = CampanaDialerCreateView.FORMS[:-1]

    form_list = FORMS

    def done(self, form_list, *args, **kwargs):
        self._save_forms(form_list, Campana.ESTADO_TEMPLATE_ACTIVO)
        return HttpResponseRedirect(reverse('lista_campana_dialer_template'))


class CampanaDialerTemplateCreateCampanaView(CampanaTemplateCreateCampanaMixin,
                                             CampanaDialerCreateView):
    """Vista que crea campana a partir de template"""

    def get_form_initial(self, step):
        pk = self.kwargs.get('pk_campana_template', None)
        campana_template = get_object_or_404(Campana, pk=pk)

        if step == self.ACTUACION_VIGENTE:
            initial = model_to_dict(campana_template.actuacionvigente)
        elif step == self.COLA:
            initial = super(CampanaDialerTemplateCreateCampanaView, self).get_form_initial(step)
            queue = campana_template.queue_campana
            initial['wrapuptime'] = queue.wrapuptime
            initial['detectar_contestadores'] = queue.detectar_contestadores
            initial['initial_predictive_model'] = queue.initial_predictive_model
            initial['initial_boost_factor'] = queue.initial_boost_factor
            initial['dial_timeout'] = queue.dial_timeout
        else:
            initial = super(CampanaDialerTemplateCreateCampanaView, self).get_form_initial(step)
        return initial

    def get_context_data(self, form, *args, **kwargs):
        context = super(
            CampanaDialerTemplateCreateCampanaView, self).get_context_data(form=form, **kwargs)
        if self.steps.current == self.REGLAS_INCIDENCIA:
            pk = self.kwargs.get('pk_campana_template', None)
            campana_template = get_object_or_404(Campana, pk=pk)
            initial_data = campana_template.reglas_incidencia.values()
            reglas_incidencia_init_formset = context['wizard']['form']
            reglas_incidencia_formset = ReglasIncidenciaFormSet(initial=initial_data)
            reglas_incidencia_formset.extra = len(initial_data) + 1
            reglas_incidencia_formset.prefix = reglas_incidencia_init_formset.prefix
            context['wizard']['form'] = reglas_incidencia_formset
        return context

    def done(self, form_list, *args, **kwargs):
        borrar_template = bool(int(kwargs.get('borrar_template')))
        if borrar_template:
            # para el caso de cuando se usa la vista en el reciclado y se hace necesario
            # eliminar la campaña que la genera
            pk = self.kwargs.get('pk_campana_template', None)
            campana_template = get_object_or_404(Campana, pk=pk)
            campana_template.delete()
        return super(CampanaDialerTemplateCreateCampanaView, self).done(form_list, *args, **kwargs)


class TemplateDetailView(DetailView):
    """Vista muestra el detalle de la campana"""
    template_name = 'template/template_detalle.html'
    model = Campana


class TemplateDeleteView(DeleteView):
    """
    Esta vista se encarga de la eliminación del
    objeto Campana-->Template.
    """

    model = Campana
    template_name = 'campana_dialer/delete_campana.html'

    def dispatch(self, request, *args, **kwargs):
        self.campana = \
            Campana.objects.obtener_activo_para_eliminar_crear_ver(
                kwargs['pk_campana'])
        return super(TemplateDeleteView, self).dispatch(request, *args,
                                                        **kwargs)

    def get_object(self, queryset=None):
        return Campana.objects.obtener_activo_para_eliminar_crear_ver(
            self.kwargs['pk_campana'])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()

        self.object.borrar_template()

        message = '<strong>Operación Exitosa!</strong>\
        Se llevó a cabo con éxito la eliminación del Template.'

        messages.add_message(
            self.request,
            messages.SUCCESS,
            message,
        )
        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        return reverse('lista_campana_dialer_template')
