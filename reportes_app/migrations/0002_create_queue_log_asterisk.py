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
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reportes_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='QueueLog',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('callid', models.CharField(blank=True, default='', max_length=100)),
                ('queuename', models.CharField(blank=True, default='', max_length=100)),
                ('agent', models.CharField(blank=True, default='', max_length=100)),
                ('event', models.CharField(blank=True, default='', max_length=100)),
                ('data1', models.CharField(blank=True, default='', max_length=100)),
                ('data2', models.CharField(blank=True, default='', max_length=100)),
                ('data3', models.CharField(blank=True, default='', max_length=100)),
                ('data4', models.CharField(blank=True, default='', max_length=100)),
                ('data5', models.CharField(blank=True, default='', max_length=100)),
            ],
            options={
                'db_table': 'queue_log',
            },
        ),
    ]
