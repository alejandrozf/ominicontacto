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

import threading
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext as _
from django.utils.timezone import now

from rest_framework.authentication import SessionAuthentication
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from constance import config as config_constance

from api_app.authentication import ExpiringTokenAuthentication
from api_app.views.permissions import TienePermisoOML
from ominicontacto_app.services.wombat_service import WombatReloader, WombatService


class ReiniciarWombat(APIView):
    """Reinicia el servicio de Wombat"""
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post']

    def post(self, request):
        if not config_constance.WOMBAT_DIALER_ALLOW_REFRESH:
            raise PermissionDenied
        state = config_constance.WOMBAT_DIALER_STATE
        msg = _('Refrescando. Espere al menos 15 segundos mientras finaliza el proceso.')
        if state in [WombatReloader.STATE_DOWN, WombatReloader.STATE_STARTING]:
            return Response(data={
                'status': 'ERROR',
                'WD-state': state,
                'message': msg
            })

        # Hilo para efectuar el restart
        reloader = WombatReloader()
        thread_restart = threading.Thread(
            target=reloader.reload,
            # args=[key_task, ]
        )
        thread_restart.setDaemon(True)
        thread_restart.start()
        return Response(data={
            'status': 'OK',
            'WD-state': WombatReloader.STATE_STARTING,
            'message': msg,
        })


class WombatState(APIView):
    """ Informa el estado del servicio de Wombat """
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request):
        if not config_constance.WOMBAT_DIALER_ALLOW_REFRESH:
            raise PermissionDenied
        service = WombatService()
        state, uptime = service.get_dialer_state()
        response_data = {
            'status': 'OK',
            'WD-state': config_constance.WOMBAT_DIALER_STATE,
            'REAL-WD-state': state if state else 'ERROR',
        }
        if config_constance.WOMBAT_DIALER_STATE == WombatReloader.STATE_READY:
            uptime = now() - config_constance.WOMBAT_DIALER_UP_SINCE
            response_data['uptime'] = str(uptime).split('.')[0]
        else:
            msg = _('Refrescando. Espere al menos 15 segundos mientras finaliza el proceso.')
            response_data['message'] = msg

        return Response(data=response_data)
