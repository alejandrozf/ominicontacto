# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import requests

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect
from django.conf import settings
from django.views.generic.edit import (
    CreateView, UpdateView, DeleteView, FormView
)
from django.views.generic.detail import DetailView
from ominicontacto_app.models import (
    Contacto, Campana, CalificacionCliente, AgenteProfile, MetadataCliente
)
from ominicontacto_app.forms import (
    FormularioCRMForm, CalificacionClienteForm
)

import logging as logging_


logger = logging_.getLogger(__name__)


class CalificacionClienteCreateView(CreateView):
    """
    Muestra el detalle de contacto
    """
    template_name = 'formulario/calificacion_create_update.html'
    context_object_name = 'calificacion_cliente'
    model = CalificacionCliente
    form_class = CalificacionClienteForm

    def get_initial(self):
        initial = super(CalificacionClienteCreateView, self).get_initial()
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        agente = AgenteProfile.objects.get(pk=self.kwargs['id_agente'])
        contacto = Contacto.objects.get(id_cliente=self.kwargs['id_cliente'],
                                        bd_contacto=campana.bd_contacto)
        initial.update({'campana': campana.id,
                        'contacto': contacto.id,
                        'agente': agente.id})
        return initial

    def get_form(self, form_class):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        calificaciones = campana.calificacion_campana.calificacion.all()
        return form_class(calificacion_choice=calificaciones,
                          **self.get_form_kwargs())

    def get(self, request, *args, **kwargs):
        url_wombat_agente = '/'.join([settings.OML_WOMBAT_URL,
                                      'api/calls/?op=attr&wombatid={0}&attr=id_agente&val={1}'])
        r = requests.post(
            url_wombat_agente.format(self.kwargs['wombat_id'],
                                     self.kwargs['id_agente']))
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super(CalificacionClienteCreateView, self).get_context_data(**kwargs)
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        contacto = Contacto.objects.get(id_cliente=self.kwargs['id_cliente'],
                                        bd_contacto=campana.bd_contacto)

        bd_contacto = campana.bd_contacto
        nombres = bd_contacto.get_metadata().nombres_de_columnas[2:]
        datos = json.loads(contacto.datos)
        mas_datos = []
        for nombre, dato in zip(nombres, datos):
            mas_datos.append((nombre, dato))

        context['mas_datos'] = mas_datos
        context['contacto'] = contacto
        context['campana_pk'] = self.kwargs['pk_campana']
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        calificacion = form.cleaned_data.get('calificacion')
        url_wombat = '/'.join([settings.OML_WOMBAT_URL,
                               'api/calls/?op=extstatus&wombatid={0}&status={1}'
                               ])
       # url_wombat_agente = '/'.join([settings.OML_WOMBAT_URL,
        #    'api/calls/?op=attr&wombatid={0}&attr=id_agente&val={1}'])
        #r = requests.post(
         #   url_wombat_agente.format(self.kwargs['wombat_id'],
          #                           self.kwargs['id_agente']))
        if calificacion is None:
            self.object.es_venta = True
            self.object.wombat_id = int(self.kwargs['wombat_id'])
            self.object.save()
            r = requests.post(
                url_wombat.format(self.kwargs['wombat_id'], "venta"))
            return redirect(self.get_success_url())
        else:
            self.object.es_venta = False
            self.object.wombat_id = int(self.kwargs['wombat_id'])
            self.object.save()
            r = requests.post(
                url_wombat.format(self.kwargs['wombat_id'],
                                  self.object.calificacion.nombre))
            message = 'Operación Exitosa!\
                        Se llevó a cabo con éxito la calificacion del cliente'
            messages.success(self.request, message)
            return HttpResponseRedirect(reverse('calificacion_formulario_update',
                                                kwargs={
                                                    "pk_campana": self.kwargs[
                                                        'pk_campana'],
                                                    "id_cliente": self.kwargs[
                                                        'id_cliente'],
                                                    "wombat_id": self.kwargs[
                                                        'wombat_id'],
                                                    "id_agente": self.kwargs[
                                                        'id_agente']}))

    def get_success_url(self):
        return reverse('formulario_venta',
                       kwargs={"pk_campana": self.kwargs['pk_campana'],
                               "id_cliente": self.kwargs['id_cliente'],
                               "id_agente": self.kwargs['id_agente']})


