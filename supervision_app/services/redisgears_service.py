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
    AGENTES_TASK_ID = 'agentes'
    ENTRANTES_TASK_ID = 'entrantes'
    SALIENTES_TASK_ID = 'salientes'
    DIALERS_TASK_ID = 'dialers'

    def __init__(self):
        self.conn = redis.Redis(host=settings.REDIS_HOSTNAME,
                                port=settings.CONSTANCE_REDIS_CONNECTION['port'],
                                decode_responses=True)

    def registra_stream_supervisor(self, supervisor_id):
        self.__registra_evento_agente_change()
        self.__prepara_agentes_redis_gears(supervisor_id, self.AGENTES_TASK_ID)

    def registra_stream_supervisor_entrantes(self, supervisor_id, campanas_ids, campanas_nombres):
        self.__registra_evento_agente_change()
        self.__prepara_agentes_redis_gears(supervisor_id, self.ENTRANTES_TASK_ID)
        self.__registra_evento_supervision_entrantes_change()
        self.__prepara_supervision_entrantes_redis_gears(
            supervisor_id, self.ENTRANTES_TASK_ID, campanas_ids, campanas_nombres)

    def registra_stream_supervisor_salientes(self, supervisor_id, campanas_ids, campanas_nombres):
        self.__registra_evento_supervision_salientes_change()
        self.__prepara_supervision_salientes_redis_gears(
            supervisor_id, self.SALIENTES_TASK_ID, campanas_ids, campanas_nombres)

    def registra_stream_supervisor_dialers(self, supervisor_id, campanas_ids, campanas_nombres):
        self.__registra_evento_agente_change()
        self.__prepara_agentes_redis_gears(supervisor_id, self.DIALERS_TASK_ID)
        self.__registra_evento_supervision_dialers_change()
        self.__prepara_supervision_dialers_redis_gears(
            supervisor_id, self.DIALERS_TASK_ID, campanas_ids, campanas_nombres)

    def __prepara_agentes_redis_gears(self, supervisor_id, task_id):
        SCRIPT_NAME = 'prepara_agentes_para_stream_redis.py'
        script = open(f'{settings.BASE_DIR}/{self.SCRIPT_PATH}/{SCRIPT_NAME}', 'r') \
            .read() % (task_id, supervisor_id)

        self.conn.execute_command("RG.PYEXECUTE", script)

    def __registra_evento_agente_change(self):
        AGENTE_KEY = 'OML:AGENT:*'
        EVENT_DESC = 'sup_agent'
        SCRIPT_NAME = 'registrar_evento_agente_change.py'
        if not self.__existe_evento_key_change(AGENTE_KEY, EVENT_DESC):
            script = open(f'{settings.BASE_DIR}/{self.SCRIPT_PATH}/{SCRIPT_NAME}', 'r').read()
            self.conn.execute_command("RG.PYEXECUTE", script)

    def __registra_evento_supervision_entrantes_change(self):
        SUP_CAMPAIGN_KEY = 'OML:SUPERVISION_CAMPAIGN:*'
        EVENT_DESC = 'sup_entrantes'
        SCRIPT_NAME = 'registrar_evento_supervision_entrantes.py'
        if not self.__existe_evento_key_change(SUP_CAMPAIGN_KEY, EVENT_DESC):
            script = open(f'{settings.BASE_DIR}/{self.SCRIPT_PATH}/{SCRIPT_NAME}', 'r').read() \
                % SUP_CAMPAIGN_KEY
            self.conn.execute_command("RG.PYEXECUTE", script)

    def __registra_evento_supervision_salientes_change(self):
        SUP_CAMPAIGN_KEY = 'OML:SUPERVISION_SALIENTE:*'
        EVENT_DESC = 'sup_salientes'
        SCRIPT_NAME = 'registrar_evento_supervision_salientes.py'
        if not self.__existe_evento_key_change(SUP_CAMPAIGN_KEY, EVENT_DESC):
            script = open(f'{settings.BASE_DIR}/{self.SCRIPT_PATH}/{SCRIPT_NAME}', 'r').read() \
                % SUP_CAMPAIGN_KEY
            self.conn.execute_command("RG.PYEXECUTE", script)

    def __registra_evento_supervision_dialers_change(self):
        SUP_CAMPAIGN_KEY = 'OML:SUPERVISION_DIALER:*'
        EVENT_DESC = 'sup_dialers'
        SCRIPT_NAME = 'registrar_evento_supervision_dialers.py'
        if not self.__existe_evento_key_change(SUP_CAMPAIGN_KEY, EVENT_DESC):
            script = open(f'{settings.BASE_DIR}/{self.SCRIPT_PATH}/{SCRIPT_NAME}', 'r').read() \
                % SUP_CAMPAIGN_KEY
            self.conn.execute_command("RG.PYEXECUTE", script)

    def __prepara_supervision_entrantes_redis_gears(self, supervisor_id, stream_task_id,
                                                    campanas_ids, campanas_nombres):
        SCRIPT_NAME = 'prepara_supervision_entrantes_para_stream_redis.py'
        script = open(f'{settings.BASE_DIR}/{self.SCRIPT_PATH}/{SCRIPT_NAME}', 'r').read() \
            % (campanas_ids, campanas_nombres, stream_task_id, supervisor_id)

        self.conn.execute_command("RG.PYEXECUTE", script)

    def __prepara_supervision_salientes_redis_gears(self, supervisor_id, stream_task_id,
                                                    campanas_ids, campanas_nombres):
        SCRIPT_NAME = 'prepara_supervision_salientes_para_stream_redis.py'
        script = open(f'{settings.BASE_DIR}/{self.SCRIPT_PATH}/{SCRIPT_NAME}', 'r').read() \
            % (campanas_ids, campanas_nombres, stream_task_id, supervisor_id)

        self.conn.execute_command("RG.PYEXECUTE", script)

    def __prepara_supervision_dialers_redis_gears(self, supervisor_id, stream_task_id,
                                                  campanas_ids, campanas_nombres):
        SCRIPT_NAME = 'prepara_supervision_dialers_para_stream_redis.py'
        script = open(f'{settings.BASE_DIR}/{self.SCRIPT_PATH}/{SCRIPT_NAME}', 'r').read() \
            % (campanas_ids, campanas_nombres, stream_task_id, supervisor_id)

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
