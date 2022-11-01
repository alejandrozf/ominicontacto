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
import django
from django.utils.translation import gettext_lazy as _


class Config(django.apps.AppConfig):

    name = "notification_app.message"

    verbose_name = "NotificationMessage"

    def configuraciones_de_permisos(self):
        return [
            {
                "nombre": "notification-message--emsg-list",
                "roles": [
                    "Administrador",
                ]
            },
            {
                "nombre": "notification-message--emsg-detail",
                "roles": [
                    "Administrador",
                ]
            },
        ]

    informacion_de_permisos = {
        "notification-message--emsg-list": {
            "descripcion": _("Lista de los mensajes de correos que el sistema soporta"),
            "version": ""
        },
        "notification-message--emsg-detail": {
            "descripcion": _("Obtiene detalle de un mensaje de correo"),
            "version": ""
        },
    }
