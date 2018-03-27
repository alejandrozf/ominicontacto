# -*- coding: utf-8 -*-

"""En este modulo se encuentran las vista de interaccion formularios de calificacion
y gestion con el agente en campañas manuales
"""

from __future__ import unicode_literals

import json
import logging as logging_

from django.contrib import messages
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.views.generic.edit import FormView

from ominicontacto_app.models import CalificacionCliente, Campana, AgenteProfile, Contacto
from ominicontacto_app.forms import CalificacionClienteForm, FormularioContactoCalificacion
from ominicontacto_app.utiles import convertir_ascii_string

logger = logging_.getLogger(__name__)


class CalificacionManualFormView(FormView):
    """
    Vista para la creacion y actualización de las calificaciones.
    Además actualiza los datos del contacto.
    """
    template_name = 'campana_manual/calificacion_create_update.html'
    context_object_name = 'calificacion_manual'
    model = CalificacionCliente
    form_class = CalificacionClienteForm

    def get_contacto(self):
        if 'pk_contacto' in self.kwargs and self.kwargs['pk_contacto'] is not None:
            try:
                return Contacto.objects.get(pk=self.kwargs['pk_contacto'])
            except Contacto.DoesNotExist:
                return None
        return None

    def get_object(self):
        if self.contacto is not None:
            try:
                return CalificacionCliente.objects.get(
                    opcion_calificacion__campana=self.campana,
                    contacto_id=self.contacto.id)
            except CalificacionCliente.DoesNotExist:
                return None
        return None

    def dispatch(self, *args, **kwargs):
        self.agente = AgenteProfile.objects.get(pk=self.kwargs['id_agente'])
        self.campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        self.contacto = self.get_contacto()
        self.wombat_id = self.kwargs.get('wombat_id', '0')

        self.object = self.get_object()
        return super(CalificacionManualFormView, self).dispatch(*args, **kwargs)

    def get_calificacion_form_kwargs(self):
        if self.request.method == 'GET':

            if self.contacto is not None:
                initial = {'contacto': self.contacto.id}
                return {'instance': self.object, 'initial': initial}
            return {'instance': self.object}
        elif self.request.method == 'POST':
            post_data = self.request.POST
            return {'instance': self.object, 'data': post_data}

    def get_form(self):
        kwargs = self.get_calificacion_form_kwargs()
        return CalificacionClienteForm(campana=self.campana, **kwargs)

    def get_contacto_form_kwargs(self):
        kwargs = {}
        initial = {}
        if self.contacto is not None:
            kwargs['instance'] = self.contacto
        else:
            initial['telefono'] = self.kwargs['telefono']

        if self.request.method == 'GET':
            # TODO: Pasar esta logica al formulario?
            base_datos = self.campana.bd_contacto
            nombres = base_datos.get_metadata().nombres_de_columnas[1:]
            if self.contacto is not None:
                datos = json.loads(self.contacto.datos)
            else:
                # Si no tengo contacto, paso los datos vacios.
                datos = [''] * len(nombres)
            for nombre, dato in zip(nombres, datos):
                initial.update({convertir_ascii_string(nombre): dato})
            kwargs['initial'] = initial
        elif self.request.method == 'POST':
            kwargs['data'] = self.request.POST

        return kwargs

    def get_campos_formulario_contacto(self):
        # TODO: Pasar esta logica al formulario?
        base_datos = self.campana.bd_contacto
        metadata = base_datos.get_metadata()
        campos = metadata.nombres_de_columnas
        return campos

    def get_contacto_form(self):
        return FormularioContactoCalificacion(campos=self.get_campos_formulario_contacto(),
                                              **self.get_contacto_form_kwargs())

    def get(self, request, *args, **kwargs):
        contacto_form = self.get_contacto_form()
        calificacion_form = self.get_form()

        return self.render_to_response(self.get_context_data(
            contacto_form=contacto_form, calificacion_form=calificacion_form))

    def post(self, request, *args, **kwargs):
        """
        Valida formulario de Contacto y de CalificacionCliente
        """
        contacto_form = self.get_contacto_form()
        calificacion_form = self.get_form()
        if contacto_form.is_valid() and calificacion_form.is_valid():
            return self.form_valid(contacto_form, calificacion_form)
        else:
            return self.form_invalid(contacto_form, calificacion_form)

    def form_valid(self, contacto_form, calificacion_form):
        contacto = contacto_form.save(commit=False)
        # TODO: Pasar esta logica al formulario?
        base_datos = self.campana.bd_contacto
        metadata = base_datos.get_metadata()
        nombres = metadata.nombres_de_columnas
        datos = []
        nombres.remove('telefono')
        for nombre in nombres:
            campo = contacto_form.cleaned_data.get(convertir_ascii_string(nombre))
            datos.append(campo)
        contacto.datos = json.dumps(datos)
        contacto.bd_contacto = base_datos
        contacto.save()
        self.contacto = contacto

        self.object_calificacion = calificacion_form.save(commit=False)
        self.object_calificacion.set_es_venta()
        self.object_calificacion.agente = self.agente
        self.object_calificacion.contacto = contacto

        self.object_calificacion.es_calificacion_manual = True
        self.object_calificacion.save()

        # Finalizar relacion de contacto con agente
        # Optimizacion: si ya hay calificacion ya se termino la relacion agente contacto antes.
        if self.campana.type == Campana.TYPE_PREVIEW and self.object is None:
            self.campana.gestionar_finalizacion_relacion_agente_contacto(contacto.id)

        if self.object_calificacion.es_venta:
            return redirect(self.get_success_url_venta())
        else:
            message = 'Operación Exitosa!\
                        Se llevó a cabo con éxito la calificacion del cliente'
            messages.success(self.request, message)

        if self.object_calificacion.es_agenda():
            return redirect(self.get_success_url_agenda())
        # elif self.kwargs['from'] == 'reporte':
        #    return redirect(self.get_success_url_reporte())
        else:
            return redirect(self.get_success_url())

    def form_invalid(self, contacto_form, calificacion_form):
        """
        Re-renders the context data with the data-filled forms and errors.
        """
        return self.render_to_response(self.get_context_data(contacto_form=contacto_form,
                                                             calificacion_form=calificacion_form))

    def get_success_url_venta(self):
        return reverse('formulario_venta',
                       kwargs={"pk_campana": self.campana.id,
                               "pk_contacto": self.contacto.id,
                               "id_agente": self.agente.id})

    def get_success_url_agenda(self):
        return reverse('agenda_contacto_create',
                       kwargs={"pk_campana": self.campana.id,
                               "pk_contacto": self.contacto.id,
                               "id_agente": self.agente.id})

    def get_success_url_reporte(self):
        return reverse('reporte_agente_calificaciones',
                       kwargs={"pk_agente": self.object_calificacion.agente.pk})

    def get_success_url(self):
        return reverse('campana_manual_calificacion_update',
                       kwargs={"pk_campana": self.campana.id,
                               "pk_contacto": self.contacto.id,
                               # "wombat_id": self.wombat_id,
                               "id_agente": self.agente.id})
