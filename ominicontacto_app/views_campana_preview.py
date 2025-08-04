# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3, as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

from __future__ import unicode_literals

import csv
import json
import tablib

import redis

from import_export import resources

import logging as logging_

from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, View, DetailView, DeleteView, TemplateView, FormView

from ominicontacto_app.forms.base import (CampanaPreviewForm, OpcionCalificacionFormSet,
                                          ParametrosCrmFormSet, CampanaSupervisorUpdateForm,
                                          QueueMemberFormset, AsignacionContactosForm,
                                          OrdenarAsignacionContactosForm,
                                          CampanaPreviewCampoDesactivacion,
                                          CampanaConfiguracionWhatsappForm,
                                          ActualizarContactosPreviewForm)
from ominicontacto_app.models import AgenteEnContacto, Campana, AgenteProfile, Contacto
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
    CONFIGURACION_WHATSAPP = '1'
    OPCIONES_CALIFICACION = '2'
    PARAMETROS_CRM = '3'
    ADICION_SUPERVISORES = '4'
    ADICION_AGENTES = '5'
    ASIGNACION_CONTACTOS = '6'

    FORMS = [(INICIAL, CampanaPreviewForm),
             (CONFIGURACION_WHATSAPP, CampanaConfiguracionWhatsappForm),
             (OPCIONES_CALIFICACION, OpcionCalificacionFormSet),
             (PARAMETROS_CRM, ParametrosCrmFormSet),
             (ADICION_SUPERVISORES, CampanaSupervisorUpdateForm),
             (ADICION_AGENTES, QueueMemberFormset),
             (ASIGNACION_CONTACTOS, AsignacionContactosForm)]

    TEMPLATES = {INICIAL: "campanas/campana_preview/campana_preview.html",
                 CONFIGURACION_WHATSAPP: "campanas/campana_manual/configuracion_whatsapp.html",
                 OPCIONES_CALIFICACION: "campanas/campana_preview/opcion_calificacion.html",
                 PARAMETROS_CRM: "campanas/campana_preview/parametros_crm_sitio_externo.html",
                 ADICION_SUPERVISORES: "campanas/campana_preview/adicionar_supervisores.html",
                 ADICION_AGENTES: "campanas/campana_preview/adicionar_agentes.html",
                 ASIGNACION_CONTACTOS: "campanas/campana_preview/asignar_contactos.html"}

    form_list = FORMS


class CampanaPreviewCreateView(CampanaPreviewMixin, CampanaManualCreateView):
    """
    Crea una campaña de tipo Preview
    """

    def get_context_data(self, form, *args, **kwargs):
        context = super(CampanaPreviewCreateView, self).get_context_data(form, *args, **kwargs)
        context['create'] = True
        if context["wizard"]["steps"].current == self.ASIGNACION_CONTACTOS:
            agentes_adicionados_temp = self.get_cleaned_data_for_step(self.ADICION_AGENTES)
            if not any(agentes_adicionados_temp):
                context["is_disabled_add_contacts"] = True
                message = _(u'No se han seleccionado agentes para esta campaña')
                messages.warning(self.request, message)
        return context

    def done(self, form_list, form_dict, **kwargs):
        queue = self._save_forms(form_list, form_dict, Campana.ESTADO_ACTIVA, Campana.TYPE_PREVIEW)
        self._insert_queue_asterisk(queue)
        # salvamos los supervisores y agentes asignados a la campaña
        self.save_supervisores(form_list, -3)
        self.save_agentes(form_list, -2)
        # rellenar la tabla que relación agentes y contactos con los valores iniciales
        asignar_contactos_form = list(form_list)[-1]
        asignacion_proporcional = asignar_contactos_form.cleaned_data.get(
            'proporcionalmente', False)
        asignacion_aleatoria = asignar_contactos_form.cleaned_data.get('aleatorio', False)
        queue.campana.establecer_valores_iniciales_agente_contacto(
            asignacion_proporcional, asignacion_aleatoria)
        campana = queue.campana
        self.alertas_por_sistema_externo(campana)
        return HttpResponseRedirect(reverse('campana_preview_list'))


class FinalizarCampanaPreviewView(View):
    """
    Esta vista actualiza la campañana finalizandola.
    """

    def post(self, request, *args, **kwargs):
        campana_id = request.POST.get('campana_pk')
        campana = Campana.objects.get(pk=campana_id)
        campana.finalizar()
        return HttpResponseRedirect(reverse('campana_preview_list'))


