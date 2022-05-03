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
var table_dialers;
var table_data = [];
var inicio = true;
const MENSAJE_CONEXION_WEBSOCKET = 'Stream subscribed!';

$(function() {
    campanas_supervisor = $('input#campanas_list').val().split(',');
    if (campanas_supervisor.length == 1 && campanas_supervisor[0] == '') {
        campanas_supervisor = [];
    }
    campanas_id_supervisor = $('input#campanas_list_id').val().split(',');
    createDataTable();
    subcribeFilterChange();
    handle_filter();

    const url = `wss://${window.location.host}/consumers/stream/supervisor/${$('input#supervisor_id').val()}/dialers`;
    const rws = new ReconnectingWebSocket(url, [], {
        connectionTimeout: 2000,
        maxReconnectionDelay: 3000,
        minReconnectionDelay: 1000,
    });

    rws.addEventListener('message', function(e) {
        if (e.data != MENSAJE_CONEXION_WEBSOCKET) {
            try {
                var data = JSON.parse(e.data);
                if (campanas_supervisor.length > 0) {
                    processData(data);
                } else {
                    table_dialers.clear().draw();
                }
            } catch (err) {
                console.log(err);
            }
        }
    });

    function processData(data) {
        let haveAgentsData = false;
        let fistCallStats = {};
        data.forEach(info => {
            try {
                let row = JSON.parse(info
                    .replaceAll('\'', '"')
                    .replaceAll('"[', '[')
                    .replaceAll(']"', ']')
                    .replaceAll('"{', '{')
                    .replaceAll('}"', '}'));
                if (row['NAME']) {
                    agents.updateAgent(row);
                    haveAgentsData = true;
                } else if (row['NOMBRE'] && !fistCallStats[row['NOMBRE']]) {
                    fistCallStats[row['NOMBRE']] = row;
                }
            } catch (err) {
                console.log(err);
            }
        });

        for (const campaign in fistCallStats) {
            const nombre_saneado = campaign
                .replaceAll('(', '')
                .replaceAll(')', '');
            let row = table_dialers
                .row('#' + nombre_saneado);
            let dataRow = row.data();
            if (!dataRow) {
                let newDataRow = new DialerStats(campanas_id_supervisor[campanas_supervisor.indexOf(campaign)], campaign);
                newDataRow.updateCallStats(fistCallStats[campaign]);
                table_dialers.row.add(newDataRow);
            } else {
                dataRow.updateCallStats(fistCallStats[campaign]);
                row.data(dataRow);
            }
        }

        if (haveAgentsData) {
            let newAgentStats = agents.calculateStats(campanas_supervisor);
            for (const campaign in newAgentStats) {
                const nombre_saneado = campaign
                    .replaceAll('(', '')
                    .replaceAll(')', '');
                const statsEmpty = emptyStats(newAgentStats[campaign]);
                let row = table_dialers
                    .row('#' + nombre_saneado);
                let dataRow = row.data();
                if (!dataRow && !statsEmpty) {
                    let newDataRow = new DialerStats(campanas_id_supervisor[campanas_supervisor.indexOf(campaign)], campaign);
                    newDataRow.updateAgentStats(newAgentStats[campaign]);
                    table_dialers.row.add(newDataRow);
                } else if (dataRow && dataRow.isEmpty() && statsEmpty) {
                    row.remove();
                } else if (dataRow) {
                    dataRow.updateAgentStats(newAgentStats[campaign]);
                    row.data(dataRow);
                }
            }
        }
        table_dialers.draw();
    }

    function emptyStats(stats) {
        return stats.agentes_online == 0 &&
            stats.agentes_llamada == 0 &&
            stats.agentes_pausa == 0;
    }
});

