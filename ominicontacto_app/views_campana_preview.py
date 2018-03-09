# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging as logging_

from ast import literal_eval
from collections import defaultdict
from random import choice

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.db.utils import DatabaseError
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, View, DetailView, DeleteView

from ominicontacto_app.forms import CampanaPreviewForm, OpcionCalificacionFormSet
from ominicontacto_app.models import AgenteEnContacto, CalificacionCliente, Campana
from ominicontacto_app.views_campana_creacion import (CampanaWizardMixin,
                                                      CampanaTemplateCreateMixin,
                                                      CampanaTemplateCreateCampanaMixin,
                                                      CampanaTemplateDeleteMixin)
from ominicontacto_app.views_campana import CampanaSupervisorUpdateView
from ominicontacto_app.views_campana_dialer_reportes import CampanaDialerReporteGrafico
from ominicontacto_app.views_campana_manual_creacion import (CampanaManualCreateView,
                                                             CampanaManualUpdateView)
from ominicontacto_app.views_campana_manual import CampanaManualListView, CampanaManualDeleteView


logger = logging_.getLogger(__name__)


class CampanaPreviewMixin(CampanaWizardMixin):
    INICIAL = '0'
    COLA = None
    OPCIONES_CALIFICACION = '1'

    FORMS = [(INICIAL, CampanaPreviewForm),
             (OPCIONES_CALIFICACION, OpcionCalificacionFormSet)]

    TEMPLATES = {INICIAL: "campana_preview/campana_preview.html",
                 OPCIONES_CALIFICACION: "campana_manual/opcion_calificacion.html"}

    form_list = FORMS


class CampanaPreviewCreateView(CampanaPreviewMixin, CampanaManualCreateView):
    """
    Crea una campaña de tipo Preview
    """

    def done(self, form_list, **kwargs):
        queue = self._save_forms(form_list, Campana.ESTADO_ACTIVA, Campana.TYPE_PREVIEW)
        # rellenar la tabla que relación agentes y contactos con los valores iniciales
        queue.campana.establecer_valores_iniciales_agente_contacto()
        # crear(sobreescribir) archivo de crontab con la configuración de llamadas al procedimiento
        # de actualización de las asignaciones de agente a contactos
        queue.campana.crear_tarea_actualizacion()
        return HttpResponseRedirect(reverse('campana_preview_list'))


class CampanaPreviewUpdateView(CampanaPreviewMixin, CampanaManualUpdateView):
    """
    Modifica una campaña de tipo Preview
    """

    def done(self, form_list, **kwargs):
        self._save_forms(form_list, **kwargs)
        return HttpResponseRedirect(reverse('campana_preview_list'))


class CampanaPreviewTemplateListView(ListView):
    """
    Vista que muestra todos los templates de campañas entrantes activos
    """
    template_name = "campana_preview/lista_template.html"
    context_object_name = 'templates_activos_preview'
    model = Campana

    def get_queryset(self):
        return Campana.objects.obtener_templates_activos_preview()


class CampanaPreviewTemplateCreateView(CampanaTemplateCreateMixin, CampanaPreviewCreateView):
    """
    Crea una campaña sin acción en el sistema, sólo con el objetivo de servir de
    template base para agilizar la creación de las campañas preview
    """
    def done(self, form_list, **kwargs):
        self._save_forms(form_list, Campana.ESTADO_TEMPLATE_ACTIVO, Campana.TYPE_PREVIEW)
        return HttpResponseRedirect(reverse('campana_preview_template_list'))


class CampanaPreviewTemplateCreateCampanaView(
        CampanaTemplateCreateCampanaMixin, CampanaPreviewCreateView):
    """
    Crea una campaña preview a partir de una campaña de template existente
    """
    pass


class CampanaPreviewTemplateDetailView(DetailView):
    """
    Muestra el detalle de un template para crear una campaña preview
    """
    template_name = "campana_preview/detalle_campana_template.html"
    model = Campana


class CampanaPreviewTemplateDeleteView(CampanaTemplateDeleteMixin, DeleteView):
    """
    Esta vista se encarga de la eliminación del
    objeto Campana Preview-->Template.
    """
    model = Campana
    template_name = "campana_preview/delete_campana_template.html"

    def get_success_url(self):
        return reverse("campana_preview_template_list")


