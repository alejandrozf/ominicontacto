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

"""Vistas para la gestión de campañas entrantes"""

from __future__ import unicode_literals

from django import forms
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import ListView, DetailView, DeleteView
from django.utils.translation import gettext as _


from formtools.wizard.views import SessionWizardView

from ominicontacto_app.services.queue_member_service import QueueMemberService
from configuracion_telefonia_app.models import DestinoEntrante
from ominicontacto_app.forms.base import (
    CampanaEntranteForm, QueueEntranteForm, OpcionCalificacionFormSet, ParametrosCrmFormSet,
    CampanaSupervisorUpdateForm, QueueMemberFormset, GrupoAgenteForm,
    CampanaConfiguracionWhatsappForm)
from ominicontacto_app.models import (Campana, ArchivoDeAudio, SitioExterno, SupervisorProfile,
                                      AgenteProfile)
from ominicontacto_app.services.creacion_queue import (ActivacionQueueService,
                                                       RestablecerDialplanError)
from ominicontacto_app.tests.factories import BaseDatosContactoFactory, COLUMNAS_DB_DEFAULT
from ominicontacto_app.utiles import cast_datetime_part_date, obtener_opciones_columnas_bd

import logging as logging_
from ominicontacto_app.services.asterisk.asterisk_ami import AMIManagerConnectorError

logger = logging_.getLogger(__name__)


def asignar_bd_contactos_defecto_campo_vacio(campana_form):
    """
    Crea una base de datos de contactos vacía en caso de que el usuario no escoja
    una de las existentes en el sistema y la campaña no sea un template, la asigna a
    la instancia que crea el formulario de campaña y devuelve el formulario con el
    cambio
    """
    if (campana_form.cleaned_data['bd_contacto'] is None and
            not campana_form.initial.get('es_template', False)):
        bd_contacto = BaseDatosContactoFactory.build()
        sistema_externo = campana_form.cleaned_data.get('sistema_externo', False)
        if sistema_externo:
            columna_dni = 3
            metadata = bd_contacto.get_metadata()
            metadata.columna_id_externo = columna_dni
            metadata.save()
            bd_contacto = metadata.bd
        else:
            bd_contacto.save()
        campana_form.instance.bd_contacto = bd_contacto
    return campana_form


class CampanaTemplateCreateMixin(object):
    def get_form_initial(self, step):
        initial_data = super(CampanaTemplateCreateMixin, self).get_form_initial(step)
        ultimo_id = Campana.objects.obtener_ultimo_id_campana()
        if step == self.INICIAL:
            campana_nombre = "CAMPANA_CLONADA_{0}".format(ultimo_id)
            initial_data.update({'nombre': campana_nombre,
                                 'bd_contacto': None, 'es_template': True})
        elif step == self.COLA:
            step_cleaned_data = self.get_cleaned_data_for_step(self.INICIAL)
            name = step_cleaned_data['nombre']
            initial_data.update({'name': name})
        return initial_data

    def get_context_data(self, form, *args, **kwargs):
        context = super(CampanaTemplateCreateMixin, self).get_context_data(form=form, **kwargs)
        context['es_template'] = True
        return context


