# -*- coding: utf-8 -*-

"""Aca se encuentran las vistas para agregar los agente a la campañas/cola
por la relacion esta en cola ya que se hizo con un modelo de queue sacado de la
documentacion de asterisk"""

from __future__ import unicode_literals


from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import FormView, TemplateView
from ominicontacto_app.forms import QueueMemberForm, GrupoAgenteForm
from ominicontacto_app.models import Campana, Queue, QueueMember, Grupo, AgenteProfile
from ominicontacto_app.services.creacion_queue import (ActivacionQueueService,
                                                       RestablecerDialplanError)
from ominicontacto_app.services.asterisk_service import AsteriskService
from ominicontacto_app.utiles import elimina_espacios


import logging as logging_

logger = logging_.getLogger(__name__)


class QueueMemberCreateView(FormView):
    """Vista para agregar un agente a una campana"""
    model = QueueMember
    form_class = QueueMemberForm
    template_name = 'queue/queue_member.html'

    def get_form(self):
        self.form_class = self.get_form_class()
        #agentes = AgenteProfile.objects.filter(reported_by=self.request.user)
        agentes = AgenteProfile.objects.filter(is_inactive=False)
        return self.form_class(members=agentes, **self.get_form_kwargs())

    def form_valid(self, form):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        self.object = form.save(commit=False)
        # valido que este agente no se encuentre agregado en esta campana
        existe_member = QueueMember.objects.\
            existe_member_queue(self.object.member, campana.queue_campana)

        if existe_member:
            message = 'Operación Errónea! \
                Este miembro ya se encuentra en esta cola'
            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return self.form_invalid(form)
        else:
            self.object.queue_name = campana.queue_campana
            self.object.id_campana = "{0}_{1}".format(campana.id,
                                                      elimina_espacios(campana.nombre))
            self.object.membername = self.object.member.user.get_full_name()
            self.object.interface = """Local/{0}@from-queue/n""".format(
            self.object.member.sip_extension)
            self.object.paused = 0  # por ahora no lo definimos
            self.object.save()

        return super(QueueMemberCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(
            QueueMemberCreateView, self).get_context_data(**kwargs)
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        context['campana'] = campana
        if campana.type is Campana.TYPE_ENTRANTE:
            context['url_finalizar'] = 'campana_list'
        elif campana.type is Campana.TYPE_DIALER:
            context['url_finalizar'] = 'campana_dialer_list'
        elif campana.type is Campana.TYPE_MANUAL:
            context['url_finalizar'] = 'campana_manual_list'
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
        #agentes = grupo.agentes.filter(reported_by=self.request.user)
        agentes = grupo.agentes.filter(is_inactive=False)
        # agrega los agentes a la campana siempre cuando no se encuentren agregados
        for agente in agentes:
            QueueMember.objects.get_or_create(
                member=agente,
                queue_name=campana.queue_campana,
                defaults={'membername': agente.user.get_full_name(),
                          'interface': """Local/{0}@from-queue/n""".format(
                              agente.sip_extension),
                          'penalty': 0,
                          'paused': 0,
                          'id_campana': "{0}_{1}".format(
                              campana.id, elimina_espacios(campana.nombre))
                            },
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
        return context

    def get_success_url(self):
        return reverse(
            'queue_member_campana',
            kwargs={"pk_campana": self.kwargs['pk_campana']})


class QueueMemberCampanaView(TemplateView):
    """Vista template despliega el template de cual se van agregar agente o grupos de
    agentes a la campana"""
    template_name = 'queue/queue_member.html'

    def get_object(self, queryset=None):
         campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
         return campana.queue_campana

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        activacion_queue_service = ActivacionQueueService()
        try:
            activacion_queue_service.activar()
        except RestablecerDialplanError, e:
            message = ("<strong>Operación Errónea!</strong> "
                       "No se pudo confirmar la creación del dialplan  "
                       "al siguiente error: {0}".format(e))
            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )

        #agentes = AgenteProfile.objects.filter(reported_by=request.user)
        agentes = AgenteProfile.objects.filter(is_inactive=False)
        queue_member_form = QueueMemberForm(data=self.request.GET or None,
                                            members=agentes)
        grupo_agente_form = GrupoAgenteForm(self.request.GET or None)
        context = self.get_context_data(**kwargs)
        context['queue_member_form'] = queue_member_form
        context['grupo_agente_form'] = grupo_agente_form
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(
            QueueMemberCampanaView, self).get_context_data(**kwargs)
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        context['campana'] = campana
        if campana.type is Campana.TYPE_ENTRANTE:
            context['url_finalizar'] = 'campana_list'
        elif campana.type is Campana.TYPE_DIALER:
            context['url_finalizar'] = 'campana_dialer_list'
        elif campana.type is Campana.TYPE_MANUAL:
            context['url_finalizar'] = 'campana_manual_list'
        return context


def queue_member_delete_view(request, pk_queuemember, pk_campana):
    """Elimina agente asignado en la campana"""
    queue_member = QueueMember.objects.get(pk=pk_queuemember)
    queue_member.delete()
    return HttpResponseRedirect(
        reverse('queue_member_campana',
                kwargs={"pk_campana": pk_campana}
                )
    )
