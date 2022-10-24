# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3, as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

"""Vista relacionada con la creacion de una calificacion en el sentido no llamar,
no interesado,etc y luego la agrupacion de la misma en un grupo lo cual se va utilizar
 para la creacion de una campana en el momento de ser calificada"""
from django.views.generic import TemplateView


class CalificacionListView(TemplateView):
    """
    Esta vista es para generar el listado de sitios externos.
    """
    template_name = 'calificacion/calificacion_list.html'
