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

import logging

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from ominicontacto_app.models import AutenticacionExternaDeUsuario

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Desactiva la autenticación externa usuarios administradores
    """

    help = 'Desactiva la autenticación externa usuarios administradores'

    def _desactivar_autenticacion_externa_administradores(self):
        AutenticacionExternaDeUsuario.desactivar_autenticacion_de_administradores()
        logger.info(_('Desactivando autenticación externa para usuarios administradores'))

    def handle(self, *args, **options):
        try:
            self._desactivar_autenticacion_externa_administradores()
        except Exception as e:
            logger.error('Fallo del comando: {0}'.format(e))
