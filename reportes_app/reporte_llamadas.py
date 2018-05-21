# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygal
from pygal.style import Style

from django.utils.translation import ugettext as _
from django.utils.encoding import force_text

from ominicontacto_app.models import Campana
from reportes_app.models import LlamadaLog


NO_CONNECT = ['NOANSWER', 'BUSY', 'CANCEL', 'CHANUNAVAIL', 'OTHER', 'FAIL', 'AMD', 'BLACKLIST']


class ReporteDeLlamadas(object):

    def __init__(self, desde, hasta, incluir_finalizadas, user):
        self.campanas = self._campanas_implicadas(user, incluir_finalizadas)
        campanas_ids = self.campanas.values_list('id', flat=True)
        self.logs = LlamadaLog.objects.filter(time__gte=desde,
                                              time__lte=hasta,
                                              campana_id__in=campanas_ids)
        self._inicializar_conteo_de_estadisticas(desde, hasta)

        self._contabilizar_estadisticas()

    def _campanas_implicadas(self, user, incluir_finalizadas):
        if incluir_finalizadas:
            campanas = Campana.objects.obtener_all_activas_finalizadas()
        else:
            campanas = Campana.objects.obtener_all_dialplan_asterisk()

        if not user.get_is_administrador():
            #TODO: Verificar que pasa con las finalizadas
            campanas = Campana.objects.obtener_campanas_vista_by_user(campanas, user)

        return campanas

    def _get_campana_type_display(self, campana_type):
        return (i[1] for i in Campana.TYPES_CAMPANA if i[0] == campana_type).next()

    def _inicializar_conteo_de_estadisticas(self, desde, hasta):

        self.estadisticas = {
            'total_llamadas_procesadas': 0,  # DIAL + ENTERQUEUE(data3 = Entrante:3),

            'llamadas_por_tipo': {
                Campana.TYPE_MANUAL_DISPLAY: {
                    'total': 0,  # DIAL(tipo_llamada = Manual:1)
                    'conectadas': 0,  # ANSWER(tipo_llamada = Manual:1)
                    'no_conectadas': 0,  # NO CONNECT(tipo_llamada = Manual:1)
                },
                Campana.TYPE_DIALER_DISPLAY: {
                    'total': 0,  # DIAL(tipo_llamada = Dialer:2),
                    'atendidas': 0,  # ANSWER(tipo_llamada = Dialer:2)  (puede ser ENTERQUEUE),
                    'no_atendidas': 0,  # EXITWITHTIMEOUT(tipo_llamada = Dialer:2) +
                                        # ABANDON(tipo_llamada = Dialer:2),
                    'perdidas': 0,  # NO CONNECT(tipo_llamada = Dialer:2),
                },
                Campana.TYPE_ENTRANTE_DISPLAY: {
                    'total': 0,  # ENTERQUEUE(tipo_llamada = Entrante:3)
                    'atendidas': 0,  # CONNECT(tipo_llamada = Entrante:3)
                    'expiradas': 0,  # EXITWITHTIMEOUT(tipo_llamada = Entrante:3)
                    'abandonadas': 0,  # ABANDON(tipo_llamada = Entrante:3)
                },
                Campana.TYPE_PREVIEW_DISPLAY: {
                    'total': 0,  # DIAL(tipo_llamada = Preview:4)
                    'conectadas': 0,  # ANSWER(tipo_llamada = Preview:4)
                    'no_conectadas': 0,  # NO CONNECT(tipo_llamada = Preview:4)
                }
            },

            'llamadas_por_campana': {},

            'tipos_de_llamada_por_campana':
            {
                Campana.TYPE_MANUAL_DISPLAY: {},
                Campana.TYPE_DIALER_DISPLAY: {},
                Campana.TYPE_ENTRANTE_DISPLAY: {},
                Campana.TYPE_PREVIEW_DISPLAY: {},
            }
        }

        for campana in self.campanas:
            self._inicializar_conteo_de_estadisticas_de_campana(campana)

    def _inicializar_conteo_de_estadisticas_de_campana(self, campana):
        tipo = self._get_campana_type_display(campana.type)

        # Inicializar Llamadas por campaña
        self.estadisticas['llamadas_por_campana'][campana.id] = {
            'nombre': campana.nombre,
            'tipo': tipo,
            'total': 0,
            'manuales': 0,
        }

        # Inicializar Tipos de llamadas por campaña
        tipos_por_campana = {
            'nombre': campana.nombre,
        }
        if campana.type == Campana.TYPE_MANUAL:
            tipos_por_campana['efectuadas'] = 0
            tipos_por_campana['conectadas'] = 0
            tipos_por_campana['no_conectadas'] = 0
            tipos_por_campana['t_espera_conexion'] = 0
        elif campana.type == Campana.TYPE_DIALER:
            tipos_por_campana['efectuadas'] = 0
            tipos_por_campana['conectadas'] = 0
            tipos_por_campana['atendidas'] = 0
            tipos_por_campana['expiradas'] = 0
            tipos_por_campana['abandonadas'] = 0
            tipos_por_campana['t_abandono'] = 0
            tipos_por_campana['t_espera_atencion'] = 0
            tipos_por_campana['t_espera_conexion'] = 0
            tipos_por_campana['efectuadas_manuales'] = 0
            tipos_por_campana['conectadas_manuales'] = 0
            tipos_por_campana['no_conectadas_manuales'] = 0
            tipos_por_campana['t_espera_conexion_manuales'] = 0
        elif campana.type == Campana.TYPE_ENTRANTE:
            tipos_por_campana['recibidas'] = 0
            tipos_por_campana['atendidas'] = 0
            tipos_por_campana['expiradas'] = 0
            tipos_por_campana['abandonadas'] = 0
            tipos_por_campana['t_abandono'] = 0
            tipos_por_campana['t_espera_conexion'] = 0
            tipos_por_campana['efectuadas_manuales'] = 0
            tipos_por_campana['conectadas_manuales'] = 0
            tipos_por_campana['no_conectadas_manuales'] = 0
            tipos_por_campana['t_espera_conexion_manuales'] = 0
        elif campana.type == Campana.TYPE_PREVIEW:
            tipos_por_campana['efectuadas'] = 0
            tipos_por_campana['conectadas'] = 0
            tipos_por_campana['no_conectadas'] = 0
            tipos_por_campana['t_espera_conexion'] = 0
            tipos_por_campana['efectuadas_manuales'] = 0
            tipos_por_campana['conectadas_manuales'] = 0
            tipos_por_campana['no_conectadas_manuales'] = 0
            tipos_por_campana['t_espera_conexion_manuales'] = 0

        self.estadisticas['tipos_de_llamada_por_campana'][tipo][campana.id] = tipos_por_campana

    def _contabilizar_estadisticas(self):
        for log in self.logs:
            tipo_campana = self._get_campana_type_display(log.tipo_campana)
            tipo_llamada = self._get_campana_type_display(log.tipo_llamada)
            self._contabilizar_total_llamadas_procesadas(log)
            self._contabilizar_llamada_por_tipo(tipo_llamada, log)
            self._contabilizar_llamadas_por_campana(log)
            self._contabilizar_tipos_de_llamada_por_campana(tipo_campana, log)
        self._aplicar_promedios_a_tiempos()

        self._generar_graficos()

        # Preparar datos para exportar a csv
        #   total_llamadas_json
        #   Zip reportes:               Exportar a CSV todos los reportes
        #       total_llamadas_json
        #       dict_campana_counter_json  ?? Deberia ir queues_llamadas_preview_json?
        #       queues_llamadas_dialer_json
        #       queues_llamadas_entrantes_json
        #       queues_llamadas_manuales_json
        #
        #   dict_campana_counter_json ??  'Exportar llamadas por campaña'
        #
        #   queues_llamadas_dialer_json     'Exportar llamadas campañas dialer
        #   queues_llamadas_entrantes_json    Exportar llamadas campañas entrantes
        #   queues_llamadas_manuales_json   'Exportar llamadas campañas manuales'
        #   queues_llamadas_preview_json
        #

    def _contabilizar_total_llamadas_procesadas(self, log):
        if log.event == 'DIAL' or \
                (log.event == 'ENTERQUEUE' and log.tipo_campana == Campana.TYPE_ENTRANTE):
            self.estadisticas['total_llamadas_procesadas'] += 1

    def _contabilizar_llamada_por_tipo(self, tipo, log):
            if log.event == 'DIAL':
                if not log.tipo_llamada == Campana.TYPE_ENTRANTE:
                    self.estadisticas['llamadas_por_tipo'][tipo]['total'] += 1
            elif log.event == 'ENTERQUEUE':
                if log.tipo_llamada == Campana.TYPE_ENTRANTE:
                    self.estadisticas['llamadas_por_tipo'][tipo]['total'] += 1
            elif log.event == 'ANSWER':
                if log.tipo_llamada == Campana.TYPE_MANUAL or \
                        log.tipo_llamada == Campana.TYPE_PREVIEW:
                    self.estadisticas['llamadas_por_tipo'][tipo]['conectadas'] += 1
                elif log.tipo_llamada == Campana.TYPE_DIALER:
                    self.estadisticas['llamadas_por_tipo'][tipo]['atendidas'] += 1
            elif log.event == 'CONNECT':
                if log.tipo_llamada == Campana.TYPE_ENTRANTE:
                    self.estadisticas['llamadas_por_tipo'][tipo]['atendidas'] += 1
            elif log.event == 'EXITWITHTIMEOUT':
                if log.tipo_llamada == Campana.TYPE_DIALER:
                    self.estadisticas['llamadas_por_tipo'][tipo]['perdidas'] += 1
                elif log.tipo_llamada == Campana.TYPE_ENTRANTE:
                    self.estadisticas['llamadas_por_tipo'][tipo]['expiradas'] += 1
            elif log.event == 'ABANDON':
                if log.tipo_llamada == Campana.TYPE_DIALER:
                    self.estadisticas['llamadas_por_tipo'][tipo]['perdidas'] += 1
                if log.tipo_llamada == Campana.TYPE_ENTRANTE:
                    self.estadisticas['llamadas_por_tipo'][tipo]['abandonadas'] += 1
            elif log.event in NO_CONNECT:
                if log.tipo_llamada == Campana.TYPE_MANUAL or \
                        log.tipo_llamada == Campana.TYPE_PREVIEW:
                    self.estadisticas['llamadas_por_tipo'][tipo]['no_conectadas'] += 1
                elif log.tipo_llamada == Campana.TYPE_DIALER:
                    self.estadisticas['llamadas_por_tipo'][tipo]['no_atendidas'] += 1

    def _contabilizar_llamadas_por_campana(self, log):
            if log.event == 'DIAL':
                self.estadisticas['llamadas_por_campana'][log.campana_id]['total'] += 1
                if log.tipo_llamada == Campana.TYPE_MANUAL:
                    self.estadisticas['llamadas_por_campana'][log.campana_id]['manuales'] += 1

            elif log.event == 'ENTERQUEUE':
                if log.tipo_campana == Campana.TYPE_ENTRANTE:
                    self.estadisticas['llamadas_por_campana'][log.campana_id]['total'] += 1

    def _contabilizar_tipos_de_llamada_por_campana(self, tipo, log):
        if tipo == Campana.TYPE_MANUAL_DISPLAY:
            self._contabilizar_tipos_de_llamada_por_campana_saliente(tipo, log)
        elif tipo == Campana.TYPE_DIALER_DISPLAY:
            self._contabilizar_tipos_de_llamada_por_campana_dialer(tipo, log)
        elif tipo == Campana.TYPE_ENTRANTE_DISPLAY:
            self._contabilizar_tipos_de_llamada_por_campana_entrante(tipo, log)
        elif tipo == Campana.TYPE_PREVIEW_DISPLAY:
            self._contabilizar_tipos_de_llamada_por_campana_saliente(tipo, log)

    def _contabilizar_tipos_de_llamada_por_campana_saliente(self, tipo, log):
        datos_campana = self.estadisticas['tipos_de_llamada_por_campana'][tipo][log.campana_id]
        if not log.tipo_campana == log.tipo_llamada:
            self._contabilizar_tipos_de_llamada_manual(datos_campana, log)
        if log.event == 'DIAL':
            datos_campana['efectuadas'] += 1
        elif log.event == 'ANSWER':
            datos_campana['conectadas'] += 1
            datos_campana['t_espera_conexion'] += log.bridge_wait_time
        elif log.event in NO_CONNECT:
            datos_campana['no_conectadas'] += 1
            datos_campana['t_espera_conexion'] += log.bridge_wait_time

    def _contabilizar_tipos_de_llamada_por_campana_dialer(self, tipo, log):
        datos_campana = self.estadisticas['tipos_de_llamada_por_campana'][tipo][log.campana_id]
        if not log.tipo_campana == log.tipo_llamada:
            self._contabilizar_tipos_de_llamada_manual(datos_campana, log)
        elif log.event == 'DIAL':
            datos_campana['efectuadas'] += 1
        elif log.event == 'ANSWER':
            datos_campana['atendidas'] += 1
            datos_campana['t_espera_atencion'] += log.bridge_wait_time
        elif log.event == 'CONNECT':
            datos_campana['conectadas'] += 1
            datos_campana['t_espera_conexion'] += log.bridge_wait_time
        elif log.event == 'EXITWITHTIMEOUT':
            datos_campana['expiradas'] += 1
        elif log.event == 'ABANDON':
            datos_campana['abandonadas'] += 1
            datos_campana['t_abandono'] += log.bridge_wait_time

    def _contabilizar_tipos_de_llamada_por_campana_entrante(self, tipo, log):
        datos_campana = self.estadisticas['tipos_de_llamada_por_campana'][tipo][log.campana_id]
        if not log.tipo_campana == log.tipo_llamada:
            self._contabilizar_tipos_de_llamada_manual(datos_campana, log)
        elif log.event == 'ENTERQUEUE':
            datos_campana['recibidas'] += 1
        elif log.event == 'CONNECT':
            datos_campana['atendidas'] += 1
            datos_campana['t_espera_conexion'] += log.bridge_wait_time
        elif log.event == 'EXITWITHTIMEOUT':
            datos_campana['expiradas'] += 1
        elif log.event == 'ABANDON':
            datos_campana['abandonadas'] += 1
            datos_campana['t_abandono'] += log.bridge_wait_time

    def _contabilizar_tipos_de_llamada_manual(self, datos_campana, log):
        if log.event == 'DIAL':
            datos_campana['efectuadas_manuales'] += 1
        elif log.event == 'ANSWER':
            datos_campana['conectadas_manuales'] += 1
            datos_campana['t_espera_conexion_manuales'] += log.bridge_wait_time
        elif log.event in NO_CONNECT:
            datos_campana['no_conectadas_manuales'] += 1
            datos_campana['t_espera_conexion_manuales'] += log.bridge_wait_time

    def _aplicar_promedios_a_tiempos(self):
        for tipo, datos_tipo in self.estadisticas['tipos_de_llamada_por_campana'].iteritems():
            for datos_campana in datos_tipo.itervalues():
                if tipo in [Campana.TYPE_MANUAL_DISPLAY, Campana.TYPE_PREVIEW_DISPLAY]:
                    efectuadas = datos_campana['efectuadas']
                    if efectuadas > 0:
                        suma_esperas = datos_campana['t_espera_conexion']
                        datos_campana['t_espera_conexion'] = suma_esperas / efectuadas
                elif tipo == Campana.TYPE_DIALER_DISPLAY:
                    abandonadas = datos_campana['abandonadas']
                    if abandonadas > 0:
                        datos_campana['t_abandono'] = datos_campana['t_abandono'] / abandonadas
                    conectadas = datos_campana['conectadas']
                    if conectadas > 0:
                        datos_campana['t_espera_atencion'] = datos_campana['t_espera_atencion'] \
                            / conectadas
                    atendidas = datos_campana['atendidas']
                    if abandonadas > 0:
                        datos_campana['t_espera_atencion'] = datos_campana['t_espera_atencion'] \
                            / atendidas

                elif tipo == Campana.TYPE_ENTRANTE_DISPLAY:
                    atendidas = datos_campana['atendidas']
                    if atendidas > 0:
                        datos_campana['t_espera_conexion'] = datos_campana['t_espera_conexion'] \
                            / atendidas
                    abandonadas = datos_campana['abandonadas']
                    if abandonadas > 0:
                        datos_campana['t_abandono'] = datos_campana['t_abandono'] / abandonadas
                if not tipo == Campana.TYPE_MANUAL_DISPLAY:
                    efectuadas = datos_campana['efectuadas_manuales']
                    if efectuadas > 0:
                        suma_esperas = datos_campana['t_espera_conexion_manuales']
                        datos_campana['t_espera_conexion_manuales'] = suma_esperas / efectuadas


    def _generar_graficos(self):
        graficador = GraficosReporteDeLlamadas(self.estadisticas)
        self.graficos = graficador.graficos


