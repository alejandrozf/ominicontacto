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

""" Vistas para el reciclados de las campanas"""

from __future__ import unicode_literals

from django.urls import reverse
from django.contrib import messages
from django.shortcuts import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from ominicontacto_app.errors import OmlRecicladoCampanaError
from django.views.generic import FormView
from ominicontacto_app.models import Campana
from reciclado_app.forms import RecicladoForm
from reciclado_app.resultado_contactacion import (
    EstadisticasContactacion, RecicladorContactosCampanaDIALER)
from ominicontacto_app.services.campana_service import CampanaService

import logging as logging_


logger = logging_.getLogger(__name__)


class ReciclarCampanaMixin(object):

    form_class = RecicladoForm
    template_name = 'nuevo_reciclado.html'

    def get_form_kwargs(self):
        kwargs = super(ReciclarCampanaMixin, self).get_form_kwargs()
        estadisticas = EstadisticasContactacion()
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])

        contactados = estadisticas.obtener_cantidad_calificacion(campana)
        contactados_choice = [(contactacion.id, contactacion.label_checkbox)
                              for contactacion in contactados]
        no_contactados = estadisticas.obtener_cantidad_no_contactados(campana)
        no_contactados_choice = [(value.id, value.label_checkbox)
                                 for key, value in no_contactados.items()]
        kwargs['reciclado_choice'] = contactados_choice
        kwargs['no_contactados_choice'] = no_contactados_choice
        return kwargs

    def form_valid(self, form):
        reciclado_calificacion = form.cleaned_data.get('reciclado_calificacion')
        reciclado_no_contactacion = form.cleaned_data.get('reciclado_no_contactacion')
        reciclado_radio = form.cleaned_data.get('reciclado_radio')

        if not (reciclado_calificacion or reciclado_no_contactacion):
            message = _(u'<strong>Operación Errónea!</strong> \
                        Debe seleccionar al menos una opcion para reciclar ')

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return self.form_invalid(form)

        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        reciclador = RecicladorContactosCampanaDIALER()
        bd_contacto_reciclada = reciclador.reciclar(
            campana, reciclado_calificacion, reciclado_no_contactacion)
        if reciclado_radio == 'nueva_campaña':
            try:
                # Intenta reciclar la campana con el tipo de reciclado
                # seleccionado.
                campana_reciclada = Campana.objects.reciclar_campana(
                    campana, bd_contacto_reciclada)
            except OmlRecicladoCampanaError:

                message = _(u'<strong>Operación Errónea!</strong>\
                No se pudo reciclar la Campana.')

                messages.add_message(
                    self.request,
                    messages.ERROR,
                    message,
                )
                return self.form_invalid(form)

            crea_campana_template = self._reciclar_crear_nueva_campana(campana_reciclada, campana)
            return HttpResponseRedirect(crea_campana_template)
        elif reciclado_radio == 'misma_campana':
            campana.update_basedatoscontactos(bd_contacto_reciclada)
            update_campana = self._reciclar_misma_campana(campana)
            return HttpResponseRedirect(reverse(update_campana, kwargs={"pk_campana": campana.pk}))

    def get_context_data(self, **kwargs):
        context = super(ReciclarCampanaMixin, self).get_context_data(**kwargs)
        estadisticas = EstadisticasContactacion()
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        contactados = estadisticas.obtener_cantidad_calificacion(campana)
        contactados_choice = [(contactacion.id, contactacion.nombre, contactacion.cantidad)
                              for contactacion in contactados]
        no_contactados = estadisticas.obtener_cantidad_no_contactados(campana)
        no_contactados_choice = [(value.id, value.nombre, value.cantidad)
                                 for key, value in no_contactados.items()]
        context['contactados'] = contactados_choice
        context['no_contactados'] = no_contactados_choice
        return context


class ReciclarCampanaDialerFormView(ReciclarCampanaMixin, FormView):
    """
    Esta vista muestra los distintos tipo de reciclados de las campanas
    dialer
    """
    def dispatch(self, request, *args, **kwargs):
        form = self.get_form_kwargs()
        contactados = form.get('reciclado_choice')
        no_contactados = form.get('no_contactados_choice')
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        if campana.estado not in [Campana.ESTADO_FINALIZADA, Campana.ESTADO_PAUSADA]:
            message = _(u'Solo se pueden reciclar campañas activas o pausadas.')
            messages.add_message(self.request, messages.WARNING, message)
            return HttpResponseRedirect(reverse('campana_dialer_list'))
        if not (contactados or no_contactados) and campana.estado != Campana.ESTADO_FINALIZADA:
            message = _(u'Esta campaña no se puede reciclar.')
            messages.add_message(self.request, messages.WARNING, message)
            return HttpResponseRedirect(reverse('campana_dialer_list'))
        return super(ReciclarCampanaMixin, self).dispatch(request, *args, **kwargs)

    def _reciclar_crear_nueva_campana(self, campana_reciclada, campana):
        if campana.estado != Campana.ESTADO_FINALIZADA:
            campana_service = CampanaService()
            campana_service.remove_campana_wombat(campana)
            campana.estado = Campana.ESTADO_FINALIZADA
            campana.save()
        crea_campana_template = reverse("crea_campana_dialer_template",
                                        kwargs={"pk_campana_template": campana_reciclada.pk,
                                                "borrar_template": 1})
        return crea_campana_template

    def _reciclar_misma_campana(self, campana):
        campana_service = CampanaService()
        campana_service.cambiar_base(campana, [], False, False, "")
        update_campana = "campana_dialer_update"
        campana.estado = Campana.ESTADO_INACTIVA
        campana.save()
        return update_campana


class ReciclarCampanaPreviewFormView(ReciclarCampanaMixin, FormView):
    """
    Esta vista muestra los distintos tipo de reciclados de las campanas
    preview
    """
    def _reciclar_crear_nueva_campana(self, campana_reciclada, campana):
        crea_campana_template = reverse("campana_preview_template_create_campana",
                                        kwargs={"pk_campana_template": campana_reciclada.pk,
                                                "borrar_template": 1})
        return crea_campana_template

    def _reciclar_misma_campana(self, campana):
        update_campana = "campana_preview_update"
        campana.estado = Campana.ESTADO_ACTIVA
        campana.save()
        campana.establecer_valores_iniciales_agente_contacto(False, False)
        return update_campana
