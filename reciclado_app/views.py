# -*- coding: utf-8 -*-

""" Vistas para el reciclados de las campanas"""

from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.contrib import messages
from django.shortcuts import HttpResponseRedirect
from ominicontacto_app.errors import OmlRecicladoCampanaError
from django.views.generic import FormView
from ominicontacto_app.models import Campana
from reciclado_app.forms import RecicladoForm
from reciclado_app.resultado_contactacion import (
    EstadisticasContactacion, RecicladorContactosCampanaDIALER)

import logging as logging_


logger = logging_.getLogger(__name__)


class ReciclarCampanaDialerFormView(FormView):
    """
    Esta vista muestra los distintos tipo de reciclados de las campanas
    dialer
    """

    form_class = RecicladoForm
    template_name = 'nuevo_reciclado.html'

    def get_form_kwargs(self):
        kwargs = super(ReciclarCampanaDialerFormView, self).get_form_kwargs()
        estadisticas = EstadisticasContactacion()
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])

        contactados = estadisticas.obtener_cantidad_calificacion(campana)
        contactados_choice = [(contactacion.id, contactacion.label_checkbox)
                              for contactacion in contactados]
        no_contactados = estadisticas.obtener_cantidad_no_contactados(campana)
        no_contactados_choice = [(value.id, value.label_checkbox)
                                 for key, value in no_contactados.items()]
        kwargs['reciclado_choice'] = contactados_choice
        kwargs['no_contactados_choice'] = no_contactados_choice
        return kwargs

    def form_valid(self, form):
        reciclado_calificacion = form.cleaned_data.get('reciclado_calificacion')
        reciclado_no_contactacion = form.cleaned_data.get('reciclado_no_contactacion')
        reciclado_radio = form.cleaned_data.get('reciclado_radio')

        if not (reciclado_calificacion or reciclado_no_contactacion):
            message = '<strong>Operación Errónea!</strong> \
                        Debe seleccionar al menos una opcion para reciclar '

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return self.form_invalid(form)

        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        reciclador = RecicladorContactosCampanaDIALER()
        bd_contacto_reciclada = reciclador.reciclar(
            campana, reciclado_calificacion, reciclado_no_contactacion)
        try:
            # Intenta reciclar la campana con el tipo de reciclado
            # seleccionado.
            campana_reciclada = Campana.objects.reciclar_campana(
                campana, bd_contacto_reciclada)
        except OmlRecicladoCampanaError:

            message = '<strong>Operación Errónea!</strong>\
            No se pudo reciclar la Campana.'

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return self.form_invalid(form)

        if reciclado_radio == 'nueva_campaña':
            return HttpResponseRedirect(
                reverse("crea_campana_dialer_template",
                        kwargs={"pk_campana_template": campana_reciclada.pk,
                                "borrar_template": 1}))
