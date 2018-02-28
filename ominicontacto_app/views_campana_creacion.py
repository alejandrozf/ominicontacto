# -*- coding: utf-8 -*-

"""Vistas para la gestión de campañas entrantes"""

from __future__ import unicode_literals


from django import forms
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, DeleteView
from django.utils.translation import ugettext as _


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


class CampanaEntranteMixin(object):
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

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]

    def get_form(self, step=None, data=None, files=None):
        if step is None:
            step = self.steps.current
        if step != self.COLA:
            return super(CampanaEntranteMixin, self).get_form(step, data, files)
        else:
            # se mantiene la mayor parte del código existente en el plug-in 'formtools
            # con la excepción de que se le pasa el argumento 'audio_choices' para instanciar
            # con éxito el formulario correspondiente pues formtools no es lo suficientemente
            # flexible
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

    def _insert_queue_asterisk(self, queue):
        servicio_asterisk = AsteriskService()
        servicio_asterisk.insertar_cola_asterisk(queue)
        activacion_queue_service = ActivacionQueueService()
        try:
            activacion_queue_service.activar()
        except RestablecerDialplanError:
            raise


class CampanaEntranteCreateView(CampanaEntranteMixin, SessionWizardView):
    """
    Esta vista crea una campaña entrante
    """

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
        return queue_form.instance

    def _save_forms(self, form_list, estado):
        campana_form = form_list[int(self.INICIAL)]
        queue_form = form_list[int(self.COLA)]
        opciones_calificacion_formset = form_list[int(self.OPCIONES_CALIFICACION)]
        campana_form.instance.type = Campana.TYPE_ENTRANTE
        campana_form.instance.reported_by = self.request.user
        campana_form.instance.estado = estado
        campana_form.save()
        campana = campana_form.instance
        queue_form.instance.campana = campana
        queue = self._save_queue(queue_form)
        opciones_calificacion_formset.instance = campana
        opciones_calificacion_formset.save()
        return queue

    def done(self, form_list, **kwargs):
        queue = self._save_forms(form_list, Campana.ESTADO_ACTIVA)
        self._insert_queue_asterisk(queue)
        return HttpResponseRedirect(reverse('campana_list'))

    def get_form_initial(self, step):
        initial_data = super(CampanaEntranteCreateView, self).get_form_initial(step)
        if step == self.COLA:
            step_cleaned_data = self.get_cleaned_data_for_step(self.INICIAL)
            name = step_cleaned_data['nombre']
            initial_data.update({'name': name})
        return initial_data


class CampanaEntranteUpdateView(CampanaEntranteMixin, SessionWizardView):
    """
    Esta vista modifica una campaña entrante
    """

    def done(self, form_list, *args, **kwargs):
        campana_form = form_list[int(self.INICIAL)]
        queue_form = form_list[int(self.COLA)]
        campana_form.instance.save()
        queue_form.instance.save()
        campana = campana_form.instance
        opts_calif_init_formset = form_list[int(self.OPCIONES_CALIFICACION)]
        opts_calif_formset = OpcionCalificacionFormSet(
            self.request.POST, prefix=opts_calif_init_formset.prefix,
            instance=campana)
        opts_calif_formset.save()
        self._insert_queue_asterisk(queue_form.instance)
        return HttpResponseRedirect(reverse('campana_list'))

    def get_form_instance(self, step):
        pk = self.kwargs.get('pk_campana', None)
        campana = get_object_or_404(Campana, pk=pk)
        if step == self.INICIAL:
            return campana
        if step == self.COLA:
            return campana.queue_campana

    def get_context_data(self, form, *args, **kwargs):
        context = super(CampanaEntranteUpdateView, self).get_context_data(form=form, **kwargs)
        if self.steps.current == self.OPCIONES_CALIFICACION:
            campana = self.get_form_instance(self.INICIAL)
            context['wizard']['form'].queryset = campana.opciones_calificacion.all()
        return context


class CampanaEntranteTemplateListView(ListView):
    """
    Vista que muestra todos los templates de campañas entrantes activos
    """
    template_name = "campana/lista_template.html"
    context_object_name = 'templates_activos_entrantes'
    model = Campana

    def get_queryset(self):
        return Campana.objects.obtener_templates_activos_entrantes()


