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

import csv
from datetime import datetime
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from ominicontacto_app.utiles import datetime_hora_minima_dia, datetime_hora_maxima_dia
from reportes_app.models import LlamadaLog
from ominicontacto_app.models import CalificacionCliente


class Command(BaseCommand):
    """
    Genera un archivo csv con los siguites metadatos:
    Audio_name: nombre del audio sin extensión.
    Timestamp: tiempo inicial de llamada
    Operador: username de agente
    Codification: tipo de llamada (Llamada Dialer / Llamada Manual)
    ANI: Número telefónico
    Agente: nombre de agente
    Servicio: nombre de campaña
    Calificación: última calif de llamada
    Fecha: fecha de llamada.
    """

    help = u'Genera un archivo csv con los metadatos solicitados por KONECTA'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--date', nargs='?',
                            type=lambda d: datetime.strptime(d, '%d-%m-%Y').date(),
                            help="Date in the format dd-mm-YYYY")

    def generar_archivo_csv(self, date=None):
        date = date if date else timezone.localtime(timezone.now())
        fecha_desde = datetime_hora_minima_dia(date)
        fecha_hasta = datetime_hora_maxima_dia(date)
        grabaciones = LlamadaLog.objects.filter(time__range=(fecha_desde, fecha_hasta),
                                                archivo_grabacion__isnull=False)
        grabaciones = grabaciones.filter(Q(duracion_llamada__gt=0) | Q(event='CT-ANSWER'))
        grabaciones = grabaciones.exclude(
            archivo_grabacion='-1').exclude(event='ENTERQUEUE-TRANSFER')
        file_name = '/opt/omnileads/log/metadata_{}'
        with open(file_name.format(date.strftime('%d-%m-%Y')), 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Audio_name', 'Timestamp', 'Operador', 'Codification',
                             'ANI', 'Agente', 'Servicio', 'Calificación', 'Fecha'])
            for grabacion in grabaciones:
                row = []
                calificacion = CalificacionCliente.objects.filter(callid=grabacion.callid).last()
                row.append(grabacion.archivo_grabacion)
                grabacion_time = grabacion.time.astimezone(timezone.get_current_timezone())
                row.append(grabacion_time.strftime('%d/%m/%Y %H:%M:%S'))  # fecha hms
                row.append(grabacion.agente.user.username)  # username
                row.append(grabacion.tipo_llamada_show)  # tipo de llamada
                row.append(grabacion.numero_marcado)  # Número telefónico
                row.append(grabacion.agente.user.get_full_name())  # nombre del agente
                row.append(grabacion.campana.nombre)  # nombre de campana
                row.append(calificacion.opcion_calificacion.nombre if calificacion else "")
                row.append(grabacion_time.strftime('%d/%m/%Y'))  # fecha
                writer.writerow(row)

    def handle(self, *args, **options):
        try:
            date = options["date"] if options["date"] else None
            self.generar_archivo_csv(date)
            self.stdout.write(self.style.SUCCESS('====== Creado el archivo exitosamente ======='))
        except Exception as e:
            raise CommandError('Fallo del comando: {0}'.format(e))
