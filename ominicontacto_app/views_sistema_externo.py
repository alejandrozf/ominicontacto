# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

from django.views.generic import ListView, CreateView, UpdateView
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render

from ominicontacto_app.forms import AgenteEnSistemaExternoFormset
from ominicontacto_app.models import SistemaExterno


class SistemaExternoMixin(object):

    def form_valid(self, form):
        sistema_externo = form.save(commit=False)
        agente_en_sistema_formset = AgenteEnSistemaExternoFormset(
            self.request.POST, instance=sistema_externo, prefix='agente_en_sistema')
        if agente_en_sistema_formset.is_valid():
            form.save()
            agente_en_sistema_formset.save()
            return super(SistemaExternoMixin, self).form_valid(form)
        return render(self.request, 'sistema_externo/sistema_externo.html',
                      {'form': form,
                       'agente_en_sistema_externo_formset': agente_en_sistema_formset})


class SistemaExternoCreateView(SistemaExternoMixin, CreateView):
    """Vista para crear un SistemaExterno"""
    model = SistemaExterno
    template_name = 'sistema_externo/sistema_externo.html'
    fields = ('nombre',)

    def get_context_data(self, **kwargs):
        context = super(SistemaExternoCreateView, self).get_context_data()
        context['agente_en_sistema_externo_formset'] = AgenteEnSistemaExternoFormset(
            prefix='agente_en_sistema')
        return context

    def get_success_url(self):
        return reverse('sistema_externo_list')


class SistemaExternoUpdateView(SistemaExternoMixin, UpdateView):
    """Vista para modificar un SistemaExterno"""
    model = SistemaExterno
    template_name = 'sistema_externo/sistema_externo.html'
    fields = ('nombre',)

    def _inicializar_agentes_en_sistema(self, sistema_externo):
        initial_data = sistema_externo.agentes.values()
        agente_en_sistema_externo_formset = AgenteEnSistemaExternoFormset(
            initial=initial_data, instance=sistema_externo, prefix='agente_en_sistema')
        return agente_en_sistema_externo_formset

    def get_context_data(self, **kwargs):
        pk_sistema_externo = self.kwargs.get('pk')
        sistema_externo = get_object_or_404(SistemaExterno, pk=pk_sistema_externo)
        agente_en_sistema_externo_formset = self._inicializar_agentes_en_sistema(sistema_externo)
        context = super(SistemaExternoUpdateView, self).get_context_data()
        context['agente_en_sistema_externo_formset'] = agente_en_sistema_externo_formset
        return context

    def get_success_url(self):
        return reverse('sistema_externo_list')


class SistemaExternoListView(ListView):
    """Vista para listar los modulos"""
    model = SistemaExterno
    template_name = 'sistema_externo/sistema_externo_list.html'
