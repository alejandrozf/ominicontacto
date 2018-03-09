# -*- coding: utf-8 -*-

"""Vista para generar templates de campana"""

from __future__ import unicode_literals

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DeleteView
from django.views.generic.detail import DetailView

from ominicontacto_app.views_campana_creacion import CampanaTemplateCreateMixin
from ominicontacto_app.models import Campana

from ominicontacto_app.views_campana_creacion import CampanaTemplateCreateCampanaMixin
from ominicontacto_app.views_campana_dialer_creacion import CampanaDialerCreateView


import logging as logging_

logger = logging_.getLogger(__name__)


class TemplateListView(ListView):
    """
    Esta vista lista los objetos Capanas-->Templates activos.
    """

    template_name = 'template/lista_template.html'
    context_object_name = 'campanas'
    model = Campana

    def get_context_data(self, **kwargs):
        context = super(TemplateListView, self).get_context_data(**kwargs)
        context['templates_activos'] = \
            Campana.objects.obtener_templates_activos_dialer()
        return context


class CampanaDialerTemplateCreateView(CampanaTemplateCreateMixin, CampanaDialerCreateView):
    """
    Crea una campaña sin acción en el sistema, sólo con el objetivo de servir de
    template base para agilizar la creación de las campañas dialer
    """

    def done(self, form_list, *args, **kwargs):
        self._save_forms(form_list, Campana.ESTADO_TEMPLATE_ACTIVO)
        return HttpResponseRedirect(reverse('campana_dialer_list'))


class CampanaDialerCreateCampana(CampanaTemplateCreateCampanaMixin, CampanaDialerCreateView):
    """Vista que crea campana a partir de template"""
    pass


class TemplateDetailView(DetailView):
    """Vista muestra el detalle de la campana"""
    template_name = 'template/template_detalle.html'
    model = Campana


class TemplateDeleteView(DeleteView):
    """
    Esta vista se encarga de la eliminación del
    objeto Campana-->Template.
    """

    model = Campana
    template_name = 'campana_dialer/delete_campana.html'

    def dispatch(self, request, *args, **kwargs):
        self.campana = \
            Campana.objects.obtener_activo_para_eliminar_crear_ver(
                kwargs['pk_campana'])
        return super(TemplateDeleteView, self).dispatch(request, *args,
                                                        **kwargs)

    def get_object(self, queryset=None):
        return Campana.objects.obtener_activo_para_eliminar_crear_ver(
            self.kwargs['pk_campana'])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()

        self.object.borrar_template()

        message = '<strong>Operación Exitosa!</strong>\
        Se llevó a cabo con éxito la eliminación del Template.'

        messages.add_message(
            self.request,
            messages.SUCCESS,
            message,
        )
        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        return reverse('lista_campana_dialer_template')
