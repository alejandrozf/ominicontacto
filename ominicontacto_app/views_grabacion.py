# -*- coding: utf-8 -*-

"""
Aca se encuentran las vistas relacionada con las grabaciones en cuanto a su busqueda
ya que el insert lo hace kamailio-debian/asterisk(hablar con fabian como hace el insert )
"""

from django.utils import timezone
import json

from StringIO import StringIO
from zipfile import ZipFile

from django.conf import settings
from django.views.generic import FormView, View
from django.core import paginator as django_paginator
from django.http import HttpResponse, JsonResponse

from ominicontacto_app.forms import (
    GrabacionBusquedaForm, GrabacionReporteForm
)
from ominicontacto_app.models import (
    Grabacion, GrabacionMarca, Campana
)
from ominicontacto_app.services.reporte_grafico import GraficoService
from utiles import convert_fecha_datetime, UnicodeWriter
from ominicontacto_app.services.reporte_campana_csv import (obtener_filas_reporte,
                                                            obtener_datos_reporte_general,
                                                            REPORTE_SIN_DATOS)


class BusquedaGrabacionFormView(FormView):
    """Vista que realiza la busqeda de las grabaciones"""
    form_class = GrabacionBusquedaForm
    template_name = 'busqueda_grabacion.html'

    def get_context_data(self, **kwargs):
        context = super(BusquedaGrabacionFormView, self).get_context_data(
            **kwargs)

        listado_de_grabaciones = []

        if 'listado_de_grabaciones' in context:
            listado_de_grabaciones = context['listado_de_grabaciones']

        qs = listado_de_grabaciones
        # ----- <Paginate> -----
        page = self.kwargs['pagina']
        if context['pagina']:
            page = context['pagina']
        result_paginator = django_paginator.Paginator(qs, 40)
        try:
            qs = result_paginator.page(page)
        except django_paginator.PageNotAnInteger:
            qs = result_paginator.page(1)
        except django_paginator.EmptyPage:
            qs = result_paginator.page(result_paginator.num_pages)
        # ----- </Paginate> -----
        context['listado_de_grabaciones'] = qs
        context['grabacion_url'] = settings.OML_GRABACIONES_URL
        return context

    def get(self, request, *args, **kwargs):
        hoy_ahora = timezone.now()
        hoy = hoy_ahora.date()
        campanas = Campana.objects.all()
        if self.request.user.get_is_supervisor_customer():
            user = self.request.user
            campanas = Campana.objects.obtener_campanas_vista_by_user(campanas, user)
        return self.render_to_response(
            self.get_context_data(
                listado_de_grabaciones=Grabacion.objects.
                grabacion_by_fecha_intervalo_campanas(hoy, hoy, campanas),
                pagina=self.kwargs['pagina']))

    def get_form(self):
        self.form_class = self.get_form_class()
        campanas = Campana.objects.all()
        if self.request.user.get_is_supervisor_customer():
            user = self.request.user
            campanas = Campana.objects.obtener_campanas_vista_by_user(campanas, user)
        campana_choice = [(campana.pk, campana.nombre)
                          for campana in campanas]
        return self.form_class(campana_choice=campana_choice, **self.get_form_kwargs())

    def form_valid(self, form):
        fecha = form.cleaned_data.get('fecha')
        if fecha:
            fecha_desde, fecha_hasta = fecha.split('-')
            fecha_desde = convert_fecha_datetime(fecha_desde)
            fecha_hasta = convert_fecha_datetime(fecha_hasta)
        else:
            fecha_desde = ''
            fecha_hasta = ''
        tipo_llamada = form.cleaned_data.get('tipo_llamada')
        tel_cliente = form.cleaned_data.get('tel_cliente')
        sip_agente = form.cleaned_data.get('sip_agente')
        campana = form.cleaned_data.get('campana')
        marcadas = form.cleaned_data.get('marcadas', False)
        duracion = form.cleaned_data.get('duracion', 0)
        campanas = Campana.objects.all()
        if self.request.user.get_is_supervisor_customer():
            user = self.request.user
            campanas = Campana.objects.obtener_campanas_vista_by_user(campanas, user)
        pagina = form.cleaned_data.get('pagina')
        listado_de_grabaciones = Grabacion.objects.grabacion_by_filtro(
            fecha_desde, fecha_hasta, tipo_llamada, tel_cliente, sip_agente, campana, campanas,
            marcadas, duracion)

        return self.render_to_response(self.get_context_data(
            listado_de_grabaciones=listado_de_grabaciones, pagina=pagina))


