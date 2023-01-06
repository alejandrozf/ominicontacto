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

from configuracion_telefonia_app.models import (DestinoEntrante, OpcionDestino, IVR,
                                                ValidacionFechaHora, RutaEntrante)


@admin.register(DestinoEntrante)
class DestinoEntranteAdmin(admin.ModelAdmin):
    pass


@admin.register(OpcionDestino)
class OpcionDestinoAdmin(admin.ModelAdmin):
    pass


@admin.register(IVR)
class IVRAdmin(admin.ModelAdmin):
    pass


@admin.register(ValidacionFechaHora)
class ValidacionFechaHoraAdmin(admin.ModelAdmin):
    pass


@admin.register(RutaEntrante)
class RutaEntranteAdmin(admin.ModelAdmin):
    pass
