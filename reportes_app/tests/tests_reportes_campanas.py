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

"""Tests para los reportes que se realizan desde una campaña"""

from __future__ import unicode_literals

from datetime import timedelta


from pygal import Bar
from mock import patch

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from ominicontacto_app.models import Campana, CalificacionCliente, OpcionCalificacion
from ominicontacto_app.services.estadisticas_campana import (
    EstadisticasService, CampanaService)
from ominicontacto_app.services.reporte_campana_pdf import ReporteCampanaPDFService
from reportes_app.reportes.reporte_llamados_contactados_csv import (
    ReporteContactadosCSV, ExportacionCampanaCSV)
from ominicontacto_app.services.reporte_campana_csv import (
    ExportacionArchivoCampanaCSV, CrearArchivoDeReporteCsv)
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.tests.factories import ActividadAgenteLogFactory, AgenteProfileFactory, \
    CalificacionClienteFactory, CampanaFactory, ContactoFactory, LlamadaLogFactory, \
    NombreCalificacionFactory, OpcionCalificacionFactory
from ominicontacto_app.utiles import (fecha_hora_local,
                                      datetime_hora_minima_dia_utc, datetime_hora_maxima_dia_utc)
from reportes_app.models import LlamadaLog
from reportes_app.tests.utiles import GeneradorDeLlamadaLogs


class BaseTestDeReportes(OMLBaseTest):

    GESTION = 'Gestión'
    CALIFICACION_NOMBRE = "calificacion_nombre"
    DURACION_LLAMADA = 80

    def setUp(self):
        self.usuario_admin_supervisor = self.crear_administrador()
        self.agente_profile = self.crear_agente_profile()

        self.nombre_calificacion = NombreCalificacionFactory.create(nombre=self.CALIFICACION_NOMBRE)
        self.nombre_calificacion_gestion = NombreCalificacionFactory.create(nombre=self.GESTION)

        self.campana_activa = CampanaFactory.create(
            estado=Campana.ESTADO_ACTIVA, type=Campana.TYPE_PREVIEW)

        self.contacto_calificado_gestion = ContactoFactory(
            bd_contacto=self.campana_activa.bd_contacto)
        self.contacto_calificado_no_accion = ContactoFactory(
            bd_contacto=self.campana_activa.bd_contacto)
        self.contacto_no_atendido = ContactoFactory(bd_contacto=self.campana_activa.bd_contacto)
        self.contacto_no_calificado = ContactoFactory(bd_contacto=self.campana_activa.bd_contacto)

        self.opcion_calificacion_gestion = OpcionCalificacionFactory.create(
            campana=self.campana_activa, nombre=self.nombre_calificacion_gestion.nombre,
            tipo=OpcionCalificacion.GESTION)
        self.opcion_calificacion_noaccion = OpcionCalificacionFactory.create(
            campana=self.campana_activa, nombre=self.nombre_calificacion.nombre,
            tipo=OpcionCalificacion.NO_ACCION)

        self.telefono1 = self.contacto_calificado_gestion.telefono
        self.telefono2 = self.contacto_calificado_no_accion.telefono
        self.telefono3 = self.contacto_no_atendido.telefono
        self.telefono4 = self.contacto_no_calificado.telefono

        self.generador_log_llamadas = GeneradorDeLlamadaLogs()
        self.generador_log_llamadas.generar_log(
            self.campana_activa, False, 'COMPLETEAGENT', self.telefono1, agente=self.agente_profile,
            contacto=self.contacto_calificado_gestion, duracion_llamada=self.DURACION_LLAMADA,
            callid=1)
        self.generador_log_llamadas.generar_log(
            self.campana_activa, False, 'COMPLETEAGENT', self.telefono2, agente=self.agente_profile,
            contacto=self.contacto_calificado_no_accion, duracion_llamada=self.DURACION_LLAMADA,
            callid=2)
        self.generador_log_llamadas.generar_log(
            self.campana_activa, True, 'NOANSWER', self.telefono3, agente=self.agente_profile,
            contacto=self.contacto_no_atendido, callid=3)
        self.generador_log_llamadas.generar_log(
            self.campana_activa, True, 'COMPLETEOUTNUM', self.telefono4, agente=self.agente_profile,
            contacto=self.contacto_no_calificado, duracion_llamada=0, callid=4)
        callid_gestion = LlamadaLog.objects.get(
            contacto_id=self.contacto_calificado_gestion.pk, event='COMPLETEAGENT').callid
        callid_no_accion = LlamadaLog.objects.get(
            contacto_id=self.contacto_calificado_no_accion.pk, event='COMPLETEAGENT').callid
        self.calif_gestion = CalificacionClienteFactory.create(
            opcion_calificacion=self.opcion_calificacion_gestion, agente=self.agente_profile,
            contacto=self.contacto_calificado_gestion, callid=callid_gestion)
        self.calif_no_accion = CalificacionClienteFactory.create(
            opcion_calificacion=self.opcion_calificacion_noaccion, agente=self.agente_profile,
            contacto=self.contacto_calificado_no_accion, callid=callid_no_accion)
        CalificacionCliente.history.all().update(history_change_reason='calificacion')

        self.client.login(username=self.usuario_admin_supervisor.username, password=PASSWORD)


