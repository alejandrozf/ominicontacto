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
from __future__ import unicode_literals, division

import pygal

from django.utils.translation import ugettext as _
from django.utils.encoding import force_text

from ominicontacto_app.models import Campana
from ominicontacto_app.utiles import fecha_hora_local
from reportes_app.models import LlamadaLog
from reportes_app.utiles import (
    ESTILO_AMARILLO_VERDE_ROJO, ESTILO_AZUL_VIOLETA_NARANJA_CELESTE, ESTILO_VERDE_AZUL,
    ESTILO_ROJO_VERDE_GRIS_NEGRO, ESTILO_VERDE_GRIS_NEGRO_ROJO, ESTILO_VERDE_ROJO
)

from utiles_globales import adicionar_render_unicode

LLAMADA_MANUAL = Campana.TYPE_MANUAL
LLAMADA_DIALER = Campana.TYPE_DIALER
LLAMADA_ENTRANTE = Campana.TYPE_ENTRANTE
LLAMADA_PREVIEW = Campana.TYPE_PREVIEW
LLAMADA_TRANSF_INTERNA = 8
LLAMADA_TRANSF_EXTERNA = 9
TYPE_TRANSFERENCIA_DISPLAY = _('Transferencias')

LLAMADAS_MANUALES = [LLAMADA_MANUAL]
LLAMADAS_DE_AGENTE = [LLAMADA_MANUAL, LLAMADA_PREVIEW]
LLAMADAS_TRANSFERENCIA = [LLAMADA_TRANSF_INTERNA, LLAMADA_TRANSF_EXTERNA]

INICIALES_POR_TIPO = {
    str(Campana.TYPE_MANUAL): {
        'total': 0,  # DIAL(tipo_llamada = Manual:1)
        'conectadas': 0,  # ANSWER(tipo_llamada = Manual:1)
        'no_conectadas': 0,  # NO CONNECT(tipo_llamada = Manual:1)
    },
    str(Campana.TYPE_DIALER): {
        'total': 0,  # DIAL(tipo_llamada = Dialer:2),
        'atendidas': 0,  # ANSWER(tipo_llamada = Dialer:2)  (puede ser ENTERQUEUE),
        'no_atendidas': 0,  # EXITWITHTIMEOUT(tipo_llamada = Dialer:2) +
                            # ABANDON(tipo_llamada = Dialer:2),
        'perdidas': 0,  # NO CONNECT(tipo_llamada = Dialer:2),
    },
    str(Campana.TYPE_ENTRANTE): {
        'total': 0,  # ENTERQUEUE + ABANDONWEL + ENTERQUEUE-TRANSFER (tipo_llamada = Entrante:3)
        'atendidas': 0,  # CONNECT(tipo_llamada = Entrante:3)
        'expiradas': 0,  # EXITWITHTIMEOUT(tipo_llamada = Entrante:3)
        'abandonadas': 0,  # ABANDON(tipo_llamada = Entrante:3)
        'abandonadas_anuncio': 0,  # ABANDONWEL(tipo_llamada = Entrante:3)
        'transferidas_atendidas': 0,  # CONNECT (tipo_llamada = Transf_interna:8)
        'transferidas_no_atendidas': 0,  # CAMPT-FAIL (tipo_llamada = cualquiera)
    },
    str(Campana.TYPE_PREVIEW): {
        'total': 0,  # DIAL(tipo_llamada = Preview:4)
        'conectadas': 0,  # ANSWER(tipo_llamada = Preview:4)
        'no_conectadas': 0,  # NO CONNECT(tipo_llamada = Preview:4)
    },
}

INICIALES_POR_CAMPANA = {
    str(Campana.TYPE_MANUAL): {
        'nombre': '',
        'efectuadas': 0,
        'conectadas': 0,
        'no_conectadas': 0,
        't_espera_conexion': 0,
    },
    str(Campana.TYPE_DIALER): {
        'nombre': '',
        'efectuadas': 0,
        'conectadas': 0,
        'atendidas': 0,
        'expiradas': 0,
        'abandonadas': 0,
        't_abandono': 0,
        't_espera_atencion': 0,
        't_espera_conexion': 0,
        'efectuadas_manuales': 0,
        'conectadas_manuales': 0,
        'no_conectadas_manuales': 0,
        't_espera_conexion_manuales': 0,
    },
    str(Campana.TYPE_ENTRANTE): {
        'nombre': '',
        'recibidas': 0,
        'recibidas_transferencias': 0,
        'atendidas': 0,
        'expiradas': 0,
        'abandonadas': 0,
        'abandonadas_anuncio': 0,
        't_abandono': 0,
        't_espera_conexion': 0,
        'efectuadas_manuales': 0,
        'conectadas_manuales': 0,
        'no_conectadas_manuales': 0,
        't_espera_conexion_manuales': 0,
    },
    str(Campana.TYPE_PREVIEW): {
        'nombre': '',
        'efectuadas': 0,
        'conectadas': 0,
        'no_conectadas': 0,
        't_espera_conexion': 0,
        'efectuadas_manuales': 0,
        'conectadas_manuales': 0,
        'no_conectadas_manuales': 0,
        't_espera_conexion_manuales': 0,
    }
}

