# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3, as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView,
    DetailView)

from ominicontacto_app.forms import GrupoForm
from ominicontacto_app.models import Grupo
from utiles_globales import obtener_paginas


class GrupoCreateView(CreateView):
    """Vista para crear un grupo
    DT: eliminar fields de la vista crear un form para ello
    """
    model = Grupo
    template_name = 'usuarios_grupos/grupo_create_update.html'
    form_class = GrupoForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if not self.object.auto_unpause:
            self.object.auto_unpause = 0
        self.object.save()
        return super(GrupoCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('grupo_list')


class GrupoUpdateView(UpdateView):
    """Vista para modificar un grupo
        DT: eliminar fields de la vista crear un form para ello
        """
    model = Grupo
    template_name = 'usuarios_grupos/grupo_create_update.html'
    form_class = GrupoForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        auto_unpause = form.cleaned_data.get('auto_unpause')
        if not auto_unpause:
            self.object.auto_unpause = 0
        self.object.save()
        return super(GrupoUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('grupo_list')


class GrupoListView(ListView):
    """Vista para listar los grupos"""
    model = Grupo
    template_name = 'usuarios_grupos/grupo_list.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(GrupoListView, self).get_context_data(**kwargs)
        obtener_paginas(context, 7)
        return context

    def get_queryset(self):
        queryset = Grupo.objects.all()
        if 'search' in self.request.GET:
            search = self.request.GET.get('search')
            return queryset.filter(Q(nombre__icontains=search))
        else:
            return queryset


class GrupoDeleteView(DeleteView):
    """
    Esta vista se encarga de la eliminación del
    objeto grupo
    """
    model = Grupo
    template_name = 'usuarios_grupos/delete_grupo.html'

    def dispatch(self, request, *args, **kwargs):
        grupo = Grupo.objects.get(pk=self.kwargs['pk'])
        agentes = grupo.agentes.all()
        if agentes:
            message = ("No está permitido eliminar un grupo que tiene agentes")
            messages.warning(self.request, message)
            return HttpResponseRedirect(
                reverse('grupo_list'))
        return super(GrupoDeleteView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('grupo_list')


class GrupoDetalleView(DetailView):
    """
    Esta vista se encarga de mostrar la info del grupo
    """
    model = Grupo
    template_name = 'usuarios_grupos/grupo_detalle.html'
