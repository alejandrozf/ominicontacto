# -*- coding: utf-8 -*-
from django.contrib import admin

from configuracion_telefonia_app.models import DestinoEntrante, OpcionDestino


@admin.register(DestinoEntrante)
class RutaEntranteAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        qs = super(RutaEntranteAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)

@admin.register(OpcionDestino)
class OpcionDestino(admin.ModelAdmin):
    pass
