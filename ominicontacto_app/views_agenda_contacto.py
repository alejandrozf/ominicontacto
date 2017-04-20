# -*- coding: utf-8 -*-

from __future__ import unicode_literals


from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, FormView
)
from django.views.generic.detail import DetailView
from ominicontacto_app.models import AgendaContacto, Contacto, AgenteProfile
from ominicontacto_app.forms import AgendaContactoForm, AgendaBusquedaForm
from ominicontacto_app.utiles import convert_string_in_boolean,\
    convert_fecha_datetime


class AgendaContactoCreateView(CreateView):

    template_name = 'agenda_contacto/create_agenda_contacto.html'
    model = AgendaContacto
    context_object_name = 'agendacontacto'
    form_class = AgendaContactoForm

    def get_initial(self):
        initial = super(AgendaContactoCreateView, self).get_initial()
        contacto = Contacto.objects.get(pk=self.kwargs['pk_contacto'])
        agente = AgenteProfile.objects.get(pk=self.kwargs['id_agente'])
        initial.update({'contacto': contacto,
                        'agente': agente})
        return initial

    def get_context_data(self, **kwargs):
        context = super(
            AgendaContactoCreateView, self).get_context_data(**kwargs)
        context['contacto'] = Contacto.objects.get(pk=self.kwargs['pk_contacto'])
        return context

    def get_success_url(self):
        return reverse(
            'agenda_contacto_detalle', kwargs={'pk': self.object.pk})


class AgendaContactoDetailView(DetailView):
    template_name = 'agenda_contacto/agenda_detalle.html'
    model = AgendaContacto

    def get_context_data(self, **kwargs):
        context = super(
            AgendaContactoDetailView, self).get_context_data(**kwargs)
        return context


class AgenteContactoListFormView(FormView):
    model = AgendaContacto
    template_name = 'agenda_contacto/agenda_agente.html'
    form_class = AgendaBusquedaForm

    def get(self, request, *args, **kwargs):
        agente = self.request.user.get_agente_profile()
        listado_de_eventos = agente.agendacontacto.eventos_filtro_fecha('', '')
        return self.render_to_response(self.get_context_data(
            listado_de_eventos=listado_de_eventos))

    def form_valid(self, form):
        fecha = form.cleaned_data.get('fecha')
        if fecha:
            fecha_desde, fecha_hasta = fecha.split('-')
            fecha_desde = convert_fecha_datetime(fecha_desde)
            fecha_hasta = convert_fecha_datetime(fecha_hasta)
        else:
            fecha_desde = ''
            fecha_hasta = ''
        agente = self.request.user.get_agente_profile()
        listado_de_eventos = agente.agendacontacto.eventos_filtro_fecha(fecha_desde,
                                                                        fecha_hasta)
        return self.render_to_response(self.get_context_data(
            listado_de_eventos=listado_de_eventos))
