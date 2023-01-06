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

from __future__ import unicode_literals

import json
from io import BytesIO
from zipfile import ZipFile

from django.utils.timezone import now
from django.utils.crypto import get_random_string
from django.views.generic import FormView, TemplateView
from django.http import HttpResponse
from django.shortcuts import redirect

# Ominicontacto App
from ominicontacto_app.models import Campana
from ominicontacto_app.utiles import (
    fecha_local, fecha_hora_local,
    datetime_hora_minima_dia, UnicodeWriter
)
from ominicontacto_app.views_utils import handler400

# Reportes App
from reportes_app.forms import (
    ReporteLlamadasForm,
    ExportarReporteLlamadasForm,
    EstadisticasJSONForm
)
from reportes_app.reportes.reporte_llamadas import (
    ReporteDeLlamadas,
    GeneradorReportesLlamadasCSV
)
from reportes_app.reportes.reporte_resultados import (
    ReporteDeResultadosDeCampana
)
from utiles_globales import obtener_paginas


class ReporteLlamadasFormView(FormView):
    """Vista que despliega reporte de las grabaciones de las llamadas"""
    template_name = 'reporte_llamadas.html'
    form_class = ReporteLlamadasForm

    def get_initial(self):
        initial = super(ReporteLlamadasFormView, self).get_initial()
        hoy = fecha_local(now()).strftime('%d/%m/%Y')
        initial['fecha'] = ' - '.join([hoy] * 2)
        return initial

    def get(self, request, *args, **kwargs):
        hoy_ahora = fecha_hora_local(now())
        hoy_inicio = datetime_hora_minima_dia(hoy_ahora)
        reporte = ReporteDeLlamadas(hoy_inicio, hoy_ahora, False, request.user)
        return self.render_to_response(self.get_context_data(
            desde=hoy_inicio,
            hasta=hoy_ahora,
            estadisticas=reporte.estadisticas,
            graficos=reporte.graficos,
            estadisticas_por_fecha=reporte.estadisticas_por_fecha,
            estadisticas_json=json.dumps(reporte.estadisticas)))

    def form_valid(self, form):
        desde = form.desde
        hasta = form.hasta
        finalizadas = form.cleaned_data['finalizadas']
        reporte = ReporteDeLlamadas(desde, hasta, finalizadas, self.request.user)
        return self.render_to_response(self.get_context_data(
            desde=desde,
            hasta=hasta,
            estadisticas=reporte.estadisticas,
            graficos=reporte.graficos,
            estadisticas_por_fecha=reporte.estadisticas_por_fecha,
            estadisticas_json=json.dumps(reporte.estadisticas)))


class ExportarReporteLlamadasFormView(FormView):
    form_class = ExportarReporteLlamadasForm

    def form_valid(self, form):
        response = HttpResponse(content_type='text/csv')
        estadisticas = form.cleaned_data.get('estadisticas')
        tipo_reporte = form.cleaned_data.get('tipo_reporte')

        response['Content-Disposition'] = 'attachment; filename="{0}.csv"'.format(tipo_reporte)
        writer = UnicodeWriter(response)

        generador = GeneradorReportesLlamadasCSV()
        filas_csv = generador.obtener_filas_reporte(estadisticas, tipo_reporte)
        writer.writerows(filas_csv)
        # writer.writerow(REPORTE_SIN_DATOS)

        return response

    def form_invalid(self, form):
        return handler400(self.request, None)


