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

"""
Aca se encuentran las vistas relacionada con las grabaciones en cuanto a su busqueda
ya que el insert lo hace kamailio-debian/asterisk(hablar con fabian como hace el insert )
"""

from __future__ import unicode_literals

from django.utils.translation import gettext as _
from django.utils import timezone
from django.db.models import Q

from django.views.generic import FormView, View
from django.core import paginator as django_paginator
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied

from ominicontacto_app.forms import GrabacionBusquedaForm, GrabacionBusquedaSupervisorForm
from ominicontacto_app.models import (
    GrabacionMarca, Campana, CalificacionCliente, OpcionCalificacion)
from .utiles import convert_fecha_datetime, fecha_local
from reportes_app.models import LlamadaLog


class BusquedaGrabacionFormView(FormView):
    """Vista abstracta para subclasear para agente o supervisor"""

    def get_context_data(self, **kwargs):
        context = super(BusquedaGrabacionFormView, self).get_context_data(
            **kwargs)
        listado_de_grabaciones = []

        if 'listado_de_grabaciones' in context:
            listado_de_grabaciones = context['listado_de_grabaciones']

        qs = listado_de_grabaciones
        # ----- <Paginate> -----
        page = self.kwargs['pagina']
        if 'pagina' in context and context['pagina']:
            page = context['pagina']

        if 'grabaciones_x_pagina' in context:
            grabaciones_x_pagina = context['grabaciones_x_pagina']
        else:
            grabaciones_x_pagina = 10

        result_paginator = django_paginator.Paginator(qs, grabaciones_x_pagina)
        try:
            qs = result_paginator.page(page)
        except django_paginator.PageNotAnInteger:
            qs = result_paginator.page(1)
        except django_paginator.EmptyPage:
            qs = result_paginator.page(result_paginator.num_pages)

        num_pages = result_paginator.num_pages
        page_no = int(page)
        if num_pages <= 7 or page_no <= 4:  # case 1 and 2
            pages = [x for x in range(1, min(num_pages + 1, 8))]
        elif page_no > num_pages - 4:  # case 4
            pages = [x for x in range(num_pages - 6, num_pages + 1)]
        else:  # case 3
            pages = [x for x in range(page_no - 3, page_no + 4)]
        context.update({'pages': pages})
        # ----- </Paginate> -----
        context['listado_de_grabaciones'] = qs

        context['calificaciones'] = self._get_calificaciones(qs)
        context['base_url'] = "%s://%s" % (self.request.scheme,
                                           self.request.get_host())
        context['user_id'] = self.request.user.id
        return context

    def _get_campanas(self):
        raise NotImplementedError()

    def _get_filtro_agente(self, form):
        raise NotImplementedError()

    def _get_grabaciones_del_dia(self):
        raise NotImplementedError()

    def get(self, request, *args, **kwargs):
        return self.render_to_response(
            self.get_context_data(
                listado_de_grabaciones=self._get_grabaciones_del_dia(),
                pagina=self.kwargs['pagina'],))

    def get_form(self):
        self.form_class = self.get_form_class()
        campanas = self._get_campanas()
        campana_choice = []
        for campana in campanas:
            nombre = campana.nombre
            if campana.estado == Campana.ESTADO_BORRADA:
                nombre = nombre + " (%s)" % _('Borrada')
            campana_choice.append((campana.pk, nombre))
        return self.form_class(campana_choice=campana_choice, **self.get_form_kwargs())

    def form_valid(self, form):
        fecha = form.cleaned_data.get('fecha')
        if fecha:
            fecha_desde, fecha_hasta = fecha.split('-')
            fecha_desde = convert_fecha_datetime(fecha_desde)
            fecha_hasta = convert_fecha_datetime(fecha_hasta)
        else:
            fecha_desde = ''
            fecha_hasta = ''
        tipo_llamada = form.cleaned_data.get('tipo_llamada')
        tel_cliente = form.cleaned_data.get('tel_cliente')
        callid = form.cleaned_data.get('callid')
        id_contacto_externo = form.cleaned_data.get('id_contacto_externo')
        agente = self._get_filtro_agente(form)
        campana = form.cleaned_data.get('campana')
        marcadas = form.cleaned_data.get('marcadas', False)
        duracion = form.cleaned_data.get('duracion', 0)
        gestion = form.cleaned_data.get('gestion', False)
        campanas = self._get_campanas()
        nombre_calificacion = form.cleaned_data.get('calificacion', None)
        calificaciones = OpcionCalificacion.objects.filter(nombre=nombre_calificacion)\
                                                   .values_list('id', flat=True)
        pagina = form.cleaned_data.get('pagina')
        grabaciones_x_pagina = form.cleaned_data.get('grabaciones_x_pagina')
        listado_de_grabaciones = self._get_grabaciones_por_filtro(fecha_desde, fecha_hasta,
                                                                  tipo_llamada, tel_cliente,
                                                                  callid, id_contacto_externo,
                                                                  agente, campana, campanas,
                                                                  marcadas, duracion, gestion,
                                                                  calificaciones)

        return self.render_to_response(self.get_context_data(
            listado_de_grabaciones=listado_de_grabaciones, pagina=pagina,
            grabaciones_x_pagina=grabaciones_x_pagina))

    def _get_grabaciones_por_filtro(self, fecha_desde, fecha_hasta, tipo_llamada, tel_cliente,
                                    callid, id_contacto_externo, agente, campana, campanas,
                                    marcadas, duracion, gestion, calificaciones):
        return LlamadaLog.objects.obtener_grabaciones_by_filtro(
            fecha_desde, fecha_hasta, tipo_llamada, tel_cliente, callid, id_contacto_externo,
            agente, campana, campanas, marcadas, duracion, gestion, calificaciones)

    def _get_calificaciones(self, grabaciones):
        try:
            identificadores = grabaciones.object_list.values_list(
                'contacto_id', 'campana_id', 'callid')

        except AttributeError:
            identificadores = [(str(a['contacto_id']), a['campana_id'], a['callid'])
                               for a in grabaciones]
        filtro = Q()
        callids = []
        for contacto_id, campana_id, callid in identificadores:
            # Calificaciones si o si tienen contacto y campaña.
            if contacto_id and campana_id and not contacto_id == '-1':
                filtro = filtro | Q(contacto_id=contacto_id,
                                    opcion_calificacion__campana_id=campana_id)
            # Pero si la grabacion no tiene esos datos uso el callid
            else:
                callids.append(callid)
        calificaciones = CalificacionCliente.history.filter(
            filtro | Q(callid__in=callids))
        return calificaciones


