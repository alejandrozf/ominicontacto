# -*- coding: utf-8 -*-

"""
Tests relacionados con las grabaciones
"""
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.timezone import now, timedelta

from ominicontacto_app.models import Grabacion, GrabacionMarca

from ominicontacto_app.tests.factories import GrabacionFactory, GrabacionMarcaFactory, UserFactory
from ominicontacto_app.tests.utiles import OMLBaseTest


class BaseGrabacionesTests(OMLBaseTest):

    PWD = 'admin123'

    def setUp(self):
        self.usuario_admin_supervisor = UserFactory(is_staff=True, is_supervisor=True)
        self.usuario_admin_supervisor.set_password(self.PWD)
        self.usuario_admin_supervisor.save()

        self.user_agente = self.crear_user_agente()
        self.agente_profile = self.crear_agente_profile(self.user_agente)
        sip_extension = self.agente_profile.sip_extension

        self.grabacion1 = GrabacionFactory.create(duracion=0, sip_agente=sip_extension)
        self.grabacion2 = GrabacionFactory.create(duracion=0, sip_agente=sip_extension)
        self.grabacion3 = GrabacionFactory.create(duracion=0, sip_agente=sip_extension)
        self.marca_campana1 = GrabacionMarcaFactory.create(uid=self.grabacion1.uid)
        self.marca_campana2 = GrabacionMarcaFactory.create(uid=self.grabacion2.uid)

        self.client.login(username=self.usuario_admin_supervisor.username,
                          password=self.PWD)


class GrabacionesTests(BaseGrabacionesTests):

    def test_vista_creacion_grabaciones_marcadas(self):
        url = reverse('grabacion_marcar')
        descripcion = 'descripcion de prueba'
        post_data = {'uid': self.grabacion3.uid,
                     'descripcion': descripcion}
        self.client.post(url, post_data)

        self.assertTrue(GrabacionMarca.objects.filter(
            uid=self.grabacion3.uid, descripcion=descripcion).exists())

    def test_usuarios_no_logueados_no_acceden_a_vista_creacion_grabaciones_marcadas(self):
        self.client.logout()
        url = reverse('grabacion_marcar')
        descripcion = 'descripcion de prueba'
        post_data = {'uid': self.grabacion3.uid,
                     'descripcion': descripcion}
        self.client.post(url, post_data)
        self.assertFalse(GrabacionMarca.objects.filter(
            uid=self.grabacion3.uid, descripcion=descripcion).exists())

    def test_usuarios_no_logueados_no_acceden_a_obtener_descripciones_grabaciones(self):
        self.client.logout()
        url = reverse('grabacion_descripcion', kwargs={'uid': self.grabacion1.uid})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.template_name, 'registration/login.html')

    def test_respuesta_api_descripciones_grabaciones_marcadas(self):
        url = reverse('grabacion_descripcion', kwargs={'uid': self.grabacion2.uid})
        response = self.client.get(url, follow=True)
        data_response = json.loads(response.content)
        self.assertEqual(data_response['result'], 'Descripción')

    def test_respuesta_api_descripciones_grabaciones_no_marcadas(self):
        url = reverse('grabacion_descripcion', kwargs={'uid': self.grabacion3.uid})
        response = self.client.get(url, follow=True)
        data_response = json.loads(response.content)
        self.assertEqual(data_response['result'], 'No encontrada')

    def test_url_de_grabacion_segun_fecha(self):
        hoy = now()
        hace_mucho = hoy - timedelta(days=3)
        self.grabacion2.fecha = hace_mucho
        self.grabacion1.fecha = hoy
        self.assertTrue(self.grabacion2.url.endswith(settings.MONITORFORMAT))
        self.assertTrue(self.grabacion1.url.endswith('.wav'))


class FiltrosGrabacionesTests(BaseGrabacionesTests):

    def test_filtro_grabaciones_marcadas(self):
        self.assertEqual(Grabacion.objects.marcadas().count(), 2)

    def test_buscar_grabaciones_por_duracion(self):
        Grabacion.objects.filter(id=self.grabacion2.id).update(duracion=15, tel_cliente='42222222')
        Grabacion.objects.filter(id=self.grabacion1.id).update(duracion=15, tel_cliente='41111111')
        Grabacion.objects.filter(id=self.grabacion3.id).update(duracion=12, tel_cliente='43333333')
        url = reverse('grabacion_buscar', kwargs={'pagina': 1})
        post_data = {'fecha': '', 'tipo_llamada': '', 'tel_cliente': '', 'sip_agente': '',
                     'campana': '', 'marcadas': '', 'duracion': '0'}

        post_data['duracion'] = 12
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, '41111111')
        self.assertContains(response, '42222222')
        self.assertContains(response, '43333333')

        post_data['duracion'] = 15
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, '41111111')
        self.assertContains(response, '42222222')
        self.assertNotContains(response, '43333333')

        post_data['duracion'] = 16
        response = self.client.post(url, post_data, follow=True)
        self.assertNotContains(response, '41111111')
        self.assertNotContains(response, '42222222')
        self.assertNotContains(response, '43333333')

    def _obtener_fechas(self):
        hoy = now()
        hace_mucho = hoy - timedelta(days=3)
        ahora = now()
        return (hoy, hace_mucho, ahora)

    def test_buscar_grabaciones_por_fecha(self):
        (hoy, hace_mucho, ahora) = self._obtener_fechas()
        if hoy.date() < ahora.date():
            (hoy, hace_mucho, ahora) = self._obtener_fechas()
        Grabacion.objects.filter(id=self.grabacion2.id).update(fecha=hace_mucho,
                                                               tel_cliente='42222222')
        Grabacion.objects.filter(id=self.grabacion1.id).update(fecha=hoy, tel_cliente='41111111')
        Grabacion.objects.filter(id=self.grabacion3.id).update(fecha=hoy, tel_cliente='43333333')
        url = reverse('grabacion_buscar', kwargs={'pagina': 1})
        post_data = {'fecha': '', 'tipo_llamada': '', 'tel_cliente': '', 'sip_agente': '',
                     'campana': '', 'marcadas': '', 'duracion': '0'}

        rango_hace_mucho = hace_mucho.date().strftime('%d/%m/%Y') + ' - ' + \
            ahora.date().strftime('%d/%m/%Y')
        post_data['fecha'] = rango_hace_mucho
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, '41111111')
        self.assertContains(response, '42222222')
        self.assertContains(response, '43333333')

        rango_hoy = ahora.date().strftime('%d/%m/%Y') + ' - ' + ahora.date().strftime('%d/%m/%Y')
        post_data['fecha'] = rango_hoy
        response = self.client.post(url, post_data, follow=True)
        self.assertNotContains(response, '42222222')
        self.assertContains(response, '41111111')
        self.assertContains(response, '43333333')
