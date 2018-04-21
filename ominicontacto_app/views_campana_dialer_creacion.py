# -*- coding: utf-8 -*-

"""Vista para generar un objecto campana de tipo dialer"""

from __future__ import unicode_literals

# from django.contrib import messages
from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
# from django.shortcuts import redirect
# from django.views.generic import CreateView, UpdateView, FormView
from ominicontacto_app.forms import (QueueDialerForm, SincronizaDialerForm, ActuacionVigenteForm,
                                     ReglasIncidenciaFormSet, CampanaDialerForm,
                                     OpcionCalificacionFormSet, ParametroExtraParaWebformFormSet)
from ominicontacto_app.models import (
    Campana,
    Queue,
)

from ominicontacto_app.services.campana_service import CampanaService
from ominicontacto_app.services.exportar_base_datos import SincronizarBaseDatosContactosService

from formtools.wizard.views import SessionWizardView

from ominicontacto_app.views_campana_creacion import CampanaWizardMixin

import logging as logging_

logger = logging_.getLogger(__name__)


class CampanaDialerMixin(CampanaWizardMixin):
    INICIAL = '0'
    COLA = '1'
    OPCIONES_CALIFICACION = '2'
    PARAMETROS_EXTRA_WEB_FORM = '3'
    ACTUACION_VIGENTE = '4'
    REGLAS_INCIDENCIA = '5'
    SINCRONIZAR = '6'

    FORMS = [(INICIAL, CampanaDialerForm),
             (COLA, QueueDialerForm),
             (OPCIONES_CALIFICACION, OpcionCalificacionFormSet),
             (PARAMETROS_EXTRA_WEB_FORM, ParametroExtraParaWebformFormSet),
             (ACTUACION_VIGENTE, ActuacionVigenteForm),
             (REGLAS_INCIDENCIA, ReglasIncidenciaFormSet),
             (SINCRONIZAR, SincronizaDialerForm)]

    TEMPLATES = {INICIAL: 'campana_dialer/nueva_edita_campana.html',
                 COLA: 'campana_dialer/create_update_queue.html',
                 OPCIONES_CALIFICACION: 'campana_dialer/opcion_calificacion.html',
                 PARAMETROS_EXTRA_WEB_FORM: 'campana_dialer/parametros_extra_web_form.html',
                 ACTUACION_VIGENTE: 'campana_dialer/actuacion_vigente_campana.html',
                 REGLAS_INCIDENCIA: 'campana_dialer/reglas_incidencia.html',
                 SINCRONIZAR: 'campana_dialer/sincronizar_lista.html'}

    form_list = FORMS

    def get_form(self, step=None, data=None, files=None):
        if step is None:
            step = self.steps.current
        if step == self.SINCRONIZAR:
            # se mantiene la mayor parte del código existente en el plug-in 'formtools
            # con la excepción de que se le pasa el argumento 'tts_choices' para instanciar
            # con éxito el formulario correspondiente pues formtools no es lo suficientemente
            # flexible y sólo usa kwargs para instanciar
            campana = self.get_cleaned_data_for_step(self.INICIAL)
            bd_contacto = campana['bd_contacto']
            if bd_contacto is None:
                tts_choices = []
            else:
                metadata = bd_contacto.get_metadata()
                nombres_de_columnas = metadata.nombres_de_columnas
                nombres_de_columnas.remove('telefono')
                tts_choices = [(columna, columna) for columna in
                               nombres_de_columnas]
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
            return form_class(tts_choices, **kwargs)
        return super(CampanaDialerMixin, self).get_form(step, data, files)


