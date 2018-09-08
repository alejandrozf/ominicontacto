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

from random import randint

from django.core.management.base import BaseCommand, CommandError
from ominicontacto_app.tests.factories import (GrabacionFactory, GrabacionMarcaFactory,
                                               AgenteProfileFactory)


class Command(BaseCommand):
    """
    Crea tantas grabaciones como se especifique en el parametro, son marcadas o no, aleatoriamente
    """

    help = u'Crea la cantidad de grabaciones de acuerdo al parámetro recibido'

    def add_arguments(self, parser):
        parser.add_argument('nro_llamadas', nargs=1, type=int)

    def grabacion_marcada_aleatoria(self, agente):
        """
        Crea un marca de grabación
        """
        grabacion = GrabacionFactory.create(agente=agente)
        crear_grabacion_marcada = bool(randint(0, 1))

        if crear_grabacion_marcada:
            GrabacionMarcaFactory.create(uid=grabacion.uid)

    def handle(self, *args, **options):
        nro_grabaciones = options['nro_llamadas'][0]
        agente = AgenteProfileFactory.create()
        for i in range(nro_grabaciones):
            try:
                self.grabacion_marcada_aleatoria(agente)
            except Exception as e:
                raise CommandError('Fallo del comando: {0}'.format(e.message))
        self.stdout.write(
            self.style.SUCCESS('Creada(s) {0} grabaciones(s)'.format(nro_grabaciones)))
