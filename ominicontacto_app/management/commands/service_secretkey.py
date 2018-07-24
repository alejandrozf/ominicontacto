# -*- coding: utf-8 -*-
############################
# Comando para generar la secret_key que se usa para generar las contraseñas SIP, recibe como
# argumento true si se quiere generar una nueva secret_key o false si se quiere consultar secret_key
# existente

import logging
import os
import subprocess

from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from django.conf import settings

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('args', nargs=1, type=str)

    def generar_secret_key(self, flag):
        try:
            cmd = "kamctl mi autheph.dump_secrets |awk -F ' ' '{print $3}' |head -1"
            actual_key = subprocess.check_output(cmd, shell=True)
            actual_key = actual_key[:-1]
            if flag == "consultar":
                secret_key = str(actual_key)
            elif flag == "generar":
                # Genero una secret_key nueva y elimino la anterior para manejar solo una, la secret
                # key es un string aleatorio de 20 caracteres
                secret_key = get_random_string(length=20)
                str_sed = "sed -i \"s/\({0}\).*/{1}!g\\\"/\" {2}kamailio-local.cfg"
                cmd = str_sed.format(actual_key, secret_key, settings.OML_KAMAILIO_LOCATION)
                os.system(cmd)
            else:
                print("Opción inválida")
            self.stdout.write(secret_key)
            return secret_key
        except Exception as e:
            logging.error("Falló el proceso de agregado de secret_key por {0}".format(e))

    def handle(self, *args, **options):
        flag = args[0]
        self.generar_secret_key(flag)
