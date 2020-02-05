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
from __future__ import unicode_literals

import logging

from compressor.management.commands.compress import Command as CompressorCommand

import inspect


def isfunction(obj):
    return hasattr(type(obj), "__code__")


inspect.isfunction = isfunction

logger = logging.getLogger(__name__)


class Command(CompressorCommand):
    """Un commando personalizado que usa el comando 'compress'
    pero permite cargar funciones cython
    """
