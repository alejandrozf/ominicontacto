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

"""Aca se encuentran las vistas para crear el objecto sitio externo lo cual consite
nombre y una url externa para crm externo en el momento de crear una campa se selecciona
el sitio externo el cual va abrirse en una pestaña
"""

from __future__ import unicode_literals
from django.db import transaction
from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.views.generic.edit import (
    CreateView, UpdateView
)
from django.views.generic import (
    ListView
)
from django.views.generic.base import RedirectView
from ominicontacto_app.models import SitioExterno
from ominicontacto_app.forms import SitioExternoForm
from configuracion_telefonia_app.regeneracion_configuracion_telefonia import (
    SincronizadorDeConfiguracionSitioExternoAsterisk, RestablecerConfiguracionTelefonicaError
)


class SitioExternoCreateUpdateMixin(object):
    """
    Mixin para create y update de sitio externo
    """

    def get_success_url(self):
        return reverse('sitio_externo_list')

    def form_valid(self, form):
        # escribe sitio externo en asterisk
        try:
            with transaction.atomic():
                form.save()
                sincronizador = SincronizadorDeConfiguracionSitioExternoAsterisk()
                sincronizador.regenerar_asterisk(form.instance)
        except RestablecerConfiguracionTelefonicaError, e:
            message = ("<strong>¡Cuidado!</strong> "
                       "con el siguiente error: {0} .".format(e))
            messages.add_message(
                self.request,
                messages.WARNING,
                message,
            )
            return self.form_invalid(form)

        return super(SitioExternoCreateUpdateMixin, self).form_valid(form)


class SitioExternoCreateView(SitioExternoCreateUpdateMixin, CreateView):
    """Vista para crear un sitio externo"""
    model = SitioExterno
    template_name = 'sitio_externo/create_update_form.html'
    form_class = SitioExternoForm


class SitioExternoUpdateView(SitioExternoCreateUpdateMixin, UpdateView):
    """Vista para modificar un sitio externo"""
    model = SitioExterno
    template_name = 'sitio_externo/create_update_form.html'
    form_class = SitioExternoForm


class SitioExternoListView(ListView):
    """
    Esta vista es para generar el listado de
    Lista de sitios externos.
    """

    template_name = 'sitio_externo/sitio_externo_list.html'
    context_object_name = 'sitios_externos'
    model = SitioExterno

    def get_queryset(self):
        queryset = SitioExterno.objects.filter(oculto=False)
        return queryset


class OcultarSitioExternoView(RedirectView):
    """
    Esta vista actualiza el sitio externo ocultandola.
    """

    pattern_name = 'sitio_externo_list'

    def get(self, request, *args, **kwargs):
        sitio = SitioExterno.objects.get(pk=self.kwargs['pk_sitio_externo'])
        sitio.ocultar()
        return HttpResponseRedirect(reverse('sitio_externo_list'))


class DesOcultarSitioExternoView(RedirectView):
    """
    Esta vista actualiza el sitio externo haciendolo visible.
    """

    pattern_name = 'sitio_externo_list'

    def get(self, request, *args, **kwargs):
        sitio = SitioExterno.objects.get(pk=self.kwargs['pk_sitio_externo'])
        sitio.desocultar()
        return HttpResponseRedirect(reverse('sitio_externo_list'))


def mostrar_sitio_externos_ocultos_view(request):
    """Esta vista muestro los sitios externos ocultos"""
    sitios = SitioExterno.objects.all()
    data = {
        'sitios_externos': sitios,
    }
    return render(request, 'sitio_externo/sitios_ocultos.html', data)