CAMPANA_TYPES = {
    Campana.TYPE_ENTRANTE: Campana.TYPE_ENTRANTE_DISPLAY,
    Campana.TYPE_DIALER: Campana.TYPE_DIALER_DISPLAY,
    Campana.TYPE_MANUAL: Campana.TYPE_MANUAL_DISPLAY,
    Campana.TYPE_PREVIEW: Campana.TYPE_PREVIEW_DISPLAY,
    LLAMADA_TRANSF_EXTERNA: TYPE_TRANSFERENCIA_DISPLAY,
    LLAMADA_TRANSF_INTERNA: TYPE_TRANSFERENCIA_DISPLAY,
}


class ReporteDeLlamadas(object):

    def __init__(self, desde, hasta, incluir_finalizadas, user):
        self.campanas = self._campanas_implicadas(user, incluir_finalizadas)
        campanas_ids = self.campanas.values_list('id', flat=True)
        self.logs = LlamadaLog.objects.using('replica')\
            .filter(time__gte=desde, time__lte=hasta, campana_id__in=campanas_ids)

        self._inicializar_conteo_de_estadisticas(desde, hasta)

        self._contabilizar_estadisticas()

    def _campanas_implicadas(self, user, incluir_finalizadas):
        if user.get_is_administrador():
            if incluir_finalizadas:
                campanas = Campana.objects.obtener_actuales()
            else:
                campanas = Campana.objects.obtener_all_dialplan_asterisk()
        else:
            supervisor = user.get_supervisor_profile()
            if incluir_finalizadas:
                campanas = supervisor.campanas_asignadas_actuales()
            else:
                campanas = supervisor.campanas_asignadas_actuales_no_finalizadas()

        return campanas

    def _get_campana_type_display(self, campana_type):
        if campana_type in CAMPANA_TYPES:
            return CAMPANA_TYPES[campana_type]

    def _inicializar_conteo_de_estadisticas(self, desde, hasta):

        self.estadisticas = {
            'total_llamadas_procesadas': 0,  # DIAL + ENTERQUEUE(data3 = Entrante:3) + ABANDONWEL,

            'llamadas_por_tipo': {
                str(Campana.TYPE_MANUAL):
                    INICIALES_POR_TIPO[str(Campana.TYPE_MANUAL)].copy(),
                str(Campana.TYPE_DIALER):
                    INICIALES_POR_TIPO[str(Campana.TYPE_DIALER)].copy(),
                str(Campana.TYPE_ENTRANTE):
                    INICIALES_POR_TIPO[str(Campana.TYPE_ENTRANTE)].copy(),
                str(Campana.TYPE_PREVIEW):
                    INICIALES_POR_TIPO[str(Campana.TYPE_PREVIEW)].copy(),
            },

            'llamadas_por_campana': {},

            'tipos_de_llamada_por_campana':
            {
                str(Campana.TYPE_MANUAL): {},
                str(Campana.TYPE_DIALER): {},
                str(Campana.TYPE_ENTRANTE): {},
                str(Campana.TYPE_PREVIEW): {},
            }
        }

        self.estadisticas_por_fecha = {
            'llamadas_por_tipo': {
                str(Campana.TYPE_MANUAL): {},
                str(Campana.TYPE_DIALER): {},
                str(Campana.TYPE_ENTRANTE): {},
                str(Campana.TYPE_PREVIEW): {},
            },
            'tipos_de_llamada_por_campana': {
                str(Campana.TYPE_MANUAL): {},
                str(Campana.TYPE_DIALER): {},
                str(Campana.TYPE_ENTRANTE): {},
                str(Campana.TYPE_PREVIEW): {},
            },
        }

        for campana in self.campanas:
            self._inicializar_conteo_de_estadisticas_de_campana(campana)

    def _inicializar_conteo_de_estadisticas_de_campana(self, campana):
        tipo_display = self._get_campana_type_display(campana.type)
        tipo = str(campana.type)

        # Inicializar Llamadas por campaña
        self.estadisticas['llamadas_por_campana'][campana.id] = {
            'nombre': campana.nombre,
            'tipo': str(tipo_display),
            'total': 0,
            'manuales': 0,
        }

        # Inicializar Tipos de llamadas por campaña
        tipos_por_campana = INICIALES_POR_CAMPANA[tipo].copy()
        tipos_por_campana['nombre'] = campana.nombre
        self.estadisticas['tipos_de_llamada_por_campana'][tipo][campana.id] = tipos_por_campana
        self.estadisticas_por_fecha['tipos_de_llamada_por_campana'][tipo][campana.id] = {}

    def _contabilizar_estadisticas(self):
        for log in self.logs:
            fecha = fecha_hora_local(log.time).strftime('%d-%m-%Y')
            tipo_campana = str(log.tipo_campana)
            tipo_llamada = str(log.tipo_llamada)
            if tipo_llamada == str(LLAMADA_TRANSF_INTERNA):
                tipo_llamada = str(LLAMADA_ENTRANTE)
            if log.event == 'CAMPT-FAIL':
                tipo_llamada = str(LLAMADA_ENTRANTE)
            self._contabilizar_total_llamadas_procesadas(log)

            # Si no se identifica el tipo de llamada no se contabiliza por tipo.
            if tipo_llamada and tipo_llamada in self.estadisticas['llamadas_por_tipo']:
                estadisticas_tipo = self.estadisticas['llamadas_por_tipo'][tipo_llamada]
                self._contabilizar_llamada_por_tipo(estadisticas_tipo, log)
                llamadas_por_fecha = self._get_llamadas_de_tipo_en_fecha(tipo_llamada, fecha)
                self._contabilizar_llamada_por_tipo(llamadas_por_fecha, log)

            self._contabilizar_llamadas_por_campana(log)

            tipos_por_campana = self.estadisticas['tipos_de_llamada_por_campana']
            estadisticas_campana = tipos_por_campana[tipo_campana][log.campana_id]
            self._contabilizar_tipos_de_llamada_por_campana(estadisticas_campana, log)
            tipos_por_fecha = self._get_llamadas_de_campana_en_fecha(
                tipo_campana, log.campana_id, fecha)
            self._contabilizar_tipos_de_llamada_por_campana(tipos_por_fecha, log)

        self._aplicar_promedios_a_tiempos()
        self._generar_graficos()

    def _contabilizar_total_llamadas_procesadas(self, log):
        if log.event == 'DIAL' or (log.event in ['ENTERQUEUE', 'ABANDONWEL'] and
                                   log.tipo_campana == Campana.TYPE_ENTRANTE):
            self.estadisticas['total_llamadas_procesadas'] += 1
        #  Contabilizar solo llamadas transferidas a OTRA CAMPAÑA: ENTERQUEUE-TRANSFER
        if log.event == 'ENTERQUEUE-TRANSFER':
            self.estadisticas['total_llamadas_procesadas'] += 1

    def _contabilizar_llamada_por_tipo(self, estadisticas_tipo, log):
        # Contabilizar solo llamadas transferidas a OTRA CAMPAÑA: ENTERQUEUE-TRANSFER
        if log.tipo_llamada == LLAMADA_TRANSF_INTERNA:
            if log.event == 'ENTERQUEUE-TRANSFER':
                estadisticas_tipo['total'] += 1
            elif log.event == 'CONNECT':
                estadisticas_tipo['transferidas_atendidas'] += 1
        elif log.event == 'CAMPT-FAIL':
            estadisticas_tipo['transferidas_no_atendidas'] += 1
        elif log.event == 'DIAL':
            if not log.tipo_llamada == Campana.TYPE_ENTRANTE:
                estadisticas_tipo['total'] += 1
        elif log.event == 'ENTERQUEUE':
            if log.tipo_llamada == Campana.TYPE_ENTRANTE:
                estadisticas_tipo['total'] += 1
        elif log.event == 'ANSWER':
            if log.tipo_llamada in LLAMADAS_DE_AGENTE:
                estadisticas_tipo['conectadas'] += 1
            elif log.tipo_llamada == Campana.TYPE_DIALER:
                estadisticas_tipo['atendidas'] += 1
        elif log.event == 'CONNECT':
            if log.tipo_llamada == Campana.TYPE_ENTRANTE:
                estadisticas_tipo['atendidas'] += 1
        elif log.event == 'EXITWITHTIMEOUT':
            if log.tipo_llamada == Campana.TYPE_DIALER:
                estadisticas_tipo['perdidas'] += 1
            elif log.tipo_llamada == Campana.TYPE_ENTRANTE:
                estadisticas_tipo['expiradas'] += 1
        elif log.event == 'ABANDON':
            if log.tipo_llamada == Campana.TYPE_DIALER:
                estadisticas_tipo['perdidas'] += 1
            if log.tipo_llamada == Campana.TYPE_ENTRANTE:
                estadisticas_tipo['abandonadas'] += 1
        elif log.event == 'ABANDONWEL':
            # solo las campañas entrantes tienen este evento
            assert log.tipo_llamada == Campana.TYPE_ENTRANTE
            estadisticas_tipo['total'] += 1
            estadisticas_tipo['abandonadas_anuncio'] += 1
        elif log.event in LlamadaLog.EVENTOS_NO_CONTACTACION:
            if log.tipo_llamada in LLAMADAS_DE_AGENTE:
                estadisticas_tipo['no_conectadas'] += 1
            elif log.tipo_llamada == Campana.TYPE_DIALER:
                estadisticas_tipo['no_atendidas'] += 1

    def _contabilizar_llamadas_por_campana(self, log):
        estadisticas_campana = self.estadisticas['llamadas_por_campana'][log.campana_id]
        if log.event == 'DIAL':
            estadisticas_campana['total'] += 1
            if log.tipo_llamada in LLAMADAS_MANUALES:
                estadisticas_campana['manuales'] += 1
        elif log.event in ['ENTERQUEUE', 'ABANDONWEL']:
            if log.tipo_campana == Campana.TYPE_ENTRANTE:
                estadisticas_campana['total'] += 1
        elif log.event == 'ENTERQUEUE-TRANSFER':
            # assert(log.tipo_campana == Campana.TYPE_ENTRANTE, 'Transfiere a campaña no entrante?')
            estadisticas_campana['total'] += 1

    def _contabilizar_tipos_de_llamada_por_campana(self, estadisticas_campana, log):
        if log.tipo_campana == Campana.TYPE_MANUAL:
            self._contabilizar_tipos_de_llamada_por_campana_saliente(estadisticas_campana, log)
        elif log.tipo_campana == Campana.TYPE_DIALER:
            self._contabilizar_tipos_de_llamada_por_campana_dialer(estadisticas_campana, log)
        elif log.tipo_campana == Campana.TYPE_ENTRANTE:
            self._contabilizar_tipos_de_llamada_por_campana_entrante(estadisticas_campana, log)
        elif log.tipo_campana == Campana.TYPE_PREVIEW:
            self._contabilizar_tipos_de_llamada_por_campana_saliente(estadisticas_campana, log)

    def _contabilizar_tipos_de_llamada_por_campana_saliente(self, datos_campana, log):
        if not log.tipo_campana == Campana.TYPE_MANUAL and log.tipo_llamada in LLAMADAS_MANUALES:
            self._contabilizar_tipos_de_llamada_manual(datos_campana, log)
        if log.event == 'DIAL':
            datos_campana['efectuadas'] += 1
        elif log.event == 'ANSWER':
            datos_campana['conectadas'] += 1
            datos_campana['t_espera_conexion'] += log.bridge_wait_time
        elif log.event in LlamadaLog.EVENTOS_NO_CONTACTACION:
            datos_campana['no_conectadas'] += 1
            datos_campana['t_espera_conexion'] += log.bridge_wait_time

    def _contabilizar_tipos_de_llamada_por_campana_dialer(self, datos_campana, log):
        if log.tipo_llamada in LLAMADAS_MANUALES:
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

    def _contabilizar_tipos_de_llamada_por_campana_entrante(self, datos_campana, log):
        if log.tipo_llamada in LLAMADAS_MANUALES:
            self._contabilizar_tipos_de_llamada_manual(datos_campana, log)
        elif log.event == 'ENTERQUEUE':
            datos_campana['recibidas'] += 1
        elif log.event == 'ENTERQUEUE-TRANSFER':
            datos_campana['recibidas'] += 1
            datos_campana['recibidas_transferencias'] += 1
        elif log.event == 'CONNECT':
            datos_campana['atendidas'] += 1
            datos_campana['t_espera_conexion'] += log.bridge_wait_time
        elif log.event == 'EXITWITHTIMEOUT':
            datos_campana['expiradas'] += 1
        elif log.event == 'ABANDON':
            datos_campana['abandonadas'] += 1
            datos_campana['t_abandono'] += log.bridge_wait_time
        elif log.event == 'ABANDONWEL':
            datos_campana['recibidas'] += 1
            datos_campana['abandonadas_anuncio'] += 1
            datos_campana['t_abandono'] += log.bridge_wait_time

    def _contabilizar_tipos_de_llamada_manual(self, datos_campana, log):
        if log.event == 'DIAL':
            datos_campana['efectuadas_manuales'] += 1
        elif log.event == 'ANSWER':
            datos_campana['conectadas_manuales'] += 1
            datos_campana['t_espera_conexion_manuales'] += log.bridge_wait_time
        elif log.event in LlamadaLog.EVENTOS_NO_CONTACTACION:
            datos_campana['no_conectadas_manuales'] += 1
            datos_campana['t_espera_conexion_manuales'] += log.bridge_wait_time

    def _aplicar_promedios_a_tiempos(self):
        for tipo, datos_tipo in self.estadisticas['tipos_de_llamada_por_campana'].items():
            for id_campana, datos_campana in datos_tipo.items():
                self._aplicar_promedios_a_tiempos_de_campana(tipo, datos_campana)

                datos_por_tipo = self.estadisticas_por_fecha['tipos_de_llamada_por_campana'][tipo]
                for fecha, datos_fecha in datos_por_tipo[id_campana].items():
                    self._aplicar_promedios_a_tiempos_de_campana(tipo, datos_fecha)

    def _aplicar_promedios_a_tiempos_de_campana(self, tipo, datos_campana):
        if tipo in [str(Campana.TYPE_MANUAL), str(Campana.TYPE_PREVIEW)]:
            efectuadas = datos_campana['efectuadas']
            if efectuadas > 0:
                suma_esperas = datos_campana['t_espera_conexion']
                datos_campana['t_espera_conexion'] = suma_esperas / efectuadas
        elif tipo == str(Campana.TYPE_DIALER):
            abandonadas = datos_campana['abandonadas']
            if abandonadas > 0:
                datos_campana['t_abandono'] = datos_campana['t_abandono'] / abandonadas
            conectadas = datos_campana['conectadas']
            if conectadas > 0:
                datos_campana['t_espera_conexion'] = datos_campana['t_espera_conexion'] / conectadas
            atendidas = datos_campana['atendidas']
            if abandonadas > 0:
                datos_campana['t_espera_atencion'] = datos_campana['t_espera_atencion'] / atendidas

        elif tipo == str(Campana.TYPE_ENTRANTE):
            atendidas = datos_campana['atendidas']
            if atendidas > 0:
                datos_campana['t_espera_conexion'] = datos_campana['t_espera_conexion'] / atendidas
            abandonadas = datos_campana['abandonadas']
            if abandonadas > 0:
                datos_campana['t_abandono'] = datos_campana['t_abandono'] / abandonadas
        if not tipo == str(Campana.TYPE_MANUAL):
            efectuadas = datos_campana['efectuadas_manuales']
            if efectuadas > 0:
                suma_esperas = datos_campana['t_espera_conexion_manuales']
                datos_campana['t_espera_conexion_manuales'] = suma_esperas / efectuadas

    def _get_llamadas_de_tipo_en_fecha(self, tipo_llamada, fecha):
        llamadas_de_tipo = self.estadisticas_por_fecha['llamadas_por_tipo'][tipo_llamada]
        if fecha not in llamadas_de_tipo:
            llamadas_de_tipo[fecha] = INICIALES_POR_TIPO[tipo_llamada].copy()
        return llamadas_de_tipo[fecha]

    def _get_llamadas_de_campana_en_fecha(self, tipo_campana, campana_id, fecha):
        tipos_por_campana = self.estadisticas_por_fecha['tipos_de_llamada_por_campana']
        fechas_por_campana = tipos_por_campana[tipo_campana][campana_id]
        if fecha not in fechas_por_campana:
            fechas_por_campana[fecha] = INICIALES_POR_CAMPANA[tipo_campana].copy()
        return fechas_por_campana[fecha]

    def _generar_graficos(self):
        graficador = GraficosReporteDeLlamadas(self.estadisticas)
        self.graficos = graficador.graficos