class GraficosReporteDeLlamadas(object):

    ESTILO_AZUL_ROJO_AMARILLO = Style(
        background='transparent',
        plot_background='transparent',
        foreground='#555',
        foreground_light='#555',
        foreground_dark='#555',
        opacity='1',
        opacity_hover='.6',
        transition='400ms ease-in',
        colors=('#428bca', '#5cb85c', '#f0ad4e', '#5bc0de', '#d9534f',
                '#a95cb8', '#5cb8b5', '#caca43', '#96ac43', '#ca43ca')
    )

    def __init__(self, estadisticas):
        self.graficos = {}
        self._generar_grafico_de_barras_de_llamadas_por_tipo(estadisticas)
        self._generar_grafico_de_torta_de_porcentajes_por_tipo(estadisticas)
        self._generar_grafico_de_barras_de_llamadas_por_campana(estadisticas)
        self._generar_grafico_de_barras_de_llamadas_dialer(estadisticas)
        self._generar_grafico_de_barras_de_llamadas_entrantes(estadisticas)
        self._generar_grafico_de_barras_de_llamadas_manuales(estadisticas)
        self._generar_grafico_de_barras_de_llamadas_preview(estadisticas)

    def _generar_grafico_de_barras_de_llamadas_por_tipo(self, estadisticas):
        # Totales llamadas por tipo de campaña y forma de finalización
        grafico = pygal.Bar(show_legend=True, style=self.ESTILO_AZUL_ROJO_AMARILLO)
        grafico.x_labels = [_('Manuales'), _(u'Dialer'), _(u'Entrantes'), _(u'Preview')]
        por_tipo = estadisticas['llamadas_por_tipo']
        grafico.add(
            _(u'Ingresadas'), [por_tipo[Campana.TYPE_MANUAL_DISPLAY]['total'],
                               por_tipo[Campana.TYPE_DIALER_DISPLAY]['total'],
                               por_tipo[Campana.TYPE_ENTRANTE_DISPLAY]['total'],
                               por_tipo[Campana.TYPE_PREVIEW_DISPLAY]['total']])

        grafico.add(
            _('Atendidas'), [por_tipo[Campana.TYPE_MANUAL_DISPLAY]['conectadas'],
                             por_tipo[Campana.TYPE_DIALER_DISPLAY]['atendidas'],
                             por_tipo[Campana.TYPE_ENTRANTE_DISPLAY]['atendidas'],
                             por_tipo[Campana.TYPE_PREVIEW_DISPLAY]['conectadas']])

        perdidas_dialer = por_tipo[Campana.TYPE_DIALER_DISPLAY]['no_atendidas'] + \
            por_tipo[Campana.TYPE_DIALER_DISPLAY]['perdidas']
        perdidas_entrantes = por_tipo[Campana.TYPE_ENTRANTE_DISPLAY]['expiradas'] + \
            por_tipo[Campana.TYPE_ENTRANTE_DISPLAY]['abandonadas']
        grafico.add(
            _('Perdidas'), [por_tipo[Campana.TYPE_MANUAL_DISPLAY]['no_conectadas'],
                            perdidas_dialer,
                            perdidas_entrantes,
                            por_tipo[Campana.TYPE_PREVIEW_DISPLAY]['no_conectadas']])

        self.graficos['barras_llamadas_por_tipo'] = grafico

    def _generar_grafico_de_torta_de_porcentajes_por_tipo(self, estadisticas):
        # Porcentajes de llamadas por tipo de llamada
        no_data_text = _("No hay llamadas para ese periodo")
        grafico = pygal.Pie(style=self.ESTILO_AZUL_ROJO_AMARILLO, no_data_text=no_data_text,
                            no_data_font_size=32, legend_font_size=25, truncate_legend=10,
                            tooltip_font_size=50)
        total = float(estadisticas['total_llamadas_procesadas'])
        total_manual = estadisticas['llamadas_por_tipo'][Campana.TYPE_MANUAL_DISPLAY]['total']
        total_dialer = estadisticas['llamadas_por_tipo'][Campana.TYPE_DIALER_DISPLAY]['total']
        total_entrante = estadisticas['llamadas_por_tipo'][Campana.TYPE_ENTRANTE_DISPLAY]['total']
        total_preview = estadisticas['llamadas_por_tipo'][Campana.TYPE_PREVIEW_DISPLAY]['total']

        porcentaje_dialer = (100.0 * float(total_dialer) / float(total)) if total > 0 else 0
        porcentaje_entrante = (100.0 * float(total_entrante) / float(total)) if total > 0 else 0
        porcentaje_manual = (100.0 * float(total_manual) / float(total)) if total > 0 else 0
        porcentaje_preview = (100.0 * float(total_preview) / float(total)) if total > 0 else 0

        grafico.add(_('Manual'), porcentaje_manual)
        grafico.add(_('Dialer'), porcentaje_dialer)
        grafico.add(_('Entrante'), porcentaje_entrante)
        grafico.add(_('Preview'), porcentaje_preview)
        self.graficos['torta_porcentajes_por_tipo'] = grafico

    def _generar_grafico_de_barras_de_llamadas_por_campana(self, estadisticas):
        # Cantidad de llamadas de las campana
        grafico = pygal.Bar(show_legend=False, style=self.ESTILO_AZUL_ROJO_AMARILLO)

        grafico.title = _(u'Cantidad de llamadas de las campañas')
        nombres_campanas = []
        totales_campanas = []
        manuales_campanas = []
        for datos_campana in estadisticas['llamadas_por_campana'].itervalues():
            nombres_campanas.append(datos_campana['nombre'])
            totales_campanas.append(datos_campana['total'])
            manuales_campanas.append(datos_campana['manuales'])
        grafico.x_labels = nombres_campanas
        grafico.add(_('Total'), totales_campanas)
        grafico.add(_('Manuales'), manuales_campanas)
        self.graficos['barra_llamada_por_campana'] = grafico

    def _generar_grafico_de_barras_de_llamadas_dialer(self, estadisticas):
        grafico = pygal.StackedBar(show_legend=False, style=self.ESTILO_AZUL_ROJO_AMARILLO)
        grafico.title = _(u'Tipos de llamadas por campaña')
        nombres_campanas = []
        no_atendidas = []
        conectadas = []
        expiradas = []
        abandonadas = []
        por_campana = estadisticas['tipos_de_llamada_por_campana'][Campana.TYPE_DIALER_DISPLAY]
        for datos_campana in por_campana.itervalues():
            nombres_campanas.append(datos_campana['nombre'])
            no_atendidas.append(datos_campana['efectuadas'] - datos_campana['atendidas'])
            conectadas.append(datos_campana['conectadas'])
            expiradas.append(datos_campana['expiradas'])
            abandonadas.append(datos_campana['abandonadas'])

        grafico.x_labels = nombres_campanas
        grafico.add(_(u'No Atendidas'), no_atendidas)
        grafico.add(_(u'Conectadas'), conectadas)
        grafico.add(_(u'Expiradas'), expiradas)
        grafico.add(_(u'Abandonadas'), abandonadas)
        self.graficos['barra_campana_llamadas_dialer'] = grafico

    def _generar_grafico_de_barras_de_llamadas_entrantes(self, estadisticas):
        grafico = pygal.StackedBar(show_legend=False, style=self.ESTILO_AZUL_ROJO_AMARILLO)
        grafico.title = _(u'Tipos de llamadas por campaña')
        nombres_campanas = []
        atendidas = []
        expiradas = []
        abandonadas = []
        por_campana = estadisticas['tipos_de_llamada_por_campana'][Campana.TYPE_ENTRANTE_DISPLAY]
        for datos_campana in por_campana.itervalues():
            nombres_campanas.append(datos_campana['nombre'])
            atendidas.append(datos_campana['atendidas'])
            expiradas.append(datos_campana['expiradas'])
            abandonadas.append(datos_campana['abandonadas'])

        grafico.x_labels = nombres_campanas
        grafico.add(_(u'Atendidas'), atendidas)
        grafico.add(_(u'Expiradas'), expiradas)
        grafico.add(_(u'Abandonadas'), abandonadas)
        self.graficos['barra_campana_llamadas_entrantes'] = grafico

    def _generar_grafico_de_barras_de_llamadas_manuales(self, estadisticas):
        grafico = pygal.StackedBar(show_legend=False, style=self.ESTILO_AZUL_ROJO_AMARILLO)
        grafico.title = _(u'Tipos de llamadas por campaña')
        nombres_campanas = []
        conectadas = []
        no_conectadas = []
        por_campana = estadisticas['tipos_de_llamada_por_campana'][Campana.TYPE_MANUAL_DISPLAY]
        for datos_campana in por_campana.itervalues():
            nombres_campanas.append(datos_campana['nombre'])
            conectadas.append(datos_campana['conectadas'])
            no_conectadas.append(datos_campana['no_conectadas'])

        grafico.x_labels = nombres_campanas
        grafico.add(_(u'Conectadas'), conectadas)
        grafico.add(_(u'No conectadas'), no_conectadas)
        self.graficos['barra_campana_llamadas_manuales'] = grafico

    def _generar_grafico_de_barras_de_llamadas_preview(self, estadisticas):
        grafico = pygal.StackedBar(show_legend=False, style=self.ESTILO_AZUL_ROJO_AMARILLO)
        grafico.title = _(u'Tipos de llamadas por campaña')
        nombres_campanas = []
        conectadas = []
        no_conectadas = []
        por_campana = estadisticas['tipos_de_llamada_por_campana'][Campana.TYPE_PREVIEW_DISPLAY]
        for datos_campana in por_campana.itervalues():
            nombres_campanas.append(datos_campana['nombre'])
            conectadas.append(datos_campana['conectadas'])
            no_conectadas.append(datos_campana['no_conectadas'])

        grafico.x_labels = nombres_campanas
        grafico.add(_(u'Conectadas'), conectadas)
        grafico.add(_(u'No conectadas'), no_conectadas)
        self.graficos['barra_campana_llamadas_preview'] = grafico


