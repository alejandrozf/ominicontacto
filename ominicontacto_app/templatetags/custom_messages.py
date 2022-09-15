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
from django.template import Library

from django.utils.translation import gettext as _

from ominicontacto_app.utiles import get_oml_last_release
from ominicontacto_app import version

register = Library()

DEVELOP_MARK_VERSION = "0000000000000000000000000000000000000000"


@register.simple_tag
def advertencia_release_desactualizado():
    current_release = version.OML_BRANCH
    last_release_info = get_oml_last_release()
    if version.OML_COMMIT != DEVELOP_MARK_VERSION and current_release not in last_release_info \
       and last_release_info != []:
        return [_("Tienes una version antigua de OMniLeads."),
                _("Te recomendamos actualizar tu sistema"),
                _("Tu versión: {0}".format(current_release)),
                _("Versión actual: {0}".format(last_release_info[0]))]
    return ''
