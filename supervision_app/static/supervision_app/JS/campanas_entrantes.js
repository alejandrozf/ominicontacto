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

/* global Urls */
/* global gettext */
var agentes = {};
var campanas = {};
var campanas_supervisor = [];
var campanas_id_supervisor = [];
var resumen_agentes_campanas = {};
var table_entrantes;
var table_data = [];
var inicio = true;
const MENSAJE_CONEXION_WEBSOCKET = 'Stream subscribed!';

$(function() {
    campanas_supervisor = $('input#campanas_list').val().split(',');
    campanas_id_supervisor = $('input#campanas_list_id').val().split(',');
    createDataTable();

    const contactadosSocket = new WebSocket(
        'wss://' +
        window.location.host +
        '/consumers/stream/supervisor/' +
        $('input#supervisor_id').val() +
        '/' +
        'entrantes'
    );

    contactadosSocket.onmessage = function(e) {
        if (e.data != MENSAJE_CONEXION_WEBSOCKET) {
            try {
                var data = JSON.parse(e.data);
                processData(data);

                var dataAux = [];
                for (let i in campanas) {
                    dataAux.push(campanas[i]);
                }
                table_entrantes.clear();
                table_entrantes.rows.add(dataAux).draw();
                table_data = dataAux;
            } catch (err) {
                console.log(err);
            }
        }
    };

    function processData(data) {
        var hay_agentes = false;
        if (inicio && data.length > 1) {
            data = data.reverse();
        }
        for (let index = 0; index < data.length; index++) {
            var row = JSON.parse(data[index]
                .replaceAll('\'', '"')
                .replaceAll('"[', '[')
                .replaceAll(']"', ']'));
            if (row['NAME']) {
                processAgent(row);
                hay_agentes = true;
            } else if (row['nombre']) {
                processCampaign(row);
            }

        }
        if (hay_agentes) {
            consolidaInfoAgentes();
        }
        inicio = false;
    }

    function consolidaInfoAgentes() {
        resumen_agentes_campanas = {};
        for (let i in agentes) {
            for (let j in agentes[i].campanas) {
                for (let k in campanas_id_supervisor) {
                    if (agentes[i].campanas[j] == campanas_supervisor[k]) {
                        if (!resumen_agentes_campanas[campanas_id_supervisor[k]]) {
                            resumen_agentes_campanas[campanas_id_supervisor[k]] = {
                                'agentes_online': 0,
                                'agentes_pausa': 0,
                                'agentes_llamada': 0,
                                'nombre_campana': campanas_supervisor[k]
                            };
                        }
                        if (agentes[i].status.indexOf('PAUSE') == 0) {
                            resumen_agentes_campanas[campanas_id_supervisor[k]]['agentes_pausa']++;
                        } else if (agentes[i].status.indexOf('ONCALL') == 0) {
                            resumen_agentes_campanas[campanas_id_supervisor[k]]['agentes_llamada']++;
                        }
                        if (agentes[i].status != '' &&
                            agentes[i].status != 'OFFLINE') {
                            resumen_agentes_campanas[campanas_id_supervisor[k]]['agentes_online']++;
                        }

                    }
                }
            }
        }
        for (let i in resumen_agentes_campanas) {
            if (!campanas[i] && (resumen_agentes_campanas[i]['agentes_pausa'] > 0 ||
                    resumen_agentes_campanas[i]['agentes_llamada'] > 0 ||
                    resumen_agentes_campanas[i]['agentes_online'] > 0)) {
                inicializaCampaign(resumen_agentes_campanas[i]['nombre_campana'], i);
            }
            if (campanas[i] && (resumen_agentes_campanas[i]['agentes_pausa'] > 0 ||
                    resumen_agentes_campanas[i]['agentes_llamada'] > 0 ||
                    resumen_agentes_campanas[i]['agentes_online'] > 0)) {
                campanas[i]['agentes_pausa'] = resumen_agentes_campanas[i]['agentes_pausa'];
                campanas[i]['agentes_llamada'] = resumen_agentes_campanas[i]['agentes_llamada'];
                campanas[i]['agentes_online'] = resumen_agentes_campanas[i]['agentes_online'];
            } else if (campanas[i] && campanaVacia(campanas[i])) {
                delete campanas[i];
            } else if (campanas[i]) {
                campanas[i]['agentes_pausa'] = 0;
                campanas[i]['agentes_llamada'] = 0;
                campanas[i]['agentes_online'] = 0;
            }
        }

    }

    function campanaVacia(campana) {
        if (campana['llamadas_en_espera'] > 0) return false;
        if (campana['atendidas'] > 0) return false;
        if (campana['abandonadas'] > 0) return false;
        if (campana['expiradas'] > 0) return false;
        if (campana['gestiones'] > 0) return false;

        return true;
    }

    function processAgent(agente) {
        var agente_id = agente.id;
        agentes[agente_id] = agentes[agente_id] ? agentes[agente_id] : {};
        agentes[agente_id]['status'] = agente.STATUS;
        agentes[agente_id]['campanas'] = agente.CAMPANAS;
        agentes[agente_id]['timestamp'] = agente.TIMESTAMP;
    }

    function processCampaign(row) {
        var campana_id = row.id;
        if (!campanas[campana_id]) {
            inicializaCampaign(row['nombre'], campana_id);
        }

        campanas[campana_id]['nombre'] = row['nombre'];
        campanas[campana_id]['llamadas_en_espera'] = row['llamadas_en_espera'];
        campanas[campana_id]['atendidas'] = row['llamadas_atendidas'];
        campanas[campana_id]['abandonadas'] = row['llamadas_abandonadas'];
        campanas[campana_id]['expiradas'] = row['llamadas_expiradas'];
        campanas[campana_id]['gestiones'] = row['gestiones'];

        var abandonadas = parseInt(row['llamadas_abandonadas']);
        if (abandonadas > 0) {
            campanas[campana_id]['t_promedio_abandono'] = parseFloat(row['tiempo_acumulado_abandonadas']) / abandonadas;
        }

        var atendidas = parseInt(row['llamadas_atendidas']);
        if (atendidas > 0) {
            campanas[campana_id]['t_promedio_espera'] = parseFloat(row['tiempo_acumulado_espera']) / atendidas;
        }

    }

    function inicializaCampaign(name, id) {
        campanas[id] = {};
        campanas[id]['id'] = id;
        campanas[id]['nombre'] = name;
        campanas[id]['llamadas_en_espera'] = 0;
        campanas[id]['atendidas'] = 0;
        campanas[id]['abandonadas'] = 0;
        campanas[id]['expiradas'] = 0;
        campanas[id]['t_promedio_abandono'] = 0;
        campanas[id]['t_promedio_espera'] = 0;
        campanas[id]['gestiones'] = 0;
        campanas[id]['agentes_online'] = 0;
        campanas[id]['agentes_llamada'] = 0;
        campanas[id]['agentes_pausa'] = 0;
    }
});