class CampanaDialerCreateView(CampanaDialerMixin, SessionWizardView):
    """
    Esta vista crea una campaña de tipo dialer
    """

    def get_form_initial(self, step):
        initial = super(CampanaDialerCreateView, self).get_form_initial(step)
        if step == self.COLA:
            step_initial_cleaned_data = self.get_cleaned_data_for_step(self.INICIAL)
            initial['name'] = step_initial_cleaned_data['nombre']
        return initial

    def get_context_data(self, form, *args, **kwargs):
        context = super(CampanaDialerCreateView, self).get_context_data(form, *args, **kwargs)
        current_step = self.steps.current
        if current_step == self.INICIAL:
            context['canales_en_uso'] = Campana.objects.obtener_canales_dialer_en_uso()
        elif current_step == self.SINCRONIZAR:
            cleaned_data_step_initial = self.get_cleaned_data_for_step(self.INICIAL)
            context['tipo_interaccion'] = cleaned_data_step_initial['tipo_interaccion']
        elif current_step == self.REGLAS_INCIDENCIA and form.forms == []:
            # reiniciamos el formset para que el usuario si no tiene formularios
            # para que el usuario tenga posibilidad de agregar nuevos formularios
            new_formset = ReglasIncidenciaFormSet()
            new_formset.prefix = form.prefix
            context['wizard']['form'] = new_formset
        return context

        return context

    def _save_campana(self, campana_form, estado):
        campana_form.instance.type = Campana.TYPE_DIALER
        campana_form.instance.reported_by = self.request.user
        campana_form.instance.estado = estado
        campana_form.save()
        return campana_form.instance

    def _save_queue(self, queue_form):
        queue_form.instance.eventmemberstatus = True
        queue_form.instance.eventwhencalled = True
        queue_form.instance.ringinuse = True
        queue_form.instance.setinterfacevar = True
        queue_form.instance.queue_asterisk = Queue.objects.ultimo_queue_asterisk()
        if queue_form.instance.initial_boost_factor is None:
            queue_form.instance.initial_boost_factor = 1.0
        queue_form.save()
        return queue_form.instance

    def _sincronizar_campana(self, sincronizar_form, campana):
        evitar_duplicados = sincronizar_form.cleaned_data.get('evitar_duplicados')
        evitar_sin_telefono = sincronizar_form.cleaned_data.get('evitar_sin_telefono')
        prefijo_discador = sincronizar_form.cleaned_data.get('prefijo_discador')
        columnas = sincronizar_form.cleaned_data.get('columnas')
        service_base = SincronizarBaseDatosContactosService()
        # Crea un achivo con la lista de contactos para importar a wombat
        service_base.crear_lista(campana, columnas, evitar_duplicados,
                                 evitar_sin_telefono, prefijo_discador)
        campana_service = CampanaService()
        # crear campana en wombat
        campana_service.crear_campana_wombat(campana)
        # crea trunk en wombat
        campana_service.crear_trunk_campana_wombat(campana)
        # crea reglas de incidencia en wombat
        for regla in campana.reglas_incidencia.all():
            parametros = [regla.get_estado_wombat(), regla.estado_personalizado,
                          regla.intento_max, regla.reintentar_tarde,
                          regla.get_en_modo_wombat()]
            campana_service.crear_reschedule_campana_wombat(campana, parametros)
        # crea endpoint en wombat
        campana_service.crear_endpoint_campana_wombat(campana)
        # asocia endpoint en wombat a campana
        campana_service.crear_endpoint_asociacion_campana_wombat(
            campana)
        # crea lista en wombat
        campana_service.crear_lista_wombat(campana)
        # asocia lista a campana en wombat
        campana_service.crear_lista_asociacion_campana_wombat(campana)

    def _save_forms(self, form_list, estado):
        campana_form = form_list[int(self.INICIAL)]
        queue_form = form_list[int(self.COLA)]
        opciones_calificacion_formset = form_list[int(self.OPCIONES_CALIFICACION)]
        parametros_extra_web_formset = form_list[int(self.PARAMETROS_EXTRA_WEB_FORM)]
        actuacion_vigente_form = form_list[int(self.ACTUACION_VIGENTE)]
        reglas_incidencia_form = form_list[int(self.REGLAS_INCIDENCIA)]

        campana = self._save_campana(campana_form, estado)

        queue_form.instance.campana = campana
        self._save_queue(queue_form)

        opciones_calificacion_formset.instance = campana
        opciones_calificacion_formset.save()

        parametros_extra_web_formset.instance = campana
        parametros_extra_web_formset.save()

        actuacion_vigente_form.instance.campana = campana
        actuacion_vigente_form.save()

        reglas_incidencia_form.instance = campana
        reglas_incidencia_form.save()

        return campana

    def done(self, form_list, **kwargs):
        sincronizar_form = form_list[int(self.SINCRONIZAR)]
        campana = self._save_forms(form_list, Campana.ESTADO_INACTIVA)
        self._sincronizar_campana(sincronizar_form, campana)
        return HttpResponseRedirect(reverse('campana_dialer_list'))


class CampanaDialerUpdateView(CampanaDialerMixin, SessionWizardView):
    """
    Esta vista modifica una campaña de tipo dialer
    """
    INICIAL = '0'
    COLA = '1'
    OPCIONES_CALIFICACION = '2'
    PARAMETROS_EXTRA_WEB_FORM = '3'

    FORMS = [(INICIAL, CampanaDialerForm),
             (COLA, QueueDialerForm),
             (OPCIONES_CALIFICACION, OpcionCalificacionFormSet),
             (PARAMETROS_EXTRA_WEB_FORM, ParametroExtraParaWebformFormSet)]

    TEMPLATES = {INICIAL: 'campana_dialer/edita_campana.html',
                 COLA: 'campana_dialer/create_update_queue.html',
                 OPCIONES_CALIFICACION: 'campana_dialer/opcion_calificacion.html',
                 PARAMETROS_EXTRA_WEB_FORM: 'campana_dialer/parametros_extra_web_form.html'}

    form_list = FORMS

    def _save_queue(self, queue_form):
        if queue_form.instance.initial_boost_factor is None:
            queue_form.instance.initial_boost_factor = 1.0
        return queue_form.save()

    def done(self, form_list, **kwargs):
        campana_form = form_list[int(self.INICIAL)]
        queue_form = form_list[int(self.COLA)]
        opciones_calificacion_formset = form_list[int(self.OPCIONES_CALIFICACION)]
        parametros_extra_web_formset = form_list[int(self.PARAMETROS_EXTRA_WEB_FORM)]

        campana = campana_form.save()
        queue = self._save_queue(queue_form)
        opciones_calificacion_formset.save()
        parametros_extra_web_formset.save()

        self._insert_queue_asterisk(queue, solo_activar=True)
        campana_service = CampanaService()
        campana_service.crear_campana_wombat(campana)
        campana_service.update_endpoint(campana)

        return HttpResponseRedirect(reverse('campana_dialer_list'))
