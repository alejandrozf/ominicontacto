# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.views.generic import ListView, CreateView, UpdateView
from ominicontacto_app.models import (User, AgenteProfile, Queue)
from ominicontacto_app.forms import QueueForm


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
        return reverse('user_list')