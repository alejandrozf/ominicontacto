# -*- coding: utf-8 -*-

import logging
import os

from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

logger = logging.getLogger(__name__)

class Command(BaseCommand):

    def generar_secret_key(self):
    	# Genero una secret_key nueva y elimino la anterior para manejar solo una, la secret_key es un string aleatorio de 20 caracteres
    	secret_key = get_random_string(length=20)
    	try:
    	    actual_key = os.system("kamctl mi autheph.dump_secrets > /dev/null 2>&1 ")
	    if actual_key != "":
	    	os.system("kamctl mi autheph.add_secret " + secret_key)
    	    	os.system("kamctl mi autheph.rm_secret 1")
    	    	#os.system("service kamailio restart")
		return secret_key
    	except:
	    logging.error("Falló el proceso de agregado de secret:key")
    
    def handle(self, *args, **options):
	self.generar_secret_key()
