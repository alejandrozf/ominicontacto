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

import os

from django.urls import resolve
from django.conf import settings
from django.forms import ValidationError
from django.utils.translation import gettext as _

from ominicontacto_app.errors import OmlArchivoImportacionInvalidoError
from ominicontacto_app.models import CalificacionCliente

from ominicontacto_app.services.asterisk.supervisor_activity import SupervisorActivityAmiManager


def validar_extension_archivo_audio(valor):
    if valor is not None and not valor.name.endswith('.wav'):
        raise ValidationError(_('Archivos permitidos: .wav'), code='invalid')


def obtener_cantidad_no_calificados(total_llamadas_qs, fecha_desde, fecha_hasta, campana):
    total_llamadas_campanas = total_llamadas_qs.count()
    total_calificados = CalificacionCliente.history.filter(
        history_date__range=(fecha_desde, fecha_hasta),
        opcion_calificacion__campana=campana, history_change_reason='calificacion').count()
    total_atendidas_sin_calificacion = total_llamadas_campanas - total_calificados
    if total_atendidas_sin_calificacion < 0:
        # significa que el agente calificó llamadas que no conectaron con el usuario
        total_atendidas_sin_calificacion = 0
    return total_atendidas_sin_calificacion


def validar_estructura_csv(data_csv_memory, err_message, logger):
    """Analiza si un archivo con extensión .csv tiene una estructura válida"""
    # chequea que el csv tenga un formato estándar de base de contactos o black list o
    # así podemos descartar archivos csv corruptos
    for i, row in enumerate(data_csv_memory):
        # controlamos que el primer valor sea numérico, como campo teléfonico
        try:
            if i > 0:
                int(row[0])
        except Exception as e:
            logger.warn("Error: {0}".format(e))
            raise(OmlArchivoImportacionInvalidoError(err_message))


def obtener_sip_agentes_sesiones_activas():
    # TODO: Controlar cantidad de conexiones a Asterisk con AMIManagerConnector
    agentes_activos_service = SupervisorActivityAmiManager()
    agentes = list(agentes_activos_service.obtener_agentes_activos())
    sips_agentes = []
    for agente in agentes:
        if agente['status'] != 'OFFLINE':
            sips_agentes.append(int(agente['sip']))
    return sips_agentes


interface = os.popen("ip route list | awk '/^default/ {print $5}'").read().strip("\n")


def adicionar_render_unicode(pygal_object):
    """Adiciona metodo que llama al metodo render
    del objeto de pygal con argumento que permite renderizarlo
    con cadenas en formato unicode
    """
    render = pygal_object.render

    def render_unicode():
        return render(disable_xml_declaration=True)

    pygal_object.render_unicode = render_unicode
    return pygal_object


def request_url_name(request):
    resolver = resolve(request.path_info)
    return resolver.url_name


def obtener_request_host_port(request):
    host = request.META['HTTP_HOST']
    port = request.META['HTTP_X_FORWARDED_PORT']

    if ':' in host:
        host_split = host.split(':')
        host = host_split[0]
        port = host_split[1]
    return host, port


def crear_grabaciones_url(host, port):
    """Obtiene la URL para acceder a las grabaciones, dependiendo de lo que reciba del
    proxy nginx"""
    grabaciones_url = "https://{0}:{1}/grabaciones".format(host, port)
    return grabaciones_url


def obtener_paginas(context, range_size):
    if not context.get('is_paginated', False):
        return context
    paginator = context.get('paginator')
    num_pages = paginator.num_pages
    current_page = context.get('page_obj')
    page_no = current_page.number
    if num_pages <= range_size or page_no <= int((range_size + 1) / 2):  # case 1 and 2
        pages = [x for x in range(1, min(num_pages + 1, range_size + 1))]
    elif page_no > num_pages - int((range_size + 1) / 2):  # case 4
        pages = [x for x in range(num_pages - (range_size - 1), num_pages + 1)]
    else:  # case 3
        pages = [x for x in range(
            page_no - int((range_size + 1) / 2 - 1),
            page_no + int((range_size + 1) / 2))]
    context.update({'pages': pages})


class AddSettingsContextMixin(object):

    def get_context_data(self, *args, **kwargs):
        context = super(AddSettingsContextMixin, self).get_context_data(*args, **kwargs)
        host, port = obtener_request_host_port(self.request)
        context['KAMAILIO_HOSTNAME'] = settings.KAMAILIO_HOSTNAME
        context['NGINX_HOSTNAME'] = host
        context['EXTERNAL_PORT'] = port
        context['GRABACIONES_URL'] = crear_grabaciones_url(host, port)
        return context
