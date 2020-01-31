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
parser.add_argument("--admin_pass", help="Omnileads admin web password")
parser.add_argument("--databases_pass", help="Postgresql and mariadb passwords")
parser.add_argument("--internal_ip", help="Sets internal IP in external server, "
                    "say 172.16.20.44")
parser.add_argument("--remote_port", help="Sets external ssh port to connect on remote server")
parser.add_argument("-dlu", "--docker_login_user", help="Username for docker hub")
parser.add_argument("-dle", "--docker_login_email", help="User email for docker hub")
parser.add_argument("-dlp", "--docker_login_password", help="User password for docker hub")
parser.add_argument("-tag", "--tag_docker_images", help="Specifies de tag for generated docker"
                    "images")
args = parser.parse_args()

# omininicontacto directorio raíz
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if args.self_hosted == "no" or args.docker_login_user is not None:
    inventory_path = os.path.join(base_dir, 'ansible/inventory')
else:
    inventory_path = '/var/tmp/ominicontacto/deploy/ansible/inventory'

inventory_file = open(inventory_path, 'r+')
inventory_contents = inventory_file.read()

if args.remote_port:
    remote_ssh_port = args.remote_port
else:
    remote_ssh_port = 22

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
                "#TZ=America/Argentina/Cordoba", "TZ=America/Argentina/Cordoba").replace(
                "#admin_pass=my_very_strong_pass", "admin_pass={0}".format(
                    args.admin_pass)).replace(
                "#postgres_password=my_very_strong_pass", "postgres_password={0}".format(
                    args.databases_pass)).replace(
                "#mysql_root_password=my_very_strong_pass", "mysql_root_password={0}".format(
                    args.databases_pass)))
    sys.exit()

if args.internal_ip and args.self_hosted == "yes":
    # modificamos el setting que define el servidor externo donde se va a instalar
    # el sistema
    inventory_file.seek(0)
    inventory_file.truncate()
    inventory_file.write(inventory_contents.replace(
        "#localhost ansible_connection=local ansible_user=root"
        " #(this line is for self-hosted installation)",
        "localhost ansible_connection=local ansible_user=root").replace(
        "#TZ=America/Argentina/Cordoba", "TZ=America/Argentina/Cordoba").replace(
            "#admin_pass=my_very_strong_pass", "admin_pass={0}".format(args.admin_pass)).replace(
            "#postgres_password=my_very_strong_pass", "postgres_password={0}".format(
                args.databases_pass)).replace(
            "#mysql_root_password=my_very_strong_pass", "mysql_root_password={0}".format(
                args.databases_pass)))
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
        "registry_username=", "registry_username={0}".format(args.docker_login_user))
    inventory_contents = inventory_contents.replace(
        "registry_email=", "registry_email={0}".format(args.docker_login_email))
    inventory_contents = inventory_contents.replace(
        "registry_password=", "registry_password={0}".format(args.docker_login_password))
    inventory_contents = inventory_contents.replace(
        "oml_release=", "oml_release={0}".format(args.tag_docker_images))
    inventory_file.seek(0)
    inventory_file.truncate()
    inventory_file.write(inventory_contents)
    sys.exit()
