# -*- coding: utf-8 -*-

"""Vistas de reportes para campañas de tipo manual"""

from __future__ import unicode_literals

from django.shortcuts import redirect
from django.views.generic import UpdateView

from ominicontacto_app.models import Campana

from ominicontacto_app.services.reporte_campana_manual_calificacion import ReporteCampanaService
from ominicontacto_app.services.reporte_campana_manual_gestion import ReporteGestionCampanaService


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
