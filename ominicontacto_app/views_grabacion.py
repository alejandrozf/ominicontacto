# -*- coding: utf-8 -*-


from django.conf import settings
from django.views.generic import FormView
from ominicontacto_app.forms import (
    GrabacionBusquedaForm
)
from ominicontacto_app.models import (
    Grabacion
)


class BusquedaGrabacionFormView(FormView):
    form_class = GrabacionBusquedaForm
    template_name = 'busqueda_grabacion.html'

    def get_context_data(self, **kwargs):
        context = super(BusquedaGrabacionFormView, self).get_context_data(
            **kwargs)
        context['grabacion_url'] = settings.OML_GRABACIONES_URL
        return context

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(
            listado_de_grabaciones=Grabacion.objects.all()))

    def form_valid(self, form):
        fecha = form.cleaned_data.get('fecha')
        tipo_llamada = form.cleaned_data.get('tipo_llamada')
        id_cliente = form.cleaned_data.get('id_cliente')
        tel_cliente = form.cleaned_data.get('tel_cliente')
        sip_agente = form.cleaned_data.get('sip_agente')
        campana = form.cleaned_data.get('campana')
        listado_de_grabaciones = Grabacion.objects.grabacion_by_filtro(fecha,
            tipo_llamada, id_cliente, tel_cliente, sip_agente, campana)
        return self.render_to_response(self.get_context_data(
            listado_de_grabaciones=listado_de_grabaciones))
