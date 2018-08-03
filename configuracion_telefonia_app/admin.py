# -*- coding: utf-8 -*-
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
