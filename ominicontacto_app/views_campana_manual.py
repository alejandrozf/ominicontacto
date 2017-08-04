# -*- coding: utf-8 -*-

"""
Vista para administrar el modelo Campana de tipo dialer
Observacion se copiaron varias vistas del modulo views_campana
"""

from __future__ import unicode_literals

import json

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from ominicontacto_app.models import Campana
from django.views.generic import (
    ListView, UpdateView
)
from ominicontacto_app.services.reporte_campana_manual_calificacion import \
    ReporteCampanaService
from ominicontacto_app.services.reporte_campana_manual_gestion import \
    ReporteGestionCampanaService


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

    def get_context_data(self, **kwargs):
        context = super(CampanaManualListView, self).get_context_data(
           **kwargs)
        campanas = Campana.objects.obtener_campanas_manuales()
        # Filtra las campanas de acuerdo al usuario logeado si tiene permiso sobre
        # las mismas
        if self.request.user.is_authenticated() and self.request.user and \
                not self.request.user.get_is_administrador():
            user = self.request.user
            campanas = Campana.objects.obtener_campanas_vista_by_user(campanas, user)

        context['activas'] = campanas.filter(estado=Campana.ESTADO_ACTIVA)
        context['borradas'] = campanas.filter(estado=Campana.ESTADO_BORRADA,
                                              oculto=False)

        return context


class CampanaManualReporteCalificacionListView(ListView):
    """
    Muestra un listado de contactos a los cuales se los calificaron en la campana
    """
    template_name = 'campana_manual/reporte_campana_formulario.html'
    context_object_name = 'campana'
    model = Campana

    def get_context_data(self, **kwargs):
        context = super(CampanaManualReporteCalificacionListView, self).get_context_data(
            **kwargs)

        service = ReporteCampanaService()
        service_formulario = ReporteGestionCampanaService()
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        service.crea_reporte_csv(campana)
        service_formulario.crea_reporte_csv(campana)
        context['campana'] = campana
        return context


class ExportaReporteFormularioGestionView(UpdateView):
    """
    Esta vista invoca a generar un csv de reporte de la la venta.
    """

    model = Campana
    context_object_name = 'campana'

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        service = ReporteGestionCampanaService()
        url = service.obtener_url_reporte_csv_descargar(self.object)
        return redirect(url)


class ExportaReporteCampanaManualView(UpdateView):
    """
    Esta vista invoca a generar un csv de reporte de la campana.
    """

    model = Campana
    context_object_name = 'campana'

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        service = ReporteCampanaService()
        url = service.obtener_url_reporte_csv_descargar(self.object)
        return redirect(url)
