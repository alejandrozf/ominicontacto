# -*- coding: utf-8 -*-

"""Vista para la creacion de un objecto campana de tipo manual"""

from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView, DeleteView

from formtools.wizard.views import SessionWizardView

from ominicontacto_app.forms import (CampanaManualForm, OpcionCalificacionFormSet,
                                     ParametroExtraParaWebformFormSet)
from ominicontacto_app.models import Campana, Queue
from ominicontacto_app.views_campana_creacion import (CampanaWizardMixin,
                                                      CampanaTemplateCreateMixin,
                                                      CampanaTemplateCreateCampanaMixin,
                                                      CampanaTemplateDeleteMixin,
                                                      asignar_bd_contactos_defecto_campo_vacio)


import logging as logging_

logger = logging_.getLogger(__name__)


class CampanaManualMixin(CampanaWizardMixin):
    INICIAL = '0'
    COLA = None
    OPCIONES_CALIFICACION = '1'
    PARAMETROS_EXTRA_WEB_FORM = '2'

    FORMS = [(INICIAL, CampanaManualForm),
             (OPCIONES_CALIFICACION, OpcionCalificacionFormSet),
             (PARAMETROS_EXTRA_WEB_FORM, ParametroExtraParaWebformFormSet)]

    TEMPLATES = {INICIAL: "campana_manual/nueva_edita_campana.html",
                 OPCIONES_CALIFICACION: "campana_manual/opcion_calificacion.html",
                 PARAMETROS_EXTRA_WEB_FORM: "campana_manual/parametros_extra_web_form.html"}

    form_list = FORMS


class CampanaManualCreateView(CampanaManualMixin, SessionWizardView):
    """
    Esta vista crea una campaña de tipo manual
    """

    def _save_forms(self, form_list, estado, tipo):
        campana_form = form_list[int(self.INICIAL)]
        opciones_calificacion_formset = form_list[int(self.OPCIONES_CALIFICACION)]
        parametros_extra_web_formset = form_list[int(self.PARAMETROS_EXTRA_WEB_FORM)]
        campana_form.instance.type = tipo
        campana_form.instance.reported_by = self.request.user
        campana_form.instance.estado = estado
        campana_form = asignar_bd_contactos_defecto_campo_vacio(campana_form)
        campana_form.save()
        auto_grabacion = campana_form.cleaned_data['auto_grabacion']
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
            auto_grabacion=auto_grabacion)
        opciones_calificacion_formset.instance = campana
        opciones_calificacion_formset.save()
        parametros_extra_web_formset.instance = campana
        parametros_extra_web_formset.save()
        return queue

    def done(self, form_list, **kwargs):
        queue = self._save_forms(form_list, Campana.ESTADO_ACTIVA, Campana.TYPE_MANUAL)
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
            initial['auto_grabacion'] = campana.queue_campana.auto_grabacion
        return initial

    def _save_forms(self, form_list, **kwargs):
        campana_form = form_list[int(self.INICIAL)]
        opciones_calificacion_formset = form_list[int(self.OPCIONES_CALIFICACION)]
        parametros_extra_web_formset = form_list[int(self.PARAMETROS_EXTRA_WEB_FORM)]
        campana_form = asignar_bd_contactos_defecto_campo_vacio(campana_form)
        campana_form.save()
        auto_grabacion = campana_form.cleaned_data['auto_grabacion']
        campana = campana_form.instance
        queue = campana.queue_campana
        queue.auto_grabacion = auto_grabacion
        queue.save()
        opciones_calificacion_formset.instance = campana
        opciones_calificacion_formset.save()
        parametros_extra_web_formset.instance = campana
        parametros_extra_web_formset.save()
        return queue

    def done(self, form_list, **kwargs):
        queue = self._save_forms(form_list, **kwargs)
        self._insert_queue_asterisk(queue)
        return HttpResponseRedirect(reverse('campana_manual_list'))


class CampanaManualTemplateListView(ListView):
    """
    Vista que muestra todos los templates de campañas entrantes activos
    """
    template_name = "campana_manual/lista_template.html"
    context_object_name = 'templates_activos_manuales'
    model = Campana

    def get_queryset(self):
        return Campana.objects.obtener_templates_activos_manuales()


class CampanaManualTemplateCreateView(CampanaTemplateCreateMixin, CampanaManualCreateView):
    """
    Crea una campaña sin acción en el sistema, sólo con el objetivo de servir de
    template base para agilizar la creación de las campañas manuales
    """
    def done(self, form_list, **kwargs):
        self._save_forms(form_list, Campana.ESTADO_TEMPLATE_ACTIVO, Campana.TYPE_MANUAL)
        return HttpResponseRedirect(reverse('campana_manual_template_list'))


class CampanaManualTemplateCreateCampanaView(
        CampanaTemplateCreateCampanaMixin, CampanaManualCreateView):
    """
    Crea una campaña manual a partir de una campaña de template existente
    """
    def get_form_initial(self, step):
        initial = super(CampanaManualTemplateCreateCampanaView, self).get_form_initial(step)
        if step == self.INICIAL:
            pk = self.kwargs.get('pk_campana_template', None)
            campana_template = get_object_or_404(Campana, pk=pk)
            initial['auto_grabacion'] = campana_template.queue_campana.auto_grabacion
        return initial


class CampanaManualTemplateDetailView(DetailView):
    """
    Muestra el detalle de un template para crear una campaña manual
    """
    template_name = "campana_manual/detalle_campana_template.html"
    model = Campana


class CampanaManualTemplateDeleteView(CampanaTemplateDeleteMixin, DeleteView):
    """
    Esta vista se encarga de la eliminación del
    objeto Campana Manual-->Template.
    """
    model = Campana
    template_name = "campana_manual/delete_campana_template.html"

    def get_success_url(self):
        return reverse("campana_manual_template_list")
