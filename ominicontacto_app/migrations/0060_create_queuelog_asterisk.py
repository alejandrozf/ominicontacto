# -*- coding: utf-8 -*-
# Generated Federico Peker
from __future__ import unicode_literals

from django.db import migrations, connection
import os


def create_procedemiento_trigger(apps, schema_editor):
    tmp_dir = os.path.abspath(__file__)  # 0060····.py
    tmp_dir = os.path.dirname(tmp_dir)  # migrations
    tmp_dir = os.path.split(tmp_dir)[0]  # ominicontacto_app

    sql_file_path = "sql/queue_log_dump_table.sql"

    tmp = os.path.join(tmp_dir, sql_file_path)

    assert os.path.exists(tmp)

    print("Creando funcion desde {0}".format(tmp))
    filename = tmp
    sql = open(filename, "r").read()
    cursor = connection.cursor()
    cursor.execute(sql)


class Migration(migrations.Migration):

    dependencies = [
        ('ominicontacto_app', '0059_auto_20170412_1035'),
    ]

    operations = [
        migrations.RunPython(create_procedemiento_trigger),
    ]