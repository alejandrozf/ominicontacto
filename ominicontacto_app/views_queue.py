# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from ominicontacto_app.models import (Queue, QueueMember)
from ominicontacto_app.forms import QueueForm, QueueMemberForm, QueueUpdateForm
from ominicontacto_app.services.creacion_queue import (ActivacionQueueService,
                                                       RestablecerDialplanError)
from ominicontacto_app.services.asterisk_service import AsteriskService
from ominicontacto_app.views_campana_creacion import CheckEstadoCampanaMixin,\
    CampanaEnDefinicionMixin


class QueueCreateView(CheckEstadoCampanaMixin, CreateView):
    model = Queue
    form_class = QueueForm
    template_name = 'queue/create_update_queue.html'

    def get_initial(self):
        initial = super(QueueCreateView, self).get_initial()
        initial.update({'campana': self.campana.id})
        return initial

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.eventmemberstatus = True
        self.object.eventwhencalled = True
        self.object.ringinuse = True
        self.object.setinterfacevar = True
        self.object.queue_asterisk = Queue.objects.ultimo_queue_asterisk()
        self.object.save()
        servicio_asterisk = AsteriskService()
        servicio_asterisk.insertar_cola_asterisk(self.object)
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

    def get_object(self, queryset=None):
        return Queue.objects.get(name=self.kwargs['pk_queue'])

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
        return self.render_to_response(self.get_context_data())

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

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()

        # Eliminamos el registro de la tabla de asterisk en mysql
        servicio_asterisk = AsteriskService()
        servicio_asterisk.delete_cola_asterisk(self.object)
        # realizamos la eliminacion de la queue
        self.object.delete()
        # actualizamos el archivo de dialplan
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


        message = '<strong>Operación Exitosa!</strong>\
        Se llevó a cabo con éxito la eliminación de la queue.'

        messages.add_message(
            self.request,
            messages.SUCCESS,
            message,
        )
        return HttpResponseRedirect(success_url)

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
