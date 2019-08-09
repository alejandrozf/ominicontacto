#!/usr/bin/env python
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
#

"""
Script para ejecutar SOLO en las tareas de CI/CD para impedir que se suban ramas con
un número de tarjeta que ya mergeado en el repositorio
"""

import os
import re
import sys


def numero_rama_existente(numero_tarjeta, tipo_tarjeta):
    if tipo_tarjeta == 'ext':
        # los numeros de las ramas externas no vienen de jira,
        # por lo que solo se controla entre esas ramas
        str_check = 'oml-{}-ext'.format(numero_tarjeta)
    else:
        str_check = 'oml-{}'.format(numero_tarjeta)
    check = os.popen('git log --oneline --grep=\'{}\''.format(str_check)).read()
    return check != ''


if not os.getenv('IS_CICD'):
    ramas = os.popen('git branch').read()
    rama_actual = re.search(r'\n\* (.+)\n', ramas).group(1)
else:
    rama_actual = os.getenv('CI_COMMIT_REF_NAME')

if rama_actual.startswith('oml'):
    rama_regex_search = re.search(
        r'oml-(\d+)-(ext|doc|dev|fix|hotfix|epica)-+.', rama_actual)
    numero_tarjeta = rama_regex_search.group(1)
    tipo_tarjeta = rama_regex_search.group(2)
    sys.exit(int(numero_rama_existente(numero_tarjeta, tipo_tarjeta)))
