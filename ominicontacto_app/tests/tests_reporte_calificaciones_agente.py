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

"""
Tests vista de listado de calificaciones de Agente
"""

from mock import patch
from django.urls import reverse

from ominicontacto_app.utiles import fecha_local
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.tests.factories import (
    CampanaFactory, OpcionCalificacionFactory, CalificacionClienteFactory, ContactoFactory,
    AuditoriaCalificacionFactory)
from ominicontacto_app.models import Campana, OpcionCalificacion, AuditoriaCalificacion
from ominicontacto_app.services.reporte_agente_calificacion import ReporteAgenteService
from ominicontacto_app.services.reporte_agente_venta import ReporteFormularioVentaService


class AgenteReporteCalificacionesTest(OMLBaseTest):

    def setUp(self):
        super(AgenteReporteCalificacionesTest, self).setUp()
        self.agente = self.crear_agente_profile()
        self.campana = CampanaFactory(estado=Campana.ESTADO_ACTIVA, type=Campana.TYPE_MANUAL)
        self.contacto1 = ContactoFactory(bd_contacto=self.campana.bd_contacto)
        self.contacto2 = ContactoFactory(bd_contacto=self.campana.bd_contacto)
        self.opcion1 = OpcionCalificacionFactory(campana=self.campana,
                                                 tipo=OpcionCalificacion.GESTION)
        self.opcion2 = OpcionCalificacionFactory(campana=self.campana,
                                                 tipo=OpcionCalificacion.GESTION)

        self.calificacion1 = CalificacionClienteFactory(
            opcion_calificacion=self.opcion1, agente=self.agente, contacto=self.contacto1)
        self.auditoria1 = AuditoriaCalificacionFactory(
            resultado=AuditoriaCalificacion.APROBADA, calificacion=self.calificacion1)
        self.calificacion2 = CalificacionClienteFactory(
            opcion_calificacion=self.opcion2, agente=self.agente, contacto=self.contacto2)
        self.auditoria2 = AuditoriaCalificacionFactory(
            resultado=AuditoriaCalificacion.RECHAZADA, calificacion=self.calificacion2)

        self.client.login(username=self.agente.user.username, password=PASSWORD)

    @patch.object(ReporteAgenteService, 'crea_reporte_csv')
    @patch.object(ReporteFormularioVentaService, 'crea_reporte_csv')
    def test_filtros_por_resultado(self, crea_reporte_formulario, crea_reporte_agente):
        url = reverse('reporte_agente_calificaciones')
        response = self.client.get(url, follow=True)
        self.assertContains(response, self.contacto1.telefono)
        self.assertContains(response, self.contacto2.telefono)

        fecha = fecha_local(self.calificacion1.fecha).strftime('%d/%m/%Y')
        filtro_fecha = '-'.join((fecha, fecha))
        filtros = {'fecha': filtro_fecha, 'resultado_auditoria': AuditoriaCalificacion.APROBADA}
        response = self.client.post(url, filtros, follow=True)
        self.assertContains(response, self.contacto1.telefono)
        self.assertNotContains(response, self.contacto2.telefono)
