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

from django.views.generic import FormView
from django.core import paginator as django_paginator

from ominicontacto_app.forms import AuditoriaBusquedaForm
from ominicontacto_app.models import CalificacionCliente

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

        qs = listado_de_calificaciones
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
        telefono = form.cleaned_data.get('telefono')
        callid = form.cleaned_data.get('callid')
        status_auditoria = form.cleaned_data.get('status_auditoria')

        pagina = form.cleaned_data.get('pagina')
        supervisor = self.request.user.get_supervisor_profile()
        campanas_supervisor_ids = list(supervisor.campanas_asignadas_actuales().values_list(
            'pk', flat=True))
        listado_de_calificaciones = CalificacionCliente.objects.calificacion_por_filtro(
            fecha_desde, fecha_hasta, agente, campana, grupo_agente, id_contacto,
            telefono, callid, status_auditoria).filter(
                opcion_calificacion__campana__pk__in=campanas_supervisor_ids)

        return self.render_to_response(self.get_context_data(
            listado_de_calificaciones=listado_de_calificaciones, pagina=pagina))
