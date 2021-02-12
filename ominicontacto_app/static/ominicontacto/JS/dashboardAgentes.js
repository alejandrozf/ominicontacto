/* Copyright (C) 2018 Freetech Solutions

 This file is part of OMniLeads

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see http://www.gnu.org/licenses/.

*/

/* global gettext Vue Vuetify */

import { DashboardAgente } from './componentes/core.js';

var agenteId = $('#agente_id').val();
var taskId = 'dashboard1';

var subscribeConfirmationMessage = 'Subscribed!';

var dataDashboardSession = JSON.parse(sessionStorage.getItem('dataDashboard'));

var vue_app = undefined;

if (dataDashboardSession == undefined) {
    // al loguearse inicialmente
    vue_app = new Vue({
        data: {
            core: {
                mensajeEspera: gettext('Calculando estadísticas del agente ...')
            }
        },
        components: {
            'dashboard-agente': DashboardAgente,
        },
        el: '#dashboard',
        vuetify: new Vuetify(),
    });

} else {
    vue_app = new Vue({
        data: { core: dataDashboardSession.core },
        components: {
            'dashboard-agente': DashboardAgente,
        },
        el: '#dashboard',
        vuetify: new Vuetify(),
    });
}


const contactadosSocket = new WebSocket(
    'wss://' +
    window.location.host +
    '/consumers/reporte_agente/estadisticas_dia_actual/' +
    agenteId +
    '/' +
    taskId
);

contactadosSocket.onmessage = function(e) {
    if (e.data != subscribeConfirmationMessage) {
        var data = JSON.parse(e.data);
        var conectadasData = JSON.parse(data.conectadas);
        var pausaData = JSON.parse(data.tiempos);
        var ventaData = JSON.parse(data.venta);
        var logsData = JSON.parse(data.logs);

        var graficoConectadas = {
            tooltip: {
                trigger: 'item',
                formatter: '{c} ({d}%)'
            },
            series: [{
                type: 'pie',
                radius: '55%',
                center: ['50%', '50%'],
                selectedMode: 'single',
                data: [
                    { value: conectadasData.salientes, name: gettext('Salientes') },
                    { value: conectadasData.entrantes, name: gettext('Entrantes') },
                ],
                emphasis: {
                    itemStyle: {
                        shadowBlur: 7,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }]
        };

        var graficoPausa = {
            tooltip: {
                trigger: 'item',
                formatter: '{c} ({d}%)'
            },
            series: [{
                type: 'pie',
                radius: '55%',
                center: ['50%', '50%'],
                selectedMode: 'single',
                data: [
                    { value: pausaData.pausa, name: gettext('Pausa') },
                    { value: pausaData.sesion, name: gettext('Sesión') },
                ],
                emphasis: {
                    itemStyle: {
                        shadowBlur: 7,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }]
        };

        var graficoVenta = {
            tooltip: {
                trigger: 'item',
                formatter: '{c} ({d}%)'
            },
            series: [{
                type: 'pie',
                radius: '55%',
                center: ['50%', '50%'],
                selectedMode: 'single',
                data: [
                    { value: ventaData.total, name: gettext('Realizadas') },
                    { value: ventaData.observadas, name: gettext('Observadas') },
                ],
                emphasis: {
                    itemStyle: {
                        shadowBlur: 7,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }]
        };
        var dashboardData = {
            core: {
                conectadas: {
                    statistics: conectadasData.total,
                    title: gettext('Llamadas conectadas'),
                    graphic: graficoConectadas,
                },
                pausa: {
                    statistics: pausaData.tiempo_pausa,
                    title: gettext('Tiempo de pausa recreativa'),
                    graphic: graficoPausa,
                },
                venta: {
                    statistics: ventaData.total,
                    title: 'Ventas',
                    graphic: graficoVenta,
                },
                logs: {
                    headers: {
                        phone: gettext('Número marcado'),
                        data: gettext('Datos del contacto'),
                        engaged: gettext('Gestionado'),
                        callDisposition: gettext('Calificación'),
                        comments: gettext('Observaciones'),
                        audit: gettext('Auditoría'),
                        actions: gettext('Acciones'),
                    },
                    values: logsData,
                }
            }
        };
        sessionStorage.setItem('dataDashboard', JSON.stringify(dashboardData));
        vue_app.core = dashboardData.core;
    }

};