class CampanaPreviewDeleteView(CampanaManualDeleteView):
    """
    Esta vista se encarga de la eliminación de una campana
    """
    model = Campana
    template_name = 'campana_preview/delete_campana.html'

    def get_success_url(self):
        return reverse('campana_preview_list')


class CampanaPreviewListView(CampanaManualListView):
    """
    Vista que lista las campañas preview
    """
    template_name = 'campana_preview/campana_list.html'

    def _get_campanas(self):
        return Campana.objects.obtener_campanas_preview()

    def get_context_data(self, **kwargs):
        context = super(CampanaPreviewListView, self).get_context_data(**kwargs)
        context['finalizadas'] = context['campanas'].filter(estado=Campana.ESTADO_FINALIZADA)
        context['mostrar_ocultas_tipo'] = "mostrar_campanas_preview_ocultas()"
        return context


class CampanaPreviewBorradasListView(CampanaPreviewListView):
    """
    Vista que lista las campañas preview pero de incluyendo las borradas ocultas
    """

    template_name = 'campana_preview/campanas_borradas.html'

    def get_context_data(self, **kwargs):
        context = super(CampanaPreviewBorradasListView, self).get_context_data(**kwargs)
        context['borradas'] = context['campanas'].filter(estado=Campana.ESTADO_BORRADA)
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return super(CampanaPreviewBorradasListView, self).get(request, *args, **kwargs)
        else:
            return JsonResponse({'result': 'desconectado'})


class CampanaPreviewSupervisorUpdateView(CampanaSupervisorUpdateView):
    """
    Esta vista agrega supervisores a una campana
    """

    def get_success_url(self):
        return reverse('campana_preview_list')


def campana_mostrar_ocultar_view(request, *args, **kwargs):
    """
    Cambia el atributo 'oculto' de la campaña hacia el valor opuesto (muestra/oculta)
    """
    pk = kwargs.get('pk_campana')
    campana = get_object_or_404(Campana, pk=pk)
    campana.oculto = not campana.oculto
    campana.save()
    return JsonResponse({'result': 'Ok'})


def campana_validar_contacto_asignado_view(request, *args, **kwargs):
    """
    Valida si un contacto sigue asignado al agente que quiere llamarlo
    """
    campana_id = request.POST.get('pk_campana')
    agente_id = request.POST.get('pk_agente')
    contacto_id = request.POST.get('pk_contacto')

    agente_en_contacto = get_object_or_404(
        AgenteEnContacto, campana_id=campana_id, contacto_id=contacto_id)
    asignado = agente_en_contacto.agente_id == int(agente_id)
    return JsonResponse({'contacto_asignado': asignado})


