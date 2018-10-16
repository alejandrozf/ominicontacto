# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from rest_framework import viewsets
from rest_framework.permissions import BasePermission, IsAuthenticated

from api_app.serializers import CampanaSerializer

from ominicontacto_app.models import Campana


class EsSupervisorPermiso(BasePermission):
    """Permiso para aplicar a vistas solo para supervisores"""

    def has_permission(self, request, view):
        super(EsSupervisorPermiso, self).has_permission(request, view)
        superv_profile = request.user.get_supervisor_profile()
        return superv_profile is not None


class SupervisorCampanasActivasViewSet(viewsets.ModelViewSet):
    """Servicio que devuelve las campañas activas relacionadas a un supervisor
    si este no es admin y todas las campañas activas en el caso de sí lo sea
    """
    serializer_class = CampanaSerializer
    permission_classes = (IsAuthenticated, EsSupervisorPermiso,)
    queryset = Campana.objects.obtener_activas()

    def get_queryset(self):
        superv_profile = self.request.user.get_supervisor_profile()
        if superv_profile.is_administrador:
            return super(SupervisorCampanasActivasViewSet, self).get_queryset()
        return superv_profile.obtener_campanas_activas_asignadas()