class GeneradorReportesLlamadasCSV(object):

    def obtener_filas_reporte(self, estadisticas, tipo_reporte):
        if tipo_reporte == 'llamadas_por_tipo':
            return self._obtener_filas_llamadas_por_tipo(estadisticas)
        if tipo_reporte == 'llamadas_por_campana':
            return self._obtener_filas_llamadas_por_campana(estadisticas)
        if tipo_reporte == 'tipos_de_llamada_manual':
            return self._obtener_filas_manual(estadisticas)
        if tipo_reporte == 'tipos_de_llamada_dialer':
            return self._obtener_filas_dialer(estadisticas)
        if tipo_reporte == 'tipos_de_llamada_entrante':
            return self._obtener_filas_entrante(estadisticas)
        if tipo_reporte == 'tipos_de_llamada_preview':
            return self._obtener_filas_preview(estadisticas)

    def obtener_filas_de_todos_los_reportes(self, estadisticas):
        llamadas_por_tipo = self._obtener_filas_llamadas_por_tipo(estadisticas)
        llamadas_por_campana = self._obtener_filas_llamadas_por_campana(estadisticas)
        tipos_de_llamada_manual = self._obtener_filas_manual(estadisticas)
        tipos_de_llamada_dialer = self._obtener_filas_dialer(estadisticas)
        tipos_de_llamada_entrante = self._obtener_filas_entrante(estadisticas)
        tipos_de_llamada_preview = self._obtener_filas_preview(estadisticas)
        return (llamadas_por_tipo,
                llamadas_por_campana,
                tipos_de_llamada_manual,
                tipos_de_llamada_dialer,
                tipos_de_llamada_entrante,
                tipos_de_llamada_preview)

    def _obtener_filas_llamadas_por_tipo(self, estadisticas):
        por_tipo = estadisticas['llamadas_por_tipo']
        filas = [['Tipo', 'Total', 'Conectadas', 'No conectadas',
                 'Atendidas', 'No Atendidas', 'Perdidas', 'Expiradas', 'Abandonadas'], ]
        filas.append([
            Campana.TYPE_MANUAL_DISPLAY,
            force_text(por_tipo[Campana.TYPE_MANUAL_DISPLAY]['total']),
            force_text(por_tipo[Campana.TYPE_MANUAL_DISPLAY]['conectadas']),
            force_text(por_tipo[Campana.TYPE_MANUAL_DISPLAY]['no_conectadas']),
            '', '', '', '', '',
        ])
        filas.append([
            Campana.TYPE_DIALER_DISPLAY,
            force_text(por_tipo[Campana.TYPE_DIALER_DISPLAY]['total']),
            '', '',
            force_text(por_tipo[Campana.TYPE_DIALER_DISPLAY]['atendidas']),
            force_text(por_tipo[Campana.TYPE_DIALER_DISPLAY]['no_atendidas']),
            force_text(por_tipo[Campana.TYPE_DIALER_DISPLAY]['perdidas']),
            '', '',
        ])
        filas.append([
            Campana.TYPE_ENTRANTE_DISPLAY,
            force_text(por_tipo[Campana.TYPE_ENTRANTE_DISPLAY]['total']),
            '', '',
            force_text(por_tipo[Campana.TYPE_ENTRANTE_DISPLAY]['atendidas']),
            '', '',
            force_text(por_tipo[Campana.TYPE_ENTRANTE_DISPLAY]['expiradas']),
            force_text(por_tipo[Campana.TYPE_ENTRANTE_DISPLAY]['abandonadas']),
        ])
        filas.append([
            Campana.TYPE_PREVIEW_DISPLAY,
            force_text(por_tipo[Campana.TYPE_PREVIEW_DISPLAY]['total']),
            force_text(por_tipo[Campana.TYPE_PREVIEW_DISPLAY]['conectadas']),
            force_text(por_tipo[Campana.TYPE_PREVIEW_DISPLAY]['no_conectadas']),
            '', '', '', '', '',
        ])
        return filas

    def _obtener_filas_llamadas_por_campana(self, estadisticas):
        por_campana = estadisticas['llamadas_por_campana']
        filas = [['Nombre', 'Tipo', 'Total', 'Manuales'], ]
        for id, estadisticas_campana in por_campana.items():
            filas.append([estadisticas_campana['nombre'],
                          estadisticas_campana['tipo'],
                          force_text(estadisticas_campana['total']),
                          force_text(estadisticas_campana['manuales']),
                          ])
        return filas

    def _obtener_filas_manual(self, estadisticas):
        por_campana = estadisticas['tipos_de_llamada_por_campana'][Campana.TYPE_MANUAL_DISPLAY]
        filas = [['Nombre', 'Efectuadas', 'Conectadas', 'No conectadas', 'T. Espera Conexion'], ]
        for id, estadisticas_campana in por_campana.items():
            filas.append([estadisticas_campana['nombre'],
                          force_text(estadisticas_campana['efectuadas']),
                          force_text(estadisticas_campana['conectadas']),
                          force_text(estadisticas_campana['no_conectadas']),
                          force_text(estadisticas_campana['t_espera_conexion']),
                          ])
        return filas

    def _obtener_filas_dialer(self, estadisticas):
        por_campana = estadisticas['tipos_de_llamada_por_campana'][Campana.TYPE_DIALER_DISPLAY]
        filas = [['Nombre', 'Efectuadas', 'Conectadas', 'Atendidas', 'Expiradas', 'Abandonadas',
                  'T. Abandono', 'T. Espera Atención', 'T. Espera Conexion', 'Manuales Efectuadas',
                  'Manuales Conectadas', 'Manuales No Conectadas',
                  'T. Espera Conexión Manuales'], ]
        for id, estadisticas_campana in por_campana.items():
            filas.append([estadisticas_campana['nombre'],
                          force_text(estadisticas_campana['efectuadas']),
                          force_text(estadisticas_campana['conectadas']),
                          force_text(estadisticas_campana['atendidas']),
                          force_text(estadisticas_campana['expiradas']),
                          force_text(estadisticas_campana['abandonadas']),
                          force_text(estadisticas_campana['t_abandono']),
                          force_text(estadisticas_campana['t_espera_atencion']),
                          force_text(estadisticas_campana['t_espera_conexion']),
                          force_text(estadisticas_campana['efectuadas_manuales']),
                          force_text(estadisticas_campana['conectadas_manuales']),
                          force_text(estadisticas_campana['no_conectadas_manuales']),
                          force_text(estadisticas_campana['t_espera_conexion_manuales']),
                          ])
        return filas

    def _obtener_filas_entrante(self, estadisticas):
        por_campana = estadisticas['tipos_de_llamada_por_campana'][Campana.TYPE_ENTRANTE_DISPLAY]
        filas = [['Nombre', 'Recibidas', 'Atendidas', 'Expiradas', 'Abandonadas',
                  'T. Abandono', 'T. Espera Conexion', 'Manuales Efectuadas',
                  'Manuales Conectadas', 'Manuales No Conectadas', 'T. Espera Conexión Manuales'], ]
        for id, estadisticas_campana in por_campana.items():
            filas.append([estadisticas_campana['nombre'],
                          force_text(estadisticas_campana['recibidas']),
                          force_text(estadisticas_campana['atendidas']),
                          force_text(estadisticas_campana['expiradas']),
                          force_text(estadisticas_campana['abandonadas']),
                          force_text(estadisticas_campana['t_abandono']),
                          force_text(estadisticas_campana['t_espera_conexion']),
                          force_text(estadisticas_campana['efectuadas_manuales']),
                          force_text(estadisticas_campana['conectadas_manuales']),
                          force_text(estadisticas_campana['no_conectadas_manuales']),
                          force_text(estadisticas_campana['t_espera_conexion_manuales']),
                          ])
        return filas

    def _obtener_filas_preview(self, estadisticas):
        por_campana = estadisticas['tipos_de_llamada_por_campana'][Campana.TYPE_PREVIEW_DISPLAY]
        filas = [['Nombre', 'Efectuadas', 'Conectadas', 'No conectadas', 'T. Espera Conexion',
                  'Manuales Efectuadas', 'Manuales Conectadas', 'Manuales No Conectadas',
                  'T. Espera Conexión Manuales'], ]
        for id, estadisticas_campana in por_campana.items():
            filas.append([estadisticas_campana['nombre'],
                          force_text(estadisticas_campana['efectuadas']),
                          force_text(estadisticas_campana['conectadas']),
                          force_text(estadisticas_campana['no_conectadas']),
                          force_text(estadisticas_campana['t_espera_conexion']),
                          force_text(estadisticas_campana['efectuadas_manuales']),
                          force_text(estadisticas_campana['conectadas_manuales']),
                          force_text(estadisticas_campana['no_conectadas_manuales']),
                          force_text(estadisticas_campana['t_espera_conexion_manuales']),
                          ])
        return filas