class CampanaTemplateCreateCampanaMixin(object):
    def get_form_initial(self, step):
        pk = self.kwargs.get('pk_campana_template', None)
        campana_template = get_object_or_404(Campana, pk=pk)
        ultimo_id = Campana.objects.obtener_ultimo_id_campana()
        if step == self.INICIAL:
            campana_nombre = "{0}_{1}".format(campana_template.nombre, ultimo_id)
            initial_data = {
                'nombre': campana_nombre,
                'bd_contacto': campana_template.bd_contacto,
                'tipo_interaccion': campana_template.tipo_interaccion,
                'sitio_externo': campana_template.sitio_externo,
                'objetivo': campana_template.objetivo,
                'outr': campana_template.outr,
                'outcid': campana_template.outcid,
                'speech': campana_template.speech,
                'es_template': False}
        elif step == self.COLA:
            step_cleaned_data = self.get_cleaned_data_for_step(self.INICIAL)
            name = step_cleaned_data['nombre']
            queue = campana_template.queue_campana
            initial_data = {
                'name': name,
                'timeout': queue.timeout,
                'retry': queue.retry,
                'maxlen': queue.maxlen,
                'wrapuptime': queue.wrapuptime,
                'servicelevel': queue.servicelevel,
                'strategy': queue.strategy,
                'weight': queue.weight,
                'wait': queue.wait,
                'announce_frequency': queue.announce_frequency,
                'audio_de_ingreso': queue.audio_de_ingreso,
                'auto_grabacion': queue.auto_grabacion,
                'announce_holdtime': queue.announce_holdtime,
                'announce_position': queue.announce_position,
                'ivr_breakdown': queue.ivr_breakdown,
                'musiconhold': queue.musiconhold,
            }
        else:
            initial_data = super(
                CampanaTemplateCreateCampanaMixin, self).get_form_initial(step)
        return initial_data

    def get_context_data(self, form, *args, **kwargs):
        context = super(
            CampanaTemplateCreateCampanaMixin, self).get_context_data(form=form, **kwargs)
        pk = self.kwargs.get('pk_campana_template', None)
        campana_template = get_object_or_404(Campana, pk=pk)
        current_step = self.steps.current
        if current_step == self.OPCIONES_CALIFICACION:
            opts_calif_init_formset = context['wizard']['form']
            if not opts_calif_init_formset.is_bound:
                initial_data = campana_template.opciones_calificacion.values(
                    'nombre', 'tipo', 'formulario')
                form_kwargs = self.get_form_kwargs(current_step)['form_kwargs']
                calif_init_formset = OpcionCalificacionFormSet(
                    initial=initial_data, form_kwargs=form_kwargs)
                calif_init_formset.extra = len(initial_data) - 1
                calif_init_formset.prefix = opts_calif_init_formset.prefix
                context['wizard']['form'] = calif_init_formset
        if current_step == self.PARAMETROS_CRM:
            params_crm_init_formset = context['wizard']['form']
            if not params_crm_init_formset.is_bound:
                initial_data = campana_template.parametros_crm.values(
                    'tipo', 'valor', 'nombre')
                bd_contacto = campana_template.bd_contacto
                columnas_bd = obtener_opciones_columnas_bd(bd_contacto, COLUMNAS_DB_DEFAULT)
                # Calculo form Kwargs
                form_kwargs = {'columnas_bd': columnas_bd}
                if campana_template.sitio_externo:
                    disparador = campana_template.sitio_externo.disparador
                    con_crm_calificacion = disparador == SitioExterno.CALIFICACION
                    form_kwargs['con_crm_calificacion'] = con_crm_calificacion
                param_crms_formset = ParametrosCrmFormSet(
                    initial=initial_data, form_kwargs=form_kwargs)
                param_crms_formset.extra = max(len(initial_data), 1)
                param_crms_formset.prefix = params_crm_init_formset.prefix
                context['wizard']['form'] = param_crms_formset
        return context


class CampanaTemplateDeleteMixin(object):
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.borrar_template()
        message = _("Operación Exitosa:\
        se llevó a cabo con éxito la eliminación del Template.")

        messages.add_message(
            self.request,
            messages.SUCCESS,
            message,
        )
        return HttpResponseRedirect(self.get_success_url())


