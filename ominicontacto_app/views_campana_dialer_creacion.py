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

"""Vista para generar un objecto campana de tipo dialer"""

from __future__ import unicode_literals
from functools import partial

from django.db import transaction
from django.utils.translation import gettext as _
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from ominicontacto_app.forms.base import (QueueDialerForm, SincronizaDialerForm,
                                          ActuacionVigenteForm,
                                          ReglasIncidenciaFormSet, CampanaDialerForm,
                                          OpcionCalificacionFormSet,
                                          ParametrosCrmFormSet, CampanaSupervisorUpdateForm,
                                          QueueMemberFormset, CampanaConfiguracionWhatsappForm)
from ominicontacto_app.models import Campana

from ominicontacto_app.services.dialer import get_dialer_service, wombat_habilitado

from formtools.wizard.views import SessionWizardView

from ominicontacto_app.views_campana_creacion import CampanaWizardMixin

import logging as logging_

logger = logging_.getLogger(__name__)


class CampanaDialerMixin(CampanaWizardMixin):
    INICIAL = '0'
    COLA = '1'
    CONFIGURACION_WHATSAPP = '2'
    OPCIONES_CALIFICACION = '3'
    PARAMETROS_CRM = '4'
    ACTUACION_VIGENTE = '5'
    REGLAS_INCIDENCIA = '6'
    ADICION_SUPERVISORES = '7'
    ADICION_AGENTES = '8'
    SINCRONIZAR = '9'

    FORMS = [(INICIAL, CampanaDialerForm),
             (COLA, QueueDialerForm),
             (CONFIGURACION_WHATSAPP, CampanaConfiguracionWhatsappForm),
             (OPCIONES_CALIFICACION, OpcionCalificacionFormSet),
             (PARAMETROS_CRM, ParametrosCrmFormSet),
             (ACTUACION_VIGENTE, ActuacionVigenteForm),
             (REGLAS_INCIDENCIA, ReglasIncidenciaFormSet),
             (ADICION_SUPERVISORES, CampanaSupervisorUpdateForm),
             (ADICION_AGENTES, QueueMemberFormset),
             (SINCRONIZAR, SincronizaDialerForm)]

    TEMPLATES = {INICIAL: 'campanas/campana_dialer/nueva_edita_campana.html',
                 COLA: 'campanas/campana_dialer/create_update_queue.html',
                 CONFIGURACION_WHATSAPP: "campanas/campana_dialer/configuracion_whatsapp.html",
                 OPCIONES_CALIFICACION: 'campanas/campana_dialer/opcion_calificacion.html',
                 PARAMETROS_CRM: 'campanas/campana_dialer/parametros_crm_sitio_externo.html',
                 ACTUACION_VIGENTE: 'campanas/campana_dialer/actuacion_vigente_campana.html',
                 REGLAS_INCIDENCIA: 'campanas/campana_dialer/reglas_incidencia.html',
                 ADICION_SUPERVISORES: "campanas/campana_dialer/adicionar_supervisores.html",
                 ADICION_AGENTES: "campanas/campana_dialer/adicionar_agentes.html",
                 SINCRONIZAR: 'campanas/campana_dialer/sincronizar_lista.html'}

    form_list = FORMS


