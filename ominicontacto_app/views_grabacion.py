# -*- coding: utf-8 -*-

"""
Aca se encuentran las vistas relacionada con las grabaciones en cuanto a su busqueda
ya que el insert lo hace kamailio-debian/asterisk(hablar con fabian como hace el insert )
"""

from django.utils import timezone

from django.views.generic import FormView, View
from django.core import paginator as django_paginator
from django.http import JsonResponse

from ominicontacto_app.forms import GrabacionBusquedaForm
from ominicontacto_app.models import (
    Grabacion, GrabacionMarca, Campana
)
from utiles import convert_fecha_datetime, fecha_local


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
        return context

    def get(self, request, *args, **kwargs):
        hoy = fecha_local(timezone.now())
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
