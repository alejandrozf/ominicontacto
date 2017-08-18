# -*- coding: utf-8 -*-

"""
Aca se encuentra las vista relacionada con la creacion de una agenda en el caso que el 
agente de desee agendar un llamado. Al modulo de agenda le esta faltando algun demonio
o algo por el estilo para que lance una llamada agenda,etc 
"""

from __future__ import unicode_literals

import requests

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, FormView
)
from django.views.generic.detail import DetailView
from ominicontacto_app.models import (
    AgendaContacto, Contacto, AgenteProfile, Campana, AgendaManual
)
from ominicontacto_app.forms import (
    AgendaContactoForm, AgendaBusquedaForm, AgendaManualForm
)
from ominicontacto_app.utiles import convert_string_in_boolean,\
    convert_fecha_datetime


class AgendaContactoCreateView(CreateView):
    """Vista para crear una nueva agenda"""
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

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if self.object.tipo_agenda == AgendaContacto.TYPE_GLOBAL:
            campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
            url_wombat = '/'.join(
                [settings.OML_WOMBAT_URL,
                 'api/calls/?op=addcall&campaign={0}&number={1}&schedule={2}&attrs=ID_CAMPANA:{3},ID_CLIENTE:{4},CAMPANA:{0}'
                                   ])
            fecha_hora = '.'.join([str(self.object.fecha), str(self.object.hora)])
            r = requests.post(
                url_wombat.format(
                    campana.nombre, self.object.contacto.telefono, fecha_hora,
                    campana.pk, self.object.contacto.pk))
        self.object.save()
        return super(AgendaContactoCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            'agenda_contacto_detalle', kwargs={'pk': self.object.pk})


class AgendaContactoDetailView(DetailView):
    """Detalle de una agenda de contacto"""
    template_name = 'agenda_contacto/agenda_detalle.html'
    model = AgendaContacto

    def get_context_data(self, **kwargs):
        context = super(
            AgendaContactoDetailView, self).get_context_data(**kwargs)
        return context


class AgenteContactoListFormView(FormView):
    """Vista listado evento de agenda por agente"""
    model = AgendaContacto
    template_name = 'agenda_contacto/agenda_agente.html'
    form_class = AgendaBusquedaForm

    def get(self, request, *args, **kwargs):
        agente = self.request.user.get_agente_profile()
        listado_de_eventos = agente.agendacontacto.eventos_filtro_fecha('', '')
        return self.render_to_response(self.get_context_data(
            listado_de_eventos=listado_de_eventos, agente=agente))

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
            listado_de_eventos=listado_de_eventos, agente=agente))


class AgendaManualCreateView(CreateView):
    """Vista para crear una nueva agenda para una llamada manual"""
    template_name = 'agenda_contacto/create_agenda_manual.html'
    model = AgendaManual
    context_object_name = 'agendamanual'
    form_class = AgendaManualForm

    def get_initial(self):
        initial = super(AgendaManualCreateView, self).get_initial()
        telefono = self.kwargs['telefono']
        agente = AgenteProfile.objects.get(pk=self.kwargs['id_agente'])
        initial.update({'telefono': telefono,
                        'agente': agente})
        return initial

    def get_success_url(self):
        return reverse(
            'agenda_manual_detalle', kwargs={'pk': self.object.pk})


class AgendaManualDetailView(DetailView):
    """Detalle de una agenda de llamada manual"""
    template_name = 'agenda_contacto/agenda_detalle_manual.html'
    model = AgendaManual

    def get_context_data(self, **kwargs):
        context = super(
            AgendaManualDetailView, self).get_context_data(**kwargs)
        return context
