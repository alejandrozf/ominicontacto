# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.views.generic import ListView, CreateView, UpdateView
from ominicontacto_app.models import Contacto
from django.core.urlresolvers import reverse


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

    def get_success_url(self):
        return reverse('view_blanco')


class ContactoListView(ListView):
    model = Contacto
    template_name = 'agente/contacto_list.html'
