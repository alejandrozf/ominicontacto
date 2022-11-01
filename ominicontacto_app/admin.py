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
from django.contrib import admin
from django.contrib.auth.models import Group
from ominicontacto_app.models import AgenteProfile, AgenteEnContacto


admin.site.unregister(Group)


@admin.register(AgenteProfile)
class AgenteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user_id'
    )


@admin.register(AgenteEnContacto)
class AgenteEnContactoAdmin(admin.ModelAdmin):
    list_display = (
        'contacto_id',
        'agente_id',
        'campana_id',
        'telefono_contacto',
        'datos_contacto',
        'estado',
        'orden'
    )

    list_filter = (
        'agente_id',
        'campana_id',
    )