class CampanaDialerCreateView(CampanaDialerMixin, SessionWizardView):
    """
    Esta vista crea una campaña de tipo dialer
    """

    def get_form_initial(self, step):
        initial = super(CampanaDialerCreateView, self).get_form_initial(step)
        if step == self.COLA:
            step_initial_cleaned_data = self.get_cleaned_data_for_step(self.INICIAL)
            initial['name'] = step_initial_cleaned_data['nombre']
        return initial

    def get_context_data(self, form, *args, **kwargs):
        context = super(CampanaDialerCreateView, self).get_context_data(form, *args, **kwargs)
        current_step = self.steps.current
        context['create'] = True
        if current_step == self.INICIAL:
            context['canales_en_uso'] = Campana.objects.obtener_canales_dialer_en_uso()
        elif current_step == self.REGLAS_INCIDENCIA and form.forms == []:
            # reiniciamos el formset para que el usuario si no tiene formularios
            # para que el usuario tenga posibilidad de agregar nuevos formularios
            new_formset = ReglasIncidenciaFormSet()
            new_formset.prefix = form.prefix
            context['wizard']['form'] = new_formset
        return context

    def _save_campana(self, campana_form, estado):
        campana_form.instance.type = Campana.TYPE_DIALER
        campana_form.instance.reported_by = self.request.user
        campana_form.instance.estado = estado
        campana_form.save()
        return campana_form.instance

    def _save_queue(self, queue_form):
        queue_form.instance.eventmemberstatus = True
        queue_form.instance.eventwhencalled = True
        queue_form.instance.ringinuse = True
        queue_form.instance.setinterfacevar = True
        if queue_form.instance.initial_boost_factor is None:
            queue_form.instance.initial_boost_factor = 1.0
        queue_form.save()
        return queue_form.instance

    def _sincronizar_campana(self, sincronizar_form, campana, campana_creada=False):
        evitar_duplicados = sincronizar_form.cleaned_data.get('evitar_duplicados')
        evitar_sin_telefono = sincronizar_form.cleaned_data.get('evitar_sin_telefono')
        prefijo_discador = sincronizar_form.cleaned_data.get('prefijo_discador')

        dialer_service = get_dialer_service()
        dialer_service.crear_campana(campana,
                                     evitar_duplicados, evitar_sin_telefono, prefijo_discador)

    def _save_forms(self, form_list, estado):
        campana_form = list(form_list)[int(self.INICIAL)]
        queue_form = list(form_list)[int(self.COLA)]
        campana = self._save_campana(campana_form, estado)
        offset = 2
        offset_partial = 1
        # Agrego este offset por si form_list no contiene el formulario de ConfiguracionWhatsapp
        if campana.whatsapp_habilitado:
            offset = offset - 1
            offset_partial = offset_partial - 1
            opciones_calificacion_formset = list(form_list)[int(self.OPCIONES_CALIFICACION)]
            configuracion_whatsapp_formset = list(form_list)[int(self.CONFIGURACION_WHATSAPP)]
            if configuracion_whatsapp_formset.is_valid():
                configuracion_whatsapp_formset.instance.campana = campana
                configuracion_whatsapp_formset.instance.created_by_id = self.request.user.id
                configuracion_whatsapp_formset.instance.updated_by_id = self.request.user.id
                configuracion_whatsapp_formset.instance.save()
        opciones_calificacion_formset =\
            list(form_list)[int(self.OPCIONES_CALIFICACION) - offset_partial]
        # Agrego este offset por si form_list no contiene el formulario de PARAMETROS_CRM
        if campana.tiene_interaccion_con_sitio_externo:
            offset = offset - 1
            parametros_crm_formset = list(form_list)[int(self.PARAMETROS_CRM) - offset_partial]
            parametros_crm_formset.instance = campana
            parametros_crm_formset.save()

        actuacion_vigente_form = list(form_list)[int(self.ACTUACION_VIGENTE) - offset]
        reglas_incidencia_form = list(form_list)[int(self.REGLAS_INCIDENCIA) - offset]
        queue_form.instance.campana = campana
        self._save_queue(queue_form)
        opciones_calificacion_formset.instance = campana
        opciones_calificacion_formset.save()

        actuacion_vigente_form.instance.campana = campana
        actuacion_vigente_form.save()

        reglas_incidencia_form.instance = campana
        reglas_incidencia_form.save()

        return campana

    def done(self, form_list, **kwargs):
        success = False
        try:
            with transaction.atomic():
                campana = self._save_forms(form_list, Campana.ESTADO_INACTIVA)
                # Agrego este offset por si form_list no contiene el formulario de PARAMETROS_CRM
                offset = 2
                if campana.tiene_interaccion_con_sitio_externo:
                    offset = offset - 1
                if campana.whatsapp_habilitado:
                    offset = offset - 1
                sincronizar_form = list(form_list)[int(self.SINCRONIZAR) - offset]
                # Intento crear la campaña en wombat como parte de la transaccion
                if wombat_habilitado():
                    self._sincronizar_campana(sincronizar_form, campana)
                self._insert_queue_asterisk(campana.queue_campana)
                self.save_supervisores(form_list, -3)
                self.save_agentes(form_list, -2)
                self.alertas_por_sistema_externo(campana)
                success = True

        except Exception as e:
            logger.error(e)
            success = False

        # Creo la campaña en OMniDialer una vez que ya existe en base
        if not wombat_habilitado():
            transaction.on_commit(partial(self._sincronizar_campana, sincronizar_form, campana))

        if success:
            messages.add_message(
                self.request,
                messages.SUCCESS,
                _('Se ha creado la nueva campaña.'))
        else:
            messages.add_message(
                self.request,
                messages.ERROR,
                _('<strong>¡ATENCIÓN!</strong> El servicio Discador no se encuentra disponible. '
                  'No se pudo crear la campaña. Por favor contacte un administrador.'))
        self.alertas_por_sistema_externo(campana)
        return HttpResponseRedirect(reverse('campana_dialer_list'))


