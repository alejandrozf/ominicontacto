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
                                          QueueMemberFormset)
from ominicontacto_app.models import Campana

from ominicontacto_app.services.campana_service import CampanaService
from ominicontacto_app.services.exportar_base_datos import SincronizarBaseDatosContactosService

from formtools.wizard.views import SessionWizardView

from ominicontacto_app.views_campana_creacion import CampanaWizardMixin

import logging as logging_

logger = logging_.getLogger(__name__)


class CampanaDialerMixin(CampanaWizardMixin):
    INICIAL = '0'
    COLA = '1'
    OPCIONES_CALIFICACION = '2'
    PARAMETROS_CRM = '3'
    ACTUACION_VIGENTE = '4'
    REGLAS_INCIDENCIA = '5'
    ADICION_SUPERVISORES = '6'
    ADICION_AGENTES = '7'
    SINCRONIZAR = '8'

    FORMS = [(INICIAL, CampanaDialerForm),
             (COLA, QueueDialerForm),
             (OPCIONES_CALIFICACION, OpcionCalificacionFormSet),
             (PARAMETROS_CRM, ParametrosCrmFormSet),
             (ACTUACION_VIGENTE, ActuacionVigenteForm),
             (REGLAS_INCIDENCIA, ReglasIncidenciaFormSet),
             (ADICION_SUPERVISORES, CampanaSupervisorUpdateForm),
             (ADICION_AGENTES, QueueMemberFormset),
             (SINCRONIZAR, SincronizaDialerForm)]

    TEMPLATES = {INICIAL: 'campanas/campana_dialer/nueva_edita_campana.html',
                 COLA: 'campanas/campana_dialer/create_update_queue.html',
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

    def _sincronizar_campana(self, sincronizar_form, campana):
        evitar_duplicados = sincronizar_form.cleaned_data.get('evitar_duplicados')
        evitar_sin_telefono = sincronizar_form.cleaned_data.get('evitar_sin_telefono')
        prefijo_discador = sincronizar_form.cleaned_data.get('prefijo_discador')
        service_base = SincronizarBaseDatosContactosService()
        # Crea un achivo con la lista de contactos para importar a wombat
        service_base.crear_lista(campana, evitar_duplicados,
                                 evitar_sin_telefono, prefijo_discador)
        campana_service = CampanaService()
        # crear campana en wombat
        campana_service.crear_campana_wombat(campana)
        # crea trunk en wombat
        campana_service.crear_trunk_campana_wombat(campana)
        # crea reglas de incidencia en wombat
        for regla in campana.reglas_incidencia.all():
            parametros = [regla.get_estado_wombat(), regla.estado_personalizado,
                          regla.intento_max, regla.reintentar_tarde,
                          regla.get_en_modo_wombat()]
            campana_service.crear_reschedule_campana_wombat(campana, parametros)
        # crea endpoint en wombat
        campana_service.guardar_endpoint_campana_wombat(campana)
        # asocia endpoint en wombat a campana
        campana_service.crear_endpoint_asociacion_campana_wombat(
            campana)
        # crea lista en wombat
        campana_service.crear_lista_contactos_wombat(campana)
        # asocia lista a campana en wombat
        campana_service.crear_lista_asociacion_campana_wombat(campana)

    def _save_forms(self, form_list, estado):
        campana_form = list(form_list)[int(self.INICIAL)]
        queue_form = list(form_list)[int(self.COLA)]
        opciones_calificacion_formset = list(form_list)[int(self.OPCIONES_CALIFICACION)]

        campana = self._save_campana(campana_form, estado)

        # Agrego este offset por si form_list no contiene el formulario de PARAMETROS_CRM
        offset = 1
        if campana.tiene_interaccion_con_sitio_externo:
            offset = 0
            parametros_crm_formset = list(form_list)[int(self.PARAMETROS_CRM)]
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
                offset = 0 if campana.tiene_interaccion_con_sitio_externo else 1
                sincronizar_form = list(form_list)[int(self.SINCRONIZAR) - offset]
                self._sincronizar_campana(sincronizar_form, campana)
                self._insert_queue_asterisk(campana.queue_campana)
                self.save_supervisores(form_list, -3)
                self.save_agentes(form_list, -2)
                self.alertas_por_sistema_externo(campana)
                success = True

        except Exception as e:
            logger.error(e)
            success = False

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
    OPCIONES_CALIFICACION = '2'
    PARAMETROS_CRM = '3'
    ACTUACION_VIGENTE = '4'

    FORMS = [(INICIAL, CampanaDialerForm),
             (COLA, QueueDialerForm),
             (OPCIONES_CALIFICACION, OpcionCalificacionFormSet),
             (PARAMETROS_CRM, ParametrosCrmFormSet),
             (ACTUACION_VIGENTE, ActuacionVigenteForm), ]

    TEMPLATES = {INICIAL: 'campanas/campana_dialer/nueva_edita_campana.html',
                 COLA: 'campanas/campana_dialer/create_update_queue.html',
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

    def done(self, form_list, **kwargs):
        success = False
        try:
            with transaction.atomic():
                campana_form = list(form_list)[int(self.INICIAL)]
                queue_form = list(form_list)[int(self.COLA)]
                opciones_calificacion_formset = list(form_list)[int(self.OPCIONES_CALIFICACION)]
                campana = campana_form.save()
                queue = self._save_queue(queue_form)
                opciones_calificacion_formset.save()

                offset = 1
                if campana.tiene_interaccion_con_sitio_externo:
                    offset = 0
                    parametros_crm_formset = list(form_list)[int(self.PARAMETROS_CRM)]
                    parametros_crm_formset.save()

                actuacion_vigente_form = list(form_list)[int(self.ACTUACION_VIGENTE) - offset]
                actuacion_vigente_form.save()

                self._insert_queue_asterisk(queue)
                campana_service = CampanaService()
                service_ok = campana_service.crear_campana_wombat(campana)
                if service_ok:
                    service_ok = campana_service.update_endpoint(campana)
                if not service_ok:
                    raise Exception('No se ha podico crear la campaña en Wombat.')
                # recarga campaña en wombat
                if campana.estado == Campana.ESTADO_ACTIVA:
                    campana_service.reload_campana_wombat(campana)

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
