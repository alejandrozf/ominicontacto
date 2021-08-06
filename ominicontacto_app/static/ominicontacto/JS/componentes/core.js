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

import { InfoNumerica, LogsLlamadas, InfoPausas } from './estadisticas.js';


var DashboardAgente = {
    components: {
        'info-numerica': InfoNumerica,
        'logs-llamadas': LogsLlamadas,
        'info-pausas': InfoPausas
    },
    methods: {
        onClick() {
            this.pausas.hiddenPausas = !this.pausas.hiddenPausas;
        }
    },
    template: `
<div v-if="pausa">
    <div>
        <div class="row">
            <div class="col-md-4">
                <info-numerica v-bind="conectadas"></info-numerica>
            </div>
            <div class="col-md-4">
                <info-numerica v-on:click.native="onClick" v-bind="pausa"></info-numerica>
                <info-pausas v-bind="pausas"></info-pausas>
            </div>
            <div class="col-md-4">
                <info-numerica v-bind="venta"></info-numerica>
            </div>
        </div>
        <div class="row">
            <div class="col-md-12">
                <logs-llamadas v-bind="logs"></logs-llamadas>
            </div>
        </div>
    </div>
</div>
<div v-else>\
    <v-list-item-title>{{ mensajeEspera }} </v-list-item-title>
    <v-progress-circular
        indeterminate
        color="green"
    ></v-progress-circular>
</div>
`,
    props: ['conectadas', 'pausa', 'venta', 'logs', 'mensajeEspera', 'pausas'],
};

export { DashboardAgente };
