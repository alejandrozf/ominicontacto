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

import { PieGraphic } from './graficos.js';

var InfoNumerica = {
    components : {
        'pie-graphic' : PieGraphic,
    },
    template: `<v-list-item>
                 <v-list-item-content>
                     <v-list-item-title>{{ title }} </v-list-item-title>
                     <v-list-item-subtitle>
                       {{ statistics }}
                     </v-list-item-subtitle>
                     <v-list-item-subtitle>
                       <pie-graphic v-bind:options="graphic"></pie-graphic>
                     </v-list-item-subtitle>
                 </v-list-item-content>
               </v-list-item>`,
    props: ['title', 'statistics', 'graphic'],
};


var LogsLlamadas = {
    template: `
  <v-simple-table>
      <thead>
        <tr>
          <th class="text-left">{{ headers.phone }}</th>
          <th class="text-left">{{ headers.data }}</th>
          <th class="text-left">{{ headers.engaged }}</th>
          <th class="text-left">{{ headers.callDisposition }}</th>
          <th class="text-left">{{ headers.comments }}</th>
          <th class="text-left">{{ headers.audit }}</th>
          <th class="text-left">{{ headers.actions }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in values" :key="item.name">
          <td><a class="btn btn-submit btn-outline-primary" href="javascript:;"
                 v-on:click="makeClick2Call(item.campana_id, item.tipo_campana, item.contacto_id, item.phone, 'agendas');" name="click2call">{{ item.phone }}</a></td>
          <td>{{ item.data }}</td>
          <td>
             <div v-if="item.engaged == true">
                <span class="icon icon-check" aria-hidden="true"></span>
             </div>
             <div v-else>
                <span class="icon icon-cancel" aria-hidden="true"></span>
             </div>
          </td>
          <td>{{ item.callDisposition }}</td>
          <td>{{ item.comments }}</td>
          <td>{{ item.audit }}</td>
          <td>
            <div v-if="item.actions != ''">
              <v-list>
                <v-list-item>
                  <v-list-group
                    :value="false"
                    no-action
                    sub-group
                    >
                    <template v-slot:activator>
                      <v-list-item-content>
                        <v-list-item-title></v-list-item-title>
                      </v-list-item-content>
                    </template>
                    <div v-if="item.actions.calificacionId != undefined">
                      <v-list-item>
                        <a class="dropdown-item" v-bind:href="formulario_calificacion(item.actions.campanaId, item.actions.contactoId)">
                          <span class="icon icon-pencil"></span>Call disposition
                        </a>
                      </v-list-item>
                    </div>
                    <div v-if="item.actions.gestionId != undefined">
                      <v-list-item>
                        <a class="dropdown-item" v-bind:href="formulario_venta(item.actions.calificacionId)">
                          <span class="icon icon-pencil"></span>Engaged
                        </a>
                      </v-list-item>
                    </div>
                  </v-list-group>
                </v-list-item>
              </v-list>
            </div>
          </td>
        </tr>
      </tbody>
  </v-simple-table>`,
    props: ['values', 'headers'],
    methods: {
        makeClick2Call: function (campaign_id, campaign_type, contact_id, phone, call_type) {
            // FIXME: Codigo de makeClick2Call copiado desde make_click2call.js, ver como importarlo
            // Utilizar click2call manager para intentar llamar.
            // Ver si tengo acceso
            if (window.parent.hasOwnProperty('click2call')){
                var click2call = window.parent.click2call;
                click2call.call_contact(campaign_id, campaign_type, contact_id, phone, call_type);
            } else {
                // console.log('Alertar al usuario que no es posible hacer una click2call');
            }
        },
        formulario_venta: function (id) {
            return Urls.formulario_venta(id);
        },
        formulario_calificacion: function (campanaId, contactoId) {
            return Urls.calificacion_cliente_actualiza_desde_reporte(campanaId, contactoId);
        }

    },
};

export { InfoNumerica, LogsLlamadas };
