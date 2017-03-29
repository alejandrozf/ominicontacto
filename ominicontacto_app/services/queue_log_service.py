# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import connection

import logging


logger = logging.getLogger(__name__)


class QueueLogService():

    def obtener_queue_log_all_sesion(self):

        cursor = connection.cursor()
        sql = """select time, agent, event from queue_log
        where queuename='ALL' and event in ('REMOVEMEMBER', 'ADDMEMBER')
        """

        cursor.execute(sql)
        values = cursor.fetchall()
        return values
