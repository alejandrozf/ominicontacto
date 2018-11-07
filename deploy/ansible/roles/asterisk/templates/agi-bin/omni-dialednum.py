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

import os
import sys
from socket import setdefaulttimeout

from asterisk.agi import AGI

from config import configParser
from utiles import write_time_stderr

sys.stderr = open('{{ install_prefix }}log/agis-errors.log', 'a')

setdefaulttimeout(20)

agi = AGI()

ASTERISK_LISTS = configParser.get('OML', 'ASTERISK_LISTS')
phone_number = sys.argv[1]
camp_id = sys.argv[2]

campaign_dialed_number_file = os.path.join(ASTERISK_LISTS, "/oml_{0}_dialednum.txt".format(camp_id))

with open(campaign_dialed_number_file, 'r') as f:
    is_dialed = int(f.read().find(phone_number) != -1)

try:
    agi.set_variable('OMLDIALEDNUM', str(is_dialed))
except Exception as e:
    write_time_stderr("Unable to set variable OMLDIALEDNUM in channel due to {0}".format(e.message))
    raise e