class CalificacionClienteUpdateView(UpdateView):
    """
    Muestra el detalle de contacto
    """
    template_name = 'formulario/calificacion_create_update.html'
    context_object_name = 'calificacion_cliente'
    model = CalificacionCliente
    form_class = CalificacionClienteForm

    def dispatch(self, *args, **kwargs):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])

        try:
            contacto = Contacto.objects.get(bd_contacto=campana.bd_contacto,
                                            id_cliente=self.kwargs[
                                                'id_cliente'])
        except Contacto.DoesNotExist:
            return HttpResponseRedirect(reverse('formulario_buscar',
                                                kwargs={"pk_campana":
                                                self.kwargs['pk_campana']}))
        try:
            CalificacionCliente.objects.get(contacto=contacto)
        except CalificacionCliente.DoesNotExist:
            return HttpResponseRedirect(reverse('calificacion_formulario_create',
                kwargs={"pk_campana": self.kwargs['pk_campana'],
                        "id_cliente": self.kwargs['id_cliente'],
                        "id_agente": self.kwargs['id_agente'],
                        "wombat_id": self.kwargs['wombat_id'],
                        }))

        return super(CalificacionClienteUpdateView, self).dispatch(*args,
                                                                  **kwargs)

    def get(self, request, *args, **kwargs):
        url_wombat_agente = '/'.join([settings.OML_WOMBAT_URL,
                                      'api/calls/?op=attr&wombatid={0}&attr=id_agente&val={1}'])
        r = requests.post(
            url_wombat_agente.format(self.kwargs['wombat_id'],
                                     self.kwargs['id_agente']))
        context = self.get_context_data(**kwargs)
        return self.render_to_response(self.get_context_data())

    def get_form(self, form_class):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        calificaciones = campana.calificacion_campana.calificacion.all()
        return form_class(calificacion_choice=calificaciones,
                          **self.get_form_kwargs())

    def get_object(self, queryset=None):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        contacto = Contacto.objects.get(id_cliente=self.kwargs['id_cliente'],
                                    bd_contacto=campana.bd_contacto)
        return CalificacionCliente.objects.get(contacto=contacto)

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super(CalificacionClienteUpdateView, self).get_context_data(**kwargs)
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        contacto = Contacto.objects.get(id_cliente=self.kwargs['id_cliente'],
                                        bd_contacto=campana.bd_contacto)

        bd_contacto = campana.bd_contacto
        nombres = bd_contacto.get_metadata().nombres_de_columnas[2:]
        datos = json.loads(contacto.datos)
        mas_datos = []
        for nombre, dato in zip(nombres, datos):
            mas_datos.append((nombre, dato))

        context['mas_datos'] = mas_datos
        context['contacto'] = contacto
        context['campana_pk'] = self.kwargs['pk_campana']
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        calificacion = form.cleaned_data.get('calificacion')
        url_wombat = '/'.join([settings.OML_WOMBAT_URL,
                               'api/calls/?op=extstatus&wombatid={0}&status={1}'
                               ])
        #url_wombat_agente = '/'.join([settings.OML_WOMBAT_URL,
        #                              'api/calls/?op=attr&wombatid={0}&attr=id_agente&val={1}'])
        #r = requests.post(
         #   url_wombat_agente.format(self.kwargs['wombat_id'],
          #                           self.kwargs['id_agente']))
        if calificacion is None:
            self.object.es_venta = True
            self.object.save()
            r = requests.post(
                url_wombat.format(self.kwargs['wombat_id'], "venta"))
            return redirect(self.get_success_url())

        else:
            self.object.es_venta = False
            self.object.save()
            r = requests.post(
                url_wombat.format(self.kwargs['wombat_id'],
                                  self.object.calificacion.nombre))
            message = 'Operación Exitosa!\
            Se llevó a cabo con éxito la calificacion del cliente'
            messages.success(self.request, message)
            return HttpResponseRedirect(
                reverse('calificacion_formulario_update',
                        kwargs={
                            "pk_campana": self.kwargs[
                                'pk_campana'],
                            "id_cliente": self.kwargs[
                                'id_cliente'],
                            "wombat_id": self.kwargs[
                                'wombat_id'],
                            "id_agente": self.kwargs[
                                'id_agente']}))

    def get_success_url(self):
        return reverse('formulario_venta',
                       kwargs={"pk_campana": self.kwargs['pk_campana'],
                               "id_cliente": self.kwargs['id_cliente'],
                               "id_agente": self.kwargs['id_agente']})