class CampanaPreviewUpdateView(CampanaPreviewMixin, CampanaManualUpdateView):
    """
    Modifica una campaña de tipo Preview
    """

    INICIAL = '0'
    COLA = None
    CONFIGURACION_WHATSAPP = '1'
    OPCIONES_CALIFICACION = '2'
    PARAMETROS_CRM = '3'

    FORMS = [(INICIAL, CampanaPreviewForm),
             (CONFIGURACION_WHATSAPP, CampanaConfiguracionWhatsappForm),
             (OPCIONES_CALIFICACION, OpcionCalificacionFormSet),
             (PARAMETROS_CRM, ParametrosCrmFormSet)]

    TEMPLATES = {INICIAL: "campanas/campana_preview/campana_preview.html",
                 CONFIGURACION_WHATSAPP: "campanas/campana_manual/configuracion_whatsapp.html",
                 OPCIONES_CALIFICACION: "campanas/campana_preview/opcion_calificacion.html",
                 PARAMETROS_CRM: "campanas/campana_preview/parametros_crm_sitio_externo.html"}

    form_list = FORMS

    def done(self, form_list, **kwargs):
        queue = self._save_forms(form_list, **kwargs)
        self._insert_queue_asterisk(queue)
        self.alertas_por_sistema_externo(queue.campana)
        return HttpResponseRedirect(reverse('campana_preview_list'))


class CampanaPreviewTemplateListView(ListView):
    """
    Vista que muestra todos los templates de campañas entrantes activos
    """
    template_name = "campanas/campana_preview/lista_template.html"
    context_object_name = 'templates_activos_preview'
    model = Campana

    def get_queryset(self):
        return Campana.objects.obtener_templates_activos_preview()


class CampanaPreviewTemplateCreateView(CampanaTemplateCreateMixin, CampanaPreviewCreateView):
    """
    Crea una campaña sin acción en el sistema, sólo con el objetivo de servir de
    template base para agilizar la creación de las campañas preview
    """

    FORMS = CampanaPreviewCreateView.FORMS[:-3]

    form_list = FORMS

    def done(self, form_list, form_dict, **kwargs):
        self._save_forms(form_list, form_dict, Campana.ESTADO_TEMPLATE_ACTIVO, Campana.TYPE_PREVIEW)
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

    def done(self, form_list, *args, **kwargs):
        borrar_template = bool(int(kwargs.get('borrar_template')))
        if borrar_template:
            # para el caso de cuando se usa la vista en el reciclado y se hace necesario
            # eliminar la campaña que la genera
            pk = self.kwargs.get('pk_campana_template', None)
            campana_template = get_object_or_404(Campana, pk=pk)
            campana_template.delete()
        return super(CampanaPreviewTemplateCreateCampanaView, self).done(form_list, *args, **kwargs)


class CampanaPreviewTemplateDetailView(DetailView):
    """
    Muestra el detalle de un template para crear una campaña preview
    """
    template_name = "campanas/campana_preview/detalle_campana_template.html"
    model = Campana


class CampanaPreviewTemplateDeleteView(CampanaTemplateDeleteMixin, DeleteView):
    """
    Esta vista se encarga de la eliminación del
    objeto Campana Preview-->Template.
    """
    model = Campana
    template_name = "campanas/campana_preview/delete_campana_template.html"

    def get_success_url(self):
        return reverse("campana_preview_template_list")


class CampanaPreviewDeleteView(CampanaManualDeleteView):
    """
    Esta vista se encarga de la eliminación de una campana
    """
    model = Campana
    template_name = 'campanas/campana_preview/delete_campana.html'

    def get_success_url(self):
        return reverse('campana_preview_list')


class CampanaPreviewListView(CampanaManualListView):
    """
    Vista que lista las campañas preview
    """
    template_name = 'campanas/campana_preview/campana_list.html'

    def _get_campanas(self):
        return Campana.objects.obtener_campanas_preview()

    def get_context_data(self, **kwargs):
        context = super(CampanaPreviewListView, self).get_context_data(**kwargs)
        context['finalizadas'] = context['campanas'].filter(estado=Campana.ESTADO_FINALIZADA)
        context['finalizadas'] = context['finalizadas'].order_by("-id")
        context['mostrar_ocultas_tipo'] = "mostrar_campanas_preview_ocultas()"
        return context


