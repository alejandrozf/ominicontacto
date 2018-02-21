# -*- coding: utf-8 -*-

"""Vistas para la gestión de campañas entrantes"""

from __future__ import unicode_literals


from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from formtools.wizard.views import SessionWizardView

from ominicontacto_app.forms import (
    CampanaForm, QueueEntranteForm, OpcionCalificacionFormSet, ParametroExtraParaWebformFormSet
)
from ominicontacto_app.models import Campana, Queue, ArchivoDeAudio

from ominicontacto_app.services.creacion_queue import (ActivacionQueueService,
                                                       RestablecerDialplanError)
from ominicontacto_app.services.asterisk_service import AsteriskService

import logging as logging_

logger = logging_.getLogger(__name__)


class CampanaEntranteCreateView(SessionWizardView):
    """
    Esta vista crea un objeto Campana de tipo entrante
    """

    INICIAL = '0'
    COLA = '1'
    OPCIONES_CALIFICACION = '2'

    FORMS = [(INICIAL, CampanaForm),
             (COLA, QueueEntranteForm),
             (OPCIONES_CALIFICACION, OpcionCalificacionFormSet)]

    TEMPLATES = {INICIAL: "campana/nueva_edita_campana.html",
                 COLA: "campana/create_update_queue.html",
                 OPCIONES_CALIFICACION: "campana/opcion_calificacion.html"}

    form_list = FORMS

    model = Campana
    context_object_name = 'campana'
    form_class = CampanaForm

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]

    def _save_queue(self, queue_form):
        queue_form.instance.eventmemberstatus = True
        queue_form.instance.eventwhencalled = True
        queue_form.instance.ringinuse = True
        queue_form.instance.setinterfacevar = True
        queue_form.instance.wrapuptime = 0
        queue_form.instance.queue_asterisk = Queue.objects.ultimo_queue_asterisk()
        audio_pk = queue_form.cleaned_data['audios']
        if audio_pk:
            audio = ArchivoDeAudio.objects.get(pk=int(audio_pk))
            queue_form.instance.announce = audio.audio_asterisk
        else:
            queue_form.instance.announce = None
        queue_form.instance.save()
        servicio_asterisk = AsteriskService()
        servicio_asterisk.insertar_cola_asterisk(queue_form.instance)
        activacion_queue_service = ActivacionQueueService()
        try:
            activacion_queue_service.activar()
        except RestablecerDialplanError:
            raise

    def done(self, form_list, **kwargs):
        campana_form = form_list[int(self.INICIAL)]
        queue_form = form_list[int(self.COLA)]
        opciones_calificacion_formset = form_list[int(self.OPCIONES_CALIFICACION)]
        campana_form.instance.type = Campana.TYPE_ENTRANTE
        campana_form.instance.reported_by = self.request.user
        campana_form.instance.estado = Campana.ESTADO_ACTIVA
        campana_form.save()
        campana = campana_form.instance
        queue_form.instance.campana = campana
        self._save_queue(queue_form)
        opciones_calificacion_formset.instance = campana
        opciones_calificacion_formset.save()
        return HttpResponseRedirect(reverse('campana_list'))

    def get_form(self, step=None, data=None, files=None):
        if step is None:
            step = self.steps.current
        if step != self.COLA:
            return super(CampanaEntranteCreateView, self).get_form(step, data, files)
        else:
            # se mantiene la mayor parte del código existente en el plug-in 'formtools
            # con la excepción de que se le pasa el argumento 'audio_choices' para instanciar
            # con éxito el formulario correspondiente
            audio_choices = ArchivoDeAudio.objects.all()
            form_class = self.form_list[step]
            kwargs = self.get_form_kwargs(step)
            kwargs.update({
                'data': data,
                'files': files,
                'prefix': self.get_form_prefix(step, form_class),
                'initial': self.get_form_initial(step),
            })
            if issubclass(form_class, (forms.ModelForm, forms.models.BaseInlineFormSet)):
                kwargs.setdefault('instance', self.get_form_instance(step))
            elif issubclass(form_class, forms.models.BaseModelFormSet):
                kwargs.setdefault('queryset', self.get_form_instance(step))
            return form_class(audio_choices, **kwargs)

    def get_form_initial(self, step):
        initial_data = super(CampanaEntranteCreateView, self).get_form_initial(step)
        if step == self.COLA:
            step_cleaned_data = self.get_cleaned_data_for_step(self.INICIAL)
            name = step_cleaned_data['nombre']
            initial_data.update({'name': name})
        return initial_data
