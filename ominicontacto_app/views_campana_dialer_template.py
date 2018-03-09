# -*- coding: utf-8 -*-

"""Vista para generar templates de campana"""

from __future__ import unicode_literals

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import (
    ListView, CreateView, DeleteView)
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from ominicontacto_app.forms import QueueDialerForm, ActuacionVigenteForm, ReglasIncidenciaForm
from ominicontacto_app.models import Campana, Queue, ActuacionVigente, ReglasIncidencia

from ominicontacto_app.views_campana_creacion import CampanaTemplateCreateMixin
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


class ActuacionVigenteCampanaDialerTemplateCreateView(CreateView):
    """
    Esta vista crea uno objeto ActuacionVigente
    para la Campana que se este creando.
    Inicializa el form con campo campana (hidden)
    con el id de campana que viene en la url.
    """

    template_name = 'campana_dialer/actuacion_vigente_campana.html'
    model = ActuacionVigente
    context_object_name = 'actuacion'
    form_class = ActuacionVigenteForm

    def get_initial(self):
        initial = super(ActuacionVigenteCampanaDialerTemplateCreateView, self).get_initial()
        initial.update({'campana': self.campana.id})
        return initial

    def get_context_data(self, **kwargs):
        context = super(
            ActuacionVigenteCampanaDialerTemplateCreateView, self).get_context_data(**kwargs)
        context['campana'] = self.campana
        return context

    def get_success_url(self):
        return reverse(
            'nueva_reglas_incidencia_campana_dialer_template',
            kwargs={"pk_campana": self.kwargs['pk_campana']}
        )


class ReglasIncidenciaCampanaDialerTemplateCreateView(CreateView):
    """
    Esta vista crea uno o varios objetos ReglasIncidencia
    para la Campana que se este creando.
    Inicializa el form con campo campana (hidden)
    con el id de campana que viene en la url.
    """

    template_name = 'campana_dialer/reglas_incidencia.html'
    model = ReglasIncidencia
    context_object_name = 'reglas_incidencia'
    form_class = ReglasIncidenciaForm

    def get_initial(self):
        initial = super(ReglasIncidenciaCampanaDialerTemplateCreateView,
                        self).get_initial()
        initial.update({'campana': self.campana.id})
        return initial

    def get_context_data(self, **kwargs):
        context = super(
            ReglasIncidenciaCampanaDialerTemplateCreateView,
            self).get_context_data(**kwargs)
        context['campana'] = self.campana
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if self.campana.valida_reglas_incidencia(self.object):
            message = """¡Cuidado!
            El estado {0} ya se encuentra cargado""".format(
                self.object.get_estado_display())
            messages.add_message(
                self.request,
                messages.WARNING,
                message,
            )
            return self.form_invalid(form)
        if self.object.estado is ReglasIncidencia.TERMINATED:
            self.object.estado_personalizado = "CONTESTADOR"
        self.object.save()

        return super(ReglasIncidenciaCampanaDialerTemplateCreateView,
                     self).form_valid(form)

    def get_success_url(self):
        return reverse(
            'nueva_reglas_incidencia_campana_dialer_template',
            kwargs={"pk_campana": self.kwargs['pk_campana']}
        )


def regla_incidencia_delete_view(request, pk_campana, pk_regla):
    """Elimina regla de incidencia de un template de campna"""
    regla = ReglasIncidencia.objects.get(pk=pk_regla)
    regla.delete()
    return HttpResponseRedirect(
        reverse(
            'nueva_reglas_incidencia_campana_dialer_template',
            kwargs={"pk_campana": pk_campana}
        ))


class QueueDialerTemplateCreateView(CreateView):
    """Vista para crear una cola dialer para template de campana"""
    model = Queue
    form_class = QueueDialerForm
    template_name = 'campana_dialer/create_update_queue.html'

    def get_initial(self):
        initial = super(QueueDialerTemplateCreateView, self).get_initial()
        initial.update({'campana': self.campana.id,
                        'name': self.campana.nombre})
        return initial

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.eventmemberstatus = True
        self.object.eventwhencalled = True
        self.object.ringinuse = True
        self.object.setinterfacevar = True
        self.object.queue_asterisk = Queue.objects.ultimo_queue_asterisk()
        self.object.save()
        return super(QueueDialerTemplateCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(QueueDialerTemplateCreateView, self).get_context_data(**kwargs)
        context['campana'] = self.campana
        context['create'] = True
        return context

    def get_success_url(self):
        return reverse(
            'nuevo_actuacion_vigente_campana_dialer_template',
            kwargs={"pk_campana": self.campana.pk}
        )


class ConfirmaCampanaDialerTemplateView(RedirectView):
    """Vista confirma la creacion de un template de campana"""
    pattern_name = 'lista_campana_dialer_template'
    url = None

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.estado = Campana.ESTADO_TEMPLATE_ACTIVO
        self.object.save()
        self.url = reverse('lista_campana_dialer_template')
        return super(ConfirmaCampanaDialerTemplateView, self).post(
            request, *args, **kwargs)


class CreaCampanaTemplateView(RedirectView):
    """Vista crea campana apartir de template"""
    permanent = False
    url = None

    def dispatch(self, request, *args, **kwargs):
        self.campana = \
            Campana.objects.obtener_activo_para_eliminar_crear_ver(kwargs['pk_campana'])
        return super(CreaCampanaTemplateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        template = get_object_or_404(
            Campana, pk=self.kwargs['pk_campana']
        )
        campana = Campana.objects.crea_campana_de_template(template)

        self.url = reverse('campana_dialer_replicar_update',
                           kwargs={"pk_campana": campana.pk})

        return super(CreaCampanaTemplateView, self).get(request, *args,
                                                        **kwargs)


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