class ReportesCampanasTests(BaseTestDeReportes):

    def test_usuario_no_logueado_no_accede_reporte_calificaciones(self):
        self.client.logout()
        url = reverse('campana_reporte_calificacion', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_usuario_logueado_accede_reporte_calificaciones(self):
        url = reverse('campana_reporte_calificacion', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, 'calificaciones_campana.html')

    @patch.object(ExportacionArchivoCampanaCSV, "exportar_reportes_csv")
    @patch.object(CrearArchivoDeReporteCsv, "ya_existe")
    def test_reporte_calificaciones_campana_exporta_archivo_csv_calificados(self,
                                                                            exportar_reportes_csv,
                                                                            ya_existe):
        url = reverse('exporta_campana_reporte_calificacion', args=[self.campana_activa.pk])
        self.client.get(url, follow=True)
        self.assertTrue(exportar_reportes_csv.called)

    @patch.object(ExportacionArchivoCampanaCSV, "exportar_reportes_csv")
    @patch.object(CrearArchivoDeReporteCsv, "ya_existe")
    def test_reporte_calificaciones_campana_exporta_archivo_csv_gestionados(self,
                                                                            exportar_reportes_csv,
                                                                            ya_existe):
        url = reverse('exporta_reporte_calificaciones_gestion', args=[self.campana_activa.pk])
        self.client.get(url, follow=True)
        self.assertTrue(exportar_reportes_csv.called)

    def test_usuario_no_logueado_no_accede_reporte_grafico_campana(self):
        self.client.logout()
        url = reverse('campana_reporte_grafico', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, 'registration/login.html')

    @patch.object(ReporteCampanaPDFService, 'crea_reporte_pdf')
    def test_usuario_logueado_accede_reporte_grafico_campana(
            self, crea_reporte_pdf):
        url = reverse('campana_reporte_grafico', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, 'reporte_grafico_campana.html')

    @patch.object(ReporteCampanaPDFService, 'crea_reporte_pdf')
    def test_reporte_grafico_exporta_pdf_resumen(
            self, crea_reporte_pdf):
        url = reverse('campana_reporte_grafico', args=[self.campana_activa.pk])
        self.client.get(url, follow=True)
        self.assertTrue(crea_reporte_pdf.called)

    @patch.object(ReporteCampanaPDFService, 'crea_reporte_pdf')
    @patch.object(Bar, 'render_to_png')
    def test_datos_reporte_grafico_calificaciones_coinciden_estadisticas_sistema(
            self, render_to_png, crea_reporte_pdf):
        url = reverse('campana_reporte_grafico', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        estadisticas = response.context_data['graficos_estadisticas']['estadisticas']
        calificaciones_list = [self.calif_gestion.opcion_calificacion.nombre,
                               self.calif_no_accion.opcion_calificacion.nombre]
        atendidas_sin_calificacion = len([self.contacto_no_calificado])
        total_asignados = len(calificaciones_list) + atendidas_sin_calificacion
        calificaciones_list.append('Llamadas Atendidas sin calificación')
        self.assertEqual(estadisticas['total_asignados'], total_asignados)
        self.assertEqual(set(estadisticas['calificaciones_nombre']), set(calificaciones_list))
        self.assertEqual(list(estadisticas['calificaciones_cantidad']), [1, 1, 1])

    @patch.object(ReporteCampanaPDFService, 'crea_reporte_pdf')
    @patch.object(Bar, 'render_to_png')
    def test_datos_reporte_grafico_llamadas_analizan_no_calificadas(
            self, render_to_png, crea_reporte_pdf):
        # hay una llamada a un contacto pero no se califica (self.contacto_no_calificado)
        url = reverse('campana_reporte_grafico', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        estadisticas = response.context_data['graficos_estadisticas']['estadisticas']
        atendidas_sin_calificacion = len([self.contacto_no_calificado])
        self.assertEqual(
            list(estadisticas['calificaciones_cantidad'])[-1], atendidas_sin_calificacion)

    @patch.object(ReporteCampanaPDFService, 'crea_reporte_pdf')
    @patch.object(Bar, 'render_to_png')
    def test_datos_reporte_grafico_no_contactados_coinciden_estadisticas_sistema(
            self, render_to_png, crea_reporte_pdf):
        url = reverse('campana_reporte_grafico', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        estadisticas = response.context_data['graficos_estadisticas']['estadisticas']
        total_no_atendidos = estadisticas['total_no_atendidos']
        self.assertEqual(total_no_atendidos, 1)

    @patch.object(ReporteCampanaPDFService, 'crea_reporte_pdf')
    @patch.object(Bar, 'render_to_png')
    def test_datos_reporte_grafico_calificaciones_por_agente_coinciden_estadisticas_sistema(
            self, render_to_png, crea_reporte_pdf):
        agente_profile1, agente_profile2, agente_profile3 = AgenteProfileFactory.create_batch(3)
        log1 = LlamadaLogFactory(campana_id=self.campana_activa.pk, agente_id=agente_profile1.pk)
        log2 = LlamadaLogFactory(campana_id=self.campana_activa.pk, agente_id=agente_profile2.pk)
        log3 = LlamadaLogFactory(campana_id=self.campana_activa.pk, agente_id=agente_profile3.pk)
        CalificacionClienteFactory(
            callid=log1.callid, opcion_calificacion=self.opcion_calificacion_gestion,
            agente=agente_profile1)
        CalificacionClienteFactory(
            callid=log2.callid, opcion_calificacion=self.opcion_calificacion_noaccion,
            agente=agente_profile2)
        CalificacionClienteFactory(
            callid=log3.callid, opcion_calificacion=self.opcion_calificacion_noaccion,
            agente=agente_profile3)
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
            campana_entrante, False, 'COMPLETEOUTNUM', self.telefono2, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_entrante, False, 'EXITWITHTIMEOUT', self.telefono3, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_entrante, False, 'ABANDON', self.telefono4, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_entrante, True, 'COMPLETEAGENT', self.telefono1, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_entrante, True, 'COMPLETEOUTNUM', self.telefono2, agente=self.agente_profile)
        hoy_ahora = fecha_hora_local(timezone.now())
        fecha_desde = datetime_hora_minima_dia_utc(hoy_ahora)
        fecha_hasta = datetime_hora_maxima_dia_utc(hoy_ahora)
        estadisticas_service = EstadisticasService(campana_entrante, fecha_desde, fecha_hasta)
        estadisticas_service.calcular_estadisticas_totales()
        reporte = estadisticas_service.reporte_detalle_llamadas.reporte
        self.assertEqual(reporte['Recibidas'], 4)
        self.assertEqual(reporte['Atendidas'], 2)
        self.assertEqual(reporte['Expiradas'], 1)
        self.assertEqual(reporte['Abandonadas'], 1)
        self.assertEqual(reporte['Manuales'], 2)
        self.assertEqual(reporte['Manuales atendidas'], 2)
        self.assertEqual(reporte['Manuales no atendidas'], 0)

    def test_datos_reporte_grafico_llamadas_entrantes_recibidas_muestran_solo_dia_actual(
            self):
        campana_entrante = CampanaFactory(type=Campana.TYPE_ENTRANTE, estado=Campana.ESTADO_ACTIVA)
        hoy = fecha_hora_local(timezone.now())
        ayer = hoy - timedelta(days=1)
        self.generador_log_llamadas.generar_log(
            campana_entrante, False, 'COMPLETEAGENT', self.telefono1, agente=self.agente_profile,
            time=ayer)
        self.generador_log_llamadas.generar_log(
            campana_entrante, False, 'COMPLETEOUTNUM', self.telefono2, agente=self.agente_profile,
            time=hoy)
        hoy_ahora = fecha_hora_local(timezone.now())
        fecha_desde = datetime_hora_minima_dia_utc(hoy_ahora)
        fecha_hasta = datetime_hora_maxima_dia_utc(hoy_ahora)
        estadisticas_service = EstadisticasService(campana_entrante, fecha_desde, fecha_hasta)
        estadisticas_service.calcular_estadisticas_totales()
        self.assertEqual(estadisticas_service.reporte_totales_llamadas.llamadas_recibidas, 1)

    def test_datos_reporte_grafico_llamadas_entrantes_realizadas_muestran_solo_dia_actual(
            self):
        campana_entrante = CampanaFactory(type=Campana.TYPE_ENTRANTE, estado=Campana.ESTADO_ACTIVA)
        hoy = fecha_hora_local(timezone.now())
        ayer = hoy - timedelta(days=1)
        self.generador_log_llamadas.generar_log(
            campana_entrante, True, 'COMPLETEAGENT', self.telefono1, agente=self.agente_profile,
            time=ayer)
        self.generador_log_llamadas.generar_log(
            campana_entrante, True, 'COMPLETEOUTNUM', self.telefono2, agente=self.agente_profile,
            time=hoy)
        hoy_ahora = fecha_hora_local(timezone.now())
        fecha_desde = datetime_hora_minima_dia_utc(hoy_ahora)
        fecha_hasta = datetime_hora_maxima_dia_utc(hoy_ahora)
        estadisticas_service = EstadisticasService(campana_entrante, fecha_desde, fecha_hasta)
        estadisticas_service.calcular_estadisticas_totales()
        self.assertEqual(estadisticas_service.reporte_totales_llamadas.llamadas_realizadas, 1)

    def test_datos_reporte_grafico_llamadas_entrantes_promedio_tiempo_espera(self):
        campana_entrante = CampanaFactory(type=Campana.TYPE_ENTRANTE, estado=Campana.ESTADO_ACTIVA)
        hoy = fecha_hora_local(timezone.now())
        self.generador_log_llamadas.generar_log(
            campana_entrante, False, 'COMPLETEAGENT', self.telefono1, agente=self.agente_profile,
            time=hoy, bridge_wait_time=4, callid=1)
        self.generador_log_llamadas.generar_log(
            campana_entrante, False, 'COMPLETEOUTNUM', self.telefono2, agente=self.agente_profile,
            time=hoy, bridge_wait_time=2, callid=2)
        hoy_ahora = fecha_hora_local(timezone.now())
        fecha_desde = datetime_hora_minima_dia_utc(hoy_ahora)
        fecha_hasta = datetime_hora_maxima_dia_utc(hoy_ahora)
        estadisticas_service = EstadisticasService(campana_entrante, fecha_desde, fecha_hasta)
        estadisticas_service.calcular_estadisticas_totales()
        self.assertEqual(estadisticas_service.reporte_totales_llamadas.tiempo_promedio_espera, 3)

    def test_datos_reporte_grafico_llamadas_entrantes_promedio_tiempo_abandono(self):
        campana_entrante = CampanaFactory(type=Campana.TYPE_ENTRANTE, estado=Campana.ESTADO_ACTIVA)
        hoy = fecha_hora_local(timezone.now())
        self.generador_log_llamadas.generar_log(
            campana_entrante, False, 'ABANDON', self.telefono1, agente=self.agente_profile,
            time=hoy, bridge_wait_time=4)
        LlamadaLogFactory(tipo_campana=Campana.TYPE_ENTRANTE,
                          tipo_llamada=LlamadaLog.LLAMADA_ENTRANTE, campana_id=campana_entrante.pk,
                          event='ABANDONWEL', bridge_wait_time=5, time=hoy)
        hoy_ahora = fecha_hora_local(timezone.now())
        fecha_desde = datetime_hora_minima_dia_utc(hoy_ahora)
        fecha_hasta = datetime_hora_maxima_dia_utc(hoy_ahora)
        estadisticas_service = EstadisticasService(campana_entrante, fecha_desde, fecha_hasta)
        estadisticas_service.calcular_estadisticas_totales()
        self.assertEqual(
            estadisticas_service.reporte_totales_llamadas.tiempo_promedio_abandono, 4.5)

    @patch.object(CampanaService, 'obtener_dato_campana_run')
    def test_datos_reporte_grafico_detalle_llamadas_dialer_coinciden_estadisticas_sistema(
            self, obtener_dato_campana_run):
        obtener_dato_campana_run.return_value = {'n_est_remaining_calls': 0}
        campana_dialer = CampanaFactory(type=Campana.TYPE_DIALER, estado=Campana.ESTADO_ACTIVA)
        self.generador_log_llamadas.generar_log(
            campana_dialer, False, 'COMPLETEAGENT', self.telefono1, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_dialer, False, 'COMPLETEOUTNUM', self.telefono2, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_dialer, False, 'ABANDON', self.telefono3, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_dialer, False, 'EXITWITHTIMEOUT', self.telefono4, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_dialer, False, 'CANCEL', self.telefono4, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_dialer, True, 'COMPLETEAGENT', self.telefono1, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_dialer, True, 'COMPLETEOUTNUM', self.telefono2, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_dialer, True, 'NOANSWER', self.telefono2, agente=self.agente_profile)
        hoy_ahora = fecha_hora_local(timezone.now())
        fecha_desde = datetime_hora_minima_dia_utc(hoy_ahora)
        fecha_hasta = datetime_hora_maxima_dia_utc(hoy_ahora)
        estadisticas_service = EstadisticasService(campana_dialer, fecha_desde, fecha_hasta)
        estadisticas_service.calcular_estadisticas_totales()
        reporte = estadisticas_service.reporte_detalle_llamadas.reporte
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
            campana_manual, True, 'COMPLETEOUTNUM', self.telefono2, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_manual, True, 'FAIL', self.telefono3, agente=self.agente_profile)
        hoy_ahora = fecha_hora_local(timezone.now())
        fecha_desde = datetime_hora_minima_dia_utc(hoy_ahora)
        fecha_hasta = datetime_hora_maxima_dia_utc(hoy_ahora)
        estadisticas_service = EstadisticasService(campana_manual, fecha_desde, fecha_hasta)
        estadisticas_service.calcular_estadisticas_totales()
        reporte = estadisticas_service.reporte_detalle_llamadas.reporte
        self.assertEqual(reporte['Discadas'], 3)
        self.assertEqual(reporte['Discadas atendidas'], 2)
        self.assertEqual(reporte['Discadas no atendidas'], 1)

    def test_datos_reporte_grafico_detalle_llamadas_preview_coinciden_estadisticas_sistema(self):
        hoy_ahora = fecha_hora_local(timezone.now())
        fecha_desde = datetime_hora_minima_dia_utc(hoy_ahora)
        fecha_hasta = datetime_hora_maxima_dia_utc(hoy_ahora)
        estadisticas_service = EstadisticasService(self.campana_activa, fecha_desde, fecha_hasta)
        estadisticas_service.calcular_estadisticas_totales()
        reporte = estadisticas_service.reporte_detalle_llamadas.reporte
        # se usan los logs de llamadas del setUp pues la campaña usada es preview
        self.assertEqual(reporte['Discadas'], 2)
        self.assertEqual(reporte['Conectadas'], 2)
        self.assertEqual(reporte['No conectadas'], 0)
        self.assertEqual(reporte['Manuales'], 2)
        self.assertEqual(reporte['Manuales atendidas'], 1)
        self.assertEqual(reporte['Manuales no atendidas'], 1)

    def test_usuario_logueado_accede_reporte_agente_campana(self):
        url = reverse(
            'campana_reporte_grafico_agente', args=[self.campana_activa.pk, self.agente_profile.pk])
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, 'reporte_agente.html')

    def test_usuario_no_logueado_no_accede_reporte_agente_campana(self):
        self.client.logout()
        url = reverse(
            'campana_reporte_grafico_agente', args=[self.campana_activa.pk, self.agente_profile.pk])
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_datos_reporte_agente_calificaciones_coinciden_estadisticas_sistema(self):
        url = reverse(
            'campana_reporte_grafico_agente', args=[self.campana_activa.pk, self.agente_profile.pk])
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
            'campana_reporte_grafico_agente', args=[self.campana_activa.pk, self.agente_profile.pk])
        response = self.client.get(url, follow=True)
        estadisticas = response.context_data['graficos_estadisticas']['estadisticas']
        agente_data = estadisticas['agente_tiempo']
        self.assertEqual(agente_data.cantidad_llamadas_procesadas, 3)
        self.assertEqual(agente_data.cantidad_intentos_fallidos, 1)
        self.assertEqual(agente_data.tiempo_llamada.total_seconds(), 2 * self.DURACION_LLAMADA)

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
            agente_id=self.agente_profile.pk, time=tiempo_agente_login, event='ADDMEMBER',
            pausa_id=0)
        ActividadAgenteLogFactory(
            agente_id=self.agente_profile.pk, time=tiempo_agente_inicio_pausa, event='PAUSEALL',
            pausa_id=0)
        ActividadAgenteLogFactory(
            agente_id=self.agente_profile.pk, time=tiempo_agente_final_pausa, event='UNPAUSEALL',
            pausa_id=0)
        ActividadAgenteLogFactory(
            agente_id=self.agente_profile.pk, time=tiempo_agente_logout, event='REMOVEMEMBER',
            pausa_id=0)
        url = reverse(
            'campana_reporte_grafico_agente', args=[self.campana_activa.pk, self.agente_profile.pk])
        response = self.client.get(url, follow=True)
        estadisticas = response.context_data['graficos_estadisticas']['estadisticas']
        agente_data = estadisticas['agente_tiempo']
        self.assertEqual(agente_data.tiempo_sesion.microseconds, DURACION_AGENTE_SESION)
        self.assertEqual(agente_data.tiempo_pausa.microseconds, DURACION_AGENTE_PAUSA)

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
        self.assertTemplateUsed(response, u'campanas/campana_preview/detalle.html')
        self.assertEqual(
            response.context_data['categorias'][self.calif_gestion.opcion_calificacion.nombre], 1)
        self.assertEqual(
            response.context['categorias'][self.calif_no_accion.opcion_calificacion.nombre], 1)

    def test_usuario_logueado_accede_a_datos_vista_detalle_express_campana_preview(self):
        url = reverse('campana_preview_detalle_express', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, u'campanas/campana_preview/detalle_express.html')
        self.assertEqual(
            response.context_data['categorias'][self.calif_gestion.opcion_calificacion.nombre], 1)
        self.assertEqual(
            response.context['categorias'][self.calif_no_accion.opcion_calificacion.nombre], 1)

    def test_calificaciones_agenda_se_adicionan_a_llamadas_pendientes(self):
        campana_manual = CampanaFactory(type=Campana.TYPE_MANUAL, estado=Campana.ESTADO_ACTIVA)
        opcion_calificacion_agenda = OpcionCalificacionFactory(
            nombre=settings.CALIFICACION_REAGENDA, campana=campana_manual,
            tipo=OpcionCalificacion.AGENDA)
        log = LlamadaLogFactory(campana_id=campana_manual.pk)
        CalificacionClienteFactory(
            callid=log.callid,
            opcion_calificacion=opcion_calificacion_agenda, agente=self.agente_profile)
        hoy_ahora = fecha_hora_local(timezone.now())
        fecha_desde = datetime_hora_minima_dia_utc(hoy_ahora)
        fecha_hasta = datetime_hora_maxima_dia_utc(hoy_ahora)
        estadisticas_service = EstadisticasService(campana_manual, fecha_desde, fecha_hasta)
        estadisticas_service.calcular_estadisticas_totales()
        self.assertEqual(estadisticas_service.reporte_totales_llamadas.llamadas_pendientes, 1)

    @patch('redis.Redis.publish')
    def test_reporte_contactados_campanas_entrantes_linkean_calificaciones_llamadas(self, publish):
        self.campana_activa.type = Campana.TYPE_ENTRANTE
        self.campana_activa.save()
        self.calif_gestion.callid = '000000'
        self.calif_gestion.save()
        key_task = 'key_task'
        hoy_ahora = fecha_hora_local(timezone.now())
        fecha_desde = datetime_hora_minima_dia_utc(hoy_ahora)
        fecha_hasta = datetime_hora_maxima_dia_utc(hoy_ahora)
        reporte_contactados_csv = ReporteContactadosCSV(
            self.campana_activa, key_task, fecha_desde, fecha_hasta)
        # muestra el histórico de contactados (aqui cuenta la linea de header)
        self.assertEqual(len(reporte_contactados_csv.datos), 4)

    @patch('redis.Redis.publish')
    @patch.object(ReporteCampanaPDFService, 'crea_reporte_pdf')
    @patch.object(ExportacionCampanaCSV, 'exportar_reportes_csv')
    def test_reporte_contactados_campanas_no_entrantes_muestran_valor_calificacion_historica(
            self, exportar_reportes_csv, crea_reporte_pdf, redis_publish):
        id_llamada = '000000'
        LlamadaLogFactory(callid=id_llamada, campana_id=self.campana_activa.pk,
                          event='COMPLETEAGENT')
        self.calif_gestion.callid = id_llamada
        self.calif_gestion.save()
        key_task = 'key_task'
        hoy_ahora = fecha_hora_local(timezone.now())
        fecha_desde = datetime_hora_minima_dia_utc(hoy_ahora)
        fecha_hasta = datetime_hora_maxima_dia_utc(hoy_ahora)
        reporte_contactados_csv = ReporteContactadosCSV(
            self.campana_activa, key_task, fecha_desde, fecha_hasta)
        # muestra el histórico de contactados (aqui cuenta la linea de header)
        self.assertEqual(len(reporte_contactados_csv.datos), 5)

    @patch.object(ReporteCampanaPDFService, 'crea_reporte_pdf')
    @patch.object(Bar, 'render_to_png')
    def test_datos_reporte_grafico_campana_entrantes_totales_calificaciones_contabiliza_historico(
            self, render_to_png, crea_reporte_pdf):
        self.campana_activa.type = Campana.TYPE_ENTRANTE
        id_llamada_1 = '000000'
        id_llamada_2 = '111111'
        LlamadaLogFactory(callid=id_llamada_1, campana_id=self.campana_activa.pk)
        LlamadaLogFactory(callid=id_llamada_2, campana_id=self.campana_activa.pk)
        self.campana_activa.save()
        self.calif_gestion.callid = id_llamada_1
        self.calif_gestion.save()
        self.calif_no_accion.callid = id_llamada_2
        self.calif_no_accion.save()
        url = reverse('campana_reporte_grafico', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        estadisticas = response.context_data['graficos_estadisticas']['estadisticas']
        total_calificados = estadisticas['total_calificados']
        self.assertEqual(total_calificados, 4)

    def test_datos_reporte_grafico_total_llamadas_entrantes_coinciden_estadisticas_sistema(self):
        campana_entrante = CampanaFactory(type=Campana.TYPE_ENTRANTE, estado=Campana.ESTADO_ACTIVA)
        self.generador_log_llamadas.generar_log(
            campana_entrante, False, 'COMPLETEAGENT', self.telefono1, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_entrante, False, 'COMPLETEOUTNUM', self.telefono2, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_entrante, False, 'EXITWITHTIMEOUT', self.telefono3, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_entrante, False, 'ABANDON', self.telefono4, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_entrante, True, 'COMPLETEAGENT', self.telefono1, agente=self.agente_profile)
        self.generador_log_llamadas.generar_log(
            campana_entrante, True, 'COMPLETEOUTNUM', self.telefono2, agente=self.agente_profile)
        hoy_ahora = fecha_hora_local(timezone.now())
        fecha_desde = datetime_hora_minima_dia_utc(hoy_ahora)
        fecha_hasta = datetime_hora_maxima_dia_utc(hoy_ahora)
        estadisticas_service = EstadisticasService(campana_entrante, fecha_desde, fecha_hasta)
        estadisticas_service.calcular_estadisticas_totales()
        reporte = estadisticas_service.reporte_detalle_llamadas.reporte
        self.assertEqual(reporte['Recibidas'], 4)
        self.assertEqual(reporte['Atendidas'], 2)
        self.assertEqual(reporte['Expiradas'], 1)
        self.assertEqual(reporte['Abandonadas'], 1)
        self.assertEqual(reporte['Manuales'], 2)
        self.assertEqual(reporte['Manuales atendidas'], 2)
        self.assertEqual(reporte['Manuales no atendidas'], 0)
