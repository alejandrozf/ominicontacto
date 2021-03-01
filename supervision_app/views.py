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

from django.views.generic import TemplateView

from ominicontacto_app.services.kamailio_service import KamailioService

from utiles_globales import AddSettingsContextMixin
from ominicontacto_app.forms import GrupoAgenteForm

from ominicontacto_app.models import Campana, Grupo, AgenteProfile
from supervision_app.services.redisgears_service import RedisGearsService


class SupervisionAgentesView(AddSettingsContextMixin, TemplateView):
    template_name = 'supervision_agentes.html'
    form_class = GrupoAgenteForm

    def get_context_data(self, **kwargs):
        context = super(SupervisionAgentesView, self).get_context_data(**kwargs)
        supervisor = self.request.user.get_supervisor_profile()
        kamailio_service = KamailioService()
        sip_usuario = kamailio_service.generar_sip_user(supervisor.sip_extension)
        sip_password = kamailio_service.generar_sip_password(sip_usuario)
        if self.request.user.get_is_administrador():
            campanas = Campana.objects.obtener_all_dialplan_asterisk()
            grupo = Grupo.objects.all()
        else:
            campanas = supervisor.campanas_asignadas_actuales_no_finalizadas()
            ids_agentes = list(campanas.values_list(
                'queue_campana__members__pk', flat=True).distinct())
            id_grupo = AgenteProfile.objects.filter(id__in=ids_agentes).values_list(
                'grupo_id', flat=True).distinct()
            grupo = Grupo.objects.filter(id__in=id_grupo).values_list(
                'nombre', flat=True)
        context['campanas'] = campanas
        context['grupo'] = grupo
        context['sip_usuario'] = sip_usuario
        context['sip_password'] = sip_password

        RedisGearsService().registra_stream_supervisor(supervisor.id)
        return context


class SupervisionCampanasEntrantesView(TemplateView):
    template_name = 'supervision_campanas_entrantes.html'

    def get_context_data(self, **kwargs):
        context = super(SupervisionCampanasEntrantesView, self).get_context_data(**kwargs)
        supervisor = self.request.user.get_supervisor_profile()
        context['supervisor_id'] = supervisor.id
        if self.request.user.get_is_administrador():
            campanas = Campana.objects.obtener_actuales()
        else:
            campanas = supervisor.campanas_asignadas_actuales()
        campanas = campanas.filter(type=Campana.TYPE_ENTRANTE).order_by('id')
        context['campanas'] = ",".join([x.nombre for x in campanas])
        context['campanas_ids'] = ",".join([str(x.id) for x in campanas])
        RedisGearsService().registra_stream_supervisor_entrantes(
            supervisor.id, context['campanas_ids'], context['campanas'])
        return context


class SupervisionCampanasSalientesView(TemplateView):
    template_name = 'supervision_campanas_salientes.html'

    def get_context_data(self, **kwargs):
        context = super(SupervisionCampanasSalientesView, self).get_context_data(**kwargs)
        supervisor = self.request.user.get_supervisor_profile()
        context['supervisor_id'] = supervisor.id
        if self.request.user.get_is_administrador():
            campanas = Campana.objects.obtener_actuales()
        else:
            campanas = supervisor.campanas_asignadas_actuales()
        campanas = campanas.filter(type__in=[Campana.TYPE_DIALER,
                                             Campana.TYPE_PREVIEW,
                                             Campana.TYPE_MANUAL]).order_by('id')
        context['campanas'] = ",".join([x.nombre for x in campanas])
        context['campanas_ids'] = ",".join([str(x.id) for x in campanas])
        RedisGearsService().registra_stream_supervisor_salientes(
            supervisor.id, context['campanas_ids'], context['campanas'])
        return context


class SupervisionCampanasDialerView(TemplateView):
    template_name = 'supervision_campanas_dialers.html'

    def get_context_data(self, **kwargs):
        context = super(SupervisionCampanasDialerView, self).get_context_data(**kwargs)
        supervisor = self.request.user.get_supervisor_profile()
        context['supervisor_id'] = supervisor.id
        if self.request.user.get_is_administrador():
            campanas = Campana.objects.obtener_actuales()
        else:
            campanas = supervisor.campanas_asignadas_actuales()
        campanas = campanas.filter(type=Campana.TYPE_DIALER).order_by('id')
        context['campanas'] = ",".join([x.nombre for x in campanas])
        context['campanas_ids'] = ",".join([str(x.id) for x in campanas])
        RedisGearsService().registra_stream_supervisor_dialers(
            supervisor.id, context['campanas_ids'], context['campanas'])
        return context
