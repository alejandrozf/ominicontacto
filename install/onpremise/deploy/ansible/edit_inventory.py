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

import argparse
import os
import sys

parser = argparse.ArgumentParser(description='Modify Ansible inventory')

parser.add_argument("--ami_user", default="omnileadsami", help="Specifies ami user")
parser.add_argument("--ami_password", default="5_MeO_DMT", help="Specifies ami password")
parser.add_argument("--asterisk_host", help="Specifies asterisk host")
parser.add_argument("--nginx_host", help="Specifies nginx host")
parser.add_argument("--kamailio_host", help="Specifies kamailio host")
parser.add_argument("--dialer_host", help="Specifies dialer host")
parser.add_argument("--dialer_user", default="demoadmin", help="Specifies dialer user")
parser.add_argument("--dialer_password", default="demo", help="Specifies dialer passowrd")
parser.add_argument("--ecctl", help="Specifies ECCTL")
parser.add_argument("--extern_ip", default="auto", help="Specifies the extern_ip")
parser.add_argument("--sca", help="Specifies SCA")
parser.add_argument("--postgres_host", help="Specifies postgresql host")
parser.add_argument("--postgres_port", help="Specifies postgresql port")
parser.add_argument("--postgres_database", help="Specifies postgresql database")
parser.add_argument("--postgres_user", default="omnileads", help="Specifies postgresql user")
parser.add_argument("--postgres_password", default="admin123", help="Specifies postgresql user")
parser.add_argument("--mysql_host", help="Specifies external mysql host")
parser.add_argument("--redis_host", help="Specifies external redis host")
parser.add_argument("--rtpengine_host", help="Specifies external rtpengine host")
parser.add_argument("--schedule", help="Specifies de tag for generated docker images")
parser.add_argument("--TZ", default="America/Argentina/Cordoba", help="Specifies TZ")
parser.add_argument("--websocket_host", help="Specifies websocket host")
parser.add_argument("--websocket_port", help="Specifies websocket port")
args = parser.parse_args()

# omininicontacto directorio raíz
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
inventory_path = os.path.join(base_dir, 'ansible/inventory')
inventory_file = open(inventory_path, 'r+')
inventory_contents = inventory_file.read()

if args.ami_user:
    inventory_contents = inventory_contents.replace(
        "#ami_user=omnileadsami", "ami_user={0}".format(args.ami_user))
if args.ami_password:
    inventory_contents = inventory_contents.replace(
        "#ami_password=5_MeO_DMT", "ami_password={0}".format(args.ami_password))
if args.asterisk_host:
    inventory_contents = inventory_contents.replace(
        "#asterisk_host=", "asterisk_host={0}".format(args.asterisk_host))
if args.nginx_host:
    inventory_contents = inventory_contents.replace(
        "#nginx_host=", "nginx_host={0}".format(args.nginx_host))
if args.kamailio_host:
    inventory_contents = inventory_contents.replace(
        "#kamailio_host=", "kamailio_host={0}".format(args.kamailio_host))
if args.dialer_user:
    inventory_contents = inventory_contents.replace(
        "#dialer_user=demoadmin", "dialer_user={0}".format(args.dialer_user))
if args.extern_ip:
    inventory_contents = inventory_contents.replace(
        "#extern_ip=auto", "extern_ip={0}".format(args.extern_ip))
if args.dialer_password:
    inventory_contents = inventory_contents.replace(
        "#dialer_password=demo", "dialer_password={0}".format(args.dialer_password))
if args.postgres_user:
    inventory_contents = inventory_contents.replace(
        "#postgres_user=omnileads", "postgres_user={0}".format(args.postgres_user))
if args.postgres_password:
    inventory_contents = inventory_contents.replace(
        "#postgres_password=my_very_strong_pass", "postgres_password={0}".format(
            args.postgres_password))
if args.postgres_database:
    inventory_contents = inventory_contents.replace(
        "postgres_database=omnileads", "postgres_database={0}".format(args.postgres_database))
if args.postgres_host:
    inventory_contents = inventory_contents.replace(
        "#postgres_host=", "postgres_host={0}".format(args.postgres_host))
if args.postgres_port:
    inventory_contents = inventory_contents.replace(
        "#postgres_port=", "postgres_port={0}".format(args.postgres_port))
if args.ecctl:
    inventory_contents = inventory_contents.replace(
        "ECCTL=28800", "ECCTL={0}".format(args.ecctl))
if args.dialer_host:
    inventory_contents = inventory_contents.replace(
        "#dialer_host=", "dialer_host={0}".format(args.dialer_host))
if args.mysql_host:
    inventory_contents = inventory_contents.replace(
        "#mysql_host=", "mysql_host={0}".format(args.mysql_host))
if args.redis_host:
    inventory_contents = inventory_contents.replace(
        "#redis_host=", "redis_host={0}".format(args.redis_host))
if args.rtpengine_host:
    inventory_contents = inventory_contents.replace(
        "#rtpengine_host=", "rtpengine_host={0}".format(args.rtpengine_host))
if args.sca:
    inventory_contents = inventory_contents.replace(
        "SCA=3600", "SCA={0}".format(args.sca))
if args.schedule:
    inventory_contents = inventory_contents.replace(
        "schedule=Agenda", "schedule={0}".format(args.schedule))
if args.TZ:
    inventory_contents = inventory_contents.replace(
        "#TZ=America/Argentina/Cordoba", "TZ={0}".format(args.TZ))
if args.websocket_host:
    inventory_contents = inventory_contents.replace(
        "#websocket_host=", "websocket_host={0}".format(args.websocket_host))
if args.websocket_port:
    inventory_contents = inventory_contents.replace(
        "#websocket_port=", "websocket_port={0}".format(args.websocket_port))
inventory_file.seek(0)
inventory_file.truncate()
inventory_file.write(inventory_contents)

inventory_file.seek(0)
inventory_file.truncate()
inventory_file.write(inventory_contents.replace(
     "#localhost ansible_connection=local ansible_user=root"
     " #(this line is for self-hosted installation)",
     "localhost ansible_connection=local ansible_user=root"))
sys.exit()