def mostrar_form_parametros_crm_form(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step(CampanaWizardMixin.INICIAL) or {}
    interaccion = cleaned_data.get('tipo_interaccion', '')
    return interaccion in [Campana.SITIO_EXTERNO, Campana.FORMULARIO_Y_SITIO_EXTERNO]


def mostrar_form_configuracion_whatsapp_form(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step(CampanaWizardMixin.INICIAL) or {}
    return cleaned_data.get('whatsapp_habilitado', '')


class CampanaWizardMixin(object):
    INICIAL = '0'
    COLA = '1'
    CONFIGURACION_WHATSAPP = '2'
    OPCIONES_CALIFICACION = '3'
    PARAMETROS_CRM = '4'
    ADICION_SUPERVISORES = '5'
    ADICION_AGENTES = '6'

    FORMS = [(INICIAL, CampanaEntranteForm),
             (COLA, QueueEntranteForm),
             (CONFIGURACION_WHATSAPP, CampanaConfiguracionWhatsappForm),
             (OPCIONES_CALIFICACION, OpcionCalificacionFormSet),
             (PARAMETROS_CRM, ParametrosCrmFormSet),
             (ADICION_SUPERVISORES, CampanaSupervisorUpdateForm),
             (ADICION_AGENTES, QueueMemberFormset)]

    TEMPLATES = {INICIAL: "campanas/campana_entrante/nueva_edita_campana.html",
                 COLA: "campanas/campana_entrante/create_update_queue.html",
                 CONFIGURACION_WHATSAPP: "campanas/campana_entrante/configuracion_whatsapp.html",
                 OPCIONES_CALIFICACION: "campanas/campana_entrante/opcion_calificacion.html",
                 PARAMETROS_CRM: "campanas/campana_entrante/parametros_crm_sitio_externo.html",
                 ADICION_SUPERVISORES: "campanas/campana_entrante/adicionar_supervisores.html",
                 ADICION_AGENTES: "campanas/campana_entrante/adicionar_agentes.html"}

    form_list = FORMS
    condition_dict = {
        PARAMETROS_CRM: mostrar_form_parametros_crm_form,
        CONFIGURACION_WHATSAPP: mostrar_form_configuracion_whatsapp_form
    }

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]

    def _get_instance_from_campana(self, pk, step):
        campana = get_object_or_404(Campana, pk=pk)
        if step in [self.INICIAL, self.OPCIONES_CALIFICACION, self.PARAMETROS_CRM,
                    self.ADICION_SUPERVISORES]:
            return campana
        if step == self.COLA or step == self.ADICION_AGENTES:
            return campana.queue_campana
        if step == self.CONFIGURACION_WHATSAPP:
            return campana.configuracionwhatsapp.filter(is_active=True).last()

    def get_form_kwargs(self, step):
        if step == self.ADICION_SUPERVISORES:
            supervisores = SupervisorProfile.objects.exclude(borrado=True)
            supervisors_choices = [(supervisor.user.pk, ": ".join([supervisor.user.get_username(),
                                   supervisor.user.get_full_name()])) for supervisor in
                                   supervisores]
            return {'supervisors_choices': supervisors_choices}
        if step == self.ADICION_AGENTES:
            members = AgenteProfile.objects.obtener_activos().prefetch_related('user')
            return {'form_kwargs': {'members': members}}
        if step == self.OPCIONES_CALIFICACION:
            cleaned_data = self.get_cleaned_data_for_step(self.INICIAL)
            con_formulario = cleaned_data.get('tipo_interaccion') in \
                [Campana.FORMULARIO, Campana.FORMULARIO_Y_SITIO_EXTERNO]
            con_crm_calificacion = cleaned_data.get("sitio_externo", None) and \
                cleaned_data.get("sitio_externo", None).disparador == SitioExterno.CALIFICACION
            return {'form_kwargs': {'con_formulario': con_formulario,
                                    'con_crm_calificacion': con_crm_calificacion}}
        else:
            return {}

    def get_form(self, step=None, data=None, files=None):
        if step is None:
            step = self.steps.current
        if step == self.PARAMETROS_CRM:
            # se mantiene la mayor parte del código existente en el plug-in 'formtools
            # con la excepción de que se le pasa el argumento 'columnas_bd' para instanciar
            # con éxito el formulario correspondiente pues formtools no es lo suficientemente
            # flexible y sólo usa kwargs para instanciar
            campana = self.get_cleaned_data_for_step(self.INICIAL)
            bd_contacto = campana['bd_contacto']
            columnas_bd = obtener_opciones_columnas_bd(bd_contacto, COLUMNAS_DB_DEFAULT)
            form_class = self.form_list[step]
            con_crm_calificacion = campana.get("sitio_externo", None) and \
                campana.get("sitio_externo", None).disparador == SitioExterno.CALIFICACION
            kwargs = self.get_form_kwargs(step)
            kwargs.update({
                'data': data,
                'files': files,
                'prefix': self.get_form_prefix(step, form_class),
                'initial': self.get_form_initial(step),
                'form_kwargs': {'columnas_bd': columnas_bd,
                                'con_crm_calificacion': con_crm_calificacion},
            })
            if issubclass(form_class, (forms.ModelForm, forms.models.BaseInlineFormSet)):
                kwargs.setdefault('instance', self.get_form_instance(step))
            elif issubclass(form_class, forms.models.BaseModelFormSet):
                kwargs.setdefault('queryset', self.get_form_instance(step))
            return form_class(**kwargs)
        return super(CampanaWizardMixin, self).get_form(step, data, files)

    def get_form_instance(self, step):
        pk = self.kwargs.get('pk_campana', False)
        if pk:
            # vista de modificación de campaña
            return self._get_instance_from_campana(pk, step)
        else:
            # vista de creación de campaña
            return super(CampanaWizardMixin, self).get_form_instance(step)

    def _insert_queue_asterisk(self, queue):
        """ Sincronizar informacion de Campaña / Queue """
        activacion_queue_service = ActivacionQueueService()
        try:
            activacion_queue_service.activar()
        except RestablecerDialplanError:
            raise

    def get_context_data(self, form, *args, **kwargs):
        context = super(CampanaWizardMixin, self).get_context_data(form, *args, **kwargs)
        context['interaccion_crm'] = False
        current_step = self.steps.current
        if current_step != self.INICIAL:
            cleaned_data_step_initial = self.get_cleaned_data_for_step(self.INICIAL)
            tipo_interaccion = cleaned_data_step_initial['tipo_interaccion']
            context['interaccion_crm'] = tipo_interaccion in \
                [Campana.SITIO_EXTERNO, Campana.FORMULARIO_Y_SITIO_EXTERNO]
        else:
            pk = self.kwargs.get('pk_campana', False)
            if pk:
                campana = get_object_or_404(Campana, pk=pk)
                # Es necesario en el primer form?
                context['whatsapp_habilitado'] = campana.whatsapp_habilitado

        # se adiciona el formulario de los grupos para etapa de asignación de agentes
        if current_step == self.ADICION_AGENTES:
            context['grupos_form'] = GrupoAgenteForm
        return context

    def save_supervisores(self, form_list, index_form_supervisores):
        campana_form = list(form_list)[int(self.INICIAL)]
        supervisores_form = list(form_list)[index_form_supervisores]
        supervisores = supervisores_form.cleaned_data.get('supervisors', [])
        campana = campana_form.instance
        campana.supervisors.add(*supervisores)

    def save_agentes(self, form_list, index_form_agentes):
        campana_form = list(form_list)[int(self.INICIAL)]
        campana = campana_form.instance
        queue_member_formset = list(form_list)[index_form_agentes]
        queue_member_formset.instance = campana.queue_campana
        if queue_member_formset.is_valid():
            # Delego a queue_member_service
            agentes = set()
            penalties = {}
            for queue_form in queue_member_formset.forms:
                if queue_form.cleaned_data != {}:
                    agente = queue_form.instance.member
                    agentes.add(agente)
                    penalties[agente.id] = queue_form.instance.penalty
            try:
                queue_service = QueueMemberService()
                queue_service.agregar_agentes_en_cola(campana, agentes, penalties)
                queue_service.disconnect()
            except AMIManagerConnectorError:
                logger.exception(_("QueueAdd failed "))
            queue_service.disconnect()

    def alertas_por_sistema_externo(self, campana):
        if campana.sistema_externo:
            self.alerta_agentes_en_sistema_externo(campana)
            self.alerta_base_de_datos_en_sistema_externo(campana)
            self.alerta_sitio_externo_en_otras_campanas(campana)

    def alerta_agentes_en_sistema_externo(self, campana):
        if not set(campana.queue_campana.members.values_list('pk')).issubset(
                set(campana.sistema_externo.agentes.values_list('pk'))):
            message = _("La campaña tiene agentes no asociados al sistema externo.")
            messages.warning(self.request, message)

    def alerta_base_de_datos_en_sistema_externo(self, campana):
        if campana.sistema_externo:
            query = Campana.objects.filter(bd_contacto=campana.bd_contacto)
            query = query.exclude(sistema_externo=campana.sistema_externo)
            campanas_con_misma_bd_y_otro_sistema = query.exclude(sistema_externo__isnull=True)
            if (campanas_con_misma_bd_y_otro_sistema.exists()):
                message = _('La base de datos seleccionada esta asociada a otro sistema externo.')
                messages.warning(self.request, message)

    def alerta_sitio_externo_en_otras_campanas(self, campana):
        if campana.sistema_externo and campana.sitio_externo:
            query = Campana.objects.filter(sitio_externo=campana.sitio_externo)
            query = query.exclude(sistema_externo=campana.sistema_externo)
            campanas_con_mismo_sitio_y_otro_sistema = query.exclude(sistema_externo__isnull=True)
            if (campanas_con_mismo_sitio_y_otro_sistema.exists()):
                message = _('El sitio externo seleccionado esta asociado a otro sistema externo.')
                messages.warning(self.request, message)


class CampanaEntranteMixin(CampanaWizardMixin):
    def get_form(self, step=None, data=None, files=None):
        if step is None:
            step = self.steps.current
        if step != self.COLA:
            return super(CampanaEntranteMixin, self).get_form(step, data, files)
        else:
            # se mantiene la mayor parte del código existente en el plug-in 'formtools
            # con la excepción de que se le pasa el argumento 'audio_choices' para instanciar
            # con éxito el formulario correspondiente pues formtools no es lo suficientemente
            # flexible
            audio_choices = ArchivoDeAudio.objects.all()
            form_class = self.form_list[step]
            kwargs = self.get_form_kwargs(step)
            kwargs.update({
                'data': data,
                'files': files,
                'prefix': self.get_form_prefix(step, form_class),
                'initial': self.get_form_initial(step),
            })
            if issubclass(form_class, (forms.ModelForm, forms.models.BaseInlineFormSet)):
                kwargs.setdefault('instance', self.get_form_instance(step))
            elif issubclass(form_class, forms.models.BaseModelFormSet):
                kwargs.setdefault('queryset', self.get_form_instance(step))
            return form_class(audio_choices, **kwargs)


class CampanaEntranteCreateView(CampanaEntranteMixin, SessionWizardView):
    """
    Esta vista crea una campaña entrante
    """

    def get_context_data(self, form, *args, **kwargs):
        context = super(CampanaEntranteCreateView, self).get_context_data(form, *args, **kwargs)
        context['create'] = True
        return context

    def _save_queue(self, queue_form):
        queue_form.instance.eventmemberstatus = True
        queue_form.instance.eventwhencalled = True
        queue_form.instance.ringinuse = True
        queue_form.instance.setinterfacevar = True
        # TODO: OML-496
        audio_anuncio_periodico = queue_form.cleaned_data['audios']
        if audio_anuncio_periodico:
            queue_form.instance.announce = audio_anuncio_periodico.audio_asterisk
        queue_form.instance.save()
        return queue_form.instance

    def _save_forms(self, form_list, estado):
        campana_form = list(form_list)[int(self.INICIAL)]
        campana = campana_form.instance
        interaccion_crm = campana_form.instance.tiene_interaccion_con_sitio_externo
        whatsapp_habilitado = campana_form.instance.whatsapp_habilitado
        queue_form = list(form_list)[int(self.COLA)]
        campana_form.instance.type = Campana.TYPE_ENTRANTE
        campana_form.instance.reported_by = self.request.user
        campana_form.instance.fecha_inicio = cast_datetime_part_date(timezone.now())
        campana_form.instance.estado = estado
        campana_form = asignar_bd_contactos_defecto_campo_vacio(campana_form)
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
        queue_form.instance.campana = campana
        queue = self._save_queue(queue_form)
        opciones_calificacion_formset.instance = campana
        opciones_calificacion_formset.save()
        if interaccion_crm:
            parametros_crm_formset = list(form_list)[int(self.PARAMETROS_CRM) - offset]
            parametros_crm_formset.instance = campana
            parametros_crm_formset.save()
        return queue

    def done(self, form_list, **kwargs):
        queue = self._save_forms(form_list, Campana.ESTADO_ACTIVA)
        self._insert_queue_asterisk(queue)
        # salvamos los supervisores y agentes asignados a la campaña
        self.save_supervisores(form_list, -2)
        self.save_agentes(form_list, -1)
        # creamos un nodo destino de ruta entrante para ser que a la campaña se le pueda
        # configurar un acceso en alguna ruta entrante
        DestinoEntrante.crear_nodo_ruta_entrante(queue.campana)
        # se insertan los datos de la campaña en asterisk
        campana = queue.campana
        self.alertas_por_sistema_externo(campana)
        return HttpResponseRedirect(reverse('campana_list'))

    def get_form_initial(self, step):
        initial_data = super(CampanaEntranteCreateView, self).get_form_initial(step)
        if step == self.COLA:
            step_cleaned_data = self.get_cleaned_data_for_step(self.INICIAL)
            name = step_cleaned_data['nombre']
            initial_data.update({'name': name})
        return initial_data


class CampanaEntranteUpdateView(CampanaEntranteMixin, SessionWizardView):
    """
    Esta vista modifica una campaña entrante
    """

    INICIAL = '0'
    COLA = '1'
    CONFIGURACION_WHATSAPP = '2'
    OPCIONES_CALIFICACION = '3'
    PARAMETROS_CRM = '4'

    FORMS = [(INICIAL, CampanaEntranteForm),
             (COLA, QueueEntranteForm),
             (CONFIGURACION_WHATSAPP, CampanaConfiguracionWhatsappForm),
             (OPCIONES_CALIFICACION, OpcionCalificacionFormSet),
             (PARAMETROS_CRM, ParametrosCrmFormSet)]

    TEMPLATES = {INICIAL: "campanas/campana_entrante/nueva_edita_campana.html",
                 COLA: "campanas/campana_entrante/create_update_queue.html",
                 CONFIGURACION_WHATSAPP: "campanas/campana_entrante/configuracion_whatsapp.html",
                 OPCIONES_CALIFICACION: "campanas/campana_entrante/opcion_calificacion.html",
                 PARAMETROS_CRM: "campanas/campana_entrante/parametros_crm_sitio_externo.html"}

    form_list = FORMS

    def done(self, form_list, *args, **kwargs):
        campana_form = list(form_list)[int(self.INICIAL)]
        campana_form = asignar_bd_contactos_defecto_campo_vacio(campana_form)
        campana_form.instance.save()

        queue_form = list(form_list)[int(self.COLA)]
        # TODO: OML-496
        audio_anuncio_periodico = queue_form.cleaned_data['audios']
        if audio_anuncio_periodico:
            queue_form.instance.announce = audio_anuncio_periodico.audio_asterisk
        else:
            queue_form.instance.announce = None
        queue_form.instance.save()

        campana = campana_form.instance
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
        opts_calif_init_formset = list(form_list)[int(self.OPCIONES_CALIFICACION) - offset]
        opts_calif_init_formset.instance = campana
        opts_calif_init_formset.save()
        if campana.tiene_interaccion_con_sitio_externo:
            parametros_crm_formset = list(form_list)[int(self.PARAMETROS_CRM) - offset]
            parametros_crm_formset.instance = campana
            parametros_crm_formset.save()

        self._insert_queue_asterisk(queue_form.instance)
        self.alertas_por_sistema_externo(campana)
        return HttpResponseRedirect(reverse('campana_list'))


class CampanaEntranteTemplateListView(ListView):
    """
    Vista que muestra todos los templates de campañas entrantes activos
    """
    template_name = "campanas/campana_entrante/lista_template.html"
    context_object_name = 'templates_activos_entrantes'
    model = Campana

    def get_queryset(self):
        return Campana.objects.obtener_templates_activos_entrantes()


class CampanaEntranteTemplateCreateView(CampanaTemplateCreateMixin, CampanaEntranteCreateView):
    """
    Crea una campaña sin acción en el sistema, sólo con el objetivo de servir de
    template base para agilizar la creación de las campañas entrantes
    """

    INICIAL = '0'
    COLA = '1'
    CONFIGURACION_WHATSAPP = '2'
    OPCIONES_CALIFICACION = '3'
    PARAMETROS_CRM = '4'

    FORMS = [(INICIAL, CampanaEntranteForm),
             (COLA, QueueEntranteForm),
             (CONFIGURACION_WHATSAPP, CampanaConfiguracionWhatsappForm),
             (OPCIONES_CALIFICACION, OpcionCalificacionFormSet),
             (PARAMETROS_CRM, ParametrosCrmFormSet)]

    TEMPLATES = {INICIAL: "campanas/campana_entrante/nueva_edita_campana.html",
                 COLA: "campanas/campana_entrante/create_update_queue.html",
                 CONFIGURACION_WHATSAPP: "campanas/campana_entrante/configuracion_whatsapp.html",
                 OPCIONES_CALIFICACION: "campanas/campana_entrante/opcion_calificacion.html",
                 PARAMETROS_CRM: "campanas/campana_entrante/parametros_crm_sitio_externo.html"}

    form_list = FORMS

    def done(self, form_list, **kwargs):
        self._save_forms(form_list, Campana.ESTADO_TEMPLATE_ACTIVO)
        return HttpResponseRedirect(reverse('campana_entrante_template_list'))


class CampanaEntranteTemplateCreateCampanaView(
        CampanaTemplateCreateCampanaMixin, CampanaEntranteCreateView):
    """
    Crea una campaña entrante a partir de una campaña de template existente
    """
    pass


class CampanaEntranteTemplateDetailView(DetailView):
    """
    Muestra el detalle de un template para crear una campaña entrante
    """
    template_name = "campanas/campana_entrante/detalle_campana_template.html"
    model = Campana


class CampanaEntranteTemplateDeleteView(CampanaTemplateDeleteMixin, DeleteView):
    """
    Esta vista se encarga de la eliminación del
    objeto Campana Entrante-->Template.
    """
    template_name = "campanas/campana_entrante/delete_campana_template.html"
    model = Campana

    def get_success_url(self):
        return reverse("campana_entrante_template_list")
