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

    def login(self, agente):
        return
        ActividadAgenteLog.objects.create(agente_id=agente.id, event=ActividadAgenteLog.LOGIN)

    def logout(self, agente):
        return
        ActividadAgenteLog.objects.create(agente_id=agente.id, event=ActividadAgenteLog.LOGOUT)

    def pause(self, agente, pausa_id):
        return
        ActividadAgenteLog.objects.create(agente_id=agente.id,
                                          pausa_id=pausa_id,
                                          event=ActividadAgenteLog.PAUSE)

    def unpause(self, agente, pausa_id):
        return
        ActividadAgenteLog.objects.create(agente_id=agente.id,
                                          pausa_id=pausa_id,
                                          event=ActividadAgenteLog.UNPAUSE)

    def enforce_login(self, agente):
        return
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
