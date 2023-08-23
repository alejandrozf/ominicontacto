# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

import logging
import json
import os
import datetime
import redis
import psycopg2

OMNILEADS_HOSTNAME = os.environ.get('OMNILEADS_HOSTNAME') or 'localhost'
WSURL = f'wss://{OMNILEADS_HOSTNAME}/consumers/stream/survey_app/answers/updates'
QUEUE_KEY = 'OML:QUEUE:CALL_CUSTOM_VAR'

logger = logging.getLogger("asyncio")
INSTALL_PREFIX = os.getenv('INSTALL_PREFIX')
fh = logging.FileHandler(f'{INSTALL_PREFIX}/log/call_custom_var.log')

logger.addHandler(fh)
logger.setLevel(logging.INFO)


class PersistidorCallCustomVarLog(object):

    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.pg_connection = None

    def _get_db_cursor(self):
        if self.pg_connection:
            return self.pg_connection.cursor()
        self.pg_connection = psycopg2.connect(
            host=os.getenv('PGHOST'), dbname=os.getenv('PGDATABASE'),
            user=os.getenv('PGUSER'), port=os.getenv('PGPORT'), password=os.getenv('PGPASSWORD'))
        return self.pg_connection.cursor()

    def persistir(self, item_json):
        try:
            code = self._persistir_item(json.loads(item_json))
            if code == 'KILL':
                return 'KILL'
        except (psycopg2.ProgrammingError, psycopg2.IntegrityError):
            self.logger.info(self._log_msg('INVALID LOG DATA: ' + item_json))
        except Exception:
            self.logger.info(self._log_msg('LOG DATA PROBLEM: ' + item_json))

    def _persistir_item(self, item):
        callid = item[0]
        valor = item[1]

        if callid == 'KILL':
            return callid

        sql = """INSERT INTO public.reportes_app_callcustomvarlog(callid, valor)
            VALUES (%s, %s);
        """
        params = (callid, valor)
        cursor = self._get_db_cursor()
        cursor.execute(sql, params)
        self.pg_connection.commit()

    def _log_msg(self, message):
        return f'{datetime.datetime.now()}:-{message}'


def start():
    redis_connection = redis.Redis(
        host=os.getenv('REDIS_HOSTNAME'),
        port=6379,  # settings.CONSTANCE_REDIS_CONNECTION['port'],
        decode_responses=True)
    persistidor = PersistidorCallCustomVarLog(logger)
    alive = True
    while alive:
        queue, item_json = redis_connection.blpop(QUEUE_KEY)
        print(item_json)
        res = persistidor.persistir(item_json)
        if res == 'KILL':
            alive = False


if __name__ == '__main__':
    start()
