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
import argparse
from django.utils import timezone
from django.core.management.base import BaseCommand
from whatsapp_app.models import ConversacionWhatsapp


class Command(BaseCommand):

    def disable_argument(self, parser: argparse.ArgumentParser, arg: str) -> None:
        """Disable an argument from a parser.

        Args:
            parser (argparse.ArgumentParser): Parser.
            arg (str): Argument to be removed.
        """
        def raise_disabled_error(action):
            """Raise an argument error."""
            def raise_disabled_error_wrapper(*args) -> str:
                """Raise an exception."""
                raise argparse.ArgumentError(action, 'Has been disabled!')
            return raise_disabled_error_wrapper

        for action in parser._actions:
            opts = action.option_strings
            if (opts and opts[0] == arg) or action.dest == arg:
                action.type = raise_disabled_error(action)
                action.help = argparse.SUPPRESS
                break

    def add_arguments(self, parser):
        self.disable_argument(parser, '-v')
        self.disable_argument(parser, '--pythonpath')
        self.disable_argument(parser, '--version')
        self.disable_argument(parser, '--settings')
        self.disable_argument(parser, '--traceback')
        self.disable_argument(parser, '--no-color')
        self.disable_argument(parser, '--force-color')
        self.disable_argument(parser, '--skip-checks')
        parser.add_argument("which", choices=['all', 'att', 'queued'],
                            help='''
                                all: Cerrar todos los chats
                                att: Cerrar chats atendidos
                                queued: Cerrar chats no atendidos''')
        parser.add_argument(
            "days_limit", type=int,
            help="Cerrar los chats que sean más antiguos que la cantidad de días definida")

    def handle(self, *args, **options):
        try:
            days_limit = options['days_limit']
            today = timezone.now().astimezone(timezone.get_current_timezone())
            start_day = today - timezone.timedelta(days=days_limit)
            conversaciones = ConversacionWhatsapp.objects.filter(
                timestamp__lte=start_day,
                is_disposition=False
            )
            if options['which'] == 'att':
                conversaciones = conversaciones.filter(atendida=True)
            elif options['which'] == 'queued':
                conversaciones = conversaciones.filter(atendida=False)
            conversaciones_update = conversaciones.update(is_disposition=True)
            self.stdout.write(
                self.style.SUCCESS(
                    'Se cerraron {} chats satisfactoriamente'.format(
                        conversaciones_update))
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR('Error: {0}'.format(e))
            )
