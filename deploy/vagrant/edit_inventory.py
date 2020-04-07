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

parser.add_argument("--self_hosted", help="Modifies if the install is selfhosted")
parser.add_argument("--admin_password", help="Omnileads admin web password")
parser.add_argument("--internal_ip", help="Sets internal IP in external server, say 172.16.20.44")
parser.add_argument("--remote_port", help="Sets external ssh port to connect on remote server")
parser.add_argument("-dlu", "--docker_login_user", help="Username for docker hub")
parser.add_argument("-dle", "--docker_login_email", help="User email for docker hub")
parser.add_argument("-dlp", "--docker_login_password", help="User password for docker hub")
parser.add_argument("-tag", "--tag_docker_images", help="Specifies de tag for generated docker"
                    "images")
parser.add_argument("--ami_user", help="Specifies de tag for generated docker images")
parser.add_argument("--ami_password", help="Specifies de tag for generated docker images")
parser.add_argument("--dialer_user", help="Specifies de tag for generated docker images")
parser.add_argument("--dialer_password", help="Specifies de tag for generated docker images")
parser.add_argument("--ecctl", help="Specifies de tag for generated docker images")
parser.add_argument("--sca", help="Specifies de tag for generated docker images")
parser.add_argument("--external_hostname", help="Specifies de tag for generated docker images")
parser.add_argument("--postgres_host", help="Specifies de tag for generated docker images")
parser.add_argument("--postgres_database", help="Specifies de tag for generated docker images")
parser.add_argument("--default_postgres_user", help="Specifies de tag for generated docker images")
parser.add_argument("--postgres_user", help="Specifies de tag for generated docker images")
parser.add_argument("--default_postgres_password", help="Postgresql and mariadb passwords")
parser.add_argument("--postgres_password", help="Postgresql and mariadb passwords")
parser.add_argument("--mysql_host", help="Specifies de tag for generated docker images")
parser.add_argument("--mysql_password", help="Postgresql and mariadb passwords")
parser.add_argument("--rtpengine_host", help="Specifies de tag for generated docker images")
parser.add_argument("--schedule", help="Specifies de tag for generated docker images")
parser.add_argument("--TZ", help="Specifies de tag for generated docker"
                    "images")
args = parser.parse_args()

# omininicontacto directorio raíz
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
inventory_path = os.path.join(base_dir, 'ansible/inventory')
inventory_file = open(inventory_path, 'r+')
inventory_contents = inventory_file.read()

if args.remote_port:
    remote_ssh_port = args.remote_port
else:
    remote_ssh_port = 22

if args.admin_password:
    admin_password = args.admin_password
else:
    admin_password = "098098ZZZ"

if args.ami_user:
    ami_user = args.ami_user
else:
    ami_user = "omnileadsami"

if args.ami_password:
    ami_password = args.ami_password
else:
    ami_password = "5_MeO_DMT"

if args.dialer_user:
    dialer_user = args.dialer_user
else:
    dialer_user = "demoadmin"

if args.dialer_password:
    dialer_password = args.dialer_password
else:
    dialer_password = "demo"

if args.mysql_password:
    mysql_password = args.mysql_password
else:
    mysql_password = "admin123"

if args.postgres_user:
    postgres_user = args.postgres_user
else:
    postgres_user = "omnileads"

if args.postgres_password:
    postgres_password = args.postgres_password
else:
    postgres_password = "admin123"

if args.TZ:
    TZ = args.TZ
else:
    TZ = "America/Argentina/Cordoba"

if args.postgres_database:
    inventory_contents = inventory_contents.replace(
        "postgres_database=omnileads", "postgres_database={0}".format(args.postgres_database))
if args.postgres_host and args.default_postgres_user and args.default_postgres_password:
    inventory_contents = inventory_contents.replace(
        "#postgres_host=", "postgres_host={0}".format(args.postgres_host))
    inventory_contents = inventory_contents.replace(
        "#default_postgres_user=", "default_postgres_user={0}".format(
            args.default_postgres_user))
    inventory_contents = inventory_contents.replace(
        "#default_postgres_password=", "default_postgres_password={0}".format(
            args.default_postgres_password))
if args.ecctl:
    inventory_contents = inventory_contents.replace(
        "ECCTL=28800", "ECCTL={0}".format(args.ecctl))
if args.external_hostname:
    inventory_contents = inventory_contents.replace(
        "#external_hostname=", "external_hostname={0}".format(args.external_hostname))
if args.mysql_host:
    inventory_contents = inventory_contents.replace(
        "#mysql_host=", "mysql_host={0}".format(args.mysql_host))
if args.rtpengine_host:
    inventory_contents = inventory_contents.replace(
        "#rtpengine_host=", "rtpengine_host={0}".format(args.rtpengine_host))
