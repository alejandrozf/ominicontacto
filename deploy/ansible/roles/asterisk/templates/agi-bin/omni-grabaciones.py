#!{{ install_prefix }}virtualenv/bin/python
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

# Este script se ejecuta como AGI desde 'oml_extensions_sub.conf' para insertar una instancia del
# modelo grabación según se requiera en el sistema

import sys

import psycopg2

from socket import setdefaulttimeout

from config import configParser
from utiles import write_time_stderr

sys.stderr = open('{{ install_prefix }}log/agis-errors.log', 'a')

setdefaulttimeout(30)

# obtenemos los valores de las variables de configuración necesarias
OML_DB_HOST = configParser.get('OML', 'POSTGRES_IP')
OML_DB_NAME = configParser.get('OML', 'POSTGRES_DATABASE')
OML_DB_USER = configParser.get('OML', 'POSTGRES_USER')
OML_DB_PASS = configParser.get('OML', 'POSTGRES_PASSWORD')

tipo_llamada = sys.argv[1]
id_cliente = sys.argv[2]
tel_cliente = sys.argv[3]
grabacion = sys.argv[4]
agente_id = sys.argv[5]
campana = sys.argv[6]
fecha = sys.argv[7]
uid = sys.argv[8]
duracion = sys.argv[9]

# conectando con BD
try:
    conn = psycopg2.connect(
        host=OML_DB_HOST, dbname=OML_DB_NAME, user=OML_DB_USER, password=OML_DB_PASS)
except Exception as e:
    write_time_stderr("Unable to connect to the database due to {0}".format(e.message))
    raise e

# se realiza la inserción de los parámetros de la grabación en la BD
query = ("INSERT INTO ominicontacto_app_grabacion (fecha,tipo_llamada,id_cliente,tel_cliente,"
         "grabacion,agente_id,campana_id,uid,duracion) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}',"
         "'{6}','{7}','{8}');".format(
             fecha, tipo_llamada, id_cliente, tel_cliente, grabacion, agente_id, campana, uid,
             duracion))
cur = conn.cursor()
try:
    cur.execute(query)
except Exception as e:
    write_time_stderr("Unable to insert log in database due to {0}".format(e.message))
    raise e
conn.commit()

conn.close()
