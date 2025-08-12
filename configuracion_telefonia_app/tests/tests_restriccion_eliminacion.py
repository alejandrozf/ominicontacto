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

from mock import patch
from django.urls import reverse
from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.tests.factories import CampanaFactory
from ominicontacto_app.models import Campana
from ominicontacto_app.views_campana import CampanaDeleteView
from configuracion_telefonia_app.tests.factories import (
    RutaEntranteFactory, IVRFactory, ValidacionFechaHoraFactory, OpcionDestinoFactory)
from configuracion_telefonia_app.models import (
    ValidacionFechaHora, DestinoEntrante, OpcionDestino)
from configuracion_telefonia_app.views.base import ValidacionFechaHoraDeleteView
from configuracion_telefonia_app.views.base import DeleteNodoDestinoMixin
from whatsapp_app.tests.factories import LineaFactory, MenuInteractivoFactory
from whatsapp_app.models import OpcionMenuInteractivoWhatsapp


class BaseTestRestriccionEliminacion(OMLBaseTest):
    PWD = u'admin123'

    def setUp(self, *args, **kwargs):
        super(BaseTestRestriccionEliminacion, self).setUp(*args, **kwargs)
        self._crear_campanas_entrantes()

        self.admin = self.crear_administrador()
        self.admin.set_password(self.PWD)
        self.client.login(username=self.admin.username, password=self.PWD)

    def _crear_campanas_entrantes(self):
        self.camp_1 = CampanaFactory(type=Campana.TYPE_ENTRANTE, estado=Campana.ESTADO_ACTIVA)
        self.camp_2 = CampanaFactory(type=Campana.TYPE_ENTRANTE, estado=Campana.ESTADO_ACTIVA)
        self.nodo_camp_1 = DestinoEntrante.crear_nodo_ruta_entrante(self.camp_1)
        self.nodo_camp_2 = DestinoEntrante.crear_nodo_ruta_entrante(self.camp_2)


class TestRestriccionEliminacionValidacionFechaHora(BaseTestRestriccionEliminacion):

    @patch('configuracion_telefonia_app.regeneracion_configuracion_telefonia.'
           'SincronizadorDeConfiguracionValidacionFechaHoraAsterisk.eliminar_y_regenerar_asterisk')
    def test_elimina_validacion_fecha_hora_ok(self, mock_sincronizacion):
        # Creo una Validacion Fecha Hora que no es destino
        destinos_iniciales = DestinoEntrante.objects.count()
        validacion_fh = ValidacionFechaHoraFactory()
        nodo_validacion = DestinoEntrante.crear_nodo_ruta_entrante(validacion_fh)
        OpcionDestinoFactory(valor='True',
                             destino_anterior=nodo_validacion,
                             destino_siguiente=self.nodo_camp_1)
        OpcionDestinoFactory(valor='False',
                             destino_anterior=nodo_validacion,
                             destino_siguiente=self.nodo_camp_2)
        url = reverse('eliminar_validacion_fecha_hora', args=[validacion_fh.id])
        response = self.client.post(url, follow=True)
        mock_sincronizacion.assert_called_with(validacion_fh)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ValidacionFechaHoraDeleteView.nodo_eliminado)
        self.assertEqual(ValidacionFechaHora.objects.count(), 0)
        self.assertEqual(DestinoEntrante.objects.count(), destinos_iniciales)
        self.assertEqual(OpcionDestino.objects.count(), 0)

    @patch('configuracion_telefonia_app.regeneracion_configuracion_telefonia.'
           'SincronizadorDeConfiguracionValidacionFechaHoraAsterisk.eliminar_y_regenerar_asterisk')
    def test_no_elimina_validacion_fecha_hora_utilizado_en_ruta_entrante(self, mock_sincronizacion):
        # Creo una validacion fecha hora y la pongo como destino de una Ruta Entrante
        destinos_iniciales = DestinoEntrante.objects.count()
        validacion_fh = ValidacionFechaHoraFactory()
        nodo_validacion = DestinoEntrante.crear_nodo_ruta_entrante(validacion_fh)
        OpcionDestinoFactory(valor='True',
                             destino_anterior=nodo_validacion,
                             destino_siguiente=self.nodo_camp_1)
        OpcionDestinoFactory(valor='False',
                             destino_anterior=nodo_validacion,
                             destino_siguiente=self.nodo_camp_2)
        RutaEntranteFactory(destino=nodo_validacion)
        url = reverse('eliminar_validacion_fecha_hora', args=[validacion_fh.id])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        list_url = reverse('lista_validaciones_fecha_hora', args=(1,))
        self.assertFalse(mock_sincronizacion.called)
        mock_sincronizacion.assert_not_called()
        self.assertRedirects(response, list_url)
        self.assertContains(response, ValidacionFechaHoraDeleteView.imposible_eliminar)
        self.assertEqual(ValidacionFechaHora.objects.count(), 1)
        self.assertEqual(DestinoEntrante.objects.count(), destinos_iniciales + 1)

    @patch('configuracion_telefonia_app.regeneracion_configuracion_telefonia.'
           'SincronizadorDeConfiguracionValidacionFechaHoraAsterisk.eliminar_y_regenerar_asterisk')
    def test_no_elimina_validacion_fecha_hora_destino_de_otro_nodo(self, mock_sincronizacion):
        # Creo un Validacion Fecha Hora y lo pongo como destino de un IVR
        ivr = IVRFactory()
        nodo_ivr = DestinoEntrante.crear_nodo_ruta_entrante(ivr)
        validacion_fh = ValidacionFechaHoraFactory()
        nodo_validacion = DestinoEntrante.crear_nodo_ruta_entrante(validacion_fh)
        OpcionDestinoFactory(valor='False',
                             destino_anterior=nodo_ivr,
                             destino_siguiente=nodo_validacion)
        destinos_iniciales = DestinoEntrante.objects.count()
        url = reverse('eliminar_validacion_fecha_hora', args=[validacion_fh.id])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(mock_sincronizacion.called)
        list_url = reverse('lista_validaciones_fecha_hora', args=(1,))
        self.assertRedirects(response, list_url)
        self.assertContains(response, ValidacionFechaHoraDeleteView.imposible_eliminar)
        self.assertEqual(ValidacionFechaHora.objects.count(), 1)
        self.assertEqual(DestinoEntrante.objects.count(), destinos_iniciales)


