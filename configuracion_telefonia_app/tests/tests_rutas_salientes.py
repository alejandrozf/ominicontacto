# -*- coding: utf-8 -*-

from mock import patch
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from ominicontacto_app.tests.utiles import OMLBaseTest

from configuracion_telefonia_app.tests.factories import (
    TroncalSIPFactory, RutaSalienteFactory, OrdenTroncalFactory, PatronDeDiscadoFactory)
from configuracion_telefonia_app.models import (
    TroncalSIP, RutaSaliente, OrdenTroncal, PatronDeDiscado)


class TestsRutasSalientes(OMLBaseTest):
    PWD = u'admin123'

    def setUp(self, *args, **kwargs):
        super(TestsRutasSalientes, self).setUp(*args, **kwargs)
        self._crear_troncales_y_rutas()

        self.admin = self.crear_administrador()
        self.admin.set_password(self.PWD)

    def _crear_troncales_y_rutas(self):
        self.troncal_1 = TroncalSIPFactory()
        self.troncal_2 = TroncalSIPFactory()

        self.ruta_1 = RutaSalienteFactory()
        self.patron_1_1 = PatronDeDiscadoFactory(ruta_saliente=self.ruta_1)
        self.patron_1_2 = PatronDeDiscadoFactory(ruta_saliente=self.ruta_1)
        self.orden_1_1 = OrdenTroncalFactory(ruta_saliente=self.ruta_1, orden=1,
                                             troncal=self.troncal_1)
        self.orden_1_2 = OrdenTroncalFactory(ruta_saliente=self.ruta_1, orden=2,
                                             troncal=self.troncal_2)

        self.ruta_2 = RutaSalienteFactory()
        self.patron_2_1 = PatronDeDiscadoFactory(ruta_saliente=self.ruta_2)
        self.patron_2_2 = PatronDeDiscadoFactory(ruta_saliente=self.ruta_2)
        self.orden_2_1 = OrdenTroncalFactory(ruta_saliente=self.ruta_2, orden=1,
                                             troncal=self.troncal_1)

    def test_supervisor_normal_no_puede_eliminar(self):
        usr_sup = self.crear_user_supervisor()
        self.crear_supervisor_profile(usr_sup)
        url = reverse('eliminar_ruta_saliente', args=[self.ruta_1.id])
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_administrador_puede_eliminar(self):
        self.client.login(username=self.admin.username, password=self.PWD)
        url = reverse('eliminar_ruta_saliente', args=[self.ruta_1.id])
        self.assertEqual(TroncalSIP.objects.count(), 2)
        self.assertEqual(RutaSaliente.objects.count(), 2)
        self.assertEqual(PatronDeDiscado.objects.count(), 4)
        self.assertEqual(OrdenTroncal.objects.count(), 3)
        self.client.post(url, follow=True)
        self.assertEqual(TroncalSIP.objects.count(), 2)
        self.assertEqual(RutaSaliente.objects.count(), 1)
        self.assertEqual(PatronDeDiscado.objects.count(), 2)
        self.assertEqual(OrdenTroncal.objects.count(), 1)

    def test_lista_troncales_huerfanos(self):
        self.client.login(username=self.admin.username, password=self.PWD)
        url = reverse('eliminar_ruta_saliente', args=[self.ruta_1.id])
        response = self.client.get(url, follow=True)
        self.assertContains(response, self.troncal_2.nombre)
        self.assertNotContains(response, self.troncal_1.nombre)

    @patch('configuracion_telefonia_app.views.eliminar_ruta_saliente_config')
    def test_elimina_RutaSaliente(self, mock_sincronizacion):
        mock_sincronizacion.return_value = True
        self.client.login(username=self.admin.username, password=self.PWD)
        url = reverse('eliminar_ruta_saliente', args=[self.ruta_1.id])
        response = self.client.post(url, follow=True)
        self.assertContains(response, _(u'Se ha eliminado la Ruta Saliente.'))
        self.assertTrue(mock_sincronizacion.called)
        self.assertEqual(TroncalSIP.objects.count(), 2)
        self.assertEqual(RutaSaliente.objects.count(), 1)
        self.assertEqual(PatronDeDiscado.objects.count(), 2)
        self.assertEqual(OrdenTroncal.objects.count(), 1)

    @patch('configuracion_telefonia_app.views.eliminar_ruta_saliente_config')
    def test_no_elimina_RutaSaliente_al_fallar_sincronizacion_con_asterisk(self,
                                                                           mock_sincronizacion):
        mock_sincronizacion.side_effect = Exception('Boom!')
        mock_sincronizacion.return_value = False
        self.client.login(username=self.admin.username, password=self.PWD)
        url = reverse('eliminar_ruta_saliente', args=[self.ruta_1.id])
        response = self.client.post(url, follow=True)
        self.assertContains(response, _(u'No se ha podido eliminar la Ruta Saliente.'))
        self.assertTrue(mock_sincronizacion.called)
        self.assertEqual(TroncalSIP.objects.count(), 2)
        self.assertEqual(RutaSaliente.objects.count(), 2)
        self.assertEqual(PatronDeDiscado.objects.count(), 4)
        self.assertEqual(OrdenTroncal.objects.count(), 3)

    def test_supervisor_normal_no_puede_crear_ruta_saliente(self):
        usr_sup = self.crear_user_supervisor()
        self.crear_supervisor_profile(usr_sup)
        usr_sup.set_password(self.PWD)
        self.client.login(username=usr_sup.username, password=self.PWD)
        url = reverse('crear_ruta_saliente')
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_supervisor_normal_no_puede_modificar_ruta_saliente(self):
        usr_sup = self.crear_user_supervisor()
        self.crear_supervisor_profile(usr_sup)
        usr_sup.set_password(self.PWD)
        self.client.login(username=usr_sup.username, password=self.PWD)
        url = reverse('editar_ruta_saliente', args=[self.ruta_1.id])
        post_data = {}
        response = self.client.post(url, post_data, follow=True)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_administrador_puede_crear_ruta_saliente(self):
        self.client.login(username=self.admin.username, password=self.PWD)
        post_data = {
            'nombre': 'test',
            'ring_time': 1,
            'dial_options': 'Tt',
            'patron_discado-0-prepend': 3,
            'patron_discado-0-prefix': 4,
            'patron_discado-0-match_pattern': '5',
            'patron_discado-1-prepend': 6,
            'patron_discado-1-prefix': 7,
            'patron_discado-1-match_pattern': '8',
            'orden_troncal-0-troncal': self.orden_1_1.troncal.pk,
            'orden_troncal-0-id': self.orden_1_1.pk,
            'orden_troncal-1-troncal': self.orden_1_2.troncal.pk,
            'orden_troncal-1-id': self.orden_1_2.pk,
            'patron_discado-TOTAL_FORMS': 2,
            'patron_discado-INITIAL_FORMS': 0,
            'patron_discado-MIN_NUM_FORMS': 1,
            'patron_discado-MAX_NUM_FORMS': 1000,
            'orden_troncal-TOTAL_FORMS': 2,
            'orden_troncal-INITIAL_FORMS': 0,
            'orden_troncal-MIN_NUM_FORMS': 1,
            'orden_troncal-MAX_NUM_FORMS': 1000,
        }
        url = reverse('crear_ruta_saliente')
        n_rutas_salientes = RutaSaliente.objects.count()
        self.client.post(url, post_data, follow=True)
        self.assertEqual(RutaSaliente.objects.count(), n_rutas_salientes + 1)

    def test_administrador_puede_modificar_ruta_saliente(self):
        self.client.login(username=self.admin.username, password=self.PWD)
        nuevo_nombre = 'ruta_1_modificada'
        post_data = {
            'nombre': nuevo_nombre,
            'ring_time': 4,
            'dial_options': 'Tt',
            'patron_discado-0-prepend': 23,
            'patron_discado-0-prefix': 2,
            'patron_discado-0-match_pattern': '3',
            'patron_discado-0-id': self.patron_1_1.pk,
            'patron_discado-1-prepend': 2,
            'patron_discado-1-prefix': 1,
            'patron_discado-1-match_pattern': '2',
            'patron_discado-1-id': self.patron_1_2.pk,
            'orden_troncal-0-troncal': self.orden_1_1.troncal.pk,
            'orden_troncal-0-id': self.orden_1_1.pk,
            'orden_troncal-1-troncal': self.orden_1_2.troncal.pk,
            'orden_troncal-1-id': self.orden_1_2.pk,
            'patron_discado-TOTAL_FORMS': 2,
            'patron_discado-INITIAL_FORMS': 2,
            'patron_discado-MIN_NUM_FORMS': 1,
            'patron_discado-MAX_NUM_FORMS': 1000,
            'orden_troncal-TOTAL_FORMS': 2,
            'orden_troncal-INITIAL_FORMS': 2,
            'orden_troncal-MIN_NUM_FORMS': 1,
            'orden_troncal-MAX_NUM_FORMS': 1000,
        }
        url = reverse('editar_ruta_saliente', args=[self.ruta_1.pk])
        self.client.post(url, post_data, follow=True)
        self.ruta_1.refresh_from_db()
        self.assertEqual(self.ruta_1.nombre, nuevo_nombre)
