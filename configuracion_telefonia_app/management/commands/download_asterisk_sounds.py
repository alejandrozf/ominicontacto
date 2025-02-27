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

import logging
from django.core.management.base import BaseCommand

from configuracion_telefonia_app.services.audio_asterisk import AsteriskSoundsInstaller
from configuracion_telefonia_app.models import AudiosAsteriskConf

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Instala los Audios de Asterisk correspondiente a los AudiosAsteriskConf del sistema.
    Ignora ES y EN por estar instalados por defecto.
    """

    help = 'Instala Audios de Asterisk'

    def _instalar_audios_asterisk(self):
        instalador = AsteriskSoundsInstaller()
        erroneos = []
        for audios in AudiosAsteriskConf.objects.all():
            if audios.paquete_idioma not in ['es', 'en']:
                error = instalador.install(audios.paquete_idioma)
                if error:
                    erroneos.append(audios.get_paquete_idioma_display())
        if erroneos:
            logger.error(f'Error al instalar los idiomas: {erroneos}')

    def handle(self, *args, **options):
        try:
            self._instalar_audios_asterisk()
        except Exception as e:
            logger.error('Fallo del comando: {0}'.format(e))