class CampanaPreviewBorradasListView(CampanaPreviewListView):
    """
    Vista que lista las campañas preview pero de incluyendo las borradas ocultas
    """

    template_name = 'campanas/campana_preview/campanas_borradas.html'

    def get_context_data(self, **kwargs):
        context = super(CampanaPreviewBorradasListView, self).get_context_data(**kwargs)
        context['borradas'] = context['campanas'].filter(estado=Campana.ESTADO_BORRADA)
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return super(CampanaPreviewBorradasListView, self).get(request, *args, **kwargs)
        else:
            return JsonResponse({'result': 'desconectado'})


class CampanaPreviewSupervisorUpdateView(CampanaSupervisorUpdateView):
    """
    Esta vista agrega supervisores a una campana
    """

    def get_success_url(self):
        return reverse('campana_preview_list')

    def _get_redirecccion_campana_erronea(self):
        return redirect('campana_preview_list')


def campana_mostrar_ocultar_view(request, *args, **kwargs):
    """
    Cambia el atributo 'oculto' de la campaña hacia el valor opuesto (muestra/oculta)
    """
    pk = kwargs.get('pk_campana')
    campana = get_object_or_404(Campana, pk=pk)
    campana.oculto = not campana.oculto
    campana.save()
    return JsonResponse({'result': 'Ok'})


class CampanaPreviewContactosAsignados(TemplateView):
    """
    Vista que muestra todos los contactos asignados a algun agente.
    """
    template_name = "campanas/campana_preview/contactos_asignados.html"

    def dispatch(self, request, *args, **kwargs):
        # TODO: Permisos - Verificar que el supervisor tiene acceso a la campaña
        pk_campana = kwargs.get('pk_campana')
        self.campana = Campana.objects.get(id=pk_campana)
        return super(CampanaPreviewContactosAsignados, self).dispatch(request, *args, **kwargs)

    def datos_de_agentes_en_contacto(self):
        agentes_en_contacto = AgenteEnContacto.objects.filter(
            campana_id=self.campana.id, estado=AgenteEnContacto.ESTADO_ASIGNADO)

        contactos = Contacto.objects.filter(
            id__in=agentes_en_contacto.values_list('contacto_id', flat=True))
        contactos = dict([(x.id, x) for x in contactos])

        agentes = AgenteProfile.objects.filter(
            id__in=agentes_en_contacto.values_list('agente_id', flat=True)).select_related('user')
        agentes = dict([(x.id, x) for x in agentes])

        for agente in agentes_en_contacto:
            agente.agente = agentes[agente.agente_id]
            agente.contacto = contactos[agente.contacto_id]

        return agentes_en_contacto

    def get_context_data(self, pk_campana, **kwargs):
        context = super(CampanaPreviewContactosAsignados, self).get_context_data(**kwargs)
        context['campana'] = self.campana
        context['agentes'] = self.campana.obtener_agentes()
        context['agentes_en_contacto'] = self.datos_de_agentes_en_contacto()
        return context


