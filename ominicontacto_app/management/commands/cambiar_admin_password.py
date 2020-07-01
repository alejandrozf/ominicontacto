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

import os

from django.core.management.base import BaseCommand, CommandError

from ominicontacto_app.models import User


class Command(BaseCommand):

    help = ('Cambia la contraseña de admin por la definidida en la variable de '
            'entorno DJANGO_ADMIN_PASS')

    def cambiar_admin_pass(self):
        django_admin_pass = os.getenv('DJANGO_PASS')
        admin = User.objects.get(username='admin')
        admin.set_password(django_admin_pass)
        admin.save()

    def handle(self, *args, **options):
        try:
            self.cambiar_admin_pass()
        except Exception as e:
            raise CommandError('Fallo del comando: {0}'.format(e))