class BusquedaGrabacionSupervisorFormView(BusquedaGrabacionFormView):
    form_class = GrabacionBusquedaSupervisorForm
    template_name = 'busqueda_grabacion.html'

    def _get_campanas(self):
        campanas = Campana.objects.all()
        user = self.request.user
        if not user.get_is_administrador():
            supervisor = user.get_supervisor_profile()
            campanas = supervisor.campanas_asignadas()
        return campanas

    def _get_filtro_agente(self, form):
        return form.cleaned_data.get('agente', None)

    def _get_grabaciones_del_dia(self):
        # No muestro grabaciones sin que el usuario envíe parámetros de filtrado
        return []

    def _get_grabaciones_por_filtro(self, fecha_desde, fecha_hasta, tipo_llamada, tel_cliente,
                                    callid, id_contacto_externo, agente, campana, campanas,
                                    marcadas, duracion, gestion, calificaciones):
        logs = LlamadaLog.objects.obtener_grabaciones_by_filtro(
            fecha_desde, fecha_hasta, tipo_llamada, tel_cliente, callid, id_contacto_externo,
            agente, campana, campanas, marcadas, duracion, gestion, calificaciones)

        return self._procesa_formato_transferencias(logs)

    def _procesa_formato_transferencias(self, logs):
        listado_grabaciones = {}
        for grabacion in logs:
            if grabacion.callid not in listado_grabaciones:
                listado_grabaciones[grabacion.callid] = {}
                listado_grabaciones[grabacion.callid]['origen'] = grabacion
                listado_grabaciones[grabacion.callid]['contacto_id'] = grabacion.contacto_id
                listado_grabaciones[grabacion.callid]['campana_id'] = grabacion.campana_id
                listado_grabaciones[grabacion.callid]['callid'] = grabacion.callid
            elif listado_grabaciones[grabacion.callid]['origen'].time > grabacion.time:
                if 'transfer' not in listado_grabaciones[grabacion.callid]:
                    listado_grabaciones[grabacion.callid]['transfer'] = []
                aux = listado_grabaciones[grabacion.callid]['origen']
                listado_grabaciones[grabacion.callid]['origen'] = grabacion
                listado_grabaciones[grabacion.callid]['contacto_id'] = grabacion.contacto_id
                listado_grabaciones[grabacion.callid]['transfer'].append(aux)
                listado_grabaciones[grabacion.callid]['campana_id'] = grabacion.campana_id
            else:
                if 'transfer' not in listado_grabaciones[grabacion.callid]:
                    listado_grabaciones[grabacion.callid]['transfer'] = []
                listado_grabaciones[grabacion.callid]['transfer'].append(grabacion)

        return list(listado_grabaciones.values())


