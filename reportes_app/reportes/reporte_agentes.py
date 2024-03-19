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

from __future__ import unicode_literals
import pygal
from pygal.style import Style
from django.utils.translation import gettext as _
from django.utils.timezone import now, timedelta
from django.db.models import Count

from ominicontacto_app.models import Campana, Pausa
from ominicontacto_app.utiles import datetime_hora_maxima_dia, datetime_hora_minima_dia
from reportes_app.models import ActividadAgenteLog, LlamadaLog, TransferenciaAEncuestaLog
from reportes_app.actividad_agente_log import AgenteTiemposReporte
from reportes_app.reportes.reporte_llamadas import LLAMADA_TRANSF_INTERNA
from collections import OrderedDict
from utiles_globales import adicionar_render_unicode

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


class ReporteAgentes(object):

    def __init__(self, user=None):

        # Dict con los datos estadísticos de cada agente (ActividadAgente)
        self.datos_agentes = {}
        self.tiempos = []
        self.user = user

    def devuelve_reporte_agentes(self, agentes, fecha_inicio, fecha_fin):
        fecha_inicio = datetime_hora_minima_dia(fecha_inicio)
        fecha_fin = datetime_hora_maxima_dia(fecha_fin)
        self.genera_tiempos_pausa(agentes, fecha_inicio, fecha_fin)
        self.genera_tiempos_campana_agentes(agentes, fecha_inicio, fecha_fin)
        self.calcula_total_intentos_fallidos(agentes, fecha_inicio, fecha_fin)
        self.calcula_llamadas_entrantes_no_atendidas(agentes, fecha_inicio, fecha_fin)
        self.calcula_llamadas_entrantes_rechazadas(agentes, fecha_inicio, fecha_fin)
        self._genera_tiempos_totales_agentes()
        dict_agentes_llamadas = self._obtener_total_agentes_tipo_llamada(fecha_inicio, fecha_fin)
        return {
            'fecha_desde': fecha_inicio,
            'fecha_hasta': fecha_fin,
            'agentes_tiempos': self.tiempos,
            'agente_pausa': self.devuelve_pausas_agentes(),
            'count_llamada_campana': self._genera_tiempo_total_llamada_campana(),
            'dict_agente_counter': list(zip(dict_agentes_llamadas['nombres_agentes'],
                                            dict_agentes_llamadas['total_agentes'],
                                            dict_agentes_llamadas['total_agente_preview'],
                                            dict_agentes_llamadas['total_agente_dialer'],
                                            dict_agentes_llamadas['total_agente_inbound'],
                                            dict_agentes_llamadas['total_agente_manual'],
                                            dict_agentes_llamadas['total_transferidas_agente'],
                                            dict_agentes_llamadas['total_transferidas_campana'],
                                            dict_agentes_llamadas['total_transferidas_encuesta'],
                                            dict_agentes_llamadas['total_agente_fuera_campana'])),
            'barra_agente_total': self._generar_grafico_agentes_llamadas(dict_agentes_llamadas),

        }

    def devuelve_reporte_agente_campana(self, agente, fecha_inicio, fecha_fin, campana):
        self.genera_tiempos_pausa([agente], fecha_inicio, fecha_fin)
        self.calcula_total_intentos_fallidos([agente], fecha_inicio, fecha_fin)
        eventos_llamadas = list(LlamadaLog.EVENTOS_FIN_CONEXION)

        logs_time = LlamadaLog.objects.obtener_agentes_campanas_total(
            eventos_llamadas, fecha_inicio, fecha_fin, [agente.id],
            [campana])
        cantidades_transferencias = LlamadaLog.objects. \
            obtener_cantidades_de_transferencias_recibidas(
                fecha_inicio, fecha_fin, [agente.id], [campana.id])
        for log in logs_time:
            agente_id = int(log[0])
            transferencias = cantidades_transferencias.get(agente_id, {}).get(campana.id, 0)
            if agente_id in self.datos_agentes:
                self.datos_agentes[agente_id].obtener_tiempo_total_llamada_campana(
                    campana, log, transferencias)

        self._genera_tiempos_totales_agentes()
        if len(self.tiempos) == 0:
            return AgenteTiemposReporte(agente.id, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        return self.tiempos[0]

    # Genera la información en agentes de pausas y sesiones
    def genera_tiempos_pausa(self, agentes, fecha_inicio, fecha_fin):
        self._procesa_tiempos_pausa(agentes, fecha_inicio, fecha_fin)

    # Devuelve las pausas de los agentes en el formato que espera la vista
    def devuelve_pausas_agentes(self):
        res = []
        for agente in self.datos_agentes.values():
            res.extend(agente.devuelve_datos_pausa())

        return res

    # Genera la info de los tiempos totales de llamada de los agentes por campaña
    def genera_tiempos_campana_agentes(self, agentes, fecha_inferior, fecha_superior):
        eventos_llamadas = list(LlamadaLog.EVENTOS_FIN_CONEXION)

        campanas = Campana.objects.obtener_actuales()
        if not self.user.get_is_administrador():
            supervisor = self.user.get_supervisor_profile()
            campanas = supervisor.campanas_asignadas_actuales()

        campanas_dict = {campana.id: campana for campana in campanas}
        agentes_dict = {agente.id: agente for agente in agentes}
        totales_llamadas = LlamadaLog.objects.obtener_agentes_campanas_total(
            eventos_llamadas, fecha_inferior, fecha_superior, list(agentes_dict.keys()),
            campanas)
        lista_pausas = list(Pausa.objects.all())
        campanas_ids = campanas.values_list('id', flat=True)
        cantidades_transferencias = LlamadaLog.objects. \
            obtener_cantidades_de_transferencias_recibidas(
                fecha_inferior, fecha_superior, list(agentes_dict.keys()), campanas_ids)
        ID_AGENTE = 0
        ID_CAMPANA = 1
        fecha_limite = min(now(), fecha_superior)
        for log in totales_llamadas:
            agente_id = int(log[ID_AGENTE])
            campana_id = int(log[ID_CAMPANA])
            transferencias = cantidades_transferencias.get(agente_id, {}).get(campana_id, 0)
            if agente_id not in self.datos_agentes:
                self.datos_agentes.setdefault(
                    agente_id, ActividadAgente(
                        agentes_dict[agente_id], fecha_limite, lista_pausas=lista_pausas))
            self.datos_agentes[agente_id].obtener_tiempo_total_llamada_campana(
                campanas_dict[campana_id], log, transferencias)

    def calcula_total_intentos_fallidos(self, agentes, fecha_inferior, fecha_superior):
        eventos_llamadas = list(LlamadaLog.EVENTOS_NO_CONTACTACION)

        agentes_dict = {agente.id: agente for agente in agentes}
        logs_time = LlamadaLog.objects.obtener_count_evento_agente(
            eventos_llamadas, fecha_inferior, fecha_superior, list(agentes_dict.keys()))
        lista_pausas = list(Pausa.objects.all())
        fecha_limite = min(now(), fecha_superior)
        for log in logs_time:
            agente_id = int(log[0])
            if agente_id not in self.datos_agentes:
                self.datos_agentes.setdefault(
                    agente_id, ActividadAgente(
                        agentes_dict[agente_id], fecha_limite, lista_pausas=lista_pausas))
            self.datos_agentes[agente_id].intentos_fallidos += int(log[1])

    def calcula_llamadas_entrantes_rechazadas(self, agentes, fecha_inferior, fecha_superior):
        for agente in agentes:
            total_call_rejets = LlamadaLog.objects.\
                cantidad_llamadas_rechazadas_fecha(agente.id, fecha_inferior, fecha_superior)
            if total_call_rejets:
                self.datos_agentes[agente.id].entrantes_rechazadas += total_call_rejets

    def calcula_llamadas_entrantes_no_atendidas(self, agentes, fecha_inferior, fecha_superior):
        for agente in agentes:
            total_call = LlamadaLog.objects.\
                cantidad_llamadas_no_atendidas_fecha(agente.id, fecha_inferior, fecha_superior)
            if total_call:
                self.datos_agentes[agente.id].entrantes_no_atendidas += total_call

    def _genera_tiempos_totales_agentes(self):
        for agente in self.datos_agentes.values():
            agente.calcula_totales()
            self.tiempos.append(AgenteTiemposReporte(
                agente.agente, agente.tiempo_sesion,
                agente.tiempo_pausa,
                agente.tiempo_llamada, agente.llamadas_procesadas, agente.intentos_fallidos, 0, 0,
                agente.tiempo_hold, agente.transferidas_a_agente, agente.entrantes_no_atendidas,
                agente.entrantes_rechazadas))

    def _genera_tiempo_total_llamada_campana(self):
        res = []
        for agente in self.datos_agentes.values():
            res.extend(agente.tiempos_llamada_campana)
        return res

    def _procesa_tiempos_pausa(self, agentes, fecha_inicio, fecha_fin):
        agentes_dict = {agente.id: agente for agente in agentes}
        logs_agentes = self._cargar_logs_agentes(list(agentes_dict.keys()), fecha_inicio, fecha_fin)
        lista_pausas = list(Pausa.objects.all())
        fecha_limite = min(now(), fecha_fin)
        for agente_id, fecha, event, pausa_id in logs_agentes[::-1]:
            datos_agente_actual = self.datos_agentes.setdefault(
                agente_id, ActividadAgente(
                    agentes_dict[agente_id], fecha_limite, lista_pausas=lista_pausas))

            datos_agente_actual.procesa_log(event, fecha, pausa_id)

    def _cargar_logs_agentes(self, agente_ids, fecha_inicio, fecha_fin):
        eventos_sesion = ['ADDMEMBER', 'REMOVEMEMBER', 'PAUSEALL', 'UNPAUSEALL']

        return ActividadAgenteLog.objects.obtener_tiempos_event_agentes(
            eventos_sesion,
            fecha_inicio,
            fecha_fin,
            agente_ids)

    def _obtener_total_agentes_tipo_llamada(self, fecha_inicio, fecha_fin):
        dict_agentes_llamadas = {}
        agente_ids = self.datos_agentes.keys()
        agentes_tipo_llamadas = self._obtener_llamadas_agente(agente_ids, fecha_inicio, fecha_fin)
        dict_agentes_llamadas['nombres_agentes'] = []
        dict_agentes_llamadas['total_agentes'] = []
        for datos_agente in self.datos_agentes.values():
            dict_agentes_llamadas['nombres_agentes'].append(
                datos_agente.agente.user.get_full_name())
            dict_agentes_llamadas['total_agentes'].append(
                self._total_llamadas(datos_agente.agente.pk, fecha_inicio, fecha_fin))
        dict_agentes_llamadas['total_agente_dialer'] = self. \
            _obtener_cantidad_por_tipo_de_llamada(
            agentes_tipo_llamadas, agente_ids, Campana.TYPE_DIALER)
        dict_agentes_llamadas['total_agente_inbound'] = self. \
            _obtener_cantidad_por_tipo_de_llamada(
            agentes_tipo_llamadas, agente_ids, Campana.TYPE_ENTRANTE)
        dict_agentes_llamadas['total_agente_manual'] = self. \
            _obtener_cantidad_por_tipo_de_llamada(
            agentes_tipo_llamadas.exclude(campana_id=0), agente_ids, Campana.TYPE_MANUAL)
        dict_agentes_llamadas['total_agente_preview'] = self. \
            _obtener_cantidad_por_tipo_de_llamada(
            agentes_tipo_llamadas, agente_ids, Campana.TYPE_PREVIEW)
        dict_agentes_llamadas['total_transferidas_agente'] = self. \
            _obtener_cantidad_por_tipo_de_llamada(
            agentes_tipo_llamadas.filter(
                event__in=['BT-ANSWER', 'CT-ACCEPT']).exclude(campana_id=0),
            agente_ids, LLAMADA_TRANSF_INTERNA)
        dict_agentes_llamadas['total_transferidas_campana'] = self. \
            _obtener_cantidad_por_tipo_de_llamada(
            agentes_tipo_llamadas.filter(event='CONNECT'),
            agente_ids, LLAMADA_TRANSF_INTERNA)
        dict_agentes_llamadas['total_agente_fuera_campana'] = self. \
            _obtener_cantidad_por_tipo_de_llamada(
            agentes_tipo_llamadas.filter(campana_id=0), agente_ids, Campana.TYPE_MANUAL)
        dict_agentes_llamadas['total_transferidas_encuesta'] = self. \
            _obtener_transferidas_a_encuesta(agente_ids, fecha_inicio, fecha_fin)

        return dict_agentes_llamadas

    def _obtener_llamadas_agente(self, agente_ids, fecha_inferior, fecha_superior):

        eventos_llamadas = list(LlamadaLog.EVENTOS_INICIO_CONEXION)
        dict_agentes = LlamadaLog.objects.obtener_count_agente().filter(
            time__range=(fecha_inferior, fecha_superior),
            agente_id__in=agente_ids,
            event__in=eventos_llamadas)

        return dict_agentes

    def _obtener_cantidad_por_tipo_de_llamada(self, dict_agentes, agentes, tipo_llamada):
        total = OrderedDict(zip(agentes, [0] * len(agentes)))
        for log in dict_agentes.filter(tipo_llamada=tipo_llamada):
            id_agente = log['agente_id']
            if id_agente in agentes:
                total[id_agente] = log['cantidad']
        return total.values()

    def _generar_grafico_agentes_llamadas(self, dict_agentes_llamadas):
        # Barra: Cantidad de llamadas de los agentes por tipo de llamadas.
        barra_agente_total = pygal.Bar(show_legend=True, style=ESTILO_AZUL_ROJO_AMARILLO)
        barra_agente_total.x_labels = dict_agentes_llamadas['nombres_agentes']
        barra_agente_total.add('PREVIEW', dict_agentes_llamadas['total_agente_preview'])
        barra_agente_total.add('DIALER', dict_agentes_llamadas['total_agente_dialer'])
        barra_agente_total.add('INBOUND', dict_agentes_llamadas['total_agente_inbound'])
        barra_agente_total.add('MANUAL', dict_agentes_llamadas['total_agente_manual'])
        barra_agente_total.add('TRANS. AGENTE',
                               dict_agentes_llamadas['total_transferidas_agente'])
        barra_agente_total.add('TRANS. CAMPAÑA',
                               dict_agentes_llamadas['total_transferidas_campana'])

        return adicionar_render_unicode(barra_agente_total)

    def _total_llamadas(self, agente_id, fecha_inferior, fecha_superior):
        eventos_llamadas = list(LlamadaLog.EVENTOS_INICIO_CONEXION)

        llamadas = LlamadaLog.objects.obtener_count_agente().filter(
            time__range=(fecha_inferior, fecha_superior),
            agente_id=agente_id,
            event__in=eventos_llamadas).exclude(campana_id=0, event__in=('BT-ANSWER', 'CT-ACCEPT'))
        total = 0
        for llamada in llamadas:
            total = llamada['cantidad']
        return total

    def _obtener_transferidas_a_encuesta(self, agente_ids, fecha_inicio, fecha_fin):
        transferencias = TransferenciaAEncuestaLog.objects.filter(agente_id__in=agente_ids,
                                                                  time__gte=fecha_inicio,
                                                                  time__lte=fecha_fin)
        total = OrderedDict(zip(agente_ids, [0] * len(agente_ids)))
        transferencias_por_agente = transferencias.values_list('agente_id').annotate(
            cantidad=Count('agente_id'))
        for agente_id, cantidad in transferencias_por_agente:
            total[agente_id] = cantidad
        return total.values()


class ActividadAgente(object):

    def __init__(self, agente, fecha_limite, lista_pausas=None):
        self.agente = agente
        self.pausas = []
        self.sesiones = []
        self.tiempos_llamada_campana = []
        self.llamadas_procesadas = 0
        self.transferidas_a_agente = 0
        self.intentos_fallidos = 0
        self.entrantes_no_atendidas = 0
        self.entrantes_rechazadas = 0

        self.tiempo_sesion = timedelta()
        self.tiempo_pausa = timedelta()
        self.tiempo_llamada = timedelta()

        self.pausas_por_id = self._genera_info_pausas(lista_pausas)
        self.tiempo_hold = timedelta()
        self.fecha_limite = fecha_limite

    def _genera_info_pausas(self, lista_pausas):
        lista_pausas_oml = lista_pausas
        if lista_pausas_oml is None:
            lista_pausas_oml = Pausa.objects.all()

        res = {
            '0': Pausa(id='0', nombre=_(u'ACW')),
            '00': Pausa(id='00', nombre=_(u'Pausa-Supervisión')),
            'OW': Pausa(id='OW', nombre=_(u'On-Whatsapp')),
        }
        for pausa in lista_pausas_oml:
            res[str(pausa.id)] = pausa
        return res

    def procesa_log(self, event, time, pausa_id):
        if event == 'REMOVEMEMBER':
            if self.sesiones == []:
                self.sesiones.append(SesionAgente(
                    fecha_inicio=time, fecha_fin=time))
            else:
                self.sesiones[-1].establecer_finalizacion(time)
                self.tiempo_sesion += self.sesiones[-1].calcular_duracion()

        elif event == 'ADDMEMBER':
            if self.sesiones != []:
                sesion_anterior = self.sesiones[-1]
                sesion_anterior.establecer_finalizacion(time)
            self.sesiones.append(SesionAgente(fecha_inicio=time))

        self._procesa_pausa_log(event, time, pausa_id)

    def calcula_totales(self):
        self._totaliza_pausas()
        self._totaliza_sesiones()
        if self.sesiones != []:
            self._procesa_tiempo_hold(self.sesiones[0].fecha_inicio, self.sesiones[-1].fecha_fin)

    def obtener_tiempo_total_llamada_campana(self, campana, log, transferencias):
        DURACION = 2
        CANTIDAD_LLAMADAS = 3
        # log Tiene los datos de 1 query q sumariza tiempos de llamada y cantidad de llamadas.
        # Se resta cantidad de transferidas a agente a la cantidad de llamadas procesadas
        tiempo_agente = {
            'agente': self.agente.user.get_full_name(),
            'campana': campana.nombre,
            'tiempo_llamadas': str(timedelta(seconds=log[DURACION])),
            'llamadas_procesadas': log[CANTIDAD_LLAMADAS] - transferencias,
            'transferidas_a_agente': transferencias
        }
        self.tiempos_llamada_campana.append(tiempo_agente)

        # Sumarizacion para "reporte de tiempos"
        self.tiempo_llamada += timedelta(seconds=log[DURACION])
        self.llamadas_procesadas += int(log[CANTIDAD_LLAMADAS]) - transferencias
        self.transferidas_a_agente += transferencias

    def _totaliza_sesiones(self):
        t = timedelta()
        if len(self.sesiones) > 0 and self.sesiones[-1].fecha_fin is None:
            self.sesiones[-1].fecha_fin = self.fecha_limite
            self.sesiones[-1].calcular_duracion()
        for s in self.sesiones:
            t += s.duracion
        self.tiempo_sesion = t

    def _totaliza_pausas(self):
        t = timedelta()
        for p in self.pausas:
            t += p.duracion
        self.tiempo_pausa = t

    def devuelve_datos_pausa(self):
        res = {}
        default = {
            'id': self.agente.id,
            'nombre_agente': self.agente.user.get_full_name(),
            'pausa': None,
            'pausa_id': None,
            'tiempo': timedelta(),
            'tipo_de_pausa': None
        }
        for pausa in self.pausas:
            d = default.copy()
            res.setdefault(pausa.pausa_id, d)
            res[pausa.pausa_id]['pausa'] = pausa.nombre
            res[pausa.pausa_id]['pausa_id'] = pausa.pausa_id
            res[pausa.pausa_id]['tipo_de_pausa'] = pausa.nombre.get_tipo()
            res[pausa.pausa_id]['tiempo'] += pausa.duracion
        r = []
        for p in res.values():
            r.append(p)
        return r

    def _procesa_pausa_log(self, event, time, pausa_id):
        if (event == 'UNPAUSEALL' or event == 'REMOVEMEMBER' or event == 'ADDMEMBER')\
                and self.pausas != []:
            if not self.pausas[-1].establecer_finalizacion(time, pausa_id):
                self.pausas.append(PausaAgente(
                    pausa_id, self.pausas_por_id[str(pausa_id)],
                    fecha_inicio=self.pausas[-1].fecha_inicio))
                self.pausas[-1].establecer_finalizacion(time, pausa_id)
            self.tiempo_pausa += self.pausas[-1].calcular_duracion()
        elif event == 'PAUSEALL':
            if self.pausas != []:
                self.pausas[-1].establecer_finalizacion(time, pausa_id)
                self.tiempo_pausa += self.pausas[-1].calcular_duracion()

            self.pausas.append(PausaAgente(
                pausa_id, self.pausas_por_id[str(pausa_id)], fecha_inicio=time))

    def _procesa_tiempo_hold(self, fecha_inicio, fecha_fin):
        fecha_superior = datetime_hora_maxima_dia(fecha_fin)
        fecha_inferior = datetime_hora_minima_dia(fecha_inicio)
        logs = [hold for hold in LlamadaLog.objects.using('replica')
                .filter(agente_id=self.agente.id, event='HOLD', time__range=(fecha_inferior,
                                                                             fecha_superior))]
        for log in logs:
            inicio_hold = log.time
            callid = log.callid
            holdid = log.id
            unholds = LlamadaLog.objects.using('replica')\
                .filter(agente_id=self.agente.id, callid=callid,
                        event='UNHOLD',
                        time__range=(log.time, fecha_superior)).order_by('time').first()
            if unholds:
                # Si existen varios unhold dentro de una llamada se elige el primero
                fin_hold = unholds.time
            else:
                # Si se corta la llamada sin haber podido hacer unhold o por otro motivo
                log_llamada = LlamadaLog.objects.using('replica')\
                    .filter(agente_id=self.agente.id, callid=callid,
                            time__range=(inicio_hold, fecha_superior))\
                    .exclude(id=holdid).order_by('time').first()
                if log_llamada and log_llamada.event != 'HOLD':
                    fin_hold = log_llamada.time
                else:
                    fin_hold = now() \
                        if datetime_hora_maxima_dia(fecha_superior) >= now() else fecha_superior
            self.tiempo_hold += fin_hold - inicio_hold


class BaseActividadAgente(object):

    def __init__(self, fecha_inicio=None, fecha_fin=None):
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.duracion = timedelta()

    def establecer_finalizacion(self, fecha_fin):
        if self.fecha_fin is None:
            self.fecha_fin = fecha_fin

    def calcular_duracion(self):
        if self.fecha_inicio and self.fecha_fin:
            self.duracion = self.fecha_fin - self.fecha_inicio
        else:
            self.duracion = 0
        return self.duracion


class SesionAgente(BaseActividadAgente):
    pass


class PausaAgente(BaseActividadAgente):
    def __init__(self, pausa_id, nombre, fecha_inicio=None, fecha_fin=None):
        super(PausaAgente, self).__init__(fecha_inicio, fecha_fin)
        self.pausa_id = pausa_id
        self.nombre = nombre

    def establecer_finalizacion(self, fecha_fin, pausa_id):
        super(PausaAgente, self).establecer_finalizacion(fecha_fin)
        return True
