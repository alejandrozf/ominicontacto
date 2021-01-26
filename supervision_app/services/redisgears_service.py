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
from django.conf import settings
import redis


class RedisGearsService(object):
    SCRIPT_PATH = 'supervision_app/services/redisgears_action_scripts'

    def __init__(self):
        self.conn = redis.Redis(host=settings.REDIS_HOSTNAME,
                                port=settings.CONSTANCE_REDIS_CONNECTION['port'],
                                decode_responses=True)

    def registra_stream_supervisor(self, supervisor_id):
        self.__registra_evento_agente_change()
        self.__prepara_agentes_redis_gears(supervisor_id)

    def __prepara_agentes_redis_gears(self, supervisor_id):
        SCRIPT_NAME = 'prepara_agentes_para_stream_redis.py'
        script = open(f'{settings.BASE_DIR}/{self.SCRIPT_PATH}/{SCRIPT_NAME}', 'r') \
            .read() \
            .replace('%s', str(supervisor_id))

        self.conn.execute_command("RG.PYEXECUTE", script)

    def __registra_evento_agente_change(self):
        AGENTE_KEY = 'OML:AGENT:*'
        EVENT_DESC = 'sup_agent'
        SCRIPT_NAME = 'registrar_evento_agente_change.py'
        if not self.__existe_evento_key_change(AGENTE_KEY, EVENT_DESC):
            script = open(f'{settings.BASE_DIR}/{self.SCRIPT_PATH}/{SCRIPT_NAME}', 'r').read()
            self.conn.execute_command("RG.PYEXECUTE", script)

    def __existe_evento_key_change(self, redis_key, desc):
        REGISTRATION_DATA = 7
        ARGS = 13
        REGEX = 1
        DESCRIPTION = 5
        lista_eventos_registrados = self.conn.execute_command("RG.DUMPREGISTRATIONS")
        for evento in lista_eventos_registrados:
            if evento[REGISTRATION_DATA][ARGS][REGEX] == redis_key and evento[DESCRIPTION] == desc:
                return True
        return False
