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
var campanas_supervisor = [];
var campanas_id_supervisor = [];
var table_entrantes;
var table_data = [];
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
            } catch (err) {
                console.log(err);
            }
        }
    };

    function processData(data) {
        let haveAgentsData = false;
        let fistCallStats = {};
        data.forEach(info => {
            let row = JSON.parse(info
                .replaceAll('\'', '"')
                .replaceAll('"[', '[')
                .replaceAll(']"', ']'));
            if (row['NAME']) {
                agents.updateAgent(row);
                haveAgentsData = true;
            } else if (row['nombre'] && !fistCallStats[row['nombre']]) {
                fistCallStats[row['nombre']] = row;
            }
        });

        for (const campaign in fistCallStats) {
            let row = table_entrantes
                .row('#' + campaign);
            let dataRow = row.data();
            if (dataRow == null) {
                let newDataRow = new InboundStats(campanas_id_supervisor[campanas_supervisor.indexOf(campaign)], campaign);
                newDataRow.updateCallStats(fistCallStats[campaign]);
                table_entrantes.row.add(newDataRow);
            } else {
                dataRow.updateCallStats(fistCallStats[campaign]);
                row.data(dataRow);
            }
        }

        if (haveAgentsData) {
            let newAgentStats = agents.calculateStats(campanas_supervisor);
            console.log(newAgentStats);
            for (const campaign in newAgentStats) {
                const statsEmpty = emptyStats(newAgentStats[campaign]);
                let row = table_entrantes
                    .row('#' + campaign);
                let dataRow = row.data();
                if (dataRow == null && !statsEmpty) {
                    let newDataRow = new InboundStats(campanas_id_supervisor[campanas_supervisor.indexOf(campaign)], campaign);
                    newDataRow.updateAgentStats(newAgentStats[campaign]);
                    table_entrantes.row.add(newDataRow);
                } else if (dataRow && dataRow.isEmpty() && statsEmpty) {
                    row.remove();
                } else if (dataRow) {
                    dataRow.updateAgentStats(newAgentStats[campaign]);
                    row.data(dataRow);
                }
            }
        }
        table_entrantes.draw();
    }

    function emptyStats(stats) {
        return stats.agentes_online == 0 &&
            stats.agentes_llamada == 0 &&
            stats.agentes_pausa == 0;
    }

});

function createDataTable() {
    table_entrantes = $('#tableEntrantes').DataTable({
        data: table_data,
        rowId: 'nombre',
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
            { 'data': 'porcentaje_objetivo' },
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

class InboundStats {

    constructor(id, nombre) {
        this.id = id;
        this.nombre = nombre;
        this.llamadas_en_espera = 0;
        this.atendidas = 0;
        this.abandonadas = 0;
        this.expiradas = 0;
        this.t_promedio_abandono = 0;
        this.t_promedio_espera = 0;
        this.gestiones = 0;
        this.agentes_online = 0;
        this.agentes_llamada = 0;
        this.agentes_pausa = 0;
        this.porcentaje_objetivo = 0;
    }

    isEmpty() {
        if (this.llamadas_en_espera != 0 ||
            this.atendidas != 0 ||
            this.abandonadas != 0 ||
            this.expiradas != 0 ||
            this.gestiones != 0 ||
            this.porcentaje_objetivo != 0) return false;
        return true;
    }

    updateCallStats(newStats) {
        this.llamadas_en_espera = newStats['llamadas_en_espera'];
        this.atendidas = newStats['llamadas_atendidas'];
        this.abandonadas = newStats['llamadas_abandonadas'];
        this.expiradas = newStats['llamadas_expiradas'];
        this.gestiones = newStats['gestiones'];
        this.porcentaje_objetivo = newStats['porcentaje_objetivo'];

        var abandonadas = parseInt(newStats['llamadas_abandonadas']);
        if (abandonadas > 0) {
            this.t_promedio_abandono = parseFloat(newStats['tiempo_acumulado_abandonadas']) / abandonadas;
        }

        var atendidas = parseInt(newStats['llamadas_atendidas']);
        if (atendidas > 0) {
            this.t_promedio_espera = parseFloat(newStats['tiempo_acumulado_espera']) / atendidas;
        }
    }

    updateAgentStats(agentStats) {
        this.agentes_online = agentStats.agentes_online;
        this.agentes_llamada = agentStats.agentes_llamada;
        this.agentes_pausa = agentStats.agentes_pausa;
    }

}

class Agents {
    constructor() {
        this.agentList = {};
    }

    calculateStats(campaignList) {
        let stats = {};
        campaignList.forEach(campaign => {
            stats[campaign] = {
                'agentes_online': 0,
                'agentes_llamada': 0,
                'agentes_pausa': 0
            };
            Object.values(this.agentList).forEach(agent => {
                if (agent.campanas.includes(campaign) && agent.status != '') {
                    stats[campaign]['agentes_online']++;
                    if (agent.status.indexOf('PAUSE') == 0) {
                        stats[campaign]['agentes_pausa']++;
                    } else if (agent.status.indexOf('ONCALL') == 0) {
                        stats[campaign]['agentes_llamada']++;
                    }
                }
            });
        });
        return stats;
    }

    updateAgent(newAgentData) {
        const agentId = newAgentData.id;
        this.agentList[agentId] = (this.agentList[agentId]) ? this.agentList[agentId] : {};

        if (this.agentList[agentId]['timestamp'] &&
            this.agentList[agentId]['timestamp'] > newAgentData.TIMESTAMP) {
            return;
        }

        this.agentList[agentId]['campanas'] = newAgentData.CAMPANAS;
        this.agentList[agentId]['timestamp'] = newAgentData.TIMESTAMP;
        this.agentList[agentId]['campaign'] = newAgentData.CAMPAIGN;

        if (newAgentData.STATUS != '' &&
            newAgentData.STATUS != 'OFFLINE' &&
            newAgentData.STATUS != 'UNAVAILABLE') {
            this.agentList[agentId]['status'] = newAgentData.STATUS;

        } else {
            this.agentList[agentId]['status'] = '';
        }

    }

}

var agents = new Agents();
