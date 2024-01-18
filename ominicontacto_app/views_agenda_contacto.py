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
Aca se encuentra las vista relacionada con la creacion de una agenda en el caso que el
agente de desee agendar un llamado. Al modulo de agenda le esta faltando algun demonio
o algo por el estilo para que lance una llamada agenda,etc
"""

from __future__ import unicode_literals

import requests
import json

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import (
    PermissionDenied, ValidationError)
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils.timezone import now, datetime, make_aware
from django.views.generic import CreateView, FormView, UpdateView
from django.views.generic.detail import DetailView
from ominicontacto_app.models import AgendaContacto, Contacto, Campana, CalificacionCliente, User
from ominicontacto_app.forms.base import (
    AgendaContactoForm, AgendaBusquedaForm, FiltroUsuarioFechaForm, )
from ominicontacto_app.utiles import convert_fecha_datetime
from notification_app.notification import AgentNotifier


class AgendaContactoUpdateView(UpdateView):
    """Vista para modificar una agenda existente"""
    template_name = 'agenda_contacto/update_agenda_contacto.html'
    model = AgendaContacto
    context_object_name = 'agendacontacto'
    form_class = AgendaContactoForm

    def form_valid(self, form):
        try:
            self.object = form.save(commit=False)
            self.object.agente = self.request.user.get_agente_profile()
            self.object.save()
            calificaciones = CalificacionCliente.objects.filter(
                opcion_calificacion__campana=self.object.campana,
                contacto__pk=self.object.contacto.pk)
            if calificaciones.first().tipo_agenda != self.object.tipo_agenda:
                # para no crear una nueva historia calificación(solo se actuliaza tipo de agenda)
                calificaciones.update(tipo_agenda=self.object.tipo_agenda)
                # se actuliza la última historia creada
                ultima_calificacion_history = CalificacionCliente.history \
                    .filter(id=calificaciones.first().id).first()
                ultima_calificacion_history.tipo_agenda = self.object.tipo_agenda
                ultima_calificacion_history.save()
            return redirect(self.get_success_url())
        except ValidationError as e:
            messages.error(self.request, e.message)
            return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse(
            'agenda_contacto_detalle', kwargs={'pk': self.object.pk})


class AgendaContactoCreateView(CreateView):
    """Vista para crear una nueva agenda"""
    template_name = 'agente/frame/agenda_contacto/create_agenda_contacto.html'
    model = AgendaContacto
    context_object_name = 'agendacontacto'
    form_class = AgendaContactoForm

    def dispatch(self, request, *args, **kwargs):
        pk_contacto = kwargs['pk_contacto']
        pk_campana = kwargs['pk_campana']
        agenda = AgendaContacto.objects.filter(contacto_id=pk_contacto, campana_id=pk_campana)
        if agenda.exists():
            return redirect(reverse('agenda_contacto_update', kwargs={'pk': agenda.first().id}))
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super(AgendaContactoCreateView, self).get_initial()
        contacto = Contacto.objects.get(pk=self.kwargs['pk_contacto'])
        agente = self.request.user.get_agente_profile()
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        initial.update({'contacto': contacto,
                        'agente': agente,
                        'campana': campana})
        return initial

    def get_context_data(self, **kwargs):
        context = super(
            AgendaContactoCreateView, self).get_context_data(**kwargs)
        context['contacto'] = Contacto.objects.get(pk=self.kwargs['pk_contacto'])
        return context

    def form_valid(self, form):
        try:
            self.object = form.save(commit=False)
            self.object.agente = self.request.user.get_agente_profile()
            campana = form.instance.campana
            if self.object.tipo_agenda == AgendaContacto.TYPE_GLOBAL and \
                    campana.type == Campana.TYPE_DIALER:
                url_wombat = '/'.join(
                    [settings.OML_WOMBAT_URL,
                        'api/calls/?op=addcall&campaign={3}_{0}&number={1}&schedule={2}&'
                        'attrs=ID_CAMPANA:{3},ID_CLIENTE:{4},CAMPANA:{0}'])
                fecha_hora = '.'.join([str(self.object.fecha), str(self.object.hora)])
                requests.post(
                    url_wombat.format(
                        campana.nombre, self.object.contacto.telefono, fecha_hora,
                        campana.pk, self.object.contacto.pk))
                self.object.save()
            # Después de agendado el contacto se marca como agendado en la calificación
            calificacion = CalificacionCliente.objects.filter(
                opcion_calificacion__campana=campana, contacto__pk=self.kwargs['pk_contacto'])
            if calificacion:
                calificacion.update(agendado=True, tipo_agenda=self.object.tipo_agenda)
                # se actuliza la última historia creada
                ultima_calificacion_history = CalificacionCliente.history\
                    .filter(id=calificacion[0].id).first()
                ultima_calificacion_history.agendado = True
                ultima_calificacion_history.tipo_agenda = self.object.tipo_agenda
                ultima_calificacion_history.save()

            return super(AgendaContactoCreateView, self).form_valid(form)
        except ValidationError as e:
            messages.error(self.request, e.message)
            return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        if self.object.agente.forzar_despausa():
            AgentNotifier().notify_dispositioned(self.object.agente.user_id, None, True)
        return reverse(
            'agenda_contacto_detalle', kwargs={'pk': self.object.pk})


class AgendaContactoDetailView(DetailView):
    """Detalle de una agenda de contacto"""
    template_name = 'agente/frame/agenda_contacto/agenda_detalle.html'
    model = AgendaContacto

    def get_context_data(self, **kwargs):
        context = super(
            AgendaContactoDetailView, self).get_context_data(**kwargs)
        agente_profile = self.request.user.get_agente_profile()
        fechas_agendas = AgendaContacto.objects.proximas(agente_profile).values_list(
            'fecha', 'hora')
        fechas_agendas = [
            make_aware(datetime.combine(x[0], x[1])).isoformat() for x in fechas_agendas]
        context['fechas_agendas_json'] = json.dumps(fechas_agendas)
        return context


class AgendaContactoListFormView(FormView):
    """Vista listado evento de agenda por agente"""
    model = AgendaContacto
    template_name = 'agenda_contacto/agenda_agente.html'
    form_class = AgendaBusquedaForm

    def dispatch(self, request, *args, **kwargs):
        agente_profile = self.request.user.get_agente_profile()
        if not agente_profile.grupo.acceso_agendas_agente:
            raise PermissionDenied
        return super(AgendaContactoListFormView, self).dispatch(
            request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        agente = self.request.user.get_agente_profile()
        listado_de_eventos = agente.agendacontacto.eventos_filtro_fecha('', '')
        return self.render_to_response(self.get_context_data(
            listado_de_eventos=listado_de_eventos, agente=agente))

    def form_valid(self, form):
        fecha = form.cleaned_data.get('fecha')
        if fecha:
            fecha_desde, fecha_hasta = fecha.split('-')
            fecha_desde = convert_fecha_datetime(fecha_desde)
            fecha_hasta = convert_fecha_datetime(fecha_hasta)
        else:
            fecha_desde = ''
            fecha_hasta = ''
        agente = self.request.user.get_agente_profile()
        listado_de_eventos = agente.agendacontacto.eventos_filtro_fecha(
            fecha_desde, fecha_hasta)
        return self.render_to_response(self.get_context_data(
            listado_de_eventos=listado_de_eventos, agente=agente))


class AgendaContactosPorCampanaView(FormView):
    """ Vista para que el supervisor pueda gestionar las agendas PERSONALES de una campaña """
    form_class = FiltroUsuarioFechaForm
    template_name = 'agenda_contacto/listar_agendas_campana.html'

    def dispatch(self, request, *args, **kwargs):
        self.supervisor = self.request.user.get_supervisor_profile()
        campana_id = kwargs.get('pk_campana')
        try:
            self.campana = Campana.objects.get(id=campana_id)
        except Campana.DoesNotExist:
            message = _('La campana indicada no existe.')
            messages.error(request, message)
            return redirect('index')

        if not request.user.get_is_administrador():
            supervisor = self.request.user.get_supervisor_profile()
            if not supervisor.esta_asignado_a_campana(self.campana):
                message = _('No tiene permiso para ver las agendas de esta campaña.')
                url_por_tipo = {
                    Campana.TYPE_MANUAL: 'campana_manual_list',
                    Campana.TYPE_DIALER: 'campana_dialer_list',
                    Campana.TYPE_ENTRANTE: 'campana_list',
                    Campana.TYPE_PREVIEW: 'campana_preview_list'
                }
                return redirect(url_por_tipo[self.campana.type])

        return super(AgendaContactosPorCampanaView, self).dispatch(
            request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        agendas = AgendaContacto.objects.eventos_filtro_fecha('', '').filter(campana=self.campana)
        return self.render_to_response(self.get_context_data(agendas=agendas))

    def get_form_kwargs(self):
        kwargs = super(AgendaContactosPorCampanaView, self).get_form_kwargs()
        kwargs['initial']['fecha'] = now().date().strftime('%d/%m/%Y - %d/%m/%Y')
        agents_ids = self.campana.queue_campana.queuemember.values_list('member__user', flat=True)
        kwargs['users_choices'] = User.objects.filter(id__in=agents_ids)
        return kwargs

    def form_valid(self, form):
        fecha_desde = form.fecha_desde
        fecha_hasta = form.fecha_hasta
        agendas = AgendaContacto.objects.eventos_filtro_fecha(fecha_desde, fecha_hasta)

        usuario = form.cleaned_data['usuario']
        if usuario:
            agente = usuario.get_agente_profile()
            agendas = agendas.filter(campana=self.campana, agente_id=agente.id)
        else:
            agendas = agendas.filter(campana=self.campana)
        return self.render_to_response(self.get_context_data(agendas=agendas))

    def get_context_data(self, **kwargs):
        context = super(AgendaContactosPorCampanaView, self).get_context_data(**kwargs)
        context['members'] = self.campana.queue_campana.queuemember.all()
        return context