class LiberarReservarContactoAsignado(View):
    """
    Libera un contacto Asignado en AgenteEnContacto
    """
    def _liberar_contacto(self, contacto_id, campana_id, agente_id):

        entregado_asignado = AgenteEnContacto.objects.filter(estado__in=[
            AgenteEnContacto.ESTADO_ENTREGADO, AgenteEnContacto.ESTADO_ASIGNADO],
            agente_id=agente_id, campana_id=campana_id, contacto_id=contacto_id)
        reservado = AgenteEnContacto.objects.filter(estado=AgenteEnContacto.ESTADO_INICIAL,
                                                    agente_id=agente_id, campana_id=campana_id,
                                                    contacto_id=contacto_id)
        finalizado = AgenteEnContacto.objects.filter(
            contacto_id=contacto_id, campana_id=campana_id,
            estado=AgenteEnContacto.ESTADO_FINALIZADO)
        if finalizado.exists():
            status = 'finalizado'
            return status
        else:
            if entregado_asignado.exists():
                contacto_por_liberar = entregado_asignado.first()
                contacto_por_liberar.agente_id = -1
                contacto_por_liberar.estado = AgenteEnContacto.ESTADO_INICIAL
                contacto_por_liberar.save()

            if reservado.exists():
                contacto_por_liberar = reservado.first()
                contacto_por_liberar.agente_id = -1
                contacto_por_liberar.save()

        status = 'liberado'  # El contacto ya esta liberado
        return status

    def _reservar_contacto(self, contacto_id, campana_id, id_agente):
        finalizado = AgenteEnContacto.objects.filter(
            contacto_id=contacto_id, campana_id=campana_id,
            estado=AgenteEnContacto.ESTADO_FINALIZADO)
        contacto_esta_reservado = AgenteEnContacto.objects.filter(
            contacto_id=contacto_id, campana_id=campana_id).first()
        contacto_liberado = AgenteEnContacto.objects.activos(
            campana_id=campana_id).filter(agente_id=-1,
                                          estado=AgenteEnContacto.ESTADO_INICIAL,
                                          campana_id=campana_id, contacto_id=contacto_id)

        if finalizado.exists():
            status = 'finalizado'
            return status
        else:

            # Cuando el contacto esta liberado
            if contacto_liberado.exists():
                contacto_por_asignar = contacto_liberado.first()
                contacto_por_asignar.agente_id = id_agente
                contacto_por_asignar.save()

            if contacto_esta_reservado.agente_id != id_agente:
                contacto_reservado = AgenteEnContacto.objects.get(campana_id=campana_id,
                                                                  contacto_id=contacto_id)
                # si el contacto esta reservado por otro agente, se lo asigna al nuevo agente
                contacto_reservado.agente_id = id_agente
                # se reservar el contacto, poniendolo en estado inicial
                contacto_reservado.estado = AgenteEnContacto.ESTADO_INICIAL
                contacto_reservado.save()

            status = 'reservado'
            return status

    def post(self, request, *args, **kwargs):
        # TODO: Validar que el supervisor tiene permisos sobre la campaña
        campana_id = json.loads(request.POST.get('campana_id'))
        id_agente = json.loads(request.POST.get('id_agente'))
        accion = request.POST.get('accion')
        contacts_selected = json.loads(request.POST.get('contacts_selected'))
        if accion == 'liberar':
            contactos_liberados = ''
            contactos_finalizados = ''
            for contacto in contacts_selected:
                status = self._liberar_contacto(contacto, campana_id, id_agente)

                if status == 'liberado':
                    contactos_liberados = str(contacto) + ', ' + contactos_liberados
                if status == 'finalizado':
                    contactos_finalizados = str(contacto) + ', ' + contactos_finalizados

            if contactos_liberados:
                message = _(u'Se han liberado los contactos con los siguientes ID: '
                            ) + contactos_liberados
                messages.success(self.request, message)
            if contactos_finalizados:
                message = _(u'Se encuentran finalizados los contactos con los siguientes ID: '
                            ) + contactos_finalizados
                messages.warning(self.request, message)
        if accion == 'reservar':
            contactos_reservados = ''
            contactos_finalizados = ''
            for contacto in contacts_selected:
                status = self._reservar_contacto(contacto, campana_id, id_agente)

                if status == 'reservado':
                    contactos_reservados = str(contacto) + ', ' + contactos_reservados
                if status == 'finalizado':
                    contactos_finalizados = str(contacto) + ', ' + contactos_finalizados
            if contactos_reservados:
                message = _(u'Se han reservado los contactos con los siguientes ID: '
                            ) + contactos_reservados
                messages.success(self.request, message)
            if contactos_finalizados:
                message = _(u'Se encuentran finalizados los contactos con los siguientes ID: '
                            ) + contactos_finalizados
                messages.warning(self.request, message)

        return HttpResponseRedirect(reverse('contactos_preview_asignados', args=[campana_id]))


