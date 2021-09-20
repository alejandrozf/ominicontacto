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

"""Aca se encuentran las vistas para agregar los agente a la campañas/cola
por la relacion esta en cola ya que se hizo con un modelo de queue sacado de la
documentacion de asterisk"""

from __future__ import unicode_literals


from django.contrib import messages
from django.urls import reverse
from django.db import transaction
from django.http import HttpResponseRedirect
from django.views.generic import FormView
from django.utils.translation import ugettext as _

from ominicontacto_app.forms import QueueMemberForm, GrupoAgenteForm, QueueMemberFormset
from ominicontacto_app.models import Campana, QueueMember, Grupo, AgenteProfile
from ominicontacto_app.services.creacion_queue import ActivacionQueueService

from utiles_globales import obtener_sip_agentes_sesiones_activas


import logging as logging_
from ominicontacto_app.services.asterisk.asterisk_ami import AMIManagerConnectorError, \
    AmiManagerClient

logger = logging_.getLogger(__name__)


def adicionar_agente_cola(agente, queue_member, campana, client):
    """Adiciona agente a la cola de su respectiva campaña"""
    queue = campana.get_queue_id_name()
    interface = "PJSIP/{0}".format(agente.sip_extension)
    penalty = queue_member.penalty
    paused = queue_member.paused
    member_name = agente.get_asterisk_caller_id()

    try:
        client.queue_add(queue, interface, penalty, paused, member_name)
    except AMIManagerConnectorError:
        logger.exception(_("QueueAdd failed - agente: {0} de la campana: {1} ".format(
            agente, campana)))


def adicionar_agente_activo_cola(queue_member, campana, sip_agentes_logueados, client):
    """Si el agente tiene una sesión activa lo adiciona a la cola de su respectiva
    campaña
    """
    # chequear si el agente tiene sesion activa
    agente = queue_member.member
    if agente.sip_extension in sip_agentes_logueados:
        adicionar_agente_cola(agente, queue_member, campana, client)


def activar_cola():
    activacion_queue_service = ActivacionQueueService()
    activacion_queue_service.activar()


class QueueMemberCreateView(FormView):
    """Vista para agregar un agente a una campana"""
    model = QueueMember
    form_class = QueueMemberForm
    template_name = 'queue/queue_member.html'

    def get_form(self):
        self.form_class = self.get_form_class()
        # agentes = AgenteProfile.objects.filter(reported_by=self.request.user)
        agentes = AgenteProfile.objects.filter(is_inactive=False)
        return self.form_class(members=agentes, **self.get_form_kwargs())

    def form_valid(self, form):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        self.object = form.save(commit=False)
        # valido que este agente no se encuentre agregado en esta campana
        existe_member = QueueMember.objects.\
            existe_member_queue(self.object.member, campana.queue_campana)

        if existe_member:
            message = _('Operación Errónea! \
            Este miembro ya se encuentra en esta cola')
            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return self.form_invalid(form)
        else:
            try:
                client = AmiManagerClient()
                client.connect()
                with transaction.atomic():
                    agente = self.object.member
                    queue_member_defaults = QueueMember.get_defaults(agente, campana)
                    self.object.queue_name = campana.queue_campana
                    self.object.id_campana = queue_member_defaults['id_campana']
                    self.object.membername = queue_member_defaults['membername']
                    self.object.interface = queue_member_defaults['interface']
                    # por ahora no definimos 'paused'
                    self.object.paused = queue_member_defaults['paused']
                    self.object.save()
                    # adicionamos el agente a la cola actual que esta corriendo
                    sip_agentes_logueados = obtener_sip_agentes_sesiones_activas()
                    adicionar_agente_activo_cola(
                        self.object, campana, sip_agentes_logueados, client)
                    activar_cola()
                client.disconnect()
            except Exception as e:
                message = _("<strong>Operación Errónea!</strong> "
                            "No se pudo confirmar la creación del dialplan debido "
                            "al siguiente error: {0}".format(e))
                messages.add_message(
                    self.request,
                    messages.ERROR,
                    message,
                )

        return super(QueueMemberCreateView, self).form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(
            self.get_context_data(queue_member_form=form))

    def get_context_data(self, **kwargs):
        context = super(
            QueueMemberCreateView, self).get_context_data(**kwargs)
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        grupo_agente_form = GrupoAgenteForm(self.request.GET or None)
        context['grupo_agente_form'] = grupo_agente_form

        context['campana'] = campana
        if campana.type is Campana.TYPE_ENTRANTE:
            context['url_finalizar'] = 'campana_list'
        elif campana.type is Campana.TYPE_DIALER:
            context['url_finalizar'] = 'campana_dialer_list'
        elif campana.type is Campana.TYPE_MANUAL:
            context['url_finalizar'] = 'campana_manual_list'
        elif campana.type is Campana.TYPE_PREVIEW:
            context['url_finalizar'] = 'campana_preview_list'
        return context

    def get_success_url(self):
        return reverse(
            'queue_member_campana',
            kwargs={"pk_campana": self.kwargs['pk_campana']})