class BusquedaGrabacionAgenteFormView(BusquedaGrabacionFormView):
    form_class = GrabacionBusquedaForm
    template_name = 'agente/frame/busqueda_grabacion.html'

    def _get_campanas(self):
        agente = self.request.user.get_agente_profile()
        campanas_ids = list(
            agente.queue_set.values_list('campana_id', flat=True))
        return Campana.objects.filter(pk__in=campanas_ids) \
            .exclude(estado=Campana.ESTADO_BORRADA)

    def _get_filtro_agente(self, form):
        return self.request.user.get_agente_profile()

    def _get_grabaciones_del_dia(self):
        hoy = fecha_local(timezone.now())
        campanas = self._get_campanas()
        campanas_id = []
        for campana in campanas:
            if campana.estado != Campana.ESTADO_BORRADA:
                campanas_id.append(campana.id)
        grabaciones = LlamadaLog.objects.obtener_grabaciones_by_fecha_intervalo_campanas(
            hoy, hoy, campanas_id)
        return grabaciones.filter(agente_id=self.request.user.get_agente_profile().id)

    def dispatch(self, request, *args, **kwargs):
        agent_profile = request.user.get_agente_profile()
        agent_group = agent_profile.grupo
        if agent_group.acceso_grabaciones_agente:
            return super(BusquedaGrabacionAgenteFormView, self).dispatch(
                request, *args, **kwargs)
        else:
            raise PermissionDenied


class MarcarGrabacionView(View):
    """
    Crea o modifica la descripción de una grabacion existente
    """

    def post(self, *args, **kwargs):
        callid = self.request.POST.get('callid', False)
        descripcion = self.request.POST.get('descripcion', '')
        try:
            grabacion_marca, _ = GrabacionMarca.objects.get_or_create(
                callid=callid)
        except Exception as e:
            return JsonResponse({'result': 'failed by {0}'.format(e)})
        else:
            grabacion_marca.descripcion = descripcion
            grabacion_marca.save()
            return JsonResponse({'result': 'OK'})


class GrabacionDescripcionView(View):
    """
    Obtiene la descripción de una grabación si está marcada
    """

    def get(self, *args, **kwargs):
        callid = kwargs.get('callid', False)
        try:
            grabacion_marca = GrabacionMarca.objects.get(callid=callid)
        except GrabacionMarca.DoesNotExist:
            response = {u'result': _(u'No encontrada'),
                        u'descripcion': _(u'La grabación no tiene descripción asociada')}
        else:
            response = {u'result': _(u'Descripción'),
                        u'descripcion': grabacion_marca.descripcion}
        return JsonResponse(response)
