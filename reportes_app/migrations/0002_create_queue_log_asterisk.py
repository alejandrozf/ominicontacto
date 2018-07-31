# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, connection
import os


def create_queuelog_table(apps, schema_editor):
    tmp_dir = os.path.abspath(__file__)  # 0002····.py
    tmp_dir = os.path.dirname(tmp_dir)  # migrations
    tmp_dir = os.path.split(tmp_dir)[0]  # reportes_app

    sql_file_path = "sql/queue_log_dump_table.sql"

    tmp = os.path.join(tmp_dir, sql_file_path)

    assert os.path.exists(tmp)

    print("Creando funcion desde {0}".format(tmp))
    filename = tmp
    sql = open(filename, "r").read()
    cursor = connection.cursor()
    cursor.execute(sql)


def borrar_queuelog_table(apps, schema_editor):
    sql = """
    DROP SEQUENCE queue_log_id_seq CASCADE;
    DROP TABLE queue_log;
    """
    cursor = connection.cursor()
    cursor.execute(sql)


class Migration(migrations.Migration):

    dependencies = [
        ('reportes_app', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_queuelog_table, borrar_queuelog_table),
    ]
