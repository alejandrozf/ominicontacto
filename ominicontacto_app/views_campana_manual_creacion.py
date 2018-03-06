# -*- coding: utf-8 -*-

"""Vista para la creacion de un objecto campana de tipo manual"""

from __future__ import unicode_literals


from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, FormView, TemplateView)

from formtools.wizard.views import SessionWizardView

from ominicontacto_app.forms import CampanaManualForm, OpcionCalificacionFormSet
from ominicontacto_app.models import Campana, Queue, BaseDatosContacto
from ominicontacto_app.services.creacion_queue import (ActivacionQueueService,
                                                       RestablecerDialplanError)
from ominicontacto_app.services.asterisk_service import AsteriskService
from ominicontacto_app.services.campana_service import CampanaService
from ominicontacto_app.services.exportar_base_datos import\
    SincronizarBaseDatosContactosService
from ominicontacto_app.views_campana_creacion import CampanaEntranteMixin, CampanaEntranteCreateView


import logging as logging_

logger = logging_.getLogger(__name__)


class CampanaManualMixin(CampanaEntranteMixin):
    INICIAL = '0'
    COLA = None
    OPCIONES_CALIFICACION = '1'

    FORMS = [(INICIAL, CampanaManualForm),
             (OPCIONES_CALIFICACION, OpcionCalificacionFormSet)]

    TEMPLATES = {INICIAL: "campana_manual/nueva_edita_campana.html",
                 OPCIONES_CALIFICACION: "campana_manual/opcion_calificacion.html"}

    form_list = FORMS


class CampanaManualCreateView(CampanaManualMixin, SessionWizardView):
    """
    Esta vista crea una campaña de tipo manual
    """

    def done(self, form_list, **kwargs):
        campana_form = form_list[int(self.INICIAL)]
        opciones_calificacion_formset = form_list[int(self.OPCIONES_CALIFICACION)]
        campana_form.instance.type = Campana.TYPE_MANUAL
        campana_form.instance.reported_by = self.request.user
        campana_form.instance.estado = Campana.ESTADO_ACTIVA
        campana_form.save()
        auto_grabacion = campana_form.cleaned_data['auto_grabacion']
        detectar_contestadores = campana_form.cleaned_data['detectar_contestadores']
        campana = campana_form.instance
        queue = Queue.objects.create(
            campana=campana,
            name=campana.nombre,
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
            detectar_contestadores=detectar_contestadores)
        opciones_calificacion_formset.instance = campana
        opciones_calificacion_formset.save()
        self._insert_queue_asterisk(queue)
        return HttpResponseRedirect(reverse('campana_manual_list'))


class CampanaManualUpdateView(CampanaManualMixin, SessionWizardView):
    """
    Esta vista actualiza una campaña de tipo manual.
    """

    def get_form_initial(self, step):
        initial = super(CampanaManualUpdateView, self).get_form_initial(step)
        campana = self.get_form_instance(step)
        if step == self.INICIAL:
            initial.update({
                'auto_grabacion': campana.queue_campana.auto_grabacion,
                'detectar_contestadores': campana.queue_campana.detectar_contestadores})
        return initial

    def form_valid(self, form):
        auto_grabacion = form.cleaned_data['auto_grabacion']
        detectar_contestadores = form.cleaned_data['detectar_contestadores']
        queue = self.object.queue_campana
        queue.auto_grabacion = auto_grabacion
        queue.detectar_contestadores = detectar_contestadores
        queue.save()
        return super(CampanaManualUpdateView, self).form_valid(form)

    def done(self, form_list, **kwargs):
        campana_form = form_list[int(self.INICIAL)]
        opciones_calificacion_formset = form_list[int(self.OPCIONES_CALIFICACION)]
        campana_form.save()
        auto_grabacion = campana_form.cleaned_data['auto_grabacion']
        detectar_contestadores = campana_form.cleaned_data['detectar_contestadores']
        campana = campana_form.instance
        queue = campana.queue_campana
        queue.detectar_contestadores = detectar_contestadores
        queue.auto_grabacion = auto_grabacion
        opciones_calificacion_formset.instance = campana
        opciones_calificacion_formset.save()
        self._insert_queue_asterisk(queue)
        return HttpResponseRedirect(reverse('campana_manual_list'))

    def get_success_url(self):
        return reverse('campana_manual_list')
