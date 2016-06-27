# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.views.generic import ListView, CreateView, UpdateView
from ominicontacto_app.models import (User, AgenteProfile, Queue, QueueMember)
from ominicontacto_app.forms import QueueForm, QueueMemberForm


class QueueCreateView(CreateView):
    model = Queue
    form_class = QueueForm
    template_name = 'queue/create_update_queue.html'

    # def get_initial(self):
    #     initial = super(AgenteProfileCreateView, self).get_initial()
    #     initial.update({'user': self.kwargs['pk_user']})
    #     return initial

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.eventmemberstatus = True
        self.object.eventwhencalled = True
        self.object.ringinuse = True
        self.object.setinterfacevar = True


        self.object.save()
        #kamailio_service = KamailioService()
        #kamailio_serevice.crear_agente_kamailio(self.object)

        return super(QueueCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            'queue_member',
            kwargs={"pk_queue": self.object.pk}
        )


class QueueMemberCreateView(CreateView):
    model = QueueMember
    form_class = QueueMemberForm
    template_name = 'queue/queue_member.html'

    def get_context_data(self, **kwargs):
        context = super(
            QueueMemberCreateView, self).get_context_data(**kwargs)
        context['queue'] = Queue.objects.get(name=self.kwargs['pk_queue'])
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.queue = Queue.objects.get(name=self.kwargs['pk_queue'])
        self.object.interface = """Local/{0}@from-queue/n""".format(
            self.object.member.sip_extension)
        self.object.paused = 0  # por ahora no lo definimos



        self.object.save()
        #kamailio_service = KamailioService()
        #kamailio_serevice.crear_agente_kamailio(self.object)

        return super(QueueMemberCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            'queue_member',
            kwargs={"pk_queue": self.kwargs['pk_queue']}
        )
