# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3, as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

"""Vista para la creacion de un objecto campana de tipo manual"""

from __future__ import unicode_literals

from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView, DeleteView

from formtools.wizard.views import SessionWizardView

from ominicontacto_app.forms.base import (CampanaManualForm, OpcionCalificacionFormSet,
                                          ParametrosCrmFormSet, CampanaSupervisorUpdateForm,
                                          CustomBaseDatosContactoForm,
                                          QueueMemberFormset, CampanaConfiguracionWhatsappForm)
from ominicontacto_app.models import Campana, Queue
from ominicontacto_app.views_campana_creacion import (CampanaWizardMixin,
                                                      CampanaTemplateCreateMixin,
                                                      CampanaTemplateCreateCampanaMixin,
                                                      CampanaTemplateDeleteMixin,
                                                      use_custom_basedatoscontacto_form,
                                                      COLUMNAS_DB_DEFAULT,
                                                      COLUMNAS_DB_DEFAULT_TELEFONO,
                                                      COLUMNAS_DB_DEFAULT_ID_EXTERNO,
                                                      mostrar_form_parametros_crm_form)
from ominicontacto_app.utiles import cast_datetime_part_date

import logging as logging_

from django.core.serializers import json

logger = logging_.getLogger(__name__)


def mostrar_form_configuracion_whatsapp_form(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step(CampanaWizardMixin.INICIAL) or {}
    whatasapp_habilitado = cleaned_data.get('whatsapp_habilitado', '')
    return whatasapp_habilitado


class CampanaManualMixin(CampanaWizardMixin):
    INICIAL = '0'
    COLA = None
    CONFIGURACION_WHATSAPP = '1'
    OPCIONES_CALIFICACION = '2'
    PARAMETROS_CRM = '3'
    ADICION_SUPERVISORES = '4'
    ADICION_AGENTES = '5'
    CUSTOM_BASEDATOSCONTACTO = 'custom-basedatoscontacto'

    FORMS = [(INICIAL, CampanaManualForm),
             (CONFIGURACION_WHATSAPP, CampanaConfiguracionWhatsappForm),
             (OPCIONES_CALIFICACION, OpcionCalificacionFormSet),
             (CUSTOM_BASEDATOSCONTACTO, CustomBaseDatosContactoForm),
             (PARAMETROS_CRM, ParametrosCrmFormSet),
             (ADICION_SUPERVISORES, CampanaSupervisorUpdateForm),
             (ADICION_AGENTES, QueueMemberFormset)]

    TEMPLATES = {INICIAL: "campanas/campana_manual/nueva_edita_campana.html",
                 CONFIGURACION_WHATSAPP: "campanas/campana_manual/configuracion_whatsapp.html",
                 OPCIONES_CALIFICACION: "campanas/campana_manual/opcion_calificacion.html",
                 CUSTOM_BASEDATOSCONTACTO: "campanas/campana_manual/custom-basedatoscontacto.html",
                 PARAMETROS_CRM: "campanas/campana_manual/parametros_crm_sitio_externo.html",
                 ADICION_SUPERVISORES: "campanas/campana_manual/adicionar_supervisores.html",
                 ADICION_AGENTES: "campanas/campana_manual/adicionar_agentes.html"}

    form_list = FORMS

    condition_dict = {
        PARAMETROS_CRM: mostrar_form_parametros_crm_form,
        CUSTOM_BASEDATOSCONTACTO: use_custom_basedatoscontacto_form,
        CONFIGURACION_WHATSAPP: mostrar_form_configuracion_whatsapp_form,
    }


class CampanaManualCreateView(CampanaManualMixin, SessionWizardView):
    """
    Esta vista crea una campaña de tipo manual
    """

    def get_context_data(self, form, *args, **kwargs):
        context = super(CampanaManualCreateView, self).get_context_data(form, *args, **kwargs)
        context['create'] = True
        return context

    def get_form_initial(self, step):
        initial_data = super().get_form_initial(step)
        if step == self.CUSTOM_BASEDATOSCONTACTO:
            initial_data.update({
                "metadata": json.json.dumps(
                    {
                        "prim_fila_enc": False,
                        "cant_col": len(COLUMNAS_DB_DEFAULT),
                        "nombres_de_columnas": COLUMNAS_DB_DEFAULT,
                        "cols_telefono": COLUMNAS_DB_DEFAULT_TELEFONO,
                        "col_id_externo": COLUMNAS_DB_DEFAULT_ID_EXTERNO,
                    },
                    cls=json.DjangoJSONEncoder
                )
            })
        return initial_data

    def _save_forms(self, form_list, form_dict, estado, tipo):
        campana_form = list(form_list)[int(self.INICIAL)]
        campana = campana_form.instance
        interaccion_crm = campana.tiene_interaccion_con_sitio_externo
        whatsapp_habilitado = campana.whatsapp_habilitado
        campana_form.instance.type = tipo
        campana_form.instance.reported_by = self.request.user
        campana_form.instance.fecha_inicio = cast_datetime_part_date(timezone.now())
        campana_form.instance.estado = estado
        if custom_basedatoscontacto_form := form_dict.get(self.CUSTOM_BASEDATOSCONTACTO):
            bd_contacto = custom_basedatoscontacto_form.save(commit=False)
            bd_contacto.define()
            bd_contacto.save()
            campana_form.instance.bd_contacto = bd_contacto
        campana_form.save()
        offset = 1
        if whatsapp_habilitado:
            offset = offset - 1
            configuracion_whatsapp_formset = list(form_list)[int(self.CONFIGURACION_WHATSAPP)]
            if configuracion_whatsapp_formset.is_valid():
                configuracion_whatsapp_formset.instance.campana = campana
                configuracion_whatsapp_formset.instance.created_by_id = self.request.user.id
                configuracion_whatsapp_formset.instance.updated_by_id = self.request.user.id
                configuracion_whatsapp_formset.instance.save()

        opciones_calificacion_formset = list(form_list)[int(self.OPCIONES_CALIFICACION) - offset]
        auto_grabacion = campana_form.cleaned_data['auto_grabacion']
        summarize_percentage = campana_form.cleaned_data['summarize_percentage']
        transcription_percentage = campana_form.cleaned_data['transcription_percentage']

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
            summarize_percentage=summarize_percentage,
            transcription_percentage=transcription_percentage,
            auto_grabacion=auto_grabacion)
        opciones_calificacion_formset.instance = campana
        opciones_calificacion_formset.save()
        if interaccion_crm:
            parametros_crm_formset = list(form_list)[int(self.PARAMETROS_CRM) - offset]
            parametros_crm_formset.instance = campana
            parametros_crm_formset.save()
        return queue

    def done(self, form_list, form_dict, **kwargs):
        queue = self._save_forms(form_list, form_dict, Campana.ESTADO_ACTIVA, Campana.TYPE_MANUAL)
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
    CONFIGURACION_WHATSAPP = '1'
    OPCIONES_CALIFICACION = '2'
    PARAMETROS_CRM = '3'

    FORMS = [(INICIAL, CampanaManualForm),
             (CONFIGURACION_WHATSAPP, CampanaConfiguracionWhatsappForm),
             (OPCIONES_CALIFICACION, OpcionCalificacionFormSet),
             (PARAMETROS_CRM, ParametrosCrmFormSet)]

    TEMPLATES = {INICIAL: "campanas/campana_manual/nueva_edita_campana.html",
                 CONFIGURACION_WHATSAPP: "campanas/campana_manual/configuracion_whatsapp.html",
                 OPCIONES_CALIFICACION: "campanas/campana_manual/opcion_calificacion.html",
                 PARAMETROS_CRM: "campanas/campana_manual/parametros_crm_sitio_externo.html"}

    form_list = FORMS

    def get_form_initial(self, step):
        initial = super(CampanaManualUpdateView, self).get_form_initial(step)
        campana = self.get_form_instance(step)
        if step == self.INICIAL:
            initial['auto_grabacion'] = campana.queue_campana.auto_grabacion
            initial['summarize_percentage'] = campana.queue_campana.summarize_percentage
            initial['transcription_percentage'] = campana.queue_campana.transcription_percentage
        return initial

    def _save_forms(self, form_list, **kwargs):
        campana_form = list(form_list)[int(self.INICIAL)]
        campana_form.save()
        auto_grabacion = campana_form.cleaned_data['auto_grabacion']
        summarize_percentage = campana_form.cleaned_data['summarize_percentage']
        transcription_percentage = campana_form.cleaned_data['transcription_percentage']
        campana = campana_form.instance
        queue = campana.queue_campana
        queue.auto_grabacion = auto_grabacion
        queue.summarize_percentage = summarize_percentage
        queue.transcription_percentage = transcription_percentage
        queue.save()
        offset = 1
        if campana.whatsapp_habilitado:
            offset = offset - 1
            configuracion_whatsapp_formset = list(form_list)[int(self.CONFIGURACION_WHATSAPP)]
            if configuracion_whatsapp_formset.is_valid():
                if not configuracion_whatsapp_formset.instance.pk:
                    configuracion_whatsapp_formset.instance.created_by_id = self.request.user.id
                    configuracion_whatsapp_formset.instance.campana = campana
                configuracion_whatsapp_formset.instance.updated_by_id = self.request.user.id
                configuracion_whatsapp_formset.instance.save()
        opciones_calificacion_formset = list(form_list)[int(self.OPCIONES_CALIFICACION) - offset]
        opciones_calificacion_formset.instance = campana
        opciones_calificacion_formset.save()

        if campana.tiene_interaccion_con_sitio_externo:
            parametros_crm_formset = list(form_list)[int(self.PARAMETROS_CRM) - offset]
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
    CONFIGURACION_WHATSAPP = '1'
    OPCIONES_CALIFICACION = '2'
    PARAMETROS_CRM = '3'
    CUSTOM_BASEDATOSCONTACTO = 'custom-basedatoscontacto'

    FORMS = [(INICIAL, CampanaManualForm),
             (CONFIGURACION_WHATSAPP, CampanaConfiguracionWhatsappForm),
             (OPCIONES_CALIFICACION, OpcionCalificacionFormSet),
             (CUSTOM_BASEDATOSCONTACTO, CustomBaseDatosContactoForm),
             (PARAMETROS_CRM, ParametrosCrmFormSet)]

    TEMPLATES = {INICIAL: "campanas/campana_manual/nueva_edita_campana.html",
                 CONFIGURACION_WHATSAPP: "campanas/campana_manual/configuracion_whatsapp.html",
                 OPCIONES_CALIFICACION: "campanas/campana_manual/opcion_calificacion.html",
                 CUSTOM_BASEDATOSCONTACTO: "campanas/campana_manual/custom-basedatoscontacto.html",
                 PARAMETROS_CRM: "campanas/campana_manual/parametros_crm_sitio_externo.html"}

    form_list = FORMS

    def done(self, form_list, form_dict, **kwargs):
        self._save_forms(form_list, form_dict, Campana.ESTADO_TEMPLATE_ACTIVO, Campana.TYPE_MANUAL)
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
            qc = campana_template.queue_campana
            initial['auto_grabacion'] = qc.auto_grabacion
            initial['summarize_percentage'] = qc.summarize_percentage
            initial['transcription_percentage'] = qc.transcription_percentage
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
