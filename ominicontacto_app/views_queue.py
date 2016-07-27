# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from ominicontacto_app.models import (Queue, QueueMember)
from ominicontacto_app.forms import QueueForm, QueueMemberForm, QueueUpdateForm


class QueueCreateView(CreateView):
    model = Queue
    form_class = QueueForm
    template_name = 'queue/create_update_queue.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.eventmemberstatus = True
        self.object.eventwhencalled = True
        self.object.ringinuse = True
        self.object.setinterfacevar = True
        self.object.queue_asterisk = Queue.objects.ultimo_queue_asterisk()
        self.object.save()

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
        queue = Queue.objects.get(name=self.kwargs['pk_queue'])
        context['queuemember'] = QueueMember.objects.filter(queue_name=queue)
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        queue = Queue.objects.get(name=self.kwargs['pk_queue'])
        existe_member = QueueMember.objects.\
            existe_member_queue(self.object.member, queue)

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
            self.object.queue_name = queue
            self.object.membername = self.object.member.user.get_full_name()
            self.object.interface = """Local/{0}@from-queue/n""".format(
            self.object.member.sip_extension)
            self.object.paused = 0  # por ahora no lo definimos
            self.object.save()

        return super(QueueMemberCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            'queue_member',
            kwargs={"pk_queue": self.kwargs['pk_queue']}
        )


class QueueListView(ListView):
    model = Queue
    template_name = 'queue/queue_list.html'


class QueueDeleteView(DeleteView):
    """
    Esta vista se encarga de la eliminación del
    objeto queue.
    """
    model = Queue
    template_name = 'queue/delete_queue.html'

    def get_object(self, queryset=None):
        return Queue.objects.get(name=self.kwargs['pk_queue'])

    def get_success_url(self):
        return reverse('queue_list')


class QueueUpdateView(UpdateView):
    model = Queue
    form_class = QueueUpdateForm
    template_name = 'queue/create_update_queue.html'

    def get_object(self, queryset=None):
        return Queue.objects.get(name=self.kwargs['pk_queue'])

    def get_success_url(self):
        return reverse(
            'queue_member',
            kwargs={"pk_queue": self.kwargs['pk_queue']}
        )


# usa template de confirmacion por eso se usa la view queue_member_delete_view
class QueueMemberDeleteView(DeleteView):
    """
    Esta vista se encarga de la eliminación del
    objeto queue.
    """
    model = QueueMember

    def get_object(self, queryset=None):
        return QueueMember.objects.get(pk=self.kwargs['pk_queuemember'])

    def get_success_url(self):
        return reverse(
            'queue_member',
            kwargs={"pk_queue": self.kwargs['pk_queue']}
        )


def queue_member_delete_view(request, pk_queuemember, pk_queue):
    queue = QueueMember.objects.get(pk=pk_queuemember)
    queue.delete()
    return HttpResponseRedirect('/queue_member/' + str(pk_queue) + "/")
