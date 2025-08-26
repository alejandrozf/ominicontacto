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

"""Vista para reportes de campana dialer"""

from __future__ import unicode_literals

from django.utils.translation import gettext as _

from django.shortcuts import render
from ominicontacto_app.models import Campana, OpcionCalificacion
from django.views.generic.detail import DetailView
from ominicontacto_app.services.dialer import get_dialer_service
from reportes_app.models import LlamadaLog


class CampanaDialerDetailView(DetailView):
    """Detalle de una campana dialer"""
    template_name = 'campanas/campana_dialer/detalle.html'
    model = Campana
    context_object_name = 'campana'

    def get_context_data(self, **kwargs):
        context = super(
            CampanaDialerDetailView, self).get_context_data(**kwargs)
        campana = self.get_object()
        opciones_calificacion = campana.opciones_calificacion.all()
        context['opciones_calificacion'] = opciones_calificacion.values('nombre')
        context['opciones_calificacion_gestion'] = opciones_calificacion.filter(
            tipo=OpcionCalificacion.GESTION).values('nombre')
        estados_running = [Campana.ESTADO_ACTIVA, Campana.ESTADO_PAUSADA,
                           Campana.ESTADO_FINALIZADA]
        if campana.estado in estados_running:

            dialer_service = get_dialer_service()
            datos_campana = dialer_service.obtener_estado_campana(campana)
            if datos_campana:
                cant_contactos_llamados = LlamadaLog.objects.cantidad_contactos_llamados(campana)
                context['cant_contactos_llamados'] = cant_contactos_llamados
                context['efectuadas'] = datos_campana['efectuadas']
                context['terminadas'] = datos_campana['terminadas']
                context['estimadas'] = datos_campana['estimadas']
                context['reintentos_abiertos'] = datos_campana['reintentos_abiertos']
                context['status'] = datos_campana['status']
                context['resultado'] = True
            else:
                context['resultado'] = False
        return context

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])


def detalle_campana_dialer_view(request):
    """Vista que muestrar el detalle de campana en el servicio"""
    pk_campana = int(request.GET['pk_campana'])
    campana = Campana.objects.get(pk=pk_campana)
    dialer_service = get_dialer_service()
    datos_campana = dialer_service.obtener_estado_campana(campana)
    if datos_campana:
        cant_contactos_llamados = LlamadaLog.objects.cantidad_contactos_llamados(campana)
        data = {
            'error_consulta': False,
            'campana': campana,
            'cant_contactos_llamados': cant_contactos_llamados,
            'efectuadas': datos_campana['efectuadas'],
            'terminadas': datos_campana['terminadas'],
            'estimadas': datos_campana['estimadas'],
            'reintentos_abiertos': datos_campana['reintentos_abiertos'],
            'status': datos_campana['status']
        }
        if 'terminadas_ok' in datos_campana:  # Datos solo disponibles para OMniDialer
            data['terminadas_ok'] = datos_campana['terminadas_ok']
            data['terminadas_no'] = datos_campana['terminadas_no']
            data['estimadas_iniciales'] = datos_campana['estimadas_iniciales']
    else:
        data = {
            'campana': campana,
            'error_consulta': _(u"No se pudo consultar el estado actual de la campaña. "
                                "Consulte con su administrador.")
        }
    return render(request, 'campanas/campana_dialer/detalle_campana.html', data)
