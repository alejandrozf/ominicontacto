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

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reportes_app', '0008_transferenciaaencuestalog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actividadagentelog',
            name='time',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]