if args.sca:
    inventory_contents = inventory_contents.replace(
        "SCA=3600", "SCA={0}".format(args.sca))
if args.schedule:
    inventory_contents = inventory_contents.replace(
        "schedule=Agenda", "schedule={0}".format(args.schedule))
inventory_file.seek(0)
inventory_file.truncate()
inventory_file.write(inventory_contents)

if args.internal_ip and args.self_hosted == "no":
    # modificamos el setting que define el servidor externo donde se va a instalar
    # el sistema
    inventory_file.seek(0)
    inventory_file.truncate()
    inventory_file.write(inventory_contents.replace(
        "#X.X.X.X ansible_ssh_port=22 ansible_user=root"
        " #(this line is for node-host installation)",
        "{0} ansible_ssh_port={1} ansible_user=root".format(
            args.internal_ip, remote_ssh_port)).replace(
        "#TZ=America/Argentina/Cordoba", "TZ={0}".format(TZ)).replace(
        "#admin_pass=my_very_strong_pass", "admin_pass={0}".format(admin_password)).replace(
        "#postgres_password=my_very_strong_pass", "postgres_password={0}".format(
            postgres_password)).replace(
        "#mysql_root_password=my_very_strong_pass", "mysql_root_password={0}".format(
            mysql_password)).replace(
        "#postgres_user=omnileads", "postgres_user={0}".format(
            postgres_user)).replace(
        "#ami_user=omnileadsami", "ami_user={0}".format(ami_user)).replace(
        "#ami_password=5_MeO_DMT", "ami_password={0}".format(ami_password)).replace(
        "#dialer_user=demoadmin", "dialer_user={0}".format(dialer_user)).replace(
        "#dialer_password=demo", "dialer_password={0}".format(dialer_password)))
    sys.exit()

if args.self_hosted == "yes":
    # modificamos el setting que define el servidor externo donde se va a instalar
    # el sistema
    inventory_file.seek(0)
    inventory_file.truncate()
    inventory_file.write(inventory_contents.replace(
        "#localhost ansible_connection=local ansible_user=root"
        " #(this line is for self-hosted installation)",
        "localhost ansible_connection=local ansible_user=root").replace(
        "#TZ=America/Argentina/Cordoba", "TZ={0}".format(TZ)).replace(
        "#admin_pass=my_very_strong_pass", "admin_pass={0}".format(admin_password)).replace(
        "#postgres_password=my_very_strong_pass", "postgres_password={0}".format(
            postgres_password)).replace(
        "#mysql_root_password=my_very_strong_pass", "mysql_root_password={0}".format(
            mysql_password)).replace(
        "#postgres_user=omnileads", "postgres_user={0}".format(
            postgres_user)).replace(
        "#ami_user=omnileadsami", "ami_user={0}".format(ami_user)).replace(
        "#ami_password=5_MeO_DMT", "ami_password={0}".format(ami_password)).replace(
        "#dialer_user=demoadmin", "dialer_user={0}".format(dialer_user)).replace(
        "#dialer_password=demo", "dialer_password={0}".format(dialer_password)))
    sys.exit()

if args.docker_login_user and args.docker_login_email and args.docker_login_password \
   and args.tag_docker_images:
    # editamos las líneas del inventory que indican que se va hacer un build
    # de imágenes de producción de los componentes del sistema
    # 1) modificando inventory
    inventory_contents = inventory_contents.replace(
        "[prodenv-container]\n#localhost ansible_connection=local",
        "[prodenv-container]\nlocalhost ansible_connection=local")
    inventory_contents = inventory_contents.replace(
        "#TZ=America/Argentina/Cordoba", "TZ=America/Argentina/Cordoba")
    inventory_contents = inventory_contents.replace(
        "docker_user='{{ lookup(\"env\",\"SUDO_USER\") }}'", "docker_user='root'")
    inventory_contents = inventory_contents.replace(
        "registry_username=freetechsolutions", "registry_username={0}".format(
            args.docker_login_user))
    inventory_contents = inventory_contents.replace(
        "#registry_email=", "registry_email={0}".format(args.docker_login_email))
    inventory_contents = inventory_contents.replace(
        "#registry_password=", "registry_password={0}".format(args.docker_login_password))
    inventory_contents = inventory_contents.replace(
        "oml_release=", "oml_release={0}".format(args.tag_docker_images))
    inventory_contents = inventory_contents.replace(
        "#postgres_user=omnileads", "postgres_user=omnileads")
    inventory_contents = inventory_contents.replace(
        "#ami_user=omnileadsami", "ami_user=omnileadsami")
    inventory_contents = inventory_contents.replace(
        "#ami_password=5_MeO_DMT", "ami_password=5_MeO_DMT")
    inventory_file.seek(0)
    inventory_file.truncate()
    inventory_file.write(inventory_contents)
    sys.exit()
