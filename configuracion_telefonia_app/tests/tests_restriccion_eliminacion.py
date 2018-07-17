# -*- coding: utf-8 -*-

from mock import patch
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.tests.factories import CampanaFactory
from ominicontacto_app.models import Campana

from configuracion_telefonia_app.tests.factories import (
    RutaEntranteFactory, IVRFactory,
    ValidacionFechaHoraFactory, GrupoHorarioFactory, ValidacionTiempoFactory)
from configuracion_telefonia_app.models import (
    RutaEntrante, GrupoHorario, ValidacionTiempo, IVR, ValidacionFechaHora, DestinoEntrante)
from configuracion_telefonia_app.views import IVRDeleteView


class BaseTestRestriccionEliminacion(OMLBaseTest):
    PWD = u'admin123'

    def setUp(self, *args, **kwargs):
        super(BaseTestRestriccionEliminacion, self).setUp(*args, **kwargs)
        # self._crear_campanas_entrantes()

        self.admin = self.crear_administrador()
        self.admin.set_password(self.PWD)

    def _crear_campanas_entrantes(self):
        campana_entrante_1 = CampanaFactory(type=Campana.TYPE_ENTRANTE)
        campana_entrante_2 = CampanaFactory(type=Campana.TYPE_ENTRANTE)
        DestinoEntrante.crear_nodo_ruta_entrante(campana_entrante_1)
        DestinoEntrante.crear_nodo_ruta_entrante(campana_entrante_2)
        self.camp_1 = campana_entrante_1
        self.camp_2 = campana_entrante_2

class TestRestriccionEliminacionGrupoHorario(BaseTestRestriccionEliminacion):

    @patch('configuracion_telefonia_app.views.SincronizadorDummy.regenerar_configuracion')
    def test_elimina_grupo_horario_ok(self, mock_sincronizacion):
        # Creo un Grupo Horario sin asignarlo a ninguna Validacion Fecha Hora
        grupo_horario = GrupoHorarioFactory()
        ValidacionTiempoFactory(grupo_horario=grupo_horario)
        self.client.login(username=self.admin.username, password=self.PWD)
        url = reverse('eliminar_grupo_horario', args=[grupo_horario.id])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _(u"Se ha eliminado el Grupo Horario."))
        self.assertEqual(GrupoHorario.objects.count(), 0)
        self.assertEqual(ValidacionTiempo.objects.count(), 0)

    @patch('configuracion_telefonia_app.views.SincronizadorDummy.regenerar_configuracion')
    def test_no_elimina_grupo_horario_utilizado(self, mock_sincronizacion):
        # Creo un Grupo Horario y lo asigno a una Validacion Fecha Hora
        grupo_horario = GrupoHorarioFactory()
        ValidacionTiempoFactory(grupo_horario=grupo_horario)
        ValidacionFechaHoraFactory(grupo_horario=grupo_horario)
        self.client.login(username=self.admin.username, password=self.PWD)
        url = reverse('eliminar_grupo_horario', args=[grupo_horario.id])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        message = _('No se puede eliminar un Grupo Horario utilizado en una Validacion Fecha Hora')
        self.assertContains(response, message)
        self.assertEqual(GrupoHorario.objects.count(), 1)
        self.assertEqual(ValidacionTiempo.objects.count(), 1)

    @patch('configuracion_telefonia_app.views.SincronizadorDummy.regenerar_configuracion')
    def test_elimina_ivr_ok(self, mock_sincronizacion):
        # Creo un IVR que no es destino
        destinos_iniciales = DestinoEntrante.objects.count()
        ivr = IVRFactory()
        DestinoEntrante.crear_nodo_ruta_entrante(ivr)
        self.client.login(username=self.admin.username, password=self.PWD)
        url = reverse('eliminar_ivr', args=[ivr.id])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, IVRDeleteView.nodo_eliminado)
        self.assertEqual(IVR.objects.count(), 0)
        self.assertEqual(DestinoEntrante.objects.count(), destinos_iniciales)

    @patch('configuracion_telefonia_app.views.SincronizadorDummy.regenerar_configuracion')
    def test_no_elimina_ivr_utilizado_en_ruta_entrante(self, mock_sincronizacion):
        # Creo un IVR y lo pongo como destino de una Ruta Entrante
        destinos_iniciales = DestinoEntrante.objects.count()
        ivr = IVRFactory()
        nodo_ivr = DestinoEntrante.crear_nodo_ruta_entrante(ivr)
        RutaEntranteFactory(destino=nodo_ivr)
        self.client.login(username=self.admin.username, password=self.PWD)
        url = reverse('eliminar_ivr', args=[ivr.id])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        list_url = reverse('lista_ivrs')
        self.assertRedirects(response, list_url)
        self.assertContains(response, IVRDeleteView.imposible_eliminar)
        self.assertEqual(IVR.objects.count(), 1)
        self.assertEqual(DestinoEntrante.objects.count(), destinos_iniciales + 1)