function createDataTable() {
    table_dialers = $('#tableDialers').DataTable({
        data: table_data,
        rowId: 'nombre_saneado',
        stateSave: true,
        columns: [
            { 'data': 'nombre' },
            { 'data': 'agentes_online' },
            { 'data': 'agentes_llamada' },
            { 'data': 'agentes_pausa' },
            { 'data': 'agentes_ready' },
            { 'data': 'efectuadas' },
            { 'data': 'atendidas' },
            { 'data': 'no_atendidas' },
            { 'data': 'contestadores' },
            { 'data': 'canales_discando' },
            { 'data': 'conectadas_perdidas' },
            { 'data': 'gestiones' },
            { 'data': 'pendientes' },
            { 'data': 'porcentaje_objetivo' },
            { 'data': 'status', 'visible': false },
        ],
        'searchCols': [
            null,
            null,
            null,
            null,
            null,
            null,
            null,
            null,
            null,
            null,
            null,
            null,
            null,
            null,
            { 'search': filter_by_status(), },
        ],
        lengthMenu: [[10, 25, 50, 100, 200, 500, -1], [10, 25, 50, 100, 200, 500 , gettext('Todos')]],
        language: {
            search: gettext('Buscar: '),
            infoFiltered: gettext('(filtrando de un total de _MAX_ campañas)'),
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
class DialerStats {

    constructor(id, nombre) {
        this.id = id;
        this.nombre = nombre;
        this.nombre_saneado = nombre
            .replaceAll('(', '')
            .replaceAll(')', '');
        this.efectuadas = 0;
        this.atendidas = 0;
        this.no_atendidas = 0;
        this.contestadores = 0;
        this.conectadas_perdidas = 0;
        this.gestiones = 0;
        this.pendientes = 0;
        this.canales_discando = 0;
        this.agentes_online = 0;
        this.agentes_llamada = 0;
        this.agentes_pausa = 0;
        this.agentes_ready = 0;
        this.porcentaje_objetivo = 0;
        this.status = 0;
    }

    isEmpty() {
        if (this.efectuadas > 0) return false;
        if (this.atendidas > 0) return false;
        if (this.no_atendidas > 0) return false;
        if (this.contestadores > 0) return false;
        if (this.conectadas_perdidas > 0) return false;
        if (this.gestiones > 0) return false;
        if (this.pendientes > 0) return false;
        if (this.canales_discando > 0) return false;
        if (this.porcentaje_objetivo > 0) return false;
        return true;
    }

    updateCallStats(newStats) {
        this.nombre = newStats['NOMBRE'];
        this.nombre_saneado = this.nombre
            .replaceAll('(', '')
            .replaceAll(')', '');
        this.efectuadas = newStats['ESTADISTICAS']['efectuadas'];
        this.atendidas = newStats['ESTADISTICAS']['atendidas'];
        this.no_atendidas = newStats['ESTADISTICAS']['no_atendidas'];
        this.contestadores = newStats['ESTADISTICAS']['contestadores'];
        this.conectadas_perdidas = newStats['ESTADISTICAS']['conectadas_perdidas'];
        this.gestiones = newStats['ESTADISTICAS']['gestiones'];
        this.pendientes = newStats['ESTADISTICAS']['pendientes'];
        this.canales_discando = newStats['ESTADISTICAS']['canales_discando'];
        this.porcentaje_objetivo = newStats['ESTADISTICAS']['porcentaje_objetivo'];
        this.status = parseInt(newStats['STATUS']);
    }

    updateAgentStats(agentStats) {
        this.agentes_online = agentStats.agentes_online;
        this.agentes_llamada = agentStats.agentes_llamada;
        this.agentes_pausa = agentStats.agentes_pausa;
        this.agentes_ready = this.agentes_online - this.agentes_llamada - this.agentes_pausa;
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
        if (!agentId) return;
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

function subcribeFilterChange() {
    $('#filter_by_status').change(function() {
        handle_filter();
    });
}

function handle_filter() {
    let selection = $('#filter_by_status').find('option:selected');
    let value = selection.val();
    if(value > 0){
        table_dialers.columns(14).search(value).draw();
    } else {
        table_dialers.columns().search('').draw();
    }
}

function filter_by_status() {
    return $('#filter_by_status option:selected').val();
}

var agents = new Agents();