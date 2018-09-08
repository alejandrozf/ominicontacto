# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

from __future__ import unicode_literals

import logging as logging_

from ast import literal_eval
from random import choice

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.db.utils import DatabaseError
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, View, DetailView, DeleteView

from ominicontacto_app.forms import (CampanaPreviewForm, OpcionCalificacionFormSet,
                                     ParametroExtraParaWebformFormSet)
from ominicontacto_app.models import AgenteEnContacto, Campana
from ominicontacto_app.views_campana_creacion import (CampanaWizardMixin,
                                                      CampanaTemplateCreateMixin,
                                                      CampanaTemplateCreateCampanaMixin,
                                                      CampanaTemplateDeleteMixin)
from ominicontacto_app.views_campana import CampanaSupervisorUpdateView
from ominicontacto_app.views_campana_manual_creacion import (CampanaManualCreateView,
                                                             CampanaManualUpdateView)
from ominicontacto_app.views_campana_manual import CampanaManualListView, CampanaManualDeleteView


logger = logging_.getLogger(__name__)


class CampanaPreviewMixin(CampanaWizardMixin):
    INICIAL = '0'
    COLA = None
    OPCIONES_CALIFICACION = '1'
    PARAMETROS_EXTRA_WEB_FORM = '2'

    FORMS = [(INICIAL, CampanaPreviewForm),
             (OPCIONES_CALIFICACION, OpcionCalificacionFormSet),
             (PARAMETROS_EXTRA_WEB_FORM, ParametroExtraParaWebformFormSet)]

    TEMPLATES = {INICIAL: "campana_preview/campana_preview.html",
                 OPCIONES_CALIFICACION: "campana_preview/opcion_calificacion.html",
                 PARAMETROS_EXTRA_WEB_FORM: "campana_preview/parametros_extra_web_form.html"}

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
        self._insert_queue_asterisk(queue)
        return HttpResponseRedirect(reverse('campana_preview_list'))


class CampanaPreviewUpdateView(CampanaPreviewMixin, CampanaManualUpdateView):
    """
    Modifica una campaña de tipo Preview
    """

    def done(self, form_list, **kwargs):
        queue = self._save_forms(form_list, **kwargs)
        self._insert_queue_asterisk(queue)
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
    def get_form_initial(self, step):
        initial = super(CampanaPreviewTemplateCreateCampanaView, self).get_form_initial(step)
        if step == self.INICIAL:
            pk = self.kwargs.get('pk_campana_template', None)
            campana_template = get_object_or_404(Campana, pk=pk)
            initial['auto_grabacion'] = campana_template.queue_campana.auto_grabacion
            initial['tiempo_desconexion'] = campana_template.tiempo_desconexion
        return initial


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
