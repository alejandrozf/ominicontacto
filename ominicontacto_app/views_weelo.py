# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from ominicontacto_app.models import (
    Contacto, Campana, FormularioDatoVenta, CalificacionCliente, AgenteProfile
)
from ominicontacto_app.forms import (
    ContactoForm, FormularioDatoVentaFormSet, CalificacionClienteForm
)

import logging as logging_


logger = logging_.getLogger(__name__)


class ContactoFormularioCreateView(CreateView):
    template_name = 'agente/formulario_weelo.html'
    model = Contacto
    form_class = ContactoForm
    #success_url = 'success/'

    def get_object(self, queryset=None):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        return Contacto.objects.get(id_cliente=self.kwargs['id_cliente'],
                                    bd_contacto=campana.bd_contacto)

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        venta_form = FormularioDatoVentaFormSet(initial=[
            {'campana': self.kwargs['pk_campana'],
             'vendedor': request.user.get_agente_profile(), }])
        return self.render_to_response(
            self.get_context_data(form=form, venta_form=venta_form))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        validity.
        """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        venta_form = FormularioDatoVentaFormSet(self.request.POST)

        if form.is_valid() and venta_form.is_valid():
            return self.form_valid(form, venta_form)
        else:
            return self.form_invalid(form, venta_form)

    def form_valid(self, form, venta_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        self.object = form.save()
        venta_form.instance = self.object
        venta_form.save()
        message = 'Operación Exitosa!\
                Se llevó a cabo con éxito la carga de datos'

        messages.add_message(
            self.request,
            messages.SUCCESS,
            message,
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, venta_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        return self.render_to_response(
            self.get_context_data(form=form, venta_form=venta_form))

    def get_success_url(self):
        return reverse('formulario_tarjeta_update',
                       kwargs={"pk_campana": self.kwargs['pk_campana'],
                               "id_cliente": self.kwargs['id_cliente']})


class ContactoFormularioUpdateView(UpdateView):
    template_name = 'agente/formulario_weelo.html'
    model = Contacto
    form_class = ContactoForm
    #success_url = 'success/'

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
            FormularioDatoVenta.objects.get(contacto=contacto)
        except FormularioDatoVenta.DoesNotExist:
            return HttpResponseRedirect(reverse('formulario_tarjeta',
                                                kwargs={"pk_campana": self.kwargs['pk_campana'], "id_cliente": self.kwargs['id_cliente']}))

        return super(ContactoFormularioUpdateView, self).dispatch(*args,
                                                                  **kwargs)

    def get_object(self, queryset=None):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        return Contacto.objects.get(id_cliente=self.kwargs['id_cliente'],
                                    bd_contacto=campana.bd_contacto)

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        venta_form = FormularioDatoVentaFormSet(instance=self.object)
        return self.render_to_response(
            self.get_context_data(form=form, venta_form=venta_form))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        validity.
        """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        venta_form = FormularioDatoVentaFormSet(self.request.POST,
                                                instance=self.object)
        if form.is_valid() and venta_form.is_valid():
            return self.form_valid(form, venta_form)
        else:
            return self.form_invalid(form, venta_form)

    def form_valid(self, form, venta_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        self.object = form.save()
        venta_form.save()
        message = 'Operación Exitosa!\
                Se llevó a cabo con éxito la actualizacio de la carga de datos'

        messages.success(self.request, message)
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, venta_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        return self.render_to_response(
            self.get_context_data(form=form, venta_form=venta_form))

    def get_success_url(self):
        return reverse('formulario_tarjeta_update',
                       kwargs={"pk_campana": self.kwargs['pk_campana'],
                               "id_cliente": self.kwargs['id_cliente']})


class CalificacionClienteCreateView(CreateView):
    """
    Muestra el detalle de contacto
    """
    template_name = 'agente/contacto_detalle.html'
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

    def get_context_data(self, **kwargs):
        context = super(CalificacionClienteCreateView, self).get_context_data(**kwargs)
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        contacto = Contacto.objects.get(id_cliente=self.kwargs['id_cliente'],
                                        bd_contacto=campana.bd_contacto)
        context['contacto'] = contacto
        context['campana_pk'] = self.kwargs['pk_campana']
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        calificacion = form.cleaned_data.get('calificacion')
        if calificacion is None:
            self.object.es_venta = True
            self.object.save()
            return redirect(self.get_success_url())
        else:
            self.object.es_venta = False
            self.object.save()
            message = 'Operación Exitosa!\
                        Se llevó a cabo con éxito la calificacion del cliente'
            messages.success(self.request, message)
            return HttpResponseRedirect(reverse('calificacion_cliente_update',
                                                kwargs={
                                                    "pk_campana": self.kwargs[
                                                        'pk_campana'],
                                                    "id_cliente": self.kwargs[
                                                        'id_cliente']}))

    def get_success_url(self):
        return reverse('formulario_tarjeta_update',
                       kwargs={"pk_campana": self.kwargs['pk_campana'],
                               "id_cliente": self.kwargs['id_cliente']})


class CalificacionClienteUpdateView(UpdateView):
    """
    Muestra el detalle de contacto
    """
    template_name = 'agente/contacto_detalle.html'
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
            return HttpResponseRedirect(reverse('calificacion_cliente',
                kwargs={"pk_campana": self.kwargs['pk_campana'],
                        "id_cliente": self.kwargs['id_cliente'],
                        "id_agente": self.kwargs['id_agente']}))

        return super(CalificacionClienteUpdateView, self).dispatch(*args,
                                                                  **kwargs)

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
        context = super(CalificacionClienteUpdateView, self).get_context_data(**kwargs)
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        contacto = Contacto.objects.get(id_cliente=self.kwargs['id_cliente'],
                                        bd_contacto=campana.bd_contacto)
        context['contacto'] = contacto
        context['campana_pk'] = self.kwargs['pk_campana']
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        calificacion = form.cleaned_data.get('calificacion')
        if calificacion is None:
            self.object.es_venta = True
            self.object.save()
            return redirect(self.get_success_url())
        else:
            self.object.es_venta = False
            self.object.save()
            message = 'Operación Exitosa!\
            Se llevó a cabo con éxito la calificacion del cliente'
            messages.success(self.request, message)
            return HttpResponseRedirect(reverse('calificacion_cliente_update',
                           kwargs={"pk_campana": self.kwargs['pk_campana'],
                                   "id_cliente": self.kwargs['id_cliente'],
                                   "id_agente": self.kwargs['id_agente']}))

    def get_success_url(self):
        return reverse('formulario_tarjeta_update',
                       kwargs={"pk_campana": self.kwargs['pk_campana'],
                               "id_cliente": self.kwargs['id_cliente']})