class TestRestriccionEliminacionCampanaEntrante(BaseTestRestriccionEliminacion):

    @patch('ominicontacto_app.services.creacion_queue.ActivacionQueueService'
           '.sincronizar_por_eliminacion')
    def test_elimina_campana_ok(self, sincronizar_por_eliminacion):
        # Intento Eliminar una Campaña que no es destino
        total_campanas = Campana.objects.count()
        campanas_iniciales = Campana.objects.filter(estado=Campana.ESTADO_ACTIVA).count()
        destinos_iniciales = DestinoEntrante.objects.count()
        url = reverse('campana_elimina', args=[self.camp_1.id])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u'Se llevó a cabo con éxito la eliminación de la campana')
        self.assertEqual(Campana.objects.count(), total_campanas)
        self.assertEqual(Campana.objects.filter(estado=Campana.ESTADO_ACTIVA).count(),
                         campanas_iniciales - 1)
        self.assertEqual(DestinoEntrante.objects.count(), destinos_iniciales - 1)
        sincronizar_por_eliminacion.assert_called()

    def test_no_elimina_campana_utilizado_en_ruta_entrante(self):
        # Pongo la campaña entrante 1 como destino de una Ruta Entrante
        destinos_iniciales = DestinoEntrante.objects.count()
        campanas_iniciales = Campana.objects.filter(estado=Campana.ESTADO_ACTIVA).count()
        RutaEntranteFactory(destino=self.nodo_camp_1)
        url = reverse('campana_elimina', args=[self.camp_1.id])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        list_url = reverse('campana_list')
        self.assertRedirects(response, list_url)
        self.assertContains(response, CampanaDeleteView.imposible_eliminar)
        self.assertEqual(Campana.objects.filter(estado=Campana.ESTADO_ACTIVA).count(),
                         campanas_iniciales)
        self.assertEqual(DestinoEntrante.objects.count(), destinos_iniciales)

    def test_no_elimina_campana_destino_de_otro_nodo(self):
        # Pongo la campaña entrante 1 como destino de un IVR
        ivr = IVRFactory()
        nodo_ivr = DestinoEntrante.crear_nodo_ruta_entrante(ivr)
        OpcionDestinoFactory(valor='False',
                             destino_anterior=nodo_ivr,
                             destino_siguiente=self.nodo_camp_1)
        destinos_iniciales = DestinoEntrante.objects.count()
        campanas_iniciales = Campana.objects.filter(estado=Campana.ESTADO_ACTIVA).count()
        url = reverse('campana_elimina', args=[self.camp_1.id])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        list_url = reverse('campana_list')
        self.assertRedirects(response, list_url)
        self.assertContains(response, CampanaDeleteView.imposible_eliminar)
        self.assertEqual(Campana.objects.filter(estado=Campana.ESTADO_ACTIVA).count(),
                         campanas_iniciales)
        self.assertEqual(DestinoEntrante.objects.count(), destinos_iniciales)

    def test_no_elimina_campana_destino_directo_linea(self):
        linea = LineaFactory(destino=self.nodo_camp_1, created_by=self.admin, updated_by=self.admin)
        url = reverse('campana_elimina', args=[self.camp_1.id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('campana_list'))
        msg = DeleteNodoDestinoMixin.ERROR_DESTINO_LINEA.format(", ".join([linea.nombre, ]))
        self.assertContains(response, msg)

    def test_no_elimina_campana_destino_menu_interactivo_linea(self):
        menu = MenuInteractivoFactory()
        destino_menu = DestinoEntrante.crear_nodo_ruta_entrante(menu)
        opcion_destino_1 = OpcionDestino.crear_opcion_destino(
            destino_anterior=destino_menu, destino_siguiente=self.nodo_camp_1,
            valor='Campana 1')
        OpcionMenuInteractivoWhatsapp.objects.create(
            opcion=opcion_destino_1, descripcion='Descripcion opcion 1')
        linea = LineaFactory(destino=destino_menu, created_by=self.admin, updated_by=self.admin)
        menu.line = linea
        menu.save()
        url = reverse('campana_elimina', args=[self.camp_1.id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('campana_list'))
        msg = DeleteNodoDestinoMixin.ERROR_DESTINO_LINEA.format(", ".join([linea.nombre, ]))
        self.assertContains(response, msg)
