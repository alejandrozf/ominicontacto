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

from reportes_app.models import ActividadAgenteLog
from django.contrib.sessions.models import Session
from django.utils.timezone import now


class AgentPresenceManager(object):
    """
    Clase que se encarga de manejar los eventos relativos a la presencia y el
    estado del agente.
    TODO:
    - Hacerse cargo de la funcionalidad de
      ominicontacto_app/services/asterisk/agent_activity.AgentActivityAmiManager
    - Desacoplar el manejo de la presencia en Redis de AgentActivityAmiManager
      en un nuevo servicio AgentRedisPresenceManager
    - Solo este componente deberá usar dicho servicio
    """

    def login(self, agente, time=None):
        log = ActividadAgenteLog.objects.create(agente_id=agente.id, event=ActividadAgenteLog.LOGIN)
        self._update_log_time(log, time)

    def logout(self, agente, time=None):
        log = ActividadAgenteLog.objects.create(agente_id=agente.id,
                                                event=ActividadAgenteLog.LOGOUT)
        self._update_log_time(log, time)

    def pause(self, agente, pausa_id, time=None):
        log = ActividadAgenteLog.objects.create(agente_id=agente.id,
                                                pausa_id=pausa_id,
                                                event=ActividadAgenteLog.PAUSE)
        self._update_log_time(log, time)

    def unpause(self, agente, pausa_id, time=None):
        log = ActividadAgenteLog.objects.create(agente_id=agente.id,
                                                pausa_id=pausa_id,
                                                event=ActividadAgenteLog.UNPAUSE)
        self._update_log_time(log, time)

    def enforce_login(self, agente):
        ultimo_log = ActividadAgenteLog.objects.filter(agente_id=agente.id).last()
        # Este caso no debería ocurrir nunca ya que debe estar loggeado
        if ultimo_log.event == ActividadAgenteLog.LOGOUT:
            self.login(agente)
        # Este sería el caso en que refresca la vista estando en pausa
        elif ultimo_log.event == ActividadAgenteLog.PAUSE:
            self.unpause(agente, ultimo_log.pausa_id)
            self.logout(agente)
            self.login(agente)
        # Este sería el caso en que refresca la vista luego de una pausa
        elif ultimo_log.event == ActividadAgenteLog.UNPAUSE:
            self.logout(agente)
            self.login(agente)
        # No se toma en cuenta el caso en que refresque la vista sin haber pasado
        # a pausa para no complicar demasiado el control.

    def fix_previous_open_session_logs(self, user, agente):
        """ Fix de Logs al momento de hacer Login (antes de self.login) """
        """ Para ser usado al momento de hacer Login unicamente """
        try:
            # Si existe la Session y se está haciendo login, puede tener logs sin cierre de sesion
            # Por expiracion o por iniciar sesion en otro navegador.
            session = Session.objects.get(session_key=user.last_session_key)
            fecha_cierre = min(session.expire_date, now())
            ultimo_log = ActividadAgenteLog.objects.filter(agente_id=agente.id).last()
            # Cierro Session en el horario de expiración
            if ultimo_log.event == ActividadAgenteLog.LOGIN:
                self.logout(agente, time=fecha_cierre)
            # Este sería el caso en que expira estando en pausa
            elif ultimo_log.event == ActividadAgenteLog.PAUSE:
                self.unpause(agente, ultimo_log.pausa_id, time=fecha_cierre)
                self.logout(agente, time=fecha_cierre)
            # Este sería el caso en que expira luego de una pausa
            elif ultimo_log.event == ActividadAgenteLog.UNPAUSE:
                self.logout(agente, time=fecha_cierre)
        except Session.DoesNotExist:
            # Si no existe la Session fue borrada al hacer logout. Nada para corregir.
            pass

    def _update_log_time(self, log, time=None):
        if time is not None:
            log.time = time
            log.save(update_fields=['time'])
