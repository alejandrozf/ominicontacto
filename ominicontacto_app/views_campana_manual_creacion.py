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

"""Vista para la creacion de un objecto campana de tipo manual"""

from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView, DeleteView

from formtools.wizard.views import SessionWizardView

from ominicontacto_app.forms import (CampanaManualForm, OpcionCalificacionFormSet,
                                     ParametrosCrmFormSet, CampanaSupervisorUpdateForm,
                                     QueueMemberFormset)
from ominicontacto_app.models import Campana, Queue
from ominicontacto_app.views_campana_creacion import (CampanaWizardMixin,
                                                      CampanaTemplateCreateMixin,
                                                      CampanaTemplateCreateCampanaMixin,
                                                      CampanaTemplateDeleteMixin,
                                                      asignar_bd_contactos_defecto_campo_vacio,
                                                      mostrar_form_parametros_crm_form)
from ominicontacto_app.utiles import cast_datetime_part_date

import logging as logging_

logger = logging_.getLogger(__name__)


class CampanaManualMixin(CampanaWizardMixin):
    INICIAL = '0'
    COLA = None
    OPCIONES_CALIFICACION = '1'
    PARAMETROS_CRM = '2'
    ADICION_SUPERVISORES = '3'
    ADICION_AGENTES = '4'

    FORMS = [(INICIAL, CampanaManualForm),
             (OPCIONES_CALIFICACION, OpcionCalificacionFormSet),
             (PARAMETROS_CRM, ParametrosCrmFormSet),
             (ADICION_SUPERVISORES, CampanaSupervisorUpdateForm),
             (ADICION_AGENTES, QueueMemberFormset)]

    TEMPLATES = {INICIAL: "campanas/campana_manual/nueva_edita_campana.html",
                 OPCIONES_CALIFICACION: "campanas/campana_manual/opcion_calificacion.html",
                 PARAMETROS_CRM: "campanas/campana_manual/parametros_crm_sitio_externo.html",
                 ADICION_SUPERVISORES: "campanas/campana_manual/adicionar_supervisores.html",
                 ADICION_AGENTES: "campanas/campana_manual/adicionar_agentes.html"}

    form_list = FORMS

    condition_dict = {
        PARAMETROS_CRM: mostrar_form_parametros_crm_form
    }


class CampanaManualCreateView(CampanaManualMixin, SessionWizardView):
    """
    Esta vista crea una campaña de tipo manual
    """

    def get_context_data(self, form, *args, **kwargs):
        context = super(CampanaManualCreateView, self).get_context_data(form, *args, **kwargs)
        context['create'] = True
        return context

    def _save_forms(self, form_list, estado, tipo):
        campana_form = form_list[int(self.INICIAL)]
        interaccion_crm = campana_form.instance.tipo_interaccion == Campana.SITIO_EXTERNO
        opciones_calificacion_formset = form_list[int(self.OPCIONES_CALIFICACION)]
        campana_form.instance.type = tipo
        campana_form.instance.reported_by = self.request.user
        campana_form.instance.fecha_inicio = cast_datetime_part_date(timezone.now())
        campana_form.instance.estado = estado
        campana_form = asignar_bd_contactos_defecto_campo_vacio(campana_form)
        campana_form.save()
        auto_grabacion = campana_form.cleaned_data['auto_grabacion']
        campana = campana_form.instance
        queue = Queue.objects.create(
            campana=campana,
            name=campana.nombre,
            maxlen=5,
            wrapuptime=5,
            servicelevel=30,
            strategy='rrmemory',
            eventmemberstatus=True,
            eventwhencalled=True,
            ringinuse=True,
            setinterfacevar=True,
            weight=0,
            wait=120,
            auto_grabacion=auto_grabacion)
        opciones_calificacion_formset.instance = campana
        opciones_calificacion_formset.save()
        if interaccion_crm:
            parametros_crm_formset = form_list[int(self.PARAMETROS_CRM)]
            parametros_crm_formset.instance = campana
            parametros_crm_formset.save()
        return queue

    def done(self, form_list, **kwargs):
        queue = self._save_forms(form_list, Campana.ESTADO_ACTIVA, Campana.TYPE_MANUAL)
        self._insert_queue_asterisk(queue)
        # salvamos los supervisores y  agentes asignados a la campaña
        self.save_supervisores(form_list, -2)
        self.save_agentes(form_list, -1)
        campana = queue.campana
        self.alertas_por_sistema_externo(campana)
        return HttpResponseRedirect(reverse('campana_manual_list'))


