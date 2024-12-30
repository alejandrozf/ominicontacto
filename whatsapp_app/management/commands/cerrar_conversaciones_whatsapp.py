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
from django.utils import timezone
from django.core.management.base import BaseCommand
from whatsapp_app.models import ConversacionWhatsapp
from ominicontacto_app.models import OpcionCalificacion


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("days_passed", nargs="+", type=int,
                            help="Elimina las conversaciones de los ultimos dias")
        parser.add_argument("--all", action="store_true",
                            help="Elimina todas las conversacions")
        parser.add_argument("--att", action="store_true",
                            help="Elimina conversaciones atendidas")
        parser.add_argument("--queued", action="store_true",
                            help="Elimina conversaciones no atendidas")
        calificacion_opciones = list(
            OpcionCalificacion.objects.all().values_list('nombre', flat=True).distinct())
        parser.add_argument('--calificacion', choices=calificacion_opciones,
                            help="Elimina conversaciones con la calificacion seleccionada")

    def handle(self, *args, **options):
        try:
            days_passed = options['days_passed'][0]
            today = timezone.now().astimezone(timezone.get_current_timezone())
            start_day = today - timezone.timedelta(days=days_passed)
            conversaciones = ConversacionWhatsapp.objects.filter(
                timestamp__range=[start_day, today])
            if options['att']:
                conversaciones = conversaciones.filter(atendida=True)
            elif options['queued']:
                conversaciones = conversaciones.filter(atendida=False)
            if options['calificacion']:
                conversaciones = conversaciones.filter(
                    is_disposition=True,
                    conversation_disposition__opcion_calificacion__nombre=options['calificacion'])
            self.stdout.write(
                self.style.SUCCESS(
                    'Se eliminaron {} conversaciones satisfactoriamente'.format(
                        conversaciones.count()))
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR('Error: {0}'.format(e))
            )