class CampanaEntranteTemplateCreateView(CampanaEntranteCreateView):
    """
    Crea una campaña sin acción en el sistema, sólo con el objetivo de servir de
    template base para agilizar la creación de las campañas entrantes
    """
    def get_form_initial(self, step):
        initial_data = super(CampanaEntranteCreateView, self).get_form_initial(step)
        if step == self.INICIAL:
            ultimo_id_campana = Campana.objects.obtener_ultimo_id_campana() + 1
            campana_nombre = "CAMPANA_CLONADA_{0}".format(ultimo_id_campana)
            initial_data.update({'nombre': campana_nombre})
        elif step == self.COLA:
            step_cleaned_data = self.get_cleaned_data_for_step(self.INICIAL)
            name = step_cleaned_data['nombre']
            initial_data.update({'name': name})
        return initial_data

    def done(self, form_list, **kwargs):
        self._save_forms(form_list, Campana.ESTADO_TEMPLATE_ACTIVO)
        return HttpResponseRedirect(reverse('campana_entrante_template_list'))


class CampanaEntranteTemplateCreateCampanaView(CampanaEntranteCreateView):
    """
    Crea una campaña entrante a partir de una campaña de template existente
    """
    def get_form_initial(self, step):
        pk = self.kwargs.get('pk_campana_template', None)
        campana_template = get_object_or_404(Campana, pk=pk)
        if step == self.INICIAL:
            ultimo_id_campana = Campana.objects.obtener_ultimo_id_campana() + 1
            campana_nombre = "CAMPANA_CLONADA_{0}".format(ultimo_id_campana)
            initial_data = {
                'nombre': campana_nombre,
                'bd_contacto': campana_template.bd_contacto,
                'formulario': campana_template.formulario,
                'gestion': campana_template.gestion,
                'objetivo': campana_template.objetivo}
        elif step == self.COLA:
            step_cleaned_data = self.get_cleaned_data_for_step(self.INICIAL)
            name = step_cleaned_data['nombre']
            queue = campana_template.queue_campana
            initial_data = {
                'name': name,
                'timeout': queue.timeout,
                'retry': queue.retry,
                'maxlen': queue.maxlen,
                'servicelevel': queue.servicelevel,
                'strategy': queue.strategy,
                'weight': queue.weight,
                'wait': queue.wait,
                'announce_frequency': queue.announce_frequency,
                'audio_de_ingreso': queue.audio_de_ingreso,
            }
        else:
            initial_data = super(
                CampanaEntranteTemplateCreateCampanaView, self).get_form_initial(step)
        return initial_data

    def get_context_data(self, form, *args, **kwargs):
        context = super(
            CampanaEntranteTemplateCreateCampanaView, self).get_context_data(form=form, **kwargs)
        if self.steps.current == self.OPCIONES_CALIFICACION:
            pk = self.kwargs.get('pk_campana_template', None)
            campana_template = get_object_or_404(Campana, pk=pk)
            initial_data = campana_template.opciones_calificacion.values('nombre', 'tipo')
            opts_calif_init_formset = context['wizard']['form']
            calif_init_formset = OpcionCalificacionFormSet(initial=initial_data)
            calif_init_formset.extra = len(initial_data) - 1
            calif_init_formset.prefix = opts_calif_init_formset.prefix
            context['wizard']['form'] = calif_init_formset
        return context


class CampanaEntranteTemplateDetailView(DetailView):
    """
    Muestra el detalle de un template para crear una campaña entrante
    """
    template_name = "campana/detalle_campana_template.html"
    model = Campana


class CampanaEntranteTemplateDeleteView(DeleteView):
    """
    Esta vista se encarga de la eliminación del
    objeto Campana Entrante-->Template.
    """
    template_name = "campana/delete_campana_template.html"
    model = Campana

    def get_success_url(self):
        return reverse("campana_entrante_template_list")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.borrar_template()

        message = _("Operación Exitosa:\
        se llevó a cabo con éxito la eliminación del Template.")

        messages.add_message(
            self.request,
            messages.SUCCESS,
            message,
            extra_tags="safe",
        )
        return HttpResponseRedirect(self.get_success_url())
