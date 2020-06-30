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

import json
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core import paginator as django_paginator
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView

from ominicontacto_app.forms import AuditoriaBusquedaForm, AuditoriaCalificacionForm
from ominicontacto_app.models import CalificacionCliente, Grabacion

from .utiles import convert_fecha_datetime


class AuditarCalificacionesFormView(FormView):
    """Vista que lista las calificaciones de gestion en el sistema
    y permite filtrar de entre ellas tambien por otros criterios"""
    form_class = AuditoriaBusquedaForm
    template_name = 'busqueda_auditorias.html'

    def get_context_data(self, **kwargs):
        context = super(AuditarCalificacionesFormView, self).get_context_data(
            **kwargs)

        listado_de_calificaciones = []
        if 'listado_de_calificaciones' in [key for key in context.keys()]:
            listado_de_calificaciones = context['listado_de_calificaciones']

        qs = listado_de_calificaciones.select_related('opcion_calificacion__campana', 'contacto')
        # ----- <Paginate> -----
        page = self.kwargs['pagina']
        if context.get('pagina', False):
            page = context.get('pagina', False)
        result_paginator = django_paginator.Paginator(qs, 40)
        try:
            qs = result_paginator.page(page)
        except django_paginator.PageNotAnInteger:
            qs = result_paginator.page(1)
        except django_paginator.EmptyPage:
            qs = result_paginator.page(result_paginator.num_pages)
        # ----- </Paginate> -----

        context['calificaciones'] = qs

        return context

    def get(self, request, *args, **kwargs):
        supervisor = request.user.get_supervisor_profile()
        campanas_supervisor_ids = list(supervisor.campanas_asignadas_actuales().values_list(
            'pk', flat=True))
        calificaciones = CalificacionCliente.objects.obtener_calificaciones_auditoria().filter(
            opcion_calificacion__campana__pk__in=campanas_supervisor_ids)
        return self.render_to_response(
            self.get_context_data(
                listado_de_calificaciones=calificaciones,
                pagina=self.kwargs['pagina']))

    def get_form(self):
        supervisor = self.request.user.get_supervisor_profile()
        kwargs = self.get_form_kwargs()
        kwargs.update({'supervisor': supervisor})
        return self.form_class(**kwargs)

    def form_valid(self, form):
        fecha = form.cleaned_data.get('fecha')
        if fecha:
            fecha_desde, fecha_hasta = fecha.split('-')
            fecha_desde = convert_fecha_datetime(fecha_desde)
            fecha_hasta = convert_fecha_datetime(fecha_hasta)
        else:
            fecha_desde = ''
            fecha_hasta = ''

        agente = form.cleaned_data.get('agente')
        campana = form.cleaned_data.get('campana')
        grupo_agente = form.cleaned_data.get('grupo_agente')
        id_contacto = form.cleaned_data.get('id_contacto')
        id_contacto_externo = form.cleaned_data.get('id_contacto_externo')
        telefono = form.cleaned_data.get('telefono')
        callid = form.cleaned_data.get('callid')
        status_auditoria = form.cleaned_data.get('status_auditoria')
        revisadas = form.cleaned_data.get('revisadas')

        pagina = form.cleaned_data.get('pagina')
        supervisor = self.request.user.get_supervisor_profile()
        campanas_supervisor_ids = list(supervisor.campanas_asignadas_actuales().values_list(
            'pk', flat=True))
        listado_de_calificaciones = CalificacionCliente.objects.calificacion_por_filtro(
            fecha_desde, fecha_hasta, agente, campana, grupo_agente, id_contacto,
            id_contacto_externo, telefono, callid, status_auditoria).filter(
                opcion_calificacion__campana__pk__in=campanas_supervisor_ids)
        if revisadas:
            listado_de_calificaciones = listado_de_calificaciones.filter(
                auditoriacalificacion__revisada=True)

        return self.render_to_response(self.get_context_data(
            listado_de_calificaciones=listado_de_calificaciones, pagina=pagina))


class AuditoriaCalificacionFormView(FormView):
    template_name = 'auditoria/crear_editar_auditoria.html'
    form_class = AuditoriaCalificacionForm
    success_url = reverse_lazy('buscar_auditorias_gestion', args=(1,))

    def dispatch(self, request, *args, **kwargs):
        id_calificacion = kwargs['pk_calificacion']
        try:
            calificacion = CalificacionCliente.objects.get(id=id_calificacion)
        except CalificacionCliente.DoesNotExist:
            message = _("Calificación Inexistente")
            messages.warning(self.request, message)
            return HttpResponseRedirect(self.success_url)

        # Verifico que corresponda a una campaña que tenga asociada
        if not request.user.get_is_administrador():
            campana_id = calificacion.opcion_calificacion.campana_id
            if not request.user.campanasupervisors.filter(id=campana_id).exists():
                message = _("No tiene permiso para auditar calificaciones de esta campaña.")
                messages.warning(self.request, message)
                return HttpResponseRedirect(self.success_url)

        self.auditoria = None
        if hasattr(calificacion, 'auditoriacalificacion'):
            self.auditoria = calificacion.auditoriacalificacion
        if not calificacion.es_gestion() and self.auditoria is None:
            message = _("Sólo pueden auditarse calificaciones de gestión.")
            messages.warning(self.request, message)
            return HttpResponseRedirect(self.success_url)

        self.calificacion = calificacion

        return super(AuditoriaCalificacionFormView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AuditoriaCalificacionFormView, self).get_context_data(**kwargs)
        context['calificacion'] = self.calificacion

        # Cargo el historial asociando las grabaciones a la primer calificacion q tenga su callid
        historia = []
        callids = set()
        for historica in self.calificacion.history.all().order_by('history_date'):
            historia.append({'calificacion': historica})
            if historica.callid:
                callids.add(historica.callid)

        grabaciones = Grabacion.objects.filter(callid__in=callids)
        grabaciones_por_callid = {}
        for grabacion in grabaciones:
            grabaciones_por_callid[grabacion.callid] = grabacion

        for historica in historia:
            callid = historica['calificacion'].callid
            if callid in grabaciones_por_callid:
                historica['grabacion'] = grabaciones_por_callid.pop(callid)
        historia.reverse()
        context['historia'] = historia
        context['datos_contacto'] = self.calificacion.contacto.obtener_datos()

        if self.calificacion.respuesta_formulario_gestion.exists():
            respuesta_formulario = self.calificacion.respuesta_formulario_gestion.first()
            context['respuesta_formulario'] = json.loads(respuesta_formulario.metadata)
            historia[0]['mostrar_respuesta'] = True
        return context

    def get_form_kwargs(self):
        kwargs = super(AuditoriaCalificacionFormView, self).get_form_kwargs()
        if self.auditoria is not None:
            kwargs['instance'] = self.auditoria
        return kwargs

    def form_valid(self, form):
        auditoria = form.save(commit=False)
        auditoria.calificacion = self.calificacion
        auditoria.revisada = False
        auditoria.save()
        message = _("Auditoría de calificación guardada.")
        messages.success(self.request, message)
        return HttpResponseRedirect(self.success_url)
