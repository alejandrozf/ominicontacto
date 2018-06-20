# -*- coding: utf-8 -*-
############################
# Comando para generar la secret_key que se usa para generar las contraseñas SIP, recibe como argumento true si se quiere generar una nueva secret_key o false si se quiere consultar secret_key existente

import logging
import os
import subprocess

from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

logger = logging.getLogger(__name__)

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('args', nargs=1, type=bool)

    def generar_secret_key(self,flag):
	# Genero una secret_key nueva y elimino la anterior para manejar solo una, la secret_key es un string aleatorio de 20 caracteres
    	try:
    	    #actual_key = os.system("kamctl mi autheph.dump_secrets |awk -F ' ' '{print $3}'")
	    actual_key = subprocess.check_output("kamctl mi autheph.dump_secrets |awk -F ' ' '{print $3}'", shell=True)
	    secret_key = str(actual_key)
	    if flag:
	        secret_key = get_random_string(length=20)
		os.system("kamctl mi autheph.add_secret " + secret_key)
    	    	os.system("kamctl mi autheph.rm_secret 1")
    	    	#os.system("service kamailio restart")
    	except:
	    logging.error("Falló el proceso de agregado de secret:key")
        logger.info("Secret Key: " + secret_key)
	self.stdout.write(secret_key)
	return secret_key

    def handle(self, *args, **options):
        flag = args[0]
	self.generar_secret_key(flag)
