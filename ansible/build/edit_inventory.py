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

parser.add_argument("--docker_build", help="Modifies for build of docker images")
parser.add_argument("-dle", "--docker_login_email", help="User email for docker hub")
parser.add_argument("-dlp", "--docker_login_password", help="User password for docker hub")
parser.add_argument("--aio_build", help="Modifies for build of rpms")
args = parser.parse_args()

# omininicontacto directorio raíz
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
inventory_path = os.path.join(base_dir, 'build/inventory')
inventory_file = open(inventory_path, 'r+')
inventory_contents = inventory_file.read()

if args.docker_login_email and args.docker_login_password \
        and args.docker_build == "yes":
    # editamos las líneas del inventory que indican que se va hacer un build
    # de imágenes de producción de los componentes del sistema
    # 1) modificando inventory
    inventory_contents = inventory_contents.replace(
        "[build-docker]\n#localhost ansible_connection=local",
        "[build-docker]\nlocalhost ansible_connection=local")
    inventory_contents = inventory_contents.replace(
        "#registry_email=", "registry_email={0}".format(args.docker_login_email))
    inventory_contents = inventory_contents.replace(
        "#registry_password=", "registry_password={0}".format(args.docker_login_password))
    inventory_file.seek(0)
    inventory_file.truncate()
    inventory_file.write(inventory_contents)
    sys.exit()

if args.aio_build == 'yes':
    inventory_contents = inventory_contents.replace(
        "[build-aio]\n#localhost ansible_connection=local",
        "[build-aio]\nlocalhost ansible_connection=local")
    inventory_file.seek(0)
    inventory_file.truncate()
    inventory_file.write(inventory_contents)
    sys.exit()
