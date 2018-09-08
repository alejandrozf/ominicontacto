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

"""
Vista para administrar el modelo Campana de tipo dialer
Observacion se copiaron varias vistas del modulo views_campana
"""

from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, JsonResponse
from ominicontacto_app.models import Campana
from django.views.generic import ListView, DeleteView
from django.views.generic.base import RedirectView

from ominicontacto_app.views_campana import CampanaSupervisorUpdateView, CampanasDeleteMixin

import logging as logging_

logger = logging_.getLogger(__name__)


class CampanaManualListView(ListView):
    """
    Esta vista lista los objetos Campana de type dialer
    Vista copiada
    """

    template_name = 'campana_manual/campana_list.html'
    context_object_name = 'campanas'
    model = Campana

    def _get_campanas(self):
        return Campana.objects.obtener_campanas_manuales()

    def get_context_data(self, **kwargs):
        context = super(CampanaManualListView, self).get_context_data(**kwargs)
        campanas = self._get_campanas()
        # Filtra las campanas de acuerdo al usuario logeado si tiene permiso sobre
        # las mismas
        if self.request.user.is_authenticated() and self.request.user and \
                not self.request.user.get_is_administrador():
            user = self.request.user
            campanas = Campana.objects.obtener_campanas_vista_by_user(campanas, user)
            context['campanas'] = campanas

        context['activas'] = campanas.filter(estado=Campana.ESTADO_ACTIVA)
        context['borradas'] = campanas.filter(estado=Campana.ESTADO_BORRADA,
                                              oculto=False)
        context['campanas'] = campanas
        return context


class CampanaManualDeleteView(CampanasDeleteMixin, DeleteView):
    """
    Esta vista se encarga de la eliminación de una campana
    """
    model = Campana
    template_name = 'campana_manual/delete_campana.html'

    def delete(self, request, *args, **kwargs):
        success_url = self.get_success_url()
        super(CampanaManualDeleteView, self).delete(request, *args, **kwargs)
        return HttpResponseRedirect(success_url)

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get_success_url(self):
        return reverse('campana_manual_list')


class OcultarCampanaManualView(RedirectView):
    """
    Esta vista actualiza la campañana ocultandola.
    """

    pattern_name = 'campana_manual_list'

    def get(self, request, *args, **kwargs):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        campana.ocultar()
        return HttpResponseRedirect(reverse('campana_manual_list'))


class DesOcultarCampanaManualView(RedirectView):
    """
    Esta vista actualiza la campañana haciendola visible.
    """

    pattern_name = 'campana_manual_list'

    def get(self, request, *args, **kwargs):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        campana.desocultar()
        return HttpResponseRedirect(reverse('campana_manual_list'))


class CampanaManualSupervisorUpdateView(CampanaSupervisorUpdateView):
    """
    Esta vista agrega supervisores a una campana manual
    logica copiado para campana_preview
    """

    def get_success_url(self):
        return reverse('campana_manual_list')


class CampanaManualBorradasListView(CampanaManualListView):
    """
    Vista que lista las campañas manual pero de incluyendo las borradas ocultas
    """

    template_name = 'campana_manual/campanas_borradas.html'

    def get_context_data(self, **kwargs):
        context = super(CampanaManualBorradasListView, self).get_context_data(**kwargs)
        context['borradas'] = context['campanas'].filter(estado=Campana.ESTADO_BORRADA)
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return super(CampanaManualBorradasListView, self).get(request, *args, **kwargs)
        else:
            return JsonResponse({'result': 'desconectado'})