def campana_validar_contacto_asignado_view(request, *args, **kwargs):
    """
    Valida si un contacto sigue asignado al agente que quiere llamarlo
    """
    campana_id = request.POST.get('pk_campana')
    contacto_id = request.POST.get('pk_contacto')
    agente = request.user.get_agente_profile()
    obligar_calificacion = agente.grupo.obligar_calificacion
    asignado = AgenteEnContacto.objects.esta_asignado_o_entregado_a_agente(contacto_id, campana_id,
                                                                           agente.id)
    return JsonResponse({'contacto_asignado': asignado,
                         'obligar_calificacion': obligar_calificacion})


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
            self.agente = agente_profile
            return super(ObtenerContactoView, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied

    def post(self, request, *args, **kwargs):
        campana_id = kwargs.get('pk_campana', False)
        data_entrega = AgenteEnContacto.entregar_contacto(self.agente, campana_id)
        # adiciona informacion sobre si este contacto tiene una calificacion pendiente
        # para el agente en cuestión
        redis_connection = redis.Redis(
            host=settings.REDIS_HOSTNAME, port=settings.CONSTANCE_REDIS_CONNECTION['port'],
            decode_responses=True)
        calificacion_pendiente_agente = redis_connection.hgetall(
            'OML:CALIFICACION:LLAMADA:{0}'.format(self.agente.pk))
        if calificacion_pendiente_agente != {} and \
           calificacion_pendiente_agente.get('TELEFONO', '') == data_entrega.get(
               'telefono_contacto', False):
            data_entrega['calldata'] = calificacion_pendiente_agente['CALLDATA']
        return JsonResponse(data_entrega)


class AgenteEnContactoResourceExport(resources.ModelResource):

    class Meta:
        model = AgenteEnContacto
        fields = ('id', 'agente_id', 'contacto_id', 'telefono_contacto', 'datos_contacto')
        export_order = ('id', 'agente_id', 'contacto_id', 'telefono_contacto', 'datos_contacto')


class AgenteEnContactoResourceImport(resources.ModelResource):

    def before_import_row(self, row, **kwargs):
        telefono_contacto = row.get('phone')
        agente_id = row.get('agent_id')
        contacto_id = row.get('contact_id')
        nombres_columnas_datos = kwargs.get('nombres_columnas_datos')
        datos_contacto = {}
        for columna in nombres_columnas_datos:
            datos_contacto[columna] = row[columna]
        row['agente_id'] = agente_id
        row['contacto_id'] = contacto_id
        row['telefono_contacto'] = telefono_contacto
        row['datos_contacto'] = json.dumps(datos_contacto)

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        orden_datos = [str(i) for i in range(1, len(dataset) + 1)]
        dataset.append_col(orden_datos, header='orden')

    class Meta:
        model = AgenteEnContacto
        fields = ('id', 'agente_id', 'contacto_id', 'telefono_contacto', 'datos_contacto', 'orden')
        export_order = (
            'id', 'agente_id', 'contacto_id', 'telefono_contacto', 'datos_contacto', 'orden')


class ActualizarContactosResourceExport(resources.ModelResource):

    class Meta:
        model = AgenteEnContacto
        fields = ('id', 'contacto_id', 'telefono_contacto', 'datos_contacto')
        export_order = ('id', 'contacto_id', 'telefono_contacto', 'datos_contacto')


class ActualizarContactosBDResourceImport(resources.ModelResource):
    """ Atención: clase muy acoplada a como se guardan los datos en el modelo Contacto
                  según la lógica de MetadataBaseDatosContactoDTO """

    def before_import_row(self, row, **kwargs):
        row['id'] = row['contacto_id']

    def import_obj(self, instance, row, dry_run, **kwargs):
        """ Actualizar en "row" los nuevos datos a guardar en instance """
        try:
            nombre_campo_telefono = kwargs.get('nombre_campo_telefono')
            index_campos_a_actualizar = kwargs.get('index_campos_a_actualizar')
            read_row = row

            # Tomo los datos viejos de la instancia
            telefono = instance.telefono
            datos = json.loads(instance.datos)

            for campo in index_campos_a_actualizar:
                if campo == nombre_campo_telefono:
                    # Actualizo el campo telefónico si corresponde
                    telefono = read_row[nombre_campo_telefono]
                else:
                    # Actualizo los campos de datos correspondientes
                    pos = index_campos_a_actualizar[campo]
                    datos[pos] = read_row[campo]

            row = {
                'id': instance.id,
                'telefono': telefono,
                'datos': json.dumps(datos),
            }
        except Exception as e:
            logger.error(e)
            raise e

        super(ActualizarContactosBDResourceImport, self).import_obj(
            instance, row, dry_run, **kwargs)

    class Meta:
        model = Contacto
        fields = ('id', 'telefono', 'datos')
        export_order = ('id', 'telefono', 'datos')


class ActualizarContactosResourceImport(resources.ModelResource):

    def import_obj(self, instance, row, dry_run, **kwargs):
        """ Actualizar en "row" los nuevos datos a guardar en instance """
        try:

            campos_a_actualizar = kwargs.get('campos_a_actualizar')
            nombre_campo_telefono = kwargs.get('nombre_campo_telefono')
            read_row = row

            # Tomo los datos viejos de la instancia
            telefono = instance.telefono_contacto
            datos_contacto = json.loads(instance.datos_contacto)

            for campo in campos_a_actualizar:
                if campo == nombre_campo_telefono:
                    # Actualizo el campo telefónico si corresponde
                    telefono = read_row[nombre_campo_telefono]
                else:
                    # Actualizo los campos de datos correspondientes
                    datos_contacto[campo] = read_row[campo]

            row = {
                'id': instance.id,
                'telefono_contacto': telefono,
                'datos_contacto': json.dumps(datos_contacto)
            }
        except Exception as e:
            logger.error(e)
            raise e

        super(ActualizarContactosResourceImport, self).import_obj(
            instance, row, dry_run, **kwargs)

    class Meta:
        model = AgenteEnContacto
        fields = ('id', 'telefono_contacto', 'datos_contacto')
        export_order = (
            'id', 'telefono_contacto', 'datos_contacto')


class ActualizarContactosView(FormView):
    """Vista que permite al supervisor actualizar los datos de los contactos que
    seran entregados a los agentes"""
    template_name = 'campanas/campana_preview/actualizar_contactos.html'

    form_class = ActualizarContactosPreviewForm

    def get_success_url(self):
        pk_campana = self.kwargs.get('pk_campana')
        return reverse("actualizar_contactos_preview",
                       kwargs={'pk_campana': pk_campana})

    def get_initial(self):
        initial = super().get_initial()
        initial['campana'] = Campana.objects.get(pk=self.kwargs.get('pk_campana'))
        return initial

    def get_context_data(self, **kwargs):
        pk_campana = self.kwargs.get('pk_campana')
        campana = Campana.objects.get(pk=pk_campana)
        context = super(ActualizarContactosView, self).get_context_data(**kwargs)
        context['campana'] = campana
        return context

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        csv_file = cleaned_data['csv_actualizaciones_contactos']
        campos_a_actualizar = cleaned_data['campos_a_actualizar']
        pk_campana = self.kwargs.get('pk_campana')

        campana = Campana.objects.get(pk=pk_campana)
        metadata_bd = campana.bd_contacto.get_metadata()
        nombre_campo_telefono = metadata_bd.nombre_campo_telefono
        # Voy a necesitar las posiciones de los campos en los "datos" del Contacto
        index_campos_a_actualizar = {}
        for campo in campos_a_actualizar:
            pos = -1
            if campo != nombre_campo_telefono:
                pos = metadata_bd.nombres_de_columnas_de_datos.index(campo)
            index_campos_a_actualizar[campo] = pos

        # import file
        agents_in_contacts_dat = csv_file.read()
        # we need the id in the columns
        imported_data = tablib.Dataset().load(agents_in_contacts_dat.decode('utf8'), format='csv')
        result_agente_en_contactos = ActualizarContactosResourceImport().import_data(
            imported_data, campos_a_actualizar=campos_a_actualizar,
            nombre_campo_telefono=nombre_campo_telefono,
            dry_run=False)
        result_contactos = ActualizarContactosBDResourceImport().import_data(
            imported_data, index_campos_a_actualizar=index_campos_a_actualizar,
            nombre_campo_telefono=nombre_campo_telefono,
            dry_run=False)
        if not result_agente_en_contactos.has_errors() and not result_contactos.has_errors():
            message = _('Se ha realizado la importación con éxito.')
            messages.success(self.request, message)
        else:
            message = _('Hubo un error al importar el archivo de status de contactos')
            logger.error(
                'Error al importar el archivo de status de contactos en campana {0}'.format(
                    campana))
            messages.error(self.request, message)
        return super(ActualizarContactosView, self).form_valid(form)


class OrdenarAsignacionContactosView(FormView):
    """Vista que permite al supervisor reordenar el orden en que seran entregados
    los contactos a los agentes"""
    template_name = 'campanas/campana_preview/ordenar_asignacion_contactos.html'

    form_class = OrdenarAsignacionContactosForm

    def get_success_url(self):
        pk_campana = self.kwargs.get('pk_campana')
        return reverse("ordenar_entrega_contactos_preview",
                       kwargs={'pk_campana': pk_campana})

    def get_context_data(self, **kwargs):
        pk_campana = self.kwargs.get('pk_campana')
        campana = Campana.objects.get(pk=pk_campana)
        context = super(OrdenarAsignacionContactosView, self).get_context_data(**kwargs)
        context['campana'] = campana
        campana_form = CampanaPreviewCampoDesactivacion(instance=campana)
        context['campana_form'] = campana_form
        return context

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        campo_desactivacion = cleaned_data['campo_desactivacion']
        csv_file = cleaned_data['agentes_en_contactos_ordenados']
        pk_campana = self.kwargs.get('pk_campana')

        # salvamos la eleccion del campo de desactivacion
        campana = Campana.objects.get(pk=pk_campana)
        campana.campo_desactivacion = campo_desactivacion
        campana.save()

        bd_contacto = campana.bd_contacto
        nombres_columnas_datos = bd_contacto.get_metadata().nombres_de_columnas_de_datos
        # import file
        agents_in_contacts_dat = csv_file.read()
        imported_data = tablib.Dataset().load(agents_in_contacts_dat.decode('utf8'), format='csv')
        result = AgenteEnContactoResourceImport().import_data(
            imported_data, nombres_columnas_datos=nombres_columnas_datos, dry_run=False)
        if not result.has_errors():
            message = _('Se ha realizado la importación con éxito.')
            messages.success(self.request, message)
        else:
            message = _('Hubo un error al importar el archivo de status de contactos')
            logger.error(
                'Error al importar el archivo de status de contactos en campana {0}'.format(
                    campana))
            messages.error(self.request, message)
        return super(OrdenarAsignacionContactosView, self).form_valid(form)


class DescargarOrdenAgentesEnContactosView(View):
    """Vista que genera y descarga un archivo .csv con el orden actual de los contactos
    aún no entregados a los agentes
    """
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        pk_campana = kwargs.get('pk_campana')
        campo_desactivacion = request.POST.get('campoDesactivacionExport')

        # salvamos la eleccion del campo de desactivacion
        campana = Campana.objects.get(pk=pk_campana)
        campana.campo_desactivacion = campo_desactivacion
        campana.save()

        bd_contacto = campana.bd_contacto
        nombres_columnas_datos = bd_contacto.get_metadata().nombres_de_columnas_de_datos
        response = HttpResponse(content_type='text/csv')
        content_disposition = 'attachment; filename="agents-contacs-campaign-{0}.csv"'.format(
            pk_campana)
        response['Content-Disposition'] = content_disposition
        agentes_en_contacto_qs = AgenteEnContacto.objects.filter(
            campana_id=pk_campana,
            estado__in=[AgenteEnContacto.ESTADO_ENTREGADO, AgenteEnContacto.ESTADO_INICIAL])
        dataset = AgenteEnContactoResourceExport().export(agentes_en_contacto_qs)
        writer = csv.writer(response)
        columnas_headers = ['id', 'agent_id', 'contact_id', 'phone'] + nombres_columnas_datos
        writer.writerow(columnas_headers)

        for row in dataset:
            datos_contacto = json.loads(row[-1])
            row = row[:-1]
            for nombre_columna in nombres_columnas_datos:
                row = row + (datos_contacto[nombre_columna],)
            writer.writerow(row)
        return response


class DescargarDatosContactosView(View):
    """Vista que genera y descarga un archivo .csv con los datos de los contactos"""
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        pk_campana = kwargs.get('pk_campana')
        campana = Campana.objects.get(pk=pk_campana)

        bd_contacto = campana.bd_contacto
        metadata = bd_contacto.get_metadata()
        nombre_campo_telefono = metadata.nombre_campo_telefono
        nombres_columnas_datos = metadata.nombres_de_columnas_de_datos
        response = HttpResponse(content_type='text/csv')
        content_disposition = 'attachment; filename="agents-contacts-campaign-data-{0}.csv"'.format(
            pk_campana)
        response['Content-Disposition'] = content_disposition
        agentes_en_contacto_qs = AgenteEnContacto.objects.filter(
            campana_id=pk_campana)
        dataset = ActualizarContactosResourceExport().export(agentes_en_contacto_qs)
        writer = csv.writer(response)
        writer.writerow(['id', 'contacto_id', nombre_campo_telefono] + nombres_columnas_datos)

        for row in dataset:
            datos_contacto = json.loads(row[-1])
            row = row[:-1]
            for nombre_columna in nombres_columnas_datos:
                row = row + (datos_contacto[nombre_columna],)
            writer.writerow(row)
        return response
