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
from __future__ import unicode_literals

from django.db import migrations, connection
import os


def create_procedemiento_trigger(apps, schema_editor):
    tmp_dir = os.path.abspath(__file__)  # 0003····.py
    tmp_dir = os.path.dirname(tmp_dir)  # migrations
    tmp_dir = os.path.split(tmp_dir)[0]  # reportes_app

    for sql_file_path in (
            "sql/plpython/replace_insert_queue_log_ominicontacto_queue_log.sql",
            "sql/plpython/trigger_queue_log.sql"
    ):
        tmp = os.path.join(tmp_dir, sql_file_path)

        assert os.path.exists(tmp)

        print("Creando funcion desde {0}".format(tmp))
        filename = tmp
        sql = open(filename, "r").read()
        cursor = connection.cursor()
        cursor.execute(sql)


def borrar_trigger(apps, schema_editor):
    cursor = connection.cursor()
    sql = "DROP TRIGGER IF EXISTS trigger_queue_log ON queue_log"
    cursor.execute(sql)
    cursor = connection.cursor()
    sql = "DROP FUNCTION insert_queue_log_ominicontacto_queue_log()"
    cursor.execute(sql)


class Migration(migrations.Migration):

    dependencies = [
        ('reportes_app', '0002_create_queue_log_asterisk'),
    ]

    operations = [
        migrations.RunPython(create_procedemiento_trigger, borrar_trigger),
    ]
