# -*- coding: utf-8 -*-

"""Vista para la creacion de un objecto campana de tipo manual"""

from __future__ import unicode_literals


from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, FormView, TemplateView)
from ominicontacto_app.forms import (
    CampanaManualForm, QueueForm, QueueUpdateForm, SincronizaDialerForm
)
from ominicontacto_app.models import Campana, Queue, BaseDatosContacto
from ominicontacto_app.services.creacion_queue import (ActivacionQueueService,
                                                       RestablecerDialplanError)
from ominicontacto_app.services.asterisk_service import AsteriskService
from ominicontacto_app.services.campana_service import CampanaService
from ominicontacto_app.services.exportar_base_datos import\
    SincronizarBaseDatosContactosService


import logging as logging_

logger = logging_.getLogger(__name__)


class CheckEstadoCampanaMixin(object):
    """Mixin para utilizar en las vistas de creación de campañas.
    Utiliza `Campana.objects.obtener_en_definicion_para_editar()`
    para obtener la campaña pasada por url.
    Este metodo falla si la campaña no deberia ser editada.
    ('editada' en el contexto del proceso de creacion de la campaña)
    """

    def dispatch(self, request, *args, **kwargs):
        chequeada = kwargs.pop('_campana_chequeada', False)
        if not chequeada:
            self.campana = Campana.objects.obtener_en_definicion_para_editar(
                self.kwargs['pk_campana'])

        return super(CheckEstadoCampanaMixin, self).dispatch(request, *args,
                                                             **kwargs)


class CampanaEnDefinicionMixin(object):
    """Mixin para obtener el objeto campama que valida que siempre este en
    el estado en definición.
    """

    def get_object(self, queryset=None):
        return Campana.objects.obtener_en_definicion_para_editar(
            self.kwargs['pk_campana'])


class CampanaManualCreateView(CreateView):
    """
    Esta vista crea un objeto Campana.
    Por defecto su estado es EN_DEFICNICION,
    Redirecciona a crear las opciones para esta
    Campana.
    """

    template_name = 'campana_manual/nueva_edita_campana.html'
    model = Campana
    context_object_name = 'campana'
    form_class = CampanaManualForm

    def dispatch(self, request, *args, **kwargs):
        base_datos = BaseDatosContacto.objects.obtener_definidas()
        if not base_datos:
            message = ("Debe cargar una base de datos antes de comenzar a "
                       "configurar una campana")
            messages.warning(self.request, message)
        return super(CampanaManualCreateView, self).dispatch(request, *args, **kwargs)

    def form_invalid(self, form, error=None):

        message = '<strong>Operación Errónea!</strong> \
                . {0}'.format(error)

        messages.add_message(
            self.request,
            messages.WARNING,
            message,
        )
        return self.render_to_response(self.get_context_data())

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if self.object.tipo_interaccion is Campana.FORMULARIO and \
            not self.object.formulario:
            error = "Debe seleccionar un formulario"
            return self.form_invalid(form, error=error)
        elif self.object.tipo_interaccion is Campana.SITIO_EXTERNO and \
            not self.object.sitio_externo:
            error = "Debe seleccionar un sitio externo"
            return self.form_invalid(form, error=error)
        self.object.type = Campana.TYPE_MANUAL
        self.object.reported_by = self.request.user
        self.object.save()
        return super(CampanaManualCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            'queue_nuevo',
            kwargs={"pk_campana": self.object.pk})


class CampanaManualUpdateView(UpdateView):
    """
    Esta vista actualiza un objeto Campana.
    """

    template_name = 'campana_manual/nueva_edita_campana.html'
    model = Campana
    context_object_name = 'campana'
    form_class = CampanaManualForm

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if self.object.tipo_interaccion is Campana.FORMULARIO and \
            not self.object.formulario:
            error = "Debe seleccionar un formulario"
            return self.form_invalid(form, error=error)
        elif self.object.tipo_interaccion is Campana.SITIO_EXTERNO and \
            not self.object.sitio_externo:
            error = "Debe seleccionar un sitio externo"
            return self.form_invalid(form, error=error)
        self.object.save()
        return super(CampanaManualUpdateView, self).form_valid(form)

    def form_invalid(self, form, error=None):

        message = '<strong>Operación Errónea!</strong> \
                . {0}'.format(error)

        messages.add_message(
            self.request,
            messages.WARNING,
            message,
        )
        return self.render_to_response(self.get_context_data())

    def get_success_url(self):
        return reverse(
            'queue_update',
            kwargs={"pk_campana": self.object.pk})


class QueueCreateView(CheckEstadoCampanaMixin, CampanaEnDefinicionMixin,
                      CreateView):
    """Vista para la creacion de una Cola"""
    model = Queue
    form_class = QueueForm
    template_name = 'queue/create_update_queue.html'

    def get_initial(self):
        initial = super(QueueCreateView, self).get_initial()
        initial.update({'campana': self.campana.id,
                        'name': self.campana.nombre})
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
        self.campana.estado = Campana.ESTADO_ACTIVA
        self.campana.save()
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
        return super(QueueCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(QueueCreateView, self).get_context_data(**kwargs)
        context['campana'] = self.campana
        return context

    def get_success_url(self):
        return reverse('campana_list')


class QueueUpdateView(UpdateView):
    """Vista actualiza una Queue(Cola)"""
    model = Queue
    form_class = QueueUpdateForm
    template_name = 'queue/create_update_queue.html'

    def get_object(self, queryset=None):
         campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
         return campana.queue_campana

    def dispatch(self, *args, **kwargs):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        try:
            Queue.objects.get(campana=campana)
        except Queue.DoesNotExist:
            return HttpResponseRedirect("/campana/" + self.kwargs['pk_campana']
                                        + "/cola/")
        else:
            return super(QueueUpdateView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
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
        return super(QueueUpdateView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(QueueUpdateView, self).get_context_data(**kwargs)
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        context['campana'] = campana
        return context

    def get_success_url(self):
        return reverse('campana_list')