class CampanaManualUpdateView(CampanaManualMixin, SessionWizardView):
    """
    Esta vista actualiza una campaña de tipo manual.
    """

    INICIAL = '0'
    COLA = None
    OPCIONES_CALIFICACION = '1'
    PARAMETROS_CRM = '2'

    FORMS = [(INICIAL, CampanaManualForm),
             (OPCIONES_CALIFICACION, OpcionCalificacionFormSet),
             (PARAMETROS_CRM, ParametrosCrmFormSet)]

    TEMPLATES = {INICIAL: "campanas/campana_manual/nueva_edita_campana.html",
                 OPCIONES_CALIFICACION: "campanas/campana_manual/opcion_calificacion.html",
                 PARAMETROS_CRM: "campanas/campana_manual/parametros_crm_sitio_externo.html"}

    form_list = FORMS

    def get_form_initial(self, step):
        initial = super(CampanaManualUpdateView, self).get_form_initial(step)
        campana = self.get_form_instance(step)
        if step == self.INICIAL:
            initial['auto_grabacion'] = campana.queue_campana.auto_grabacion
        return initial

    def _save_forms(self, form_list, **kwargs):
        campana_form = form_list[int(self.INICIAL)]
        opciones_calificacion_formset = form_list[int(self.OPCIONES_CALIFICACION)]
        campana_form = asignar_bd_contactos_defecto_campo_vacio(campana_form)
        campana_form.save()
        auto_grabacion = campana_form.cleaned_data['auto_grabacion']
        campana = campana_form.instance
        queue = campana.queue_campana
        queue.auto_grabacion = auto_grabacion
        queue.save()
        opciones_calificacion_formset.instance = campana
        opciones_calificacion_formset.save()
        if campana.tipo_interaccion == Campana.SITIO_EXTERNO:
            parametros_crm_formset = form_list[int(self.PARAMETROS_CRM)]
            parametros_crm_formset.instance = campana
            parametros_crm_formset.save()
        return queue

    def done(self, form_list, **kwargs):
        queue = self._save_forms(form_list, **kwargs)
        self._insert_queue_asterisk(queue)
        self.alertas_por_sistema_externo(queue.campana)
        return HttpResponseRedirect(reverse('campana_manual_list'))


class CampanaManualTemplateListView(ListView):
    """
    Vista que muestra todos los templates de campañas entrantes activos
    """
    template_name = "campanas/campana_manual/lista_template.html"
    context_object_name = 'templates_activos_manuales'
    model = Campana

    def get_queryset(self):
        return Campana.objects.obtener_templates_activos_manuales()


class CampanaManualTemplateCreateView(CampanaTemplateCreateMixin, CampanaManualCreateView):
    """
    Crea una campaña sin acción en el sistema, sólo con el objetivo de servir de
    template base para agilizar la creación de las campañas manuales
    """

    INICIAL = '0'
    COLA = None
    OPCIONES_CALIFICACION = '1'
    PARAMETROS_CRM = '2'

    FORMS = [(INICIAL, CampanaManualForm),
             (OPCIONES_CALIFICACION, OpcionCalificacionFormSet),
             (PARAMETROS_CRM, ParametrosCrmFormSet)]

    TEMPLATES = {INICIAL: "campanas/campana_manual/nueva_edita_campana.html",
                 OPCIONES_CALIFICACION: "campanas/campana_manual/opcion_calificacion.html",
                 PARAMETROS_CRM: "campanas/campana_manual/parametros_crm_sitio_externo.html"}

    form_list = FORMS

    def done(self, form_list, **kwargs):
        self._save_forms(form_list, Campana.ESTADO_TEMPLATE_ACTIVO, Campana.TYPE_MANUAL)
        return HttpResponseRedirect(reverse('campana_manual_template_list'))


class CampanaManualTemplateCreateCampanaView(
        CampanaTemplateCreateCampanaMixin, CampanaManualCreateView):
    """
    Crea una campaña manual a partir de una campaña de template existente
    """
    def get_form_initial(self, step):
        initial = super(CampanaManualTemplateCreateCampanaView, self).get_form_initial(step)
        if step == self.INICIAL:
            pk = self.kwargs.get('pk_campana_template', None)
            campana_template = get_object_or_404(Campana, pk=pk)
            initial['auto_grabacion'] = campana_template.queue_campana.auto_grabacion
        return initial


class CampanaManualTemplateDetailView(DetailView):
    """
    Muestra el detalle de un template para crear una campaña manual
    """
    template_name = "campanas/campana_manual/detalle_campana_template.html"
    model = Campana


class CampanaManualTemplateDeleteView(CampanaTemplateDeleteMixin, DeleteView):
    """
    Esta vista se encarga de la eliminación del
    objeto Campana Manual-->Template.
    """
    model = Campana
    template_name = "campanas/campana_manual/delete_campana_template.html"

    def get_success_url(self):
        return reverse("campana_manual_template_list")