function createDataTable() {
    table_entrantes = $('#tableEntrantes').DataTable({
        data: table_data,
        columns: [
            { 'data': 'nombre' },
            { 'data': 'agentes_online' },
            { 'data': 'agentes_llamada' },
            { 'data': 'agentes_pausa' },
            { 'data': 'llamadas_en_espera' },
            { 'data': 'atendidas' },
            { 'data': 'abandonadas' },
            { 'data': 'expiradas' },
            {
                'data': 't_promedio_abandono',
                'render': function(data) { // ( data, type, row, meta)
                    return data.toFixed(1) + gettext(' segundos');
                },
            },
            {
                'data': 't_promedio_espera',
                'render': function(data) { // ( data, type, row, meta)
                    return data.toFixed(1) + gettext(' segundos');
                },
            },
            { 'data': 'gestiones' },
        ],

        language: {
            search: gettext('Buscar: '),
            infoFiltered: gettext('(filtrando de un total de _MAX_ contactos)'),
            paginate: {
                first: gettext('Primero '),
                previous: gettext('Anterior '),
                next: gettext(' Siguiente'),
                last: gettext(' Último'),
            },
            lengthMenu: gettext('Mostrar _MENU_ entradas'),
            info: gettext('Mostrando _START_ a _END_ de _TOTAL_ entradas'),
        }
    });
}