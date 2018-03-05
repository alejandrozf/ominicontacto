# -*- coding: utf-8 -*-

""" Vistas para el reciclados de las campanas"""

from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.views.generic import FormView
from ominicontacto_app.models import Campana
from reciclado_app.forms import RecicladoForm
from reciclado_app.resultado_contactacion import EstadisticasContactacion

import logging as logging_


logger = logging_.getLogger(__name__)


class ReciclarCampanaDialerFormView(FormView):
    """
    Esta vista muestra los distintos tipo de reciclados de las campanas
    dialer
    """

    form_class = RecicladoForm
    template_name = 'nuevo_reciclado.html'

    def get(self, request, *args, **kwargs):
        estadisticas = EstadisticasContactacion()
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        self.resultado = estadisticas.obtener_resultado_contactacion(campana)
        return super(ReciclarCampanaDialerFormView, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(ReciclarCampanaDialerFormView, self).get_form_kwargs()
        reciclado_choice = [(item, item) for item in self.resultado.keys()]
        kwargs['reciclado_choice'] = reciclado_choice
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ReciclarCampanaDialerFormView, self).get_context_data(**kwargs)
        context['resultados'] = self.resultado
        return context

    def form_valid(self, form):
        return super(ReciclarCampanaDialerFormView, self).form_valid(form)

    def get_success_url(self):
        reverse('view_blanco')
