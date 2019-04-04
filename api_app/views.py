# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re
import logging as _logging

from asterisk.manager import Manager, ManagerSocketException, ManagerAuthException, ManagerException

from django.conf import settings
from django.http import JsonResponse
from django.views.generic import View

from rest_framework import viewsets
from rest_framework.permissions import BasePermission, IsAuthenticated

from api_app.serializers import CampanaSerializer, AgenteProfileSerializer

from ominicontacto_app.models import Campana, AgenteProfile
from reportes_app.reportes.reporte_llamadas_supervision import (
    ReporteDeLLamadasEntrantesDeSupervision, ReporteDeLLamadasSalientesDeSupervision
)

logger = _logging.getLogger(__name__)


class EsSupervisorPermiso(BasePermission):
    """Permiso para aplicar a vistas solo para supervisores"""

    def has_permission(self, request, view):
        super(EsSupervisorPermiso, self).has_permission(request, view)
        superv_profile = request.user.get_supervisor_profile()
        return superv_profile is not None


class EsAdminPermiso(BasePermission):
    """Permiso para aplicar a vistas solo para administradores"""

    def has_permission(self, request, view):
        super(EsAdminPermiso, self).has_permission(request, view)
        return request.user.get_is_administrador()


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


class AgentesActivosGrupoViewSet(viewsets.ModelViewSet):
    """Servicio que devuelve las agentes activos de un grupo
    """
    serializer_class = AgenteProfileSerializer
    permission_classes = (IsAuthenticated, EsAdminPermiso,)

    def get_queryset(self):
        queryset = AgenteProfile.objects.obtener_activos()
        grupo_pk = self.kwargs.get('pk_grupo')
        queryset = queryset.filter(grupo__pk=grupo_pk)
        return queryset


class StatusCampanasEntrantesView(View):
    def get(self, request):
        reporte = ReporteDeLLamadasEntrantesDeSupervision(request.user)
        return JsonResponse({'errors': None,
                             'data': reporte.estadisticas})


class StatusCampanasSalientesView(View):
    def get(self, request):
        reporte = ReporteDeLLamadasSalientesDeSupervision(request.user)
        return JsonResponse({'errors': None,
                             'data': reporte.estadisticas})


class AgentesStatusAPIView(View):
    """Devuelve información de los agentes en el sistema"""

    headers_agente_regex = re.compile(r'.*(NAME|SIP|STATUS).*')
    id_agente = re.compile(r'[1-9][0-9]*')

    def _ami_obtener_agentes(self, manager):
        return manager.command("database show OML/AGENT").data

    def _parsear_datos_agentes_pasada_1(self, datos):
        # para filtrar entradas que no nos interesan, como ids de pausas
        lineas = datos.split('\n')
        lineas_result = []
        for linea in lineas:
            try:
                clave, valor = linea.split(': ')
            except ValueError:
                pass
            else:
                if self.headers_agente_regex.match(clave) is not None:
                    lineas_result.append((clave.strip(), valor.strip()))
        return lineas_result

    def _parsear_datos_agentes_pasada_2(self, datos):
        # para obtener las entradas de los agentes agrupados en una lista de diccionarios
        agentes_activos = []
        for i in xrange(0, len(datos), 3):
            sip_agente = datos[i + 1][1]
            status_agente = datos[i + 2][1]
            try:
                nombre_status, timestamp = status_agente.split(':')
            except ValueError:
                pass
            else:
                nombre_agente = datos[i][1]
                id_agente = self.id_agente.search(datos[i][0]).group(0)
                agente = {
                    'nombre': nombre_agente,
                    'id': id_agente,
                    'status': nombre_status,
                    'timestamp': timestamp,
                    'sip': sip_agente,
                }
                agentes_activos.append(agente)
        return agentes_activos

    def _obtener_agentes_activos_ami(self):
        manager = Manager()
        ami_manager_user = settings.ASTERISK['AMI_USERNAME']
        ami_manager_pass = settings.ASTERISK['AMI_PASSWORD']
        ami_manager_host = str(settings.OML_ASTERISK_HOSTNAME.replace('root@', ''))
        agentes_activos = []
        try:
            manager.connect(ami_manager_host)
            manager.login(ami_manager_user, ami_manager_pass)
            agentes_activos_raw = self._parsear_datos_agentes_pasada_1(
                self._ami_obtener_agentes(manager))
            agentes_activos = self._parsear_datos_agentes_pasada_2(agentes_activos_raw)
        except ManagerSocketException as e:
            logger.exception("Error connecting to the manager: {0}".format(e.message))
        except ManagerAuthException as e:
            logger.exception("Error logging in to the manager: {0}".format(e.message))
        except ManagerException as e:
            logger.exception("Error {0}".format(e.message))
        finally:
            manager.close()
            return agentes_activos

    def _obtener_agentes_activos(self):
        return self._obtener_agentes_ami()

    def get(self, request):
        agentes_activos = self._obtener_agentes_activos_ami()
        return JsonResponse(data={'agentes': list(agentes_activos)})