class GraficosReporteDeLlamadas(object):

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
        grafico = pygal.Bar(show_legend=True, style=ESTILO_AMARILLO_VERDE_ROJO)
        grafico.x_labels = [_('Manuales'), _(u'Dialer'), _(u'Entrantes'), _(u'Preview')]
        por_tipo = estadisticas['llamadas_por_tipo']
        grafico.add(
            _(u'Intentos'),
            [por_tipo[str(Campana.TYPE_MANUAL)]['total'],
             por_tipo[str(Campana.TYPE_DIALER)]['total'],
             por_tipo[str(Campana.TYPE_ENTRANTE)]['total'],
             por_tipo[str(Campana.TYPE_PREVIEW)]['total'], ])

        atendidas_entrantes = por_tipo[str(Campana.TYPE_ENTRANTE)]['atendidas'] + \
            por_tipo[str(Campana.TYPE_ENTRANTE)]['transferidas_atendidas']
        grafico.add(
            _('Conexión'),
            [por_tipo[str(Campana.TYPE_MANUAL)]['conectadas'],
             por_tipo[str(Campana.TYPE_DIALER)]['atendidas'],
             atendidas_entrantes,
             por_tipo[str(Campana.TYPE_PREVIEW)]['conectadas'],
             ])

        perdidas_dialer = por_tipo[str(Campana.TYPE_DIALER)]['no_atendidas'] + \
            por_tipo[str(Campana.TYPE_DIALER)]['perdidas']
        perdidas_entrantes = por_tipo[str(Campana.TYPE_ENTRANTE)]['expiradas'] + \
            por_tipo[str(Campana.TYPE_ENTRANTE)]['abandonadas'] + \
            por_tipo[str(Campana.TYPE_ENTRANTE)]['abandonadas_anuncio'] + \
            por_tipo[str(Campana.TYPE_ENTRANTE)]['transferidas_no_atendidas']
        grafico.add(
            _('Fallo'), [por_tipo[str(Campana.TYPE_MANUAL)]['no_conectadas'],
                         perdidas_dialer,
                         perdidas_entrantes,
                         por_tipo[str(Campana.TYPE_PREVIEW)]['no_conectadas'],
                         ])

        self.graficos['barras_llamadas_por_tipo'] = adicionar_render_unicode(grafico)

    def _generar_grafico_de_torta_de_porcentajes_por_tipo(self, estadisticas):
        # Porcentajes de llamadas por tipo de llamada
        no_data_text = _("No hay llamadas para ese periodo")
        grafico = pygal.Pie(style=ESTILO_AZUL_VIOLETA_NARANJA_CELESTE, no_data_text=no_data_text,
                            no_data_font_size=32, legend_font_size=25, truncate_legend=10,
                            tooltip_font_size=50)
        total = float(estadisticas['total_llamadas_procesadas'])
        total_manual = estadisticas['llamadas_por_tipo'][str(Campana.TYPE_MANUAL)]['total']
        total_dialer = estadisticas['llamadas_por_tipo'][str(Campana.TYPE_DIALER)]['total']
        total_entrante = estadisticas['llamadas_por_tipo'][str(Campana.TYPE_ENTRANTE)]['total']
        total_preview = estadisticas['llamadas_por_tipo'][str(Campana.TYPE_PREVIEW)]['total']

        porcentaje_dialer = (100.0 * float(total_dialer) / float(total)) if total > 0 else 0
        porcentaje_entrante = (100.0 * float(total_entrante) / float(total)) if total > 0 else 0
        porcentaje_manual = (100.0 * float(total_manual) / float(total)) if total > 0 else 0
        porcentaje_preview = (100.0 * float(total_preview) / float(total)) if total > 0 else 0

        grafico.add(_('Manual'), porcentaje_manual)
        grafico.add(_('Dialer'), porcentaje_dialer)
        grafico.add(_('Entrante'), porcentaje_entrante)
        grafico.add(_('Preview'), porcentaje_preview)
        self.graficos['torta_porcentajes_por_tipo'] = adicionar_render_unicode(grafico)

    def _generar_grafico_de_barras_de_llamadas_por_campana(self, estadisticas):
        # Cantidad de llamadas de las campana
        grafico = pygal.Bar(show_legend=True, style=ESTILO_VERDE_AZUL)

        nombres_campanas = []
        totales_campanas = []
        manuales_campanas = []
        for datos_campana in estadisticas['llamadas_por_campana'].values():
            nombres_campanas.append(datos_campana['nombre'])
            totales_campanas.append(datos_campana['total'])
            manuales_campanas.append(datos_campana['manuales'])
        grafico.x_labels = nombres_campanas
        grafico.add(_('Total'), totales_campanas)
        grafico.add(_('Manuales'), manuales_campanas)
        self.graficos['barra_llamada_por_campana'] = adicionar_render_unicode(grafico)

    def _generar_grafico_de_barras_de_llamadas_dialer(self, estadisticas):
        grafico = pygal.StackedBar(show_legend=True, style=ESTILO_ROJO_VERDE_GRIS_NEGRO)

        nombres_campanas = []
        no_atendidas = []
        conectadas = []
        expiradas = []
        abandonadas = []
        por_campana = estadisticas['tipos_de_llamada_por_campana'][str(Campana.TYPE_DIALER)]
        for datos_campana in por_campana.values():
            nombres_campanas.append(datos_campana['nombre'])
            no_atendidas.append(datos_campana['efectuadas'] - datos_campana['atendidas'])
            conectadas.append(datos_campana['conectadas'])
            abandonadas.append(datos_campana['abandonadas'])
            expiradas.append(datos_campana['expiradas'])

        grafico.x_labels = nombres_campanas
        grafico.add(_(u'No contactadas'), no_atendidas)
        grafico.add(_(u'Procesadas'), conectadas)
        grafico.add(_(u'Abandonadas'), abandonadas)
        grafico.add(_(u'Expiradas'), expiradas)
        self.graficos['barra_campana_llamadas_dialer'] = adicionar_render_unicode(grafico)

    def _generar_grafico_de_barras_de_llamadas_entrantes(self, estadisticas):
        grafico = pygal.StackedBar(show_legend=True, style=ESTILO_VERDE_GRIS_NEGRO_ROJO)

        nombres_campanas = []
        atendidas = []
        expiradas = []
        abandonadas = []
        abandonadas_anuncio = []
        por_campana = estadisticas['tipos_de_llamada_por_campana'][str(Campana.TYPE_ENTRANTE)]
        for datos_campana in por_campana.values():
            nombres_campanas.append(datos_campana['nombre'])
            atendidas.append(datos_campana['atendidas'])
            abandonadas.append(datos_campana['abandonadas'])
            abandonadas_anuncio.append(datos_campana['abandonadas_anuncio'])
            expiradas.append(datos_campana['expiradas'])

        grafico.x_labels = nombres_campanas
        grafico.add(_(u'Atendidas'), atendidas)
        grafico.add(_(u'Abandonadas'), abandonadas)
        grafico.add(_(u'Abandonadas durante anuncio'), abandonadas_anuncio)
        grafico.add(_(u'Expiradas'), expiradas)
        self.graficos['barra_campana_llamadas_entrantes'] = adicionar_render_unicode(grafico)

    def _generar_grafico_de_barras_de_llamadas_manuales(self, estadisticas):
        grafico = pygal.StackedBar(show_legend=True, style=ESTILO_VERDE_ROJO)

        nombres_campanas = []
        conectadas = []
        no_conectadas = []
        por_campana = estadisticas['tipos_de_llamada_por_campana'][str(Campana.TYPE_MANUAL)]
        for datos_campana in por_campana.values():
            nombres_campanas.append(datos_campana['nombre'])
            conectadas.append(datos_campana['conectadas'])
            no_conectadas.append(datos_campana['no_conectadas'])

        grafico.x_labels = nombres_campanas
        grafico.add(_(u'Conectadas'), conectadas)
        grafico.add(_(u'No conectadas'), no_conectadas)

        self.graficos['barra_campana_llamadas_manuales'] = adicionar_render_unicode(grafico)

    def _generar_grafico_de_barras_de_llamadas_preview(self, estadisticas):
        grafico = pygal.StackedBar(show_legend=True, style=ESTILO_VERDE_ROJO)

        nombres_campanas = []
        conectadas = []
        no_conectadas = []
        por_campana = estadisticas['tipos_de_llamada_por_campana'][str(Campana.TYPE_PREVIEW)]
        for datos_campana in por_campana.values():
            nombres_campanas.append(datos_campana['nombre'])
            conectadas.append(datos_campana['conectadas'])
            no_conectadas.append(datos_campana['no_conectadas'])

        grafico.x_labels = nombres_campanas
        grafico.add(_(u'Conectadas'), conectadas)
        grafico.add(_(u'No conectadas'), no_conectadas)
        self.graficos['barra_campana_llamadas_preview'] = adicionar_render_unicode(grafico)


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
        filas = [[_('Tipo'), _('Total'), _('Conectadas'), _('No conectadas'),
                  _('Atendidas'), _('No atendidas'), _('Perdidas'), _('Expiradas'),
                  _('Abandonadas'), _('Abandonadas durante anuncio'),
                  _('Transferidas Atendidas'), _('Transferidas No Atendidas')], ]
        filas.append([
            str(Campana.TYPE_MANUAL_DISPLAY),
            force_text(por_tipo[str(Campana.TYPE_MANUAL)]['total']),
            force_text(por_tipo[str(Campana.TYPE_MANUAL)]['conectadas']),
            force_text(por_tipo[str(Campana.TYPE_MANUAL)]['no_conectadas']),
            '', '', '', '', '', '', '',
        ])
        filas.append([
            str(Campana.TYPE_DIALER_DISPLAY),
            force_text(por_tipo[str(Campana.TYPE_DIALER)]['total']),
            '', '',
            force_text(por_tipo[str(Campana.TYPE_DIALER)]['atendidas']),
            force_text(por_tipo[str(Campana.TYPE_DIALER)]['no_atendidas']),
            force_text(por_tipo[str(Campana.TYPE_DIALER)]['perdidas']),
            '', '', '', '',
        ])
        filas.append([
            str(Campana.TYPE_ENTRANTE_DISPLAY),
            force_text(por_tipo[str(Campana.TYPE_ENTRANTE)]['total']),
            '', '',
            force_text(por_tipo[str(Campana.TYPE_ENTRANTE)]['atendidas']),
            '', '',
            force_text(por_tipo[str(Campana.TYPE_ENTRANTE)]['expiradas']),
            force_text(por_tipo[str(Campana.TYPE_ENTRANTE)]['abandonadas'],),
            force_text(por_tipo[str(Campana.TYPE_ENTRANTE)]['abandonadas_anuncio'],),
            force_text(por_tipo[str(Campana.TYPE_ENTRANTE)]['transferidas_atendidas'],),
            force_text(por_tipo[str(Campana.TYPE_ENTRANTE)]['transferidas_no_atendidas'],),
        ])
        filas.append([
            str(Campana.TYPE_PREVIEW_DISPLAY),
            force_text(por_tipo[str(Campana.TYPE_PREVIEW)]['total']),
            force_text(por_tipo[str(Campana.TYPE_PREVIEW)]['conectadas']),
            force_text(por_tipo[str(Campana.TYPE_PREVIEW)]['no_conectadas']),
            '', '', '', '', '', '', '',
        ])
        return filas

    def _obtener_filas_llamadas_por_campana(self, estadisticas):
        por_campana = estadisticas['llamadas_por_campana']
        filas = [[_('Nombre'), _('Tipo'), _('Total'), _('Manuales')], ]
        for id, estadisticas_campana in por_campana.items():
            filas.append([estadisticas_campana['nombre'],
                          estadisticas_campana['tipo'],
                          force_text(estadisticas_campana['total']),
                          force_text(estadisticas_campana['manuales']),
                          ])
        return filas

    def _obtener_filas_manual(self, estadisticas):
        por_campana = estadisticas['tipos_de_llamada_por_campana'][str(Campana.TYPE_MANUAL)]
        filas = [[_('Nombre'), _('Efectuadas'), _('Conectadas'), _('No conectadas'),
                  _('T. Espera Conexion')], ]
        for id, estadisticas_campana in por_campana.items():
            filas.append([estadisticas_campana['nombre'],
                          force_text(estadisticas_campana['efectuadas']),
                          force_text(estadisticas_campana['conectadas']),
                          force_text(estadisticas_campana['no_conectadas']),
                          force_text(estadisticas_campana['t_espera_conexion']),
                          ])
        return filas

    def _obtener_filas_dialer(self, estadisticas):
        por_campana = estadisticas['tipos_de_llamada_por_campana'][str(Campana.TYPE_DIALER)]
        filas = [[_('Nombre'), _('Efectuadas'), _('Conectadas'), _('Atendidas'), _('Expiradas'),
                  _('Abandonadas'), _('T. Abandono'), _('T. Espera Atención'),
                  _('T. Espera Conexion'), _('Manuales Efectuadas'), _('Manuales Conectadas'),
                  _('Manuales No Conectadas'), _('T. Espera Conexión Manuales')], ]
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
        por_campana = estadisticas['tipos_de_llamada_por_campana'][str(Campana.TYPE_ENTRANTE)]
        filas = [[_('Nombre'), _('Recibidas'), _('Atendidas'), _('Expiradas'), _('Abandonadas'),
                  _('Abandonadas durante anuncio'), _('T. Abandono'), _('T. Espera Conexion'),
                  _('Manuales Efectuadas'), _('Manuales Conectadas'), _('Manuales No Conectadas'),
                  _('T. Espera Conexión Manuales')], ]
        for id, estadisticas_campana in por_campana.items():
            filas.append([estadisticas_campana['nombre'],
                          force_text(estadisticas_campana['recibidas']),
                          force_text(estadisticas_campana['atendidas']),
                          force_text(estadisticas_campana['expiradas']),
                          force_text(estadisticas_campana['abandonadas']),
                          force_text(estadisticas_campana['abandonadas_anuncio']),
                          force_text(estadisticas_campana['t_abandono']),
                          force_text(estadisticas_campana['t_espera_conexion']),
                          force_text(estadisticas_campana['efectuadas_manuales']),
                          force_text(estadisticas_campana['conectadas_manuales']),
                          force_text(estadisticas_campana['no_conectadas_manuales']),
                          force_text(estadisticas_campana['t_espera_conexion_manuales']),
                          ])
        return filas

    def _obtener_filas_preview(self, estadisticas):
        por_campana = estadisticas['tipos_de_llamada_por_campana'][str(Campana.TYPE_PREVIEW)]
        filas = [[_('Nombre'), _('Efectuadas'), _('Conectadas'), _('No conectadas'),
                  _('T. Espera Conexion'), _('Manuales Efectuadas'), _('Manuales Conectadas'),
                  _('Manuales No Conectadas'), _('T. Espera Conexión Manuales')], ]
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


class ReporteTipoDeLlamadasDeCampana(ReporteDeLlamadas):

    def __init__(self, desde, hasta, id_campana):
        self.logs = LlamadaLog.objects.using('replica').filter(time__gte=desde,
                                                               time__lte=hasta,
                                                               campana_id=id_campana)

        self.campana = Campana.objects.get(id=id_campana)
        tipo = str(self.campana.type)
        self.estadisticas = INICIALES_POR_CAMPANA[tipo].copy()

        self._contabilizar_estadisticas()

    def _contabilizar_estadisticas(self):
        tipo = str(self.campana.type)
        for log in self.logs:
            self._contabilizar_tipos_de_llamada_por_campana(self.estadisticas, log)
        self._aplicar_promedios_a_tiempos_de_campana(tipo, self.estadisticas)
