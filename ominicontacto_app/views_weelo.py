# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from ominicontacto_app.models import Contacto, Campana, FormularioDatoVenta
from ominicontacto_app.forms import (
    ContactoForm, FormularioDatoVentaFormSet
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
        contacto = Contacto.objects.get(bd_contacto=campana.bd_contacto,
                             id_cliente=self.kwargs['id_cliente'])
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