class GrupoAgenteCreateView(FormView):
    """Vista para agregar grupo de agentes a una campana"""
    model = QueueMember
    form_class = GrupoAgenteForm
    template_name = 'queue/queue_member.html'

    def form_valid(self, form):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        grupo_id = form.cleaned_data.get('grupo')
        grupo = Grupo.objects.get(pk=grupo_id)
        sip_agentes_logueados = obtener_sip_agentes_sesiones_activas()
        # agentes = grupo.agentes.filter(reported_by=self.request.user)
        agentes = grupo.agentes.filter(is_inactive=False)
        agentes_logueados_grupo = agentes.filter(sip_extension__in=sip_agentes_logueados)
        # agrega los agentes a la campana siempre cuando no se encuentren agregados
        try:
            client = AmiManagerClient()
            client.connect()
            with transaction.atomic():
                for agente in agentes:
                    queue_member, created = QueueMember.objects.get_or_create(
                        member=agente,
                        queue_name=campana.queue_campana,
                        defaults=QueueMember.get_defaults(agente, campana))
                    if created and (agente in agentes_logueados_grupo):
                        adicionar_agente_cola(agente, queue_member, campana, client)
                activar_cola()
            client.disconnect()
        except Exception as e:
            message = _("<strong>Operación Errónea!</strong> "
                        "No se pudo confirmar la creación del dialplan debido "
                        "al siguiente error: {0}".format(e))
            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
        return super(GrupoAgenteCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(
            GrupoAgenteCreateView, self).get_context_data(**kwargs)
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        context['campana'] = campana
        if campana.type is Campana.TYPE_ENTRANTE:
            context['url_finalizar'] = 'campana_list'
        elif campana.type is Campana.TYPE_DIALER:
            context['url_finalizar'] = 'campana_dialer_list'
        elif campana.type is Campana.TYPE_MANUAL:
            context['url_finalizar'] = 'campana_manual_list'
        elif campana.type is Campana.TYPE_PREVIEW:
            context['url_finalizar'] = 'campana_preview_list'
        return context

    def get_success_url(self):
        return reverse(
            'queue_member_campana',
            kwargs={"pk_campana": self.kwargs['pk_campana']})


class QueueMemberCampanaView(FormView):
    """Vista para agregar agentes a una campana"""
    model = QueueMember
    form_class = QueueMemberFormset
    template_name = 'queue/queue_member.html'

    def get_form(self):
        return self.form_class(self.request.POST, **self.get_form_kwargs())

    def get_object(self, queryset=None):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        return campana.queue_campana

    def get_form_kwargs(self):
        members = AgenteProfile.objects.obtener_activos().prefetch_related('user')
        empty = (('', '-----'), )
        choices = ((member.id, member.user.get_full_name()) for member in members)
        choices = list(empty) + list(choices)
        return {'form_kwargs': {'members': choices}}

    def get_context_data(self, **kwargs):
        context = super(QueueMemberCampanaView, self).get_context_data(**kwargs)
        campana = self.get_object().campana
        grupo_agente_form = GrupoAgenteForm(self.request.GET or None)
        context['campana'] = campana
        context['grupos_form'] = grupo_agente_form
        if not context.get('queue_member_form'):
            queue_member_form = QueueMemberFormset(
                instance=campana.queue_campana, **self.get_form_kwargs())
            context['queue_member_form'] = queue_member_form

        if campana.sistema_externo:
            agentes_sin_id_externo = campana.queue_campana.members.exclude(
                id__in=campana.sistema_externo.agentes.values_list('id', flat=True))
            if agentes_sin_id_externo.exists():
                msg = _('Los siguientes agentes no tienen identificador externo:<ul>')
                for agente in agentes_sin_id_externo:
                    nombre = agente.user.get_full_name()
                    msg += '<li>' + nombre + '</li>'
                msg += '</ul>'
                messages.warning(self.request, msg)

        return context

    def form_valid(self, form):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        queue_member_formset = QueueMemberFormset(
            self.request.POST, instance=campana.queue_campana, **self.get_form_kwargs())
        if queue_member_formset.is_valid():
            try:
                client = AmiManagerClient()
                client.connect()
                with transaction.atomic():
                    for queue_form in queue_member_formset.forms:
                        if queue_form.cleaned_data != {}:
                            self.object = queue_form.save(commit=False)
                            agente = self.object.member
                            if queue_form.cleaned_data['DELETE']:
                                self.object.delete()
                                remover_agente_cola_asterisk(campana, agente, client)
                            else:
                                queue_member_defaults = QueueMember.get_defaults(agente, campana)
                                self.object.queue_name = campana.queue_campana
                                self.object.id_campana = queue_member_defaults['id_campana']
                                self.object.membername = queue_member_defaults['membername']
                                self.object.interface = queue_member_defaults['interface']
                                # por ahora no definimos 'paused'
                                self.object.paused = queue_member_defaults['paused']
                                self.object.save()
                                # adicionamos el agente a la cola actual que esta corriendo
                                existe_member = QueueMember.objects.\
                                    existe_member_queue(self.object.member, campana.queue_campana)

                                if not existe_member:
                                    sip_agentes_logueados = obtener_sip_agentes_sesiones_activas()
                                    adicionar_agente_activo_cola(
                                        self.object, campana, sip_agentes_logueados, client)
                    activar_cola()
                client.disconnect()
                queue_member_formset.save()
            except Exception as e:
                message = _("<strong>Operación Errónea!</strong> "
                            "No se pudo confirmar la creación del dialplan debido "
                            "al siguiente error: {0}".format(e))
                messages.add_message(
                    self.request,
                    messages.ERROR,
                    message,
                )
            return super(QueueMemberCampanaView, self).form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        return self.render_to_response(
            self.get_context_data(queue_member_form=form))

    def get_success_url(self):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        if campana.type is Campana.TYPE_ENTRANTE:
            return reverse('campana_list')
        elif campana.type is Campana.TYPE_DIALER:
            return reverse('campana_dialer_list')
        elif campana.type is Campana.TYPE_MANUAL:
            return reverse('campana_manual_list')
        elif campana.type is Campana.TYPE_PREVIEW:
            return reverse('campana_preview_list')


def remover_agente_cola_asterisk(campana, agente, client):
    queue = campana.get_queue_id_name()
    interface = "PJSIP/{0}".format(agente.sip_extension)
    sip_agentes_logueados = obtener_sip_agentes_sesiones_activas()
    if agente.sip_extension in sip_agentes_logueados:
        try:
            client.queue_remove(queue, interface)
        except AMIManagerConnectorError:
            logger.exception(_("QueueRemove failed - agente: {0} de la campana: {1} ".format(
                agente, campana)))


def queue_member_delete_view(request, pk_queuemember, pk_campana):
    """Elimina agente asignado en la campana"""
    queue_member = QueueMember.objects.get(pk=pk_queuemember)
    agente = queue_member.member
    queue_member.delete()
    campana = Campana.objects.get(pk=pk_campana)

    # ahora vamos a remover el agente de la cola de asterisk
    try:
        client = AmiManagerClient()
        client.connect()
    except AMIManagerConnectorError:
        logger.exception(_("QueueRemove failed "))
    remover_agente_cola_asterisk(campana, agente, client)
    client.disconnect()
    activar_cola()

    return HttpResponseRedirect(
        reverse('queue_member_campana',
                kwargs={"pk_campana": pk_campana}
                )
    )
