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

# este script es invocado como AGI desde 'oml_extensions_sub.conf' para detectar si un télefono
# discado está en una lista negra (no está permitido llamar), cuyo valor escribe en el canal
# correspondiente en la variable BLACKLIST

import sys
from socket import setdefaulttimeout

from asterisk.agi import AGI

from config import configParser
from utiles import write_time_stderr


sys.stderr = open('{{ install_prefix }}log/agis-errors.log', 'a')

setdefaulttimeout(20)

agi = AGI()

phone_number = sys.argv[1]
black_list_file = configParser.get('OML', 'BLACK_LIST_FIlE')

with open(black_list_file, 'r') as f:
    is_black_listed = int(f.read().find(phone_number) != -1)

try:
    agi.set_variable('BLACKLIST', str(is_black_listed))
except Exception as e:
    write_time_stderr("Unable to set variable BLACKLIST in channel due to {0}".format(e.message))
    raise e
