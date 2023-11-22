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

"""Aca se encuentran las vistas para agregar los agente a la campañas/cola
por la relacion esta en cola ya que se hizo con un modelo de queue sacado de la
documentacion de asterisk"""

from django.views.generic import TemplateView
from ominicontacto_app.models import Campana


class QueueMemberCampanaView(TemplateView):
    """Vista template despliega el template de cual se van agregar agente o grupos de
    agentes a la campana"""
    template_name = 'queue/queue_member.html'

    def get_object(self, queryset=None):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        return campana.queue_campana

    def get_context_data(self, **kwargs):
        context = super(QueueMemberCampanaView, self).get_context_data(**kwargs)
        campana = self.get_object().campana
        context['campana'] = campana
        return context