class ExportarZipReportesLlamadasFormView(FormView):
    form_class = EstadisticasJSONForm

    def form_valid(self, form):
        """
        Realiza la exportación de todos los reportes de llamadas a .csv y los devuelve
        comprimidos dentro de un zip
        """
        estadisticas = form.cleaned_data.get('estadisticas')

        buffer = self._generar_buffer_archivo_zip(estadisticas)

        response = HttpResponse(content_type="application/zip")
        response["Content-Disposition"] = "attachment; filename=reporte-general.zip"

        buffer.seek(0)
        response.write(buffer.read())

        return response

    def form_invalid(self, form):
        return handler400(self.request, None)

    def _generar_buffer_archivo_zip(self, estadisticas):

        generador = GeneradorReportesLlamadasCSV()
        (llamadas_por_tipo, llamadas_por_campana, tipos_de_llamada_manual,
         tipos_de_llamada_dialer, tipos_de_llamada_entrante,
         tipos_de_llamada_preview) = generador.obtener_filas_de_todos_los_reportes(estadisticas)

        in_memory = BytesIO()
        zip = ZipFile(in_memory, "a")

        llamadas_por_tipo_file = BytesIO()
        llamadas_por_tipo_writer = UnicodeWriter(llamadas_por_tipo_file)
        llamadas_por_tipo_writer.writerows(llamadas_por_tipo)

        llamadas_por_campana_file = BytesIO()
        llamadas_por_campana_writer = UnicodeWriter(llamadas_por_campana_file)
        llamadas_por_campana_writer.writerows(llamadas_por_campana)

        tipos_de_llamada_manual_file = BytesIO()
        tipos_de_llamada_manual_writer = UnicodeWriter(tipos_de_llamada_manual_file)
        tipos_de_llamada_manual_writer.writerows(tipos_de_llamada_manual)

        tipos_de_llamada_dialer_file = BytesIO()
        tipos_de_llamada_dialer_writer = UnicodeWriter(tipos_de_llamada_dialer_file)
        tipos_de_llamada_dialer_writer.writerows(tipos_de_llamada_dialer)

        tipos_de_llamada_entrante_file = BytesIO()
        tipos_de_llamada_entrante_writer = UnicodeWriter(tipos_de_llamada_entrante_file)
        tipos_de_llamada_entrante_writer.writerows(tipos_de_llamada_entrante)

        tipos_de_llamada_preview_file = BytesIO()
        tipos_de_llamada_preview_writer = UnicodeWriter(tipos_de_llamada_preview_file)
        tipos_de_llamada_preview_writer.writerows(tipos_de_llamada_preview)

        zip.writestr("llamadas_por_tipo.csv", llamadas_por_tipo_file.getvalue())
        zip.writestr("llamadas_por_campana.csv", llamadas_por_campana_file.getvalue())
        zip.writestr("tipos_de_llamada_manual.csv", tipos_de_llamada_manual_file.getvalue())
        zip.writestr("tipos_de_llamada_dialer.csv", tipos_de_llamada_dialer_file.getvalue())
        zip.writestr("tipos_de_llamada_entrante.csv", tipos_de_llamada_entrante_file.getvalue())
        zip.writestr("tipos_de_llamada_preview.csv", tipos_de_llamada_preview_file.getvalue())

        # fix for Linux zip files read in Windows
        for file in zip.filelist:
            file.create_system = 0
        zip.close()

        return in_memory


class ReporteDeResultadosView(TemplateView):
    page_kwarg = 'page'
    paginate_by = 250
    template_name = 'reporte_de_resultados.html'

    def dispatch(self, request, *args, **kwargs):
        # TODO: [PERMISOS] Verificar que
        # el supervisor tenga acceso a la campaña
        try:
            self.campana = Campana.objects.using('replica').get(id=kwargs['pk_campana'])
        except Campana.DoesNotExist:
            return redirect('index')
        return super(
            ReporteDeResultadosView,
            self
        ).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(
            ReporteDeResultadosView,
            self
        ).get_context_data(**kwargs)
        page_number = self.request.GET.get(self.page_kwarg, 1)
        reporte = ReporteDeResultadosDeCampana(
            self.campana,
            page_number=page_number,
            page_size=self.paginate_by,
        )
        if reporte.is_paginated:
            context['is_paginated'] = True
            context['paginator'] = reporte.paginator
            context['page_obj'] = reporte.page
            obtener_paginas(context, 7)
        context['campana'] = self.campana
        context['task_id'] = get_random_string(8)
        metadata = self.campana.bd_contacto.get_metadata()
        context['columnas_datos'] = metadata.nombres_de_columnas_de_datos
        context['reporte'] = reporte

        if self.campana.type in [Campana.TYPE_ENTRANTE, Campana.TYPE_MANUAL]:
            context['mostrar_export_todos'] = True
        else:
            context['mostrar_export_todos'] = False

        return context
