# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
from StringIO import StringIO
from zipfile import ZipFile

from django.utils.timezone import now
from django.utils.translation import ugettext as _
from django.views.generic import FormView
from django.http import HttpResponse

from ominicontacto_app.utiles import datetime_hora_minima_dia, UnicodeWriter
from ominicontacto_app.views_utils import handler400

from reportes_app.forms import (ReporteLlamadasForm, ExportarReporteLlamadasForm,
                                EstadisticasJSONForm)
from reportes_app.reporte_llamadas import ReporteDeLlamadas, GeneradorReportesLlamadasCSV


class ReporteLlamadasFormView(FormView):
    """Vista que despliega reporte de las grabaciones de las llamadas"""
    template_name = 'reporte_llamadas.html'
    form_class = ReporteLlamadasForm

    def get_initial(self):
        initial = super(ReporteLlamadasFormView, self).get_initial()
        hoy = now().date().strftime('%d/%m/%Y')
        initial['fecha'] = ' - '.join([hoy] * 2)
        return initial

    def get(self, request, *args, **kwargs):
        hoy_ahora = now()
        hoy_inicio = datetime_hora_minima_dia(hoy_ahora)
        reporte = ReporteDeLlamadas(hoy_inicio, hoy_ahora, False, request.user)
        estadisticas = reporte.estadisticas
        graficos = reporte.graficos
        return self.render_to_response(self.get_context_data(
            desde=hoy_inicio,
            hasta=hoy_ahora,
            estadisticas=estadisticas,
            graficos=graficos,
            estadisticas_json=json.dumps(estadisticas)))

    def form_valid(self, form):
        desde = form.desde
        hasta = form.hasta
        finalizadas = form.cleaned_data['finalizadas']
        reporte = ReporteDeLlamadas(desde, hasta, finalizadas, self.request.user)
        estadisticas = reporte.estadisticas
        graficos = reporte.graficos
        return self.render_to_response(self.get_context_data(
            desde=desde,
            hasta=hasta,
            estadisticas=estadisticas,
            graficos=graficos,
            estadisticas_json=json.dumps(estadisticas)))


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
        return handler400(self.request)


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
        return handler400(self.request)

    def _generar_buffer_archivo_zip(self, estadisticas):

        generador = GeneradorReportesLlamadasCSV()
        (llamadas_por_tipo, llamadas_por_campana, tipos_de_llamada_manual,
         tipos_de_llamada_dialer, tipos_de_llamada_entrante,
         tipos_de_llamada_preview) = generador.obtener_filas_de_todos_los_reportes(estadisticas)

        in_memory = StringIO()
        zip = ZipFile(in_memory, "a")

        llamadas_por_tipo_file = StringIO()
        llamadas_por_tipo_writer = UnicodeWriter(llamadas_por_tipo_file)
        llamadas_por_tipo_writer.writerows(llamadas_por_tipo)

        llamadas_por_campana_file = StringIO()
        llamadas_por_campana_writer = UnicodeWriter(llamadas_por_campana_file)
        llamadas_por_campana_writer.writerows(llamadas_por_campana)

        tipos_de_llamada_manual_file = StringIO()
        tipos_de_llamada_manual_writer = UnicodeWriter(tipos_de_llamada_manual_file)
        tipos_de_llamada_manual_writer.writerows(tipos_de_llamada_manual)

        tipos_de_llamada_dialer_file = StringIO()
        tipos_de_llamada_dialer_writer = UnicodeWriter(tipos_de_llamada_dialer_file)
        tipos_de_llamada_dialer_writer.writerows(tipos_de_llamada_dialer)

        tipos_de_llamada_entrante_file = StringIO()
        tipos_de_llamada_entrante_writer = UnicodeWriter(tipos_de_llamada_entrante_file)
        tipos_de_llamada_entrante_writer.writerows(tipos_de_llamada_entrante)

        tipos_de_llamada_preview_file = StringIO()
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