class FormularioCreateFormView(FormView):
    form_class = FormularioCRMForm
    template_name = 'formulario/formulario_create.html'

    def get_form(self, form_class):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        #formulario = Formulario.objects.get(pk=self.kwargs['pk_formulario'])
        campos = campana.formulario.campos.all()
        return form_class(campos=campos, **self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        context = super(
            FormularioCreateFormView, self).get_context_data(**kwargs)

        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        context['pk_formulario'] = campana.formulario.pk
        contacto = Contacto.objects.get(id_cliente=self.kwargs['id_cliente'],
                                        bd_contacto=campana.bd_contacto)
        bd_contacto = campana.bd_contacto
        nombres = bd_contacto.get_metadata().nombres_de_columnas[2:]
        datos = json.loads(contacto.datos)
        mas_datos = []
        for nombre, dato in zip(nombres, datos):
            mas_datos.append((nombre, dato))
        context['contacto'] = contacto
        context['mas_datos'] = mas_datos

        return context

    def form_valid(self, form):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        agente = AgenteProfile.objects.get(pk=self.kwargs['id_agente'])
        contacto = Contacto.objects.get(id_cliente=self.kwargs['id_cliente'],
                                        bd_contacto=campana.bd_contacto)
        metadata = json.dumps(form.cleaned_data)
        obj = MetadataCliente.objects.create(campana=campana, agente=agente,
                                             contacto=contacto,
                                             metadata=metadata)
        message = 'Operación Exitosa!' \
                  'Se llevó a cabo con éxito el llenado del formulario del' \
                  ' cliente'
        messages.success(self.request, message)
        return HttpResponseRedirect(reverse('formulario_detalle',
                                            kwargs={"pk": obj.pk}))

    def form_invalid(self, form):

        message = '<strong>Operación Errónea!</strong> \
                  Error en el formulario revise bien los datos llenados.'

        messages.add_message(
            self.request,
            messages.WARNING,
            message,
        )
        return self.render_to_response(self.get_context_data())

    def get_success_url(self):
        # reverse('formulario_detalle',
        #         kwargs={"pk": self.kwargs['pk_campana'],
        #                 "id_cliente": self.kwargs['id_cliente'],
        #                 "id_agente": self.kwargs['id_agente']
        #                 }
        #         )
        reverse('view_blanco')


class FormularioDetailView(DetailView):
    template_name = 'formulario/formulario_detalle.html'
    model = MetadataCliente

    def get_context_data(self, **kwargs):
        context = super(
            FormularioDetailView, self).get_context_data(**kwargs)
        metadata = MetadataCliente.objects.get(pk=self.kwargs['pk'])
        campana = Campana.objects.get(pk=metadata.campana.pk)
        contacto = Contacto.objects.get(id_cliente=metadata.contacto.id_cliente,
                                        bd_contacto=campana.bd_contacto)
        bd_contacto = campana.bd_contacto
        nombres = bd_contacto.get_metadata().nombres_de_columnas[2:]
        datos = json.loads(contacto.datos)
        mas_datos = []
        for nombre, dato in zip(nombres, datos):
            mas_datos.append((nombre, dato))

        context['contacto'] = contacto
        context['mas_datos'] = mas_datos
        context['metadata'] = json.loads(metadata.metadata)

        return context


class FormularioUpdateFormView(FormView):
    form_class = FormularioCRMForm
    template_name = 'formulario/formulario_create.html'

    def get_initial(self):
        initial = super(FormularioUpdateFormView, self).get_initial()
        metadata = MetadataCliente.objects.get(pk=self.kwargs['pk_metadata'])
        #import ipdb; ipdb.set_trace();
        for clave, valor in json.loads(metadata.metadata).items():
            initial.update({clave: valor})
        return initial

    def get_form(self, form_class):
        metadata = MetadataCliente.objects.get(pk=self.kwargs['pk_metadata'])
        #formulario = Formulario.objects.get(pk=self.kwargs['pk_formulario'])
        campos = metadata.campana.formulario.campos.all()
        return form_class(campos=campos, **self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        context = super(
            FormularioUpdateFormView, self).get_context_data(**kwargs)
        metadata = MetadataCliente.objects.get(pk=self.kwargs['pk_metadata'])

        context['pk_formulario'] = metadata.campana.formulario.pk

        bd_contacto = metadata.campana.bd_contacto
        nombres = bd_contacto.get_metadata().nombres_de_columnas[2:]
        datos = json.loads(metadata.contacto.datos)
        mas_datos = []
        for nombre, dato in zip(nombres, datos):
            mas_datos.append((nombre, dato))
        context['contacto'] = metadata.contacto
        context['mas_datos'] = mas_datos

        return context

    def form_valid(self, form):
        metadata = MetadataCliente.objects.get(pk=self.kwargs['pk_metadata'])
        metadata_datos = json.dumps(form.cleaned_data)
        metadata.metadata = metadata_datos
        metadata.save()
        message = 'Operación Exitosa!' \
                  'Se llevó a cabo con éxito el llenado del formulario del' \
                  ' cliente'
        messages.success(self.request, message)
        return HttpResponseRedirect(reverse('formulario_detalle',
                                            kwargs={"pk": metadata.pk}))

    def get_success_url(self):
        # reverse('formulario_detalle',
        #         kwargs={"pk": self.kwargs['pk_campana'],
        #                 "id_cliente": self.kwargs['id_cliente'],
        #                 "id_agente": self.kwargs['id_agente']
        #                 }
        #         )
        reverse('view_blanco')


class CalificacionUpdateView(UpdateView):

    template_name = 'formulario/calificacion_create_update.html'
    context_object_name = 'calificacion_cliente'
    model = CalificacionCliente
    form_class = CalificacionClienteForm

    def get_form(self, form_class):
        campana = self.get_object().campana
        calificaciones = campana.calificacion_campana.calificacion.all()
        return form_class(calificacion_choice=calificaciones,
                          **self.get_form_kwargs())

    def get_object(self, queryset=None):
        return CalificacionCliente.objects.get(
            pk=self.kwargs['pk_calificacion'])

    def get_context_data(self, **kwargs):
        context = super(CalificacionUpdateView,
                        self).get_context_data(**kwargs)
        campana = self.get_object().campana
        contacto = self.get_object().contacto

        bd_contacto = campana.bd_contacto
        nombres = bd_contacto.get_metadata().nombres_de_columnas[2:]
        datos = json.loads(contacto.datos)
        mas_datos = []
        for nombre, dato in zip(nombres, datos):
            mas_datos.append((nombre, dato))

        context['mas_datos'] = mas_datos
        context['contacto'] = contacto
        context['campana_pk'] = campana.pk
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        calificacion = form.cleaned_data.get('calificacion')
        url_wombat = '/'.join([settings.OML_WOMBAT_URL,
                               'api/calls/?op=extstatus&wombatid={0}&status={1}'
                               ])

        if calificacion is None:
            self.object.es_venta = True
            self.object.save()
            r = requests.post(
                url_wombat.format(self.get_object().wombat_id, "venta"))
            return redirect(self.get_success_url())

        else:
            self.object.es_venta = False
            self.object.save()
            r = requests.post(
                url_wombat.format(self.get_object().wombat_id,
                                  self.object.calificacion.nombre))
            message = 'Operación Exitosa!\
            Se llevó a cabo con éxito la calificacion del cliente'
            messages.success(self.request, message)
            return HttpResponseRedirect(reverse('reporte_agente_calificaciones',
                           kwargs={
                                   "pk_agente": self.get_object().agente.pk}))

    def get_success_url(self):
        return reverse('formulario_venta',
                       kwargs={
                           "pk_campana": self.get_object().campana.pk,
                            "id_cliente": self.get_object().contacto.id_cliente,
                            "id_agente": self.get_object().agente.pk})