class GrabacionReporteFormView(FormView):
    """Vista que despliega reporte de las grabaciones de las llamadas"""
    template_name = 'grabaciones/total_llamadas.html'
    context_object_name = 'grabacion'
    model = Grabacion
    form_class = GrabacionReporteForm

    def get(self, request, *args, **kwargs):
        # obtener_estadisticas_render_graficos_supervision()
        service = GraficoService()
        hoy_ahora = timezone.now()
        hoy_inicio = timezone.datetime(hoy_ahora.year, hoy_ahora.month, hoy_ahora.day,
                                       tzinfo=timezone.get_current_timezone())
        graficos_estadisticas = service.general_llamadas_hoy(
            hoy_inicio, hoy_ahora, request.user, False)
        return self.render_to_response(self.get_context_data(
            graficos_estadisticas=graficos_estadisticas))

    def form_valid(self, form):
        fecha = form.cleaned_data.get('fecha')
        fecha_desde, fecha_hasta = fecha.split('-')
        fecha_desde = convert_fecha_datetime(fecha_desde)
        fecha_hasta = convert_fecha_datetime(fecha_hasta, final_dia=True)
        finalizadas = form.cleaned_data.get('finalizadas')
        # obtener_estadisticas_render_graficos_supervision()
        service = GraficoService()
        graficos_estadisticas = service.general_llamadas_hoy(
            fecha_desde, fecha_hasta, self.request.user, finalizadas)
        return self.render_to_response(self.get_context_data(
            graficos_estadisticas=graficos_estadisticas))


def exportar_llamadas_view(request, tipo_reporte):
    """
    Realiza el reporte a formato .csv del reporte recibido como parámetro
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{0}.csv"'.format(tipo_reporte)
    writer = UnicodeWriter(response)
    datos_json = request.POST.get(tipo_reporte, False)

    if datos_json:
        datos_reporte = json.loads(datos_json)
        filas_csv = obtener_filas_reporte(tipo_reporte, datos_reporte)
        writer.writerows(filas_csv)
    else:
        writer.writerow(REPORTE_SIN_DATOS)

    return response


def exportar_zip_reportes_view(request):
    """
    Realiza la exportación de todos los reportes de llamadas a .csv y los devuelve
    comprimidos dentro de un zip
    """
    (filas_reporte_total_llamadas, filas_reporte_llamadas_campanas,
     filas_reporte_campanas_dialer, filas_reporte_campanas_entrantes,
     filas_reporte_campanas_manuales) = obtener_datos_reporte_general(request)

    in_memory = StringIO()

    zip = ZipFile(in_memory, "a")

    total_llamadas_file = StringIO()
    total_llamadas_writer = UnicodeWriter(total_llamadas_file)
    total_llamadas_writer.writerows(filas_reporte_total_llamadas)

    llamadas_campanas_file = StringIO()
    llamadas_campanas_writer = UnicodeWriter(llamadas_campanas_file)
    llamadas_campanas_writer.writerows(filas_reporte_llamadas_campanas)

    campanas_dialer_file = StringIO()
    campanas_dialer_writer = UnicodeWriter(campanas_dialer_file)
    campanas_dialer_writer.writerows(filas_reporte_campanas_dialer)

    campanas_entrantes_file = StringIO()
    campanas_entrantes_writer = UnicodeWriter(campanas_entrantes_file)
    campanas_entrantes_writer.writerows(filas_reporte_campanas_entrantes)

    campanas_manuales_file = StringIO()
    campanas_manuales_writer = UnicodeWriter(campanas_manuales_file)
    campanas_manuales_writer.writerows(filas_reporte_campanas_manuales)

    zip.writestr("total_llamadas.csv", total_llamadas_file.getvalue())
    zip.writestr("llamadas_campanas.csv", llamadas_campanas_file.getvalue())
    zip.writestr("llamadas_campanas_dialer.csv", campanas_dialer_file.getvalue())
    zip.writestr("llamadas_campanas_entrantes.csv", campanas_entrantes_file.getvalue())
    zip.writestr("llamadas_campanas_manuales.csv", campanas_manuales_file.getvalue())

    # fix for Linux zip files read in Windows
    for file in zip.filelist:
        file.create_system = 0
    zip.close()

    response = HttpResponse(content_type="application/zip")
    response["Content-Disposition"] = "attachment; filename=reporte-general.zip"

    in_memory.seek(0)
    response.write(in_memory.read())

    return response


class MarcarGrabacionView(View):
    """
    Crea o modifica la descripción de una grabacion existente
    """

    def post(self, *args, **kwargs):
        uid = self.request.POST.get('uid', False)
        descripcion = self.request.POST.get('descripcion', '')
        try:
            grabacion_marca, _ = GrabacionMarca.objects.get_or_create(uid=uid)
        except Exception as e:
            return JsonResponse({'result': 'failed by {0}'.format(e.message)})
        else:
            grabacion_marca.descripcion = descripcion
            grabacion_marca.save()
            return JsonResponse({'result': 'OK'})


class GrabacionDescripcionView(View):
    """
    Obtiene la descripción de una grabación si está marcada
    """

    def get(self, *args, **kwargs):
        uid = kwargs.get('uid', False)
        try:
            grabacion_marca = GrabacionMarca.objects.get(uid=uid)
        except GrabacionMarca.DoesNotExist:
            response = {u'result': u'No encontrada',
                        u'descripcion': u'La grabación no tiene descripción asociada'}
        else:
            response = {u'result': u'Descripción', u'descripcion': grabacion_marca.descripcion}
        return JsonResponse(response)