class ObtenerContactoView(View):
    """
    Devuelve un contacto de una campaña preview, y además lo marca como entregado
    para evitar que sea entregado a más de un agente de forma simultánea
    """

    def dispatch(self, request, *args, **kwargs):
        pk_campana = kwargs.get('pk_campana')
        agente_profile = request.user.get_agente_profile()
        agente_in_campana_preview = False
        if agente_profile:
            agente_in_campana_preview = agente_profile.campana_member.filter(
                queue_name__campana__pk=pk_campana).exists()
        if agente_profile and agente_in_campana_preview:
            return super(ObtenerContactoView, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied

    def _liberar_contacto(self, agente_id, campana_id):
        qs_agente_entregado = AgenteEnContacto.objects.filter(
            estado=AgenteEnContacto.ESTADO_ENTREGADO, agente_id=agente_id, campana_id=campana_id)
        if qs_agente_entregado.exists():
            agente_en_contacto = qs_agente_entregado.first()
            agente_en_contacto.agente_id = -1
            agente_en_contacto.estado = AgenteEnContacto.ESTADO_INICIAL
            agente_en_contacto.save()

    def _gestionar_contacto(self, request, qs_agentes_contactos, campana_id):
        if qs_agentes_contactos.exists():
            agente_id = request.user.get_agente_profile().pk
            # si el agente tiene algún contacto asignado previamente se libera para
            # que pueda ser entregado a otros agentes de la campaña
            self._liberar_contacto(agente_id, campana_id)
            # encuentra y devuelve de forma aleatoria los datos de uno de los
            # contactos disponibles para el agente
            agente_en_contacto = choice(qs_agentes_contactos)
            agente_en_contacto.estado = AgenteEnContacto.ESTADO_ENTREGADO
            agente_en_contacto.agente_id = agente_id
            agente_en_contacto.save()
            data = model_to_dict(agente_en_contacto)
            data['datos_contacto'] = literal_eval(data['datos_contacto'])
            data['result'] = 'OK'
            data['code'] = 'contacto-obtenido'
            return JsonResponse(data)
        else:
            return JsonResponse({'result': 'Error',
                                 'code': 'error-no-contactos',
                                 'data': 'No hay contactos para asignar en esta campaña'})

    def post(self, request, *args, **kwargs):
        campana_id = kwargs.get('pk_campana', False)
        try:
            qs_agentes_contactos = AgenteEnContacto.objects.select_for_update().filter(
                agente_id=-1, estado=AgenteEnContacto.ESTADO_INICIAL, campana_id=campana_id)
        except DatabaseError:
            return JsonResponse({'result': 'Error',
                                 'code': 'error-concurrencia',
                                 'data': 'Contacto siendo accedido por más de un agente'})
        else:
            return self._gestionar_contacto(request, qs_agentes_contactos, campana_id)


class CampanaPreviewDetailView(DetailView):
    template_name = 'campana_preview/detalle.html'
    model = Campana

    def _crear_dict_categorias(self, count_ventas, finalizadas_categorias_count_dict):
        counts_categorias = defaultdict(int)

        for cat_data in finalizadas_categorias_count_dict:
            cat_count = cat_data['calificacion__nombre__count']
            cat_name = cat_data['calificacion__nombre']
            if cat_count > 0:
                counts_categorias[cat_name] = cat_count

        # se contabilizan juntas las calificaciones con la etiqueta 'Ventas
        # y las que tienen el atributo 'is_venta' igual a True, pero no poseen etiqueta
        counts_categorias['Venta'] += count_ventas

        return dict(counts_categorias)

    def get_context_data(self, **kwargs):
        context = super(CampanaPreviewDetailView, self).get_context_data(**kwargs)
        campana = self.get_object()
        qs_campana_calificaciones = CalificacionCliente.objects.filter(
            opcion_calificacion__campana__pk=campana.pk)

        context['terminadas'] = qs_campana_calificaciones.count()
        context['estimadas'] = campana.bd_contacto.contactos.count() - context['terminadas']

        if context['terminadas']:
            qs_finalizadas_ventas = qs_campana_calificaciones.filter(es_venta=True)
            qs_finalizadas_otras_categorias = qs_campana_calificaciones.exclude(es_venta=True)

            finalizadas_ventas_count = qs_finalizadas_ventas.count()
            finalizadas_otras_categorias_count_dict = qs_finalizadas_otras_categorias.values(
                'calificacion__nombre').annotate(Count('calificacion__nombre'))
            cats_dict = self._crear_dict_categorias(
                finalizadas_ventas_count, finalizadas_otras_categorias_count_dict)
            context['categorias'] = cats_dict

        return context


class CampanaPreviewExpressView(CampanaPreviewDetailView):
    template_name = 'campana_preview/detalle_express.html'


class CampanaPreviewReporteGrafico(CampanaDialerReporteGrafico):

    def get_context_data(self, **kwargs):
        context = super(CampanaPreviewReporteGrafico, self).get_context_data(**kwargs)
        dict_llamadas_counter = context['graficos_estadisticas']['dict_llamadas_counter']
        # eliminamos la información de las llamadas recibidas pues no tiene sentido para
        # las campañas preview
        context['graficos_estadisticas']['dict_llamadas_counter'] = [
            (name, count) for name, count in dict_llamadas_counter
            if name != 'Recibidas']
        barra_campana_llamadas = context['graficos_estadisticas']['barra_campana_llamadas']
        index_recibidas = barra_campana_llamadas.x_labels.index('Recibidas')
        try:
            del barra_campana_llamadas.x_labels[index_recibidas]
            del barra_campana_llamadas.y_labels[index_recibidas]
        except AttributeError:
            pass                # significa que el gráfico estaría vacío
        return context
