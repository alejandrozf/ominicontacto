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

"""Vistas de reportes para campañas de tipo preview"""

from __future__ import unicode_literals

from collections import defaultdict

from django.db.models import Count
from django.views.generic import DetailView

from ominicontacto_app.models import Campana, CalificacionCliente, OpcionCalificacion


class CampanaPreviewDetailView(DetailView):
    template_name = 'campanas/campana_preview/detalle.html'
    model = Campana

    def _crear_dict_categorias(self, count_gestiones, finalizadas_categorias_count_dict):
        # se contabilizan juntas las calificaciones de tipo gestión con la etiqueta
        # 'Gestion'
        counts_categorias = defaultdict(int)

        for cat_data in finalizadas_categorias_count_dict:
            cat_count = cat_data['opcion_calificacion__nombre__count']
            cat_name = cat_data['opcion_calificacion__nombre']
            if cat_count > 0:
                counts_categorias[cat_name] = cat_count

        counts_categorias['Gestión'] += count_gestiones

        return dict(counts_categorias)

    def get_context_data(self, **kwargs):
        context = super(CampanaPreviewDetailView, self).get_context_data(**kwargs)
        campana = self.get_object()
        qs_campana_calificaciones = CalificacionCliente.objects.filter(
            opcion_calificacion__campana__pk=campana.pk)

        opciones_calificacion = campana.opciones_calificacion.all()
        context['opciones_calificacion'] = opciones_calificacion.values('nombre')
        context['opciones_calificacion_gestion'] = opciones_calificacion.filter(
            tipo=OpcionCalificacion.GESTION).values('nombre')
        context['terminadas'] = qs_campana_calificaciones.count()
        context['estimadas'] = campana.bd_contacto.contactos.count() - context['terminadas']

        if context['terminadas']:
            qs_finalizadas_gestiones = qs_campana_calificaciones.filter(
                opcion_calificacion__tipo=OpcionCalificacion.GESTION)
            qs_finalizadas_otras_categorias = qs_campana_calificaciones.exclude(
                opcion_calificacion__tipo=OpcionCalificacion.GESTION)

            finalizadas_gestiones_count = qs_finalizadas_gestiones.count()
            finalizadas_otras_categorias_count_dict = qs_finalizadas_otras_categorias.values(
                'opcion_calificacion__nombre').annotate(
                    Count('opcion_calificacion__nombre')).order_by()
            cats_dict = self._crear_dict_categorias(
                finalizadas_gestiones_count, finalizadas_otras_categorias_count_dict)
            context['categorias'] = cats_dict

        return context


class CampanaPreviewExpressView(CampanaPreviewDetailView):
    template_name = 'campanas/campana_preview/detalle_express.html'
