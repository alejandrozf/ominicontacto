# -*- coding: utf-8 -*-

"""
Servicio para generar reporte de las grabaciones de las llamadas
"""

import json
import pygal

from collections import OrderedDict
from pygal.style import Style

from django.db.models import Count

from ominicontacto_app.models import Queuelog, Campana
import logging as _logging

logger = _logging.getLogger(__name__)


ESTILO_AZUL_ROJO_AMARILLO = Style(
    background='transparent',
    plot_background='transparent',
    foreground='#555',
    foreground_light='#555',
    foreground_dark='#555',
    opacity='1',
    opacity_hover='.6',
    transition='400ms ease-in',
    colors=('#428bca', '#5cb85c', '#5bc0de', '#f0ad4e', '#d9534f',
            '#a95cb8', '#5cb8b5', '#caca43', '#96ac43', '#ca43ca')
)


class GraficoService():

    def _campanas_implicadas(self, user, finalizadas):
        if finalizadas:
            campanas = Campana.objects.obtener_all_activas_finalizadas()
        else:
            campanas = Campana.objects.obtener_all_dialplan_asterisk()

        if not user.get_is_administrador():
            campanas = Campana.objects.obtener_campanas_vista_by_user(campanas, user)

        return campanas

    def _computar_totales_por_tipo(self, estadisticas):
        total_llamadas_dict = OrderedDict()

        total_llamadas_dict['total_llamadas_ingresadas'] = 0

        total_llamadas_dict['llamadas_ingresadas_dialer'] = \
            estadisticas[Campana.TYPE_DIALER]['no_manuales']['ENTERQUEUE']
        total_llamadas_dict['llamadas_gestionadas_dialer'] = \
            estadisticas[Campana.TYPE_DIALER]['no_manuales']['CONNECT']
        total_llamadas_dict['llamadas_perdidas_dialer'] = \
            estadisticas[Campana.TYPE_DIALER]['no_manuales']['ABANDON'] + \
            estadisticas[Campana.TYPE_DIALER]['no_manuales']['EXITWITHTIMEOUT'] + \
            estadisticas[Campana.TYPE_DIALER]['manuales']['EXITWITHTIMEOUT']

        total_llamadas_dict['llamadas_ingresadas_entrantes'] = \
            estadisticas[Campana.TYPE_ENTRANTE]['no_manuales']['ENTERQUEUE']
        total_llamadas_dict['llamadas_atendidas_entrantes'] = \
            estadisticas[Campana.TYPE_ENTRANTE]['no_manuales']['CONNECT']
        total_llamadas_dict['llamadas_expiradas_entrantes'] = \
            estadisticas[Campana.TYPE_ENTRANTE]['no_manuales']['EXITWITHTIMEOUT']
        total_llamadas_dict['llamadas_abandonadas_entrantes'] = \
            estadisticas[Campana.TYPE_ENTRANTE]['no_manuales']['ABANDON']

        total_llamadas_dict['llamadas_ingresadas_manuales'] = \
            estadisticas['manuales']['ENTERQUEUE']
        total_llamadas_dict['llamadas_atendidas_manuales'] = \
            estadisticas['manuales']['CONNECT']
        total_llamadas_dict['llamadas_abandonadas_manuales'] = \
            estadisticas['manuales']['ABANDON']

        total_llamadas_dict['llamadas_ingresadas_preview'] = \
            estadisticas[Campana.TYPE_PREVIEW]['no_manuales']['ENTERQUEUE']
        total_llamadas_dict['llamadas_atendidas_preview'] = \
            estadisticas[Campana.TYPE_PREVIEW]['no_manuales']['CONNECT']
        total_llamadas_dict['llamadas_expiradas_preview'] = \
            estadisticas[Campana.TYPE_PREVIEW]['no_manuales']['EXITWITHTIMEOUT']
        total_llamadas_dict['llamadas_abandonadas_preview'] = \
            estadisticas[Campana.TYPE_PREVIEW]['no_manuales']['ABANDON']

        total_llamadas_ingresadas = \
            total_llamadas_dict['llamadas_ingresadas_dialer'] + \
            total_llamadas_dict['llamadas_ingresadas_entrantes'] + \
            total_llamadas_dict['llamadas_ingresadas_manuales'] + \
            total_llamadas_dict['llamadas_ingresadas_preview']
        total_llamadas_dict['total_llamadas_ingresadas'] = total_llamadas_ingresadas

        return total_llamadas_dict

    def _computar_llamadas_por_campana(self, estadisticas, campanas, tipos_campana):
        campanas_ids_nombres = OrderedDict()
        campanas_tipos = []

        for campana in campanas.order_by('pk'):
            campanas_ids_nombres[campana.pk] = campana.nombre
            campana_tipo = campana.get_type_display()
            campanas_tipos.append(campana_tipo)

        campanas_ids = campanas_ids_nombres.keys()

        campanas_dict = {}
        for tipo in tipos_campana:
            for campana_id in estadisticas[tipo]['por_campana']:
                datos_campana = estadisticas[tipo]['por_campana'][campana_id]
                cantidad = (datos_campana['manuales']['ENTERQUEUE'] +
                            datos_campana['no_manuales']['ENTERQUEUE'])
                campanas_dict[campana_id] = cantidad

        campanas_manuales_dict = {}
        for tipo in tipos_campana:
            for campana_id in estadisticas[tipo]['por_campana']:
                cantidad = \
                    estadisticas[tipo]['por_campana'][campana_id]['manuales']['CONNECT']
                cantidad += \
                    estadisticas[tipo]['por_campana'][campana_id]['manuales']['ABANDON']
                cantidad += \
                    estadisticas[tipo]['por_campana'][campana_id]['manuales']['EXITWITHTIMEOUT']
                campanas_manuales_dict[campana_id] = cantidad

        result = (campanas_dict, campanas_manuales_dict, campanas_ids,
                  campanas_ids_nombres.values(), campanas_tipos)

        return result

    def _computar_totales_por_campana(self, campanas_dict, campanas_manuales_dict, campanas):
        """
        Obtiene los totales de llamadas por campana a partir de una lista de campañas
        """
        total_campana = []
        total_manuales = []
        for campana_id in campanas:
            campana_manuales_count = campanas_manuales_dict.get(campana_id, 0)
            campana_count = campanas_dict.get(campana_id, 0)
            total_campana.append(campana_count)
            total_manuales.append(campana_manuales_count)
        return total_campana, total_manuales

    def _computar_totales_por_campanas_de_tipo(self, estadisticas, tipo):
        queues_tiempo = []
        nombres_queues = []
        total_atendidas = []
        total_abandonadas = []
        total_expiradas = []

        for campana_id in estadisticas[tipo]['por_campana']:
            datos_campana = estadisticas[tipo]['por_campana'][campana_id]
            cantidad_campana = []
            cantidad_campana.append(datos_campana['nombre'])
            cantidad_campana.append(datos_campana['manuales']['ENTERQUEUE'] +
                                    datos_campana['no_manuales']['ENTERQUEUE'])
            cantidad_campana.append(datos_campana['manuales']['CONNECT'] +
                                    datos_campana['no_manuales']['CONNECT'])
            cantidad_campana.append(datos_campana['manuales']['EXITWITHTIMEOUT'] +
                                    datos_campana['no_manuales']['EXITWITHTIMEOUT'])
            cantidad_campana.append(datos_campana['manuales']['ABANDON'] +
                                    datos_campana['no_manuales']['ABANDON'])
            queues_tiempo.append(cantidad_campana)

            nombres_queues.append(datos_campana['nombre'])
            total_atendidas.append(datos_campana['manuales']['CONNECT'] +
                                   datos_campana['no_manuales']['CONNECT'])
            total_abandonadas.append(datos_campana['manuales']['ABANDON'] +
                                     datos_campana['no_manuales']['ABANDON'])
            total_expiradas.append(datos_campana['manuales']['EXITWITHTIMEOUT'] +
                                   datos_campana['no_manuales']['EXITWITHTIMEOUT'])

        totales_grafico = {
            'nombres_queues': nombres_queues,
            'total_atendidas': total_atendidas,
            'total_abandonadas': total_abandonadas,
            'total_expiradas': total_expiradas
        }

        return queues_tiempo, totales_grafico

    def _formatear_estadisticas(self, estadisticas, campanas, tipos_campana):

        # Se organizan los datos precalculados para cargarlos al contexto y crear los graficos

        total_llamadas_dict = self._computar_totales_por_tipo(estadisticas)

        queues_llamadas_dialer, totales_grafico_dialer = \
            self._computar_totales_por_campanas_de_tipo(estadisticas, Campana.TYPE_DIALER)
        queues_llamadas_dialer_json = json.dumps({'filas_datos': queues_llamadas_dialer})
        queues_llamadas_entrantes, totales_grafico_entrantes = \
            self._computar_totales_por_campanas_de_tipo(estadisticas, Campana.TYPE_ENTRANTE)
        queues_llamadas_entrantes_json = json.dumps({'filas_datos': queues_llamadas_entrantes})
        queues_llamadas_manuales, totales_grafico_manuales = \
            self._computar_totales_por_campanas_de_tipo(estadisticas, Campana.TYPE_MANUAL)
        queues_llamadas_manuales_json = json.dumps({'filas_datos': queues_llamadas_manuales})
        queues_llamadas_preview, totales_grafico_preview = \
            self._computar_totales_por_campanas_de_tipo(estadisticas, Campana.TYPE_PREVIEW)
        queues_llamadas_preview_json = json.dumps({'filas_datos': queues_llamadas_preview})

        (dict_campana, dict_campana_manuales, campanas, campanas_nombre,
            tipos_campana) = self._computar_llamadas_por_campana(estadisticas,
                                                                 campanas,
                                                                 tipos_campana)

        total_campana, total_manuales = self._computar_totales_por_campana(
            dict_campana, dict_campana_manuales, campanas)

        dic_estadisticas = {
            'campana_nombre': campanas_nombre,
            'campana': campanas,
            'total_campana': total_campana,
            'total_manuales': total_manuales,
            'tipos_campana': tipos_campana,
            'queues_llamadas_dialer': queues_llamadas_dialer,
            'queues_llamadas_dialer_json': queues_llamadas_dialer_json,
            'totales_grafico_dialer': totales_grafico_dialer,
            'queues_llamadas_entrantes': queues_llamadas_entrantes,
            'queues_llamadas_entrantes_json': queues_llamadas_entrantes_json,
            'totales_grafico_entrantes': totales_grafico_entrantes,
            'queues_llamadas_manuales': queues_llamadas_manuales,
            'queues_llamadas_manuales_json': queues_llamadas_manuales_json,
            'totales_grafico_manuales': totales_grafico_manuales,
            'queues_llamadas_preview': queues_llamadas_preview,
            'queues_llamadas_preview_json': queues_llamadas_preview_json,
            'totales_grafico_preview': totales_grafico_preview,
            'total_llamadas_dict': total_llamadas_dict,
            'total_llamadas_json': json.dumps(total_llamadas_dict),
        }
        return dic_estadisticas

    def _inicializar_conteo_de_estadisticas(self, campanas, tipos_campana):
        estadisticas = {
            'no_manuales': {
                'ENTERQUEUE': 0,
                'CONNECT': 0,
                'ABANDON': 0,
                'EXITWITHTIMEOUT': 0,
            },
            'manuales': {
                'ENTERQUEUE': 0,
                'CONNECT': 0,
                'ABANDON': 0,
                'EXITWITHTIMEOUT': 0,
            },
        }
        for tipo_campana in tipos_campana:
            estadisticas[tipo_campana] = {
                'por_campana': {},
                'manuales': {
                    'ENTERQUEUE': 0,
                    'CONNECT': 0,
                    'ABANDON': 0,
                    'EXITWITHTIMEOUT': 0,
                },
                'no_manuales': {
                    'ENTERQUEUE': 0,
                    'CONNECT': 0,
                    'ABANDON': 0,
                    'EXITWITHTIMEOUT': 0,
                },
            }
        for campana in campanas:
            estadisticas[campana.type]['por_campana'][campana.id] = {
                'nombre': campana.nombre,
                'manuales': {
                    'ENTERQUEUE': 0,
                    'CONNECT': 0,
                    'ABANDON': 0,
                    'EXITWITHTIMEOUT': 0,
                },
                'no_manuales': {
                    'ENTERQUEUE': 0,
                    'CONNECT': 0,
                    'ABANDON': 0,
                    'EXITWITHTIMEOUT': 0,
                },
            }

        return estadisticas

    def _contabilizar_en_estadisticas(self, estadisticas, cantidad_evento):
        tipo = int(cantidad_evento['data5'])
        evento = cantidad_evento['event']
        campana_id = cantidad_evento['campana_id']
        cantidad = cantidad_evento['cantidad']

        es_manual = cantidad_evento['data4'] == 'saliente'
        if es_manual:
            estadisticas['manuales'][evento] += cantidad
            estadisticas[tipo]['manuales'][evento] += cantidad
            estadisticas[tipo]['por_campana'][campana_id]['manuales'][evento] += cantidad
        else:
            estadisticas['no_manuales'][evento] += cantidad
            estadisticas[tipo]['no_manuales'][evento] += cantidad
            estadisticas[tipo]['por_campana'][campana_id]['no_manuales'][evento] += cantidad

    def _calcular_estadisticas(self, fecha_inferior, fecha_superior, user, finalizadas):

        campanas = self._campanas_implicadas(user, finalizadas)
        events = ['ENTERQUEUE', 'CONNECT', 'ABANDON', 'EXITWITHTIMEOUT']
        tipos_campana = (Campana.TYPE_ENTRANTE,
                         Campana.TYPE_DIALER,
                         Campana.TYPE_MANUAL,
                         Campana.TYPE_PREVIEW)

        cantidades = Queuelog.objects.filter(event__in=events,
                                             data5__in=tipos_campana,
                                             campana_id__in=campanas,
                                             time__range=(fecha_inferior, fecha_superior)
                                             ).values('data4', 'data5', 'campana_id', 'event'
                                                      ).annotate(cantidad=Count('campana_id'))

        estadisticas = self._inicializar_conteo_de_estadisticas(campanas, tipos_campana)

        for cantidad in cantidades:
            self._contabilizar_en_estadisticas(estadisticas, cantidad)

        estadisticas_formato = self._formatear_estadisticas(estadisticas, campanas, tipos_campana)
        estadisticas_formato['fecha_desde'] = fecha_inferior
        estadisticas_formato['fecha_hasta'] = fecha_superior
        return estadisticas_formato

    def _generar_grafico_torta_porcentajes(self, total_llamadas_dict):

        # Muestra los porcentajes del total de llamados de cada tipo de campaña
        total_llamadas_ingresadas = total_llamadas_dict['total_llamadas_ingresadas']

        porcentaje_dialer = 0.0
        porcentaje_entrantes = 0.0
        porcentaje_manual = 0.0
        porcentaje_preview = 0.0
        total_dialer = total_llamadas_dict['llamadas_ingresadas_dialer']
        total_entrantes = total_llamadas_dict['llamadas_ingresadas_entrantes']
        total_manual = total_llamadas_dict['llamadas_ingresadas_manuales']
        total_preview = total_llamadas_dict['llamadas_ingresadas_preview']
        if total_llamadas_ingresadas > 0:
            porcentaje_dialer = (100.0 * float(total_dialer) /
                                 float(total_llamadas_ingresadas))
            porcentaje_entrantes = (100.0 * float(total_entrantes) /
                                    float(total_llamadas_ingresadas))
            porcentaje_manual = (100.0 * float(total_manual) /
                                 float(total_llamadas_ingresadas))
            porcentaje_preview = (100.0 * float(total_preview) /
                                  float(total_llamadas_ingresadas))

        no_data_text = "No hay llamadas para ese periodo"
        # torta_porcentajes_por_tipo.title = "Resultado de las llamadas"
        torta_porcentajes_por_tipo = pygal.Pie(  # @UndefinedVariable
            style=ESTILO_AZUL_ROJO_AMARILLO,
            no_data_text=no_data_text,
            no_data_font_size=32,
            legend_font_size=25,
            truncate_legend=10,
            tooltip_font_size=50,
        )
        torta_porcentajes_por_tipo.add('Dialer', porcentaje_dialer)
        torta_porcentajes_por_tipo.add('Entrantes', porcentaje_entrantes)
        torta_porcentajes_por_tipo.add('Manual', porcentaje_manual)
        torta_porcentajes_por_tipo.add('Preview', porcentaje_preview)

        return torta_porcentajes_por_tipo

    def _generar_grafico_barras_llamadas_por_tipo_de_campana(self, total_llamadas_dict):

        # Barras: muestran la desagregación de las llamadas por tipo de campaña
        barras_llamadas_por_tipo = pygal.Bar(  # @UndefinedVariable
            show_legend=True,
            style=ESTILO_AZUL_ROJO_AMARILLO)

        barras_llamadas_por_tipo.x_labels = ["Dialer", "Entrantes", "Manuales"]

        barras_llamadas_por_tipo.add(
            'Ingresadas', [total_llamadas_dict['llamadas_ingresadas_dialer'],
                           total_llamadas_dict['llamadas_ingresadas_entrantes'],
                           total_llamadas_dict['llamadas_ingresadas_manuales'],
                           total_llamadas_dict['llamadas_ingresadas_preview']])

        barras_llamadas_por_tipo.add(
            'Atendidas', [total_llamadas_dict['llamadas_gestionadas_dialer'],
                          total_llamadas_dict['llamadas_atendidas_entrantes'],
                          total_llamadas_dict['llamadas_atendidas_manuales'],
                          total_llamadas_dict['llamadas_atendidas_preview']])

        perdidas_entrantes = total_llamadas_dict['llamadas_expiradas_entrantes'] + \
            total_llamadas_dict['llamadas_abandonadas_entrantes']
        barras_llamadas_por_tipo.add(
            'Perdidas', [total_llamadas_dict['llamadas_perdidas_dialer'],
                         perdidas_entrantes,
                         total_llamadas_dict['llamadas_abandonadas_manuales'],
                         total_llamadas_dict['llamadas_abandonadas_preview']])

        return barras_llamadas_por_tipo

    def _generar_grafico_barras_llamadas_por_campana(self, estadisticas):
        # Barra: Cantidad de llamadas de las campana por tipo de llamadas
        barra_campana_total = pygal.Bar(  # @UndefinedVariable
            show_legend=False,
            style=ESTILO_AZUL_ROJO_AMARILLO)
        barra_campana_total.title = u'Cantidad de llamadas de las campañas'

        barra_campana_total.x_labels = estadisticas['campana_nombre']
        barra_campana_total.add('Total', estadisticas['total_campana'])
        barra_campana_total.add('Manuales', estadisticas['total_manuales'])

        return barra_campana_total

    def _generar_grafico_barras_llamadas_por_campanas_de_tipo(self, totales):
        # # Barra: Cantidad de llamadas por campañas
        grafico_barras = pygal.Bar(  # @UndefinedVariable
            show_legend=False,
            style=ESTILO_AZUL_ROJO_AMARILLO)
        # grafico_barras.title = 'Distribucion por campana'

        grafico_barras.x_labels = totales['nombres_queues']
        grafico_barras.add('atendidas', totales['total_atendidas'])
        grafico_barras.add('abandonadas ', totales['total_abandonadas'])
        grafico_barras.add('expiradas', totales['total_expiradas'])
        return grafico_barras

    def general_llamadas_hoy(self, fecha_inferior, fecha_superior, user, finalizadas):
        estadisticas = self._calcular_estadisticas(
            fecha_inferior, fecha_superior, user, finalizadas)

        if estadisticas:
            logger.info("Generando grafico para grabaciones de llamadas ")

        torta_porcentajes_por_tipo = self._generar_grafico_torta_porcentajes(
            estadisticas['total_llamadas_dict'])

        barras_llamadas_por_tipo = self._generar_grafico_barras_llamadas_por_tipo_de_campana(
            estadisticas['total_llamadas_dict'])

        barra_llamada_por_campana = self._generar_grafico_barras_llamadas_por_campana(estadisticas)

        barra_llamadas_dialer = self._generar_grafico_barras_llamadas_por_campanas_de_tipo(
            estadisticas['totales_grafico_dialer'])
        barra_llamadas_entrantes = self._generar_grafico_barras_llamadas_por_campanas_de_tipo(
            estadisticas['totales_grafico_entrantes'])
        barra_llamadas_manuales = self._generar_grafico_barras_llamadas_por_campanas_de_tipo(
            estadisticas['totales_grafico_manuales'])
        barra_llamadas_preview = self._generar_grafico_barras_llamadas_por_campanas_de_tipo(
            estadisticas['totales_grafico_preview'])

        dict_campana_counter = zip(estadisticas['campana_nombre'],
                                   estadisticas['total_campana'],
                                   estadisticas['total_manuales'],
                                   estadisticas['tipos_campana'])
        dict_campana_counter_json = json.dumps({'filas_datos': dict_campana_counter})

        return {
            'estadisticas': estadisticas,
            'barras_llamadas_por_tipo': barras_llamadas_por_tipo,
            'torta_porcentajes_por_tipo': torta_porcentajes_por_tipo,
            'dict_campana_counter': dict_campana_counter,
            'dict_campana_counter_json': dict_campana_counter_json,
            'barra_llamada_por_campana': barra_llamada_por_campana,
            'barra_campana_llamadas_dialer': barra_llamadas_dialer,
            'barra_campana_llamadas_entrantes': barra_llamadas_entrantes,
            'barra_campana_llamadas_manuales': barra_llamadas_manuales,
            'barra_campana_llamadas_preview': barra_llamadas_preview,
        }
