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

"""
Aca se encuentran las vistas relacionada con las grabaciones en cuanto a su busqueda
ya que el insert lo hace kamailio-debian/asterisk(hablar con fabian como hace el insert )
"""

from __future__ import unicode_literals

from django.utils.translation import gettext as _

from django.views.generic import FormView, View
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import JsonResponse

from ominicontacto_app.forms.base import GrabacionBusquedaFormEx
from ominicontacto_app.models import (
    GrabacionMarca, Campana)


class BusquedaGrabacionAgenteFormViewEx(UserPassesTestMixin, FormView):

    form_class = GrabacionBusquedaFormEx

    success_url = '.'

    template_name = 'agente/frame/busqueda_grabacion_ex/index.html'

    def test_func(self):
        agent_profile = self.request.user.get_agente_profile()
        agent_group = agent_profile.grupo
        return agent_group.acceso_grabaciones_agente

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        agente_campana_ids = self.request.user.get_agente_profile().queue_set.values_list(
            "campana_id", flat=True
        )
        campanas = Campana.objects.filter(pk__in=agente_campana_ids)\
            .exclude(estado=Campana.ESTADO_BORRADA)\
            .order_by("nombre")
        kwargs.update({
            "agente_hidden_widget": True,
            "campana_choices": [(c.id, c.nombre) for c in campanas],
        })
        return kwargs


class BusquedaGrabacionSupervisorFormViewEx(FormView):

    form_class = GrabacionBusquedaFormEx

    success_url = '.'

    template_name = 'busqueda_grabacion_ex/index.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.get_is_administrador():
            campanas = Campana.objects.all()
        else:
            campanas = self.request.user.get_supervisor_profile().campanas_asignadas()
        kwargs.update({
            "campana_choices": [(c.id, c.nombre) for c in campanas],
        })
        return kwargs


class MarcarGrabacionView(View):
    """
    Crea o modifica la descripción de una grabacion existente
    """

    def post(self, *args, **kwargs):
        callid = self.request.POST.get('callid', False)
        descripcion = self.request.POST.get('descripcion', '')
        try:
            grabacion_marca, _ = GrabacionMarca.objects.get_or_create(
                callid=callid)
        except Exception as e:
            return JsonResponse({'result': 'failed by {0}'.format(e)})
        else:
            grabacion_marca.descripcion = descripcion
            grabacion_marca.save()
            return JsonResponse({'result': 'OK'})


class GrabacionDescripcionView(View):
    """
    Obtiene la descripción de una grabación si está marcada
    """

    def get(self, *args, **kwargs):
        callid = kwargs.get('callid', False)
        try:
            grabacion_marca = GrabacionMarca.objects.get(callid=callid)
        except GrabacionMarca.DoesNotExist:
            response = {u'result': _(u'No encontrada'),
                        u'descripcion': _(u'La grabación no tiene descripción asociada')}
        else:
            response = {u'result': _(u'Descripción'),
                        u'descripcion': grabacion_marca.descripcion}
        return JsonResponse(response)
