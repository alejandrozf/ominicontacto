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
    CampanaManualForm, QueueDialerForm, QueueDialerUpdateForm, SincronizaDialerForm
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
        self.object.estado = Campana.ESTADO_ACTIVA
        self.object.save()
        auto_grabacion = form.cleaned_data['auto_grabacion']
        detectar_contestadores = form.cleaned_data['detectar_contestadores']
        queue = Queue(
            campana=self.object,
            name=self.object.nombre,
            maxlen=5,
            wrapuptime=5,
            servicelevel=30,
            strategy='rrmemory',
            eventmemberstatus=True,
            eventwhencalled=True,
            ringinuse=True,
            setinterfacevar=True,
            weight=0,
            wait=120,
            queue_asterisk=Queue.objects.ultimo_queue_asterisk(),
            auto_grabacion=auto_grabacion,
            detectar_contestadores=detectar_contestadores
        )
        queue.save()
        return super(CampanaManualCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            'campana_manual_list')


class CampanaManualUpdateView(UpdateView):
    """
    Esta vista actualiza un objeto Campana.
    """

    template_name = 'campana_manual/nueva_edita_campana.html'
    model = Campana
    context_object_name = 'campana'
    form_class = CampanaManualForm

    def get_initial(self):
        initial = super(CampanaManualUpdateView, self).get_initial()
        campana = self.get_object()
        initial.update({
            'auto_grabacion': campana.queue_campana.auto_grabacion,
            'detectar_contestadores': campana.queue_campana.detectar_contestadores})
        return initial

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
        auto_grabacion = form.cleaned_data['auto_grabacion']
        detectar_contestadores = form.cleaned_data['detectar_contestadores']
        queue = self.object.queue_campana
        queue.auto_grabacion = auto_grabacion
        queue.detectar_contestadores = detectar_contestadores
        queue.save()
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
        return reverse('campana_manual_list')
