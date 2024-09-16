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

from django.urls import path
import whatsapp_app.api.v1.proveedor
import whatsapp_app.api.v1.linea
import whatsapp_app.api.v1.destino
import whatsapp_app.api.v1.plantilla_mensaje
import whatsapp_app.api.v1.template_whatsapp
import whatsapp_app.api.v1.campana
import whatsapp_app.api.v1.grupo_plantilla_whatsapp
import whatsapp_app.api.v1.configuracion_whatsapp_campana
import whatsapp_app.api.v1.conversacion
import whatsapp_app.api.v1.transfer
import whatsapp_app.api.v1.contacto
import whatsapp_app.api.v1.calificacion
import whatsapp_app.api.v1.template
import whatsapp_app.api.v1.reporte

from whatsapp_app.api import ViewSetRouter

router = ViewSetRouter(trailing_slash=False)

routes = (
    (r"provider", whatsapp_app.api.v1.proveedor.ViewSet),
    (r"line", whatsapp_app.api.v1.linea.ViewSet),
    (r"destination", whatsapp_app.api.v1.destino.ViewSet),
    (r"templates_message", whatsapp_app.api.v1.plantilla_mensaje.ViewSet),
    (r"templates_whatsapp", whatsapp_app.api.v1.template_whatsapp.ViewSet),
    (r"campaing", whatsapp_app.api.v1.campana.ViewSet),
    (r"group_plantilla_whatsapp", whatsapp_app.api.v1.grupo_plantilla_whatsapp.ViewSet),
    (r"configuration_whatsapp", whatsapp_app.api.v1.configuracion_whatsapp_campana.ViewSet),
    (r"chat", whatsapp_app.api.v1.conversacion.ViewSet),
    (r"transfer", whatsapp_app.api.v1.transfer.ViewSet),
    (r"contact/(?P<campana_pk>[^/.]+)", whatsapp_app.api.v1.contacto.ViewSet),
    (r"disposition_chat", whatsapp_app.api.v1.calificacion.ViewSet),
    (r"templates/(?P<campana_pk>[^/.]+)", whatsapp_app.api.v1.template.ViewSet),
)

for route in routes:
    router.register(*route)

api_urls_v1 = router.urls

api_urls_v1 += [
    path("reports/", whatsapp_app.api.v1.reporte.ReportAPIView.as_view(), name="whatsapp_reports"),
]