class CampanaDialerUpdateView(CampanaDialerMixin, SessionWizardView):
    """
    Esta vista modifica una campaña de tipo dialer
    """
    INICIAL = '0'
    COLA = '1'
    CONFIGURACION_WHATSAPP = '2'
    OPCIONES_CALIFICACION = '3'
    PARAMETROS_CRM = '4'
    ACTUACION_VIGENTE = '5'

    FORMS = [(INICIAL, CampanaDialerForm),
             (COLA, QueueDialerForm),
             (CONFIGURACION_WHATSAPP, CampanaConfiguracionWhatsappForm),
             (OPCIONES_CALIFICACION, OpcionCalificacionFormSet),
             (PARAMETROS_CRM, ParametrosCrmFormSet),
             (ACTUACION_VIGENTE, ActuacionVigenteForm), ]

    TEMPLATES = {INICIAL: 'campanas/campana_dialer/nueva_edita_campana.html',
                 COLA: 'campanas/campana_dialer/create_update_queue.html',
                 CONFIGURACION_WHATSAPP: "campanas/campana_dialer/configuracion_whatsapp.html",
                 OPCIONES_CALIFICACION: 'campanas/campana_dialer/opcion_calificacion.html',
                 PARAMETROS_CRM: 'campanas/campana_dialer/parametros_crm_sitio_externo.html',
                 ACTUACION_VIGENTE: 'campanas/campana_dialer/actuacion_vigente_campana.html', }

    form_list = FORMS

    def _get_instance_from_campana(self, pk, step):
        instance = super(CampanaDialerUpdateView, self)._get_instance_from_campana(pk, step)
        if step == self.ACTUACION_VIGENTE:
            campana = get_object_or_404(Campana, pk=pk)
            instance = campana.actuacionvigente
        return instance

    def _save_queue(self, queue_form):
        if queue_form.instance.initial_boost_factor is None:
            queue_form.instance.initial_boost_factor = 1.0
        return queue_form.save()

    def _update_dialer(self, campana):
        dialer_service = get_dialer_service()
        dialer_service.editar_campana(campana)

    def done(self, form_list, **kwargs):
        success = False
        try:
            with transaction.atomic():
                campana_form = list(form_list)[int(self.INICIAL)]
                queue_form = list(form_list)[int(self.COLA)]
                campana = campana_form.save()
                offset_total = 2
                offset_parcial = 1
                if campana.whatsapp_habilitado:
                    offset_total = offset_total - 1
                    offset_parcial = offset_parcial - 1
                    configuracion_whatsapp_formset =\
                        list(form_list)[int(self.CONFIGURACION_WHATSAPP)]
                    if configuracion_whatsapp_formset.is_valid():
                        if not configuracion_whatsapp_formset.instance.pk:
                            configuracion_whatsapp_formset.instance.created_by_id =\
                                self.request.user.id
                            configuracion_whatsapp_formset.instance.campana = campana
                        configuracion_whatsapp_formset.instance.updated_by_id =\
                            self.request.user.id
                        configuracion_whatsapp_formset.instance.save()

                opciones_calificacion_formset =\
                    list(form_list)[int(self.OPCIONES_CALIFICACION) - offset_parcial]

                queue = self._save_queue(queue_form)
                opciones_calificacion_formset.save()

                if campana.tiene_interaccion_con_sitio_externo:
                    offset_total = offset_total - 1
                    parametros_crm_formset =\
                        list(form_list)[int(self.PARAMETROS_CRM) - offset_parcial]
                    parametros_crm_formset.save()

                actuacion_vigente_form =\
                    list(form_list)[int(self.ACTUACION_VIGENTE) - offset_total]
                actuacion_vigente_form.save()

                self._insert_queue_asterisk(queue)
                # Intento editar la campaña en wombat como parte de la transaccion
                if wombat_habilitado():
                    self._update_dialer(campana)

                if campana.whatsapp_habilitado:
                    configuracion_whatsapp_formset =\
                        list(form_list)[int(self.CONFIGURACION_WHATSAPP)]
                    if configuracion_whatsapp_formset.is_valid():
                        if not configuracion_whatsapp_formset.instance.pk:
                            configuracion_whatsapp_formset.instance.created_by_id =\
                                self.request.user.id
                            configuracion_whatsapp_formset.instance.campana = campana
                        configuracion_whatsapp_formset.instance.updated_by_id =\
                            self.request.user.id
                        configuracion_whatsapp_formset.instance.save()

                # Actualizo en OMniDialer una vez que ya se modifico en la base de datos
                if not wombat_habilitado():
                    transaction.on_commit(partial(self._update_dialer, campana))

            success = True

        except Exception as e:
            logger.error(e)
            success = False

        if success:
            messages.add_message(
                self.request,
                messages.SUCCESS,
                _('Se ha modificado la campaña.'))
        else:
            messages.add_message(
                self.request,
                messages.ERROR,
                _('<strong>¡ATENCIÓN!</strong> El servicio Discador no se encuentra disponible. '
                  'No se pudo modificar la campaña. Por favor contacte un administrador.'))

        return HttpResponseRedirect(reverse('campana_dialer_list'))
