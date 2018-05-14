# -*- coding: utf-8 -*-

"""Tests para los reportes que se realizan desde una campaña"""

from __future__ import unicode_literals

from datetime import timedelta

from mock import patch

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone

from simple_history.utils import update_change_reason

from ominicontacto_app.models import Campana, CalificacionCliente, OpcionCalificacion
from ominicontacto_app.services.estadisticas_campana import EstadisticasService
from ominicontacto_app.services.reporte_campana_calificacion import ReporteCampanaService
from ominicontacto_app.services.reporte_campana_pdf import ReporteCampanaPDFService
from ominicontacto_app.services.reporte_llamados_contactados_csv import ReporteCampanaContactadosCSV
from ominicontacto_app.services.reporte_metadata_cliente import ReporteMetadataClienteService
from ominicontacto_app.tests.factories import (AgenteProfileFactory, ActividadAgenteLogFactory,
                                               CalificacionClienteFactory, ContactoFactory,
                                               CampanaFactory, NombreCalificacionFactory,
                                               OpcionCalificacionFactory, UserFactory)
from reportes_app.tests.utiles import GeneradorDeLlamadaLogs


class ReportesCampanasTests(TestCase):

    PWD = 'admin123'

    GESTION = 'Gestión'
    CALIFICACION_NOMBRE = "calificacion_nombre"
    DURACION_LLAMADA = 80

    def setUp(self):
        self.usuario_admin_supervisor = UserFactory(is_staff=True, is_supervisor=True)
        self.usuario_admin_supervisor.set_password(self.PWD)
        self.usuario_admin_supervisor.save()
        self.agente_profile = AgenteProfileFactory.create(user=self.usuario_admin_supervisor)

        self.nombre_calificacion = NombreCalificacionFactory.create(nombre=self.CALIFICACION_NOMBRE)
        self.nombre_calificacion_gestion = NombreCalificacionFactory.create(nombre=self.GESTION)

        self.campana_activa = CampanaFactory.create(
            estado=Campana.ESTADO_ACTIVA, type=Campana.TYPE_PREVIEW)

        self.opcion_calificacion_gestion = OpcionCalificacionFactory.create(
            campana=self.campana_activa, nombre=self.nombre_calificacion_gestion.nombre,
            tipo=OpcionCalificacion.GESTION)
        self.opcion_calificacion_noaccion = OpcionCalificacionFactory.create(
            campana=self.campana_activa, nombre=self.nombre_calificacion.nombre)
        self.calif_gestion = CalificacionClienteFactory.create(
            opcion_calificacion=self.opcion_calificacion_gestion, agente=self.agente_profile)
        self.calif_no_accion = CalificacionClienteFactory.create(
            opcion_calificacion=self.opcion_calificacion_noaccion, agente=self.agente_profile)
        CalificacionCliente.history.all().update(history_change_reason='calificacion')
        self.contacto_calificado_gestion = self.calif_gestion.contacto
        self.contacto_calificado_no_accion = self.calif_no_accion.contacto
        self.contacto_no_atendido = ContactoFactory(bd_contacto=self.campana_activa.bd_contacto)
        self.contacto_no_calificado = ContactoFactory(bd_contacto=self.campana_activa.bd_contacto)

        self.telefono1 = self.contacto_calificado_gestion.telefono
        self.telefono2 = self.contacto_calificado_no_accion.telefono
        self.telefono3 = self.contacto_no_atendido.telefono
        self.telefono4 = self.contacto_no_atendido.telefono

        self.generador_log_llamadas = GeneradorDeLlamadaLogs()
        self.generador_log_llamadas.generar_log(
            self.campana_activa, False, 'COMPLETEAGENT', self.telefono1, agente=self.agente_profile,
            contacto=self.contacto_calificado_gestion, duracion_llamada=self.DURACION_LLAMADA)
        self.generador_log_llamadas.generar_log(
            self.campana_activa, False, 'COMPLETEAGENT', self.telefono2, agente=self.agente_profile,
            contacto=self.contacto_calificado_no_accion, duracion_llamada=self.DURACION_LLAMADA)
        self.generador_log_llamadas.generar_log(
            self.campana_activa, True, 'NOANSWER', self.telefono3, agente=self.agente_profile,
            contacto=self.contacto_no_atendido)
        self.generador_log_llamadas.generar_log(
            self.campana_activa, True, 'COMPLETECALLER', self.telefono4, agente=self.agente_profile,
            contacto=self.contacto_no_calificado, duracion_llamada=0)

        self.client.login(username=self.usuario_admin_supervisor.username, password=self.PWD)

    def test_usuario_no_logueado_no_accede_reporte_calificaciones(self):
        self.client.logout()
        url = reverse('campana_reporte_calificacion', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_usuario_logueado_accede_reporte_calificaciones(self):
        url = reverse('campana_reporte_calificacion', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, 'calificaciones_campana.html')

    def test_reporte_calificaciones_campana_coincide_con_estadisticas_sistema(self):
        url = reverse('campana_reporte_calificacion', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        self.assertContains(response, self.calif_gestion.contacto.telefono)
        self.assertContains(response, self.calif_no_accion.contacto.telefono)

    @patch.object(ReporteCampanaService, 'crea_reporte_csv')
    def test_reporte_calificaciones_campana_exporta_archivo_csv_calificados(self, crea_reporte_csv):
        url = reverse('campana_reporte_calificacion', args=[self.campana_activa.pk])
        self.client.get(url, follow=True)
        self.assertTrue(crea_reporte_csv.called)

    @patch.object(ReporteMetadataClienteService, 'crea_reporte_csv')
    def test_reporte_calificaciones_campana_exporta_archivo_csv_gestionados(self, crea_reporte_csv):
        url = reverse('campana_reporte_calificacion', args=[self.campana_activa.pk])
        self.client.get(url, follow=True)
        self.assertTrue(crea_reporte_csv.called)

    def test_usuario_no_logueado_no_accede_reporte_grafico_campana(self):
        self.client.logout()
        url = reverse('campana_reporte_grafico', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, 'registration/login.html')

    @patch.object(ReporteCampanaPDFService, 'crea_reporte_pdf')
    @patch.object(ReporteCampanaContactadosCSV, 'crea_reporte_csv')
    def test_usuario_logueado_accede_reporte_grafico_campana(
            self, crea_reporte_pdf, crea_reporte_csv):
        url = reverse('campana_reporte_grafico', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, 'reporte_grafico_campana.html')

    @patch.object(ReporteCampanaPDFService, 'crea_reporte_pdf')
    @patch.object(ReporteCampanaContactadosCSV, 'crea_reporte_csv')
    def test_reporte_grafico_exporta_pdf_resumen(self, crea_reporte_pdf, crea_reporte_csv):
        url = reverse('campana_reporte_grafico', args=[self.campana_activa.pk])
        self.client.get(url, follow=True)
        self.assertTrue(crea_reporte_pdf.called)

    @patch.object(ReporteCampanaPDFService, 'crea_reporte_pdf')
    @patch.object(ReporteCampanaContactadosCSV, 'crea_reporte_csv')
    def test_reporte_grafico_exporta_reportes_estadisticas_contactos(
            self, crea_reporte_pdf, crea_reporte_csv):
        url = reverse('campana_reporte_grafico', args=[self.campana_activa.pk])
        self.client.get(url, follow=True)
        self.assertTrue(crea_reporte_csv.called)

    @patch.object(ReporteCampanaPDFService, 'crea_reporte_pdf')
    @patch.object(ReporteCampanaContactadosCSV, 'crea_reporte_csv')
    def test_datos_reporte_grafico_calificaciones_coinciden_estadisticas_sistema(
            self, crea_reporte_pdf, crea_reporte_csv):
        url = reverse('campana_reporte_grafico', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        estadisticas = response.context_data['graficos_estadisticas']['estadisticas']
        calificaciones_list = [self.calif_gestion.opcion_calificacion.nombre,
                               self.calif_no_accion.opcion_calificacion.nombre]
        atendidas_sin_calificacion = len([self.contacto_no_atendido, self.contacto_no_calificado])
        total_asignados = len(calificaciones_list) + atendidas_sin_calificacion
        calificaciones_list.append('Llamadas Atendidas sin calificacion')
        self.assertEqual(estadisticas['total_asignados'], total_asignados)
        self.assertEqual(set(estadisticas['calificaciones_nombre']), set(calificaciones_list))
        self.assertEqual(estadisticas['calificaciones_cantidad'], [1, 1, 2])

    @patch.object(ReporteCampanaPDFService, 'crea_reporte_pdf')
    @patch.object(ReporteCampanaContactadosCSV, 'crea_reporte_csv')
    def test_datos_reporte_grafico_llamadas_analizan_no_atendidas_que_modifican_calificaciones(
            self, crea_reporte_pdf, crea_reporte_csv):
        # simulamos otra llamada a un contacto ya calificado y una modificación en la calificación
        # existente
        self.calif_gestion.observaciones = "Nueva observacion"
        self.calif_gestion.save()
        update_change_reason(self.calif_gestion, 'recalificacion')
        url = reverse('campana_reporte_grafico', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        estadisticas = response.context_data['graficos_estadisticas']['estadisticas']
        atendidas_sin_calificacion = len([self.contacto_no_atendido, self.contacto_no_calificado])
        self.assertEqual(estadisticas['calificaciones_cantidad'][-1], atendidas_sin_calificacion)

    @patch.object(ReporteCampanaPDFService, 'crea_reporte_pdf')
    @patch.object(ReporteCampanaContactadosCSV, 'crea_reporte_csv')
    def test_datos_reporte_grafico_no_contactados_coinciden_estadisticas_sistema(
            self, crea_reporte_pdf, crea_reporte_csv):
        url = reverse('campana_reporte_grafico', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        estadisticas = response.context_data['graficos_estadisticas']['estadisticas']
        total_no_atendidos = estadisticas['total_no_atendidos']
        self.assertEqual(total_no_atendidos, 1)

    @patch.object(ReporteCampanaPDFService, 'crea_reporte_pdf')
    @patch.object(ReporteCampanaContactadosCSV, 'crea_reporte_csv')
    def test_datos_reporte_grafico_calificaciones_por_agente_coinciden_estadisticas_sistema(
            self, crea_reporte_pdf, crea_reporte_csv):
        agente_profile1, agente_profile2, agente_profile3 = AgenteProfileFactory.create_batch(3)
        CalificacionClienteFactory(
            opcion_calificacion=self.opcion_calificacion_gestion, agente=agente_profile1)
        CalificacionClienteFactory(
            opcion_calificacion=self.opcion_calificacion_noaccion, agente=agente_profile2)
        CalificacionClienteFactory(
            opcion_calificacion=self.opcion_calificacion_noaccion, agente=agente_profile3)
        url = reverse('campana_reporte_grafico', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        estadisticas = response.context_data['graficos_estadisticas']['estadisticas']
        self.assertContains(response, agente_profile1.user.get_full_name())
        self.assertContains(response, agente_profile2.user.get_full_name())
        self.assertContains(response, agente_profile3.user.get_full_name())
        # se toman en cuenta las calificaciones iniciales del setUp
        self.assertEqual(estadisticas['total_ventas'], 2)
        self.assertEqual(estadisticas['total_calificados'], 5)

    def test_datos_reporte_grafico_detalle_llamadas_entrantes_coinciden_estadisticas_sistema(self):
        campana_entrante = CampanaFactory(type=Campana.TYPE_ENTRANTE, estado=Campana.ESTADO_ACTIVA)
        self.generador_log_llamadas.generar_log(
            campana_entrante, False, 'COMPLETEAGENT', self.telefono1, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_entrante, False, 'COMPLETECALLER', self.telefono2, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_entrante, False, 'EXITWITHTIMEOUT', self.telefono3, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_entrante, False, 'ABANDON', self.telefono4, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_entrante, True, 'COMPLETEAGENT', self.telefono1, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_entrante, True, 'COMPLETECALLER', self.telefono2, agente=self.agente_profile)
        estadisticas_service = EstadisticasService()
        hoy = timezone.now().date()
        reporte = estadisticas_service.calcular_cantidad_llamadas(campana_entrante, hoy, hoy)
        self.assertEqual(reporte['Recibidas'], 4)
        self.assertEqual(reporte['Atendidas'], 2)
        self.assertEqual(reporte['Expiradas'], 1)
        self.assertEqual(reporte['Abandonadas'], 1)
        self.assertEqual(reporte['Manuales'], 2)
        self.assertEqual(reporte['Manuales atendidas'], 2)
        self.assertEqual(reporte['Manuales no atendidas'], 0)

    def test_datos_reporte_grafico_detalle_llamadas_dialer_coinciden_estadisticas_sistema(self):
        campana_dialer = CampanaFactory(type=Campana.TYPE_DIALER, estado=Campana.ESTADO_ACTIVA)
        self.generador_log_llamadas.generar_log(
            campana_dialer, False, 'COMPLETEAGENT', self.telefono1, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_dialer, False, 'COMPLETECALLER', self.telefono2, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_dialer, False, 'ABANDON', self.telefono3, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_dialer, False, 'EXITWITHTIMEOUT', self.telefono4, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_dialer, False, 'CANCEL', self.telefono4, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_dialer, True, 'COMPLETEAGENT', self.telefono1, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_dialer, True, 'COMPLETECALLER', self.telefono2, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_dialer, True, 'NOANSWER', self.telefono2, agente=self.agente_profile)
        estadisticas_service = EstadisticasService()
        hoy = timezone.now().date()
        reporte = estadisticas_service.calcular_cantidad_llamadas(campana_dialer, hoy, hoy)
        self.assertEqual(reporte['Discadas'], 5)
        self.assertEqual(reporte['Conectadas al agente'], 2)
        self.assertEqual(reporte['Atendidas'], 4)
        self.assertEqual(reporte['Perdidas'], 2)
        self.assertEqual(reporte['Manuales'], 3)
        self.assertEqual(reporte['Manuales atendidas'], 2)
        self.assertEqual(reporte['Manuales no atendidas'], 1)

    def test_datos_reporte_grafico_detalle_llamadas_manuales_coinciden_estadisticas_sistema(self):
        campana_manual = CampanaFactory(type=Campana.TYPE_MANUAL, estado=Campana.ESTADO_ACTIVA)
        self.generador_log_llamadas.generar_log(
            campana_manual, True, 'COMPLETEAGENT', self.telefono1, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_manual, True, 'COMPLETECALLER', self.telefono2, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_manual, True, 'FAIL', self.telefono3, agente=self.agente_profile)
        estadisticas_service = EstadisticasService()
        hoy = timezone.now().date()
        reporte = estadisticas_service.calcular_cantidad_llamadas(campana_manual, hoy, hoy)
        self.assertEqual(reporte['Discadas'], 3)
        self.assertEqual(reporte['Discadas atendidas'], 2)
        self.assertEqual(reporte['Discadas no atendidas'], 1)

    def test_datos_reporte_grafico_detalle_llamadas_preview_coinciden_estadisticas_sistema(self):
        estadisticas_service = EstadisticasService()
        hoy = timezone.now().date()
        reporte = estadisticas_service.calcular_cantidad_llamadas(self.campana_activa, hoy, hoy)
        # se usan los logs de llamadas del setUp pues la campaña usada es preview
        self.assertEqual(reporte['Discadas'], 2)
        self.assertEqual(reporte['Conectadas'], 2)
        self.assertEqual(reporte['No conectadas'], 0)
        self.assertEqual(reporte['Manuales'], 2)
        self.assertEqual(reporte['Manuales atendidas'], 1)
        self.assertEqual(reporte['Manuales no atendidas'], 1)

    def test_usuario_logueado_accede_reporte_agente_campana(self):
        url = reverse(
            'campana_reporte_agente', args=[self.campana_activa.pk, self.agente_profile.pk])
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, 'reporte_agente.html')

    def test_usuario_no_logueado_no_accede_reporte_agente_campana(self):
        self.client.logout()
        url = reverse(
            'campana_reporte_agente', args=[self.campana_activa.pk, self.agente_profile.pk])
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_datos_reporte_agente_calificaciones_coinciden_estadisticas_sistema(self):
        url = reverse(
            'campana_reporte_agente', args=[self.campana_activa.pk, self.agente_profile.pk])
        response = self.client.get(url, follow=True)
        estadisticas = response.context_data['graficos_estadisticas']['estadisticas']
        calificaciones_list = [self.calif_gestion.opcion_calificacion.nombre,
                               self.calif_no_accion.opcion_calificacion.nombre]
        calificaciones_list.append('Llamadas Atendidas sin calificacion')
        self.assertEqual(estadisticas['total_asignados'], len(calificaciones_list))
        self.assertEqual(set(estadisticas['calificaciones_nombre']), set(calificaciones_list))
        self.assertEqual(estadisticas['calificaciones_cantidad'], [1, 1, 1])

    def test_datos_reporte_agente_detalle_llamadas_coinciden_estadisticas_sistema(self):
        url = reverse(
            'campana_reporte_agente', args=[self.campana_activa.pk, self.agente_profile.pk])
        response = self.client.get(url, follow=True)
        estadisticas = response.context_data['graficos_estadisticas']['estadisticas']
        agente_data = estadisticas['agente_tiempo']
        self.assertEqual(agente_data.cantidad_llamadas_procesadas, 3)
        self.assertEqual(agente_data.cantidad_llamadas_perdidas, 1)
        self.assertEqual(agente_data.tiempo_llamada, 2 * self.DURACION_LLAMADA)

    def test_datos_reporte_agente_detalle_actividad_coinciden_estadisticas_sistema(self):
        DURACION_AGENTE_SESION = 3600
        TIEMPO_AGENTE_ANTES_PAUSA = 120
        DURACION_AGENTE_PAUSA = 100
        tiempo_agente_login = timezone.now()
        tiempo_agente_inicio_pausa = tiempo_agente_login + timedelta(
            microseconds=TIEMPO_AGENTE_ANTES_PAUSA)
        tiempo_agente_final_pausa = tiempo_agente_inicio_pausa + timedelta(
            microseconds=DURACION_AGENTE_PAUSA)
        tiempo_agente_logout = tiempo_agente_login + timedelta(microseconds=DURACION_AGENTE_SESION)
        ActividadAgenteLogFactory(
            agente_id=self.agente_profile.pk, time=tiempo_agente_login, event='ADDMEMBER')
        ActividadAgenteLogFactory(
            agente_id=self.agente_profile.pk, time=tiempo_agente_inicio_pausa, event='PAUSEALL')
        ActividadAgenteLogFactory(
            agente_id=self.agente_profile.pk, time=tiempo_agente_final_pausa, event='UNPAUSEALL')
        ActividadAgenteLogFactory(
            agente_id=self.agente_profile.pk, time=tiempo_agente_logout, event='REMOVEMEMBER')
        url = reverse(
            'campana_reporte_agente', args=[self.campana_activa.pk, self.agente_profile.pk])
        response = self.client.get(url, follow=True)
        estadisticas = response.context_data['graficos_estadisticas']['estadisticas']
        agente_data = estadisticas['agente_tiempo']
        self.assertEqual(agente_data.tiempo_sesion.microseconds, DURACION_AGENTE_SESION)
        self.assertEqual(agente_data.tiempo_pausa.microseconds, DURACION_AGENTE_PAUSA)

    def test_datos_reporte_agente_actividad_dia_anterior_coincide_estadisticas_sistema(self):
        # si el agente comenzó sesión y pausa el día anterior y terminó en el actual
        # se  testea que se sume el tiempo de los eventos desde que inicia el día actual en el
        # reporte
        DURACION_FIN_PAUSA_A_FIN_SESION = 600
        inicio_dia = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tiempo_agente_final_pausa = timezone.now()
        tiempo_agente_logout = tiempo_agente_final_pausa + timedelta(
            microseconds=DURACION_FIN_PAUSA_A_FIN_SESION)
        tiempo_pausa = tiempo_agente_final_pausa - inicio_dia
        tiempo_sesion = tiempo_agente_logout - inicio_dia
        ActividadAgenteLogFactory(
            agente_id=self.agente_profile.pk, time=tiempo_agente_final_pausa, event='UNPAUSEALL')
        ActividadAgenteLogFactory(
            agente_id=self.agente_profile.pk, time=tiempo_agente_logout, event='REMOVEMEMBER')
        url = reverse(
            'campana_reporte_agente', args=[self.campana_activa.pk, self.agente_profile.pk])
        response = self.client.get(url, follow=True)
        estadisticas = response.context_data['graficos_estadisticas']['estadisticas']
        agente_data = estadisticas['agente_tiempo']
        self.assertEqual(agente_data.tiempo_sesion, tiempo_sesion)
        self.assertEqual(agente_data.tiempo_pausa, tiempo_pausa)

    def test_datos_reporte_agente_actividad_dia_incompleta_coincide_estadisticas_sistema(self):
        # si el agente comenzó sesión y pausa en el día actual y terminó en el siguiente
        # se testea que se sume el tiempo de los eventos desde que inician hasta el final del día
        # actual en el reporte
        DURACION_INICIO_SESION_A_INICIO_PAUSA = 600
        final_dia = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        tiempo_agente_login = timezone.now()
        tiempo_agente_inicio_pausa = tiempo_agente_login + timedelta(
            microseconds=DURACION_INICIO_SESION_A_INICIO_PAUSA)
        tiempo_pausa = final_dia - tiempo_agente_inicio_pausa
        tiempo_sesion = final_dia - tiempo_agente_login
        ActividadAgenteLogFactory(
            agente_id=self.agente_profile.pk, time=tiempo_agente_login, event='ADDMEMBER')
        ActividadAgenteLogFactory(
            agente_id=self.agente_profile.pk, time=tiempo_agente_inicio_pausa, event='PAUSEALL')
        url = reverse(
            'campana_reporte_agente', args=[self.campana_activa.pk, self.agente_profile.pk])
        response = self.client.get(url, follow=True)
        estadisticas = response.context_data['graficos_estadisticas']['estadisticas']
        agente_data = estadisticas['agente_tiempo']
        self.assertEqual(agente_data.tiempo_sesion, tiempo_sesion)
        self.assertEqual(agente_data.tiempo_pausa, tiempo_pausa)

    def test_usuario_no_logueado_no_accede_a_vista_detalle_campana_preview(self):
        self.client.logout()
        url = reverse('campana_preview_detalle', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, u'registration/login.html')

    def test_usuario_no_logueado_no_accede_a_vista_detalle_express_campana_preview(self):
        self.client.logout()
        url = reverse('campana_preview_detalle_express', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, u'registration/login.html')

    def test_usuario_logueado_accede_a_datos_vista_detalle_campana_preview(self):
        url = reverse('campana_preview_detalle', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, u'campana_preview/detalle.html')
        self.assertEqual(
            response.context_data['categorias'][self.calif_gestion.opcion_calificacion.nombre], 1)
        self.assertEqual(
            response.context['categorias'][self.calif_no_accion.opcion_calificacion.nombre], 1)

    def test_usuario_logueado_accede_a_datos_vista_detalle_express_campana_preview(self):
        url = reverse('campana_preview_detalle_express', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, u'campana_preview/detalle_express.html')
        self.assertEqual(
            response.context_data['categorias'][self.calif_gestion.opcion_calificacion.nombre], 1)
        self.assertEqual(
            response.context['categorias'][self.calif_no_accion.opcion_calificacion.nombre], 1)
