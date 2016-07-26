# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.views.generic import ListView, CreateView, UpdateView, FormView
from ominicontacto_app.models import Contacto
from django.core import paginator as django_paginator
from django.core.urlresolvers import reverse
from ominicontacto_app.forms import BusquedaContactoForm


class ContactoCreateView(CreateView):
    model = Contacto
    template_name = 'agente/contacto_create_update_form.html'
    fields = ('id_cliente', 'nombre', 'apellido', 'email', 'telefono', 'datos')

    def get_success_url(self):
        return reverse('view_blanco')


class ContactoUpdateView(UpdateView):
    model = Contacto
    template_name = 'agente/contacto_create_update_form.html'
    fields = ('id_cliente', 'nombre', 'apellido', 'email', 'telefono', 'datos')

    def get_object(self, queryset=None):
        return Contacto.objects.get(id_cliente=self.kwargs['id_cliente'])

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


class ContactoTelefonoListView(ListView):
    model = Contacto
    template_name = 'agente/contacto_list_telefono.html'

    def get_queryset(self):
        return Contacto.objects.contactos_by_telefono(self.kwargs['telefono'])


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
