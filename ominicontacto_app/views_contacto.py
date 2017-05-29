# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

from django.http import HttpResponseRedirect
from django.views.generic import DeleteView
from django.views.generic import ListView, CreateView, UpdateView, FormView
from ominicontacto_app.models import Contacto, BaseDatosContacto
from django.core import paginator as django_paginator
from django.core.urlresolvers import reverse
from ominicontacto_app.forms import (
    BusquedaContactoForm, ContactoForm, FormularioNuevoContacto
)


class ContactoCreateView(CreateView):
    model = Contacto
    template_name = 'agente/contacto_create_update_form.html'
    form_class = ContactoForm

    def get_success_url(self):
        return reverse('view_blanco')


class ContactoUpdateView(UpdateView):
    model = Contacto
    template_name = 'agente/contacto_create_update_form.html'
    form_class = ContactoForm

    def get_object(self, queryset=None):
        return Contacto.objects.get(pk=self.kwargs['pk_contacto'])

    def get_success_url(self):
        return reverse('view_blanco')


class ContactoListView(ListView):
    model = Contacto
    template_name = 'agente/contacto_list.html'

    def get_context_data(self, **kwargs):
        context = super(ContactoListView, self).get_context_data(
            **kwargs)
        qs = self.get_queryset()
         # ----- <Paginate> -----
        page = self.kwargs['pagina']
        result_paginator = django_paginator.Paginator(qs, 20)
        try:
            qs = result_paginator.page(page)
        except django_paginator.PageNotAnInteger:  # If page is not an integer, deliver first page.
            qs = result_paginator.page(1)
        except django_paginator.EmptyPage:  # If page is out of range (e.g. 9999), deliver last page of results.
            qs = result_paginator.page(result_paginator.num_pages)
        # ----- </Paginate> -----

        context['contactos'] = qs
        context['url_paginator'] = 'contacto_list'

        return context


class BusquedaContactoFormView(FormView):
    form_class = BusquedaContactoForm
    template_name = 'agente/busqueda_contacto.html'

    def get(self, request, *args, **kwargs):
        listado_de_contacto = Contacto.objects.all()
        return self.render_to_response(self.get_context_data(
            listado_de_contacto=listado_de_contacto))

    def form_valid(self, form):
        filtro = form.cleaned_data.get('buscar')
        try:
            listado_de_contacto = Contacto.objects.contactos_by_filtro(filtro)
        except Contacto.DoesNotExist:
            listado_de_contacto = Contacto.objects.all()
            return self.render_to_response(self.get_context_data(
                form=form, listado_de_contacto=listado_de_contacto))

        if listado_de_contacto:
            return self.render_to_response(self.get_context_data(
                form=form, listado_de_contacto=listado_de_contacto))
        else:
            listado_de_contacto = Contacto.objects.all()
            return self.render_to_response(self.get_context_data(
                form=form, listado_de_contacto=listado_de_contacto))


class ContactoBDContactoCreateView(CreateView):
    model = Contacto
    template_name = 'base_create_update_form.html'
    form_class = FormularioNuevoContacto

    def get_initial(self):
        initial = super(ContactoBDContactoCreateView, self).get_initial()
        initial.update({'bd_contacto': self.kwargs['bd_contacto']})

    def get_form(self):
        self.form_class = self.get_form_class()
        base_datos = BaseDatosContacto.objects.get(pk=self.kwargs['bd_contacto'])
        metadata = base_datos.get_metadata()
        campos = metadata.nombres_de_columnas
        return self.form_class(campos=campos, **self.get_form_kwargs())

    def form_valid(self, form):
        self.object = form.save(commit=False)
        base_datos = BaseDatosContacto.objects.get(pk=self.kwargs['bd_contacto'])
        base_datos.cantidad_contactos += 1
        base_datos.save()
        self.object.bd_contacto = base_datos

        metadata = base_datos.get_metadata()
        nombres = metadata.nombres_de_columnas
        datos = []
        nombres.remove('telefono')
        for nombre in nombres:
            campo = form.cleaned_data.get(nombre)
            datos.append(campo)
        self.object.datos = json.dumps(datos)
        self.object.save()
        return super(ContactoBDContactoCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('lista_base_datos_contacto')


class ContactoBDContactoListView(ListView):
    model = Contacto
    template_name = 'base_datos_contacto/contacto_list_bd_contacto.html'

    def get_context_data(self, **kwargs):
        context = super(ContactoBDContactoListView, self).get_context_data(
            **kwargs)
        context['basedatoscontacto'] = BaseDatosContacto.objects.get(
            pk=self.kwargs['bd_contacto'])
        return context

    def get_queryset(self):
        return Contacto.objects.contactos_by_bd_contacto(
            self.kwargs['bd_contacto'])


class ContactoBDContactoUpdateView(UpdateView):
    model = Contacto
    template_name = 'base_create_update_form.html'
    form_class = FormularioNuevoContacto

    def get_initial(self):
        initial = super(ContactoBDContactoUpdateView, self).get_initial()
        contacto = Contacto.objects.get(pk=self.kwargs['pk_contacto'])
        base_datos = contacto.bd_contacto
        nombres = base_datos.get_metadata().nombres_de_columnas[1:]
        datos = json.loads(contacto.datos)
        for nombre, dato in zip(nombres, datos):
            initial.update({nombre: dato})
        return initial

    def get_form(self):
        self.form_class = self.get_form_class()
        contacto = Contacto.objects.get(pk=self.kwargs['pk_contacto'])
        base_datos = contacto.bd_contacto
        metadata = base_datos.get_metadata()
        campos = metadata.nombres_de_columnas
        return self.form_class(campos=campos, **self.get_form_kwargs())

    def get_object(self, queryset=None):
        return Contacto.objects.get(pk=self.kwargs['pk_contacto'])

    def form_valid(self, form):
        self.object = form.save(commit=False)
        contacto = self.get_object()
        base_datos = contacto.bd_contacto
        metadata = base_datos.get_metadata()
        campos = metadata.nombres_de_columnas
        nombres = metadata.nombres_de_columnas
        datos = []
        nombres.remove('telefono')
        for nombre in nombres:
            campo = form.cleaned_data.get(nombre)
            datos.append(campo)
        self.object.datos = json.dumps(datos)
        self.object.save()
        return super(ContactoBDContactoUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('contacto_list_bd_contacto',
                       kwargs={'bd_contacto': self.object.bd_contacto.pk})


class ContactoBDContactoDeleteView(DeleteView):
    """
    Esta vista se encarga de la eliminación de un contacto
    """
    model = Contacto
    template_name = 'base_datos_contacto/delete_contacto.html'

    def get_object(self, queryset=None):
        return Contacto.objects.get(pk=self.kwargs['pk_contacto'])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        base_datos_contactos = self.object.bd_contacto
        base_datos_contactos.cantidad_contactos -= 1
        base_datos_contactos.save()
        self.object.delete()

        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        return reverse('contacto_list_bd_contacto',
                       kwargs={'bd_contacto': self.object.bd_contacto.pk})
