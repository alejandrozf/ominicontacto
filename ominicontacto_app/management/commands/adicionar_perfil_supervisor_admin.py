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

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from ominicontacto_app.models import User, SupervisorProfile


class Command(BaseCommand):

    help = 'Agrega SupervisorProfile y rol Administraodr al admin por defecto del sistema si falta'

    def adicionar_perfil_supervisor(self):
        admin = User.objects.get(username='admin')
        if admin.get_supervisor_profile() is None:
            SupervisorProfile.objects.create(
                user=admin, sip_extension=admin.id + 1000, is_administrador=True)
        if not admin.groups.exists():
            admin.groups.add(Group.objects.get(name=User.ADMINISTRADOR))

    def handle(self, *args, **options):
        try:
            self.adicionar_perfil_supervisor()
        except Exception as e:
            raise CommandError('Fallo del comando: {0}'.format(e))
