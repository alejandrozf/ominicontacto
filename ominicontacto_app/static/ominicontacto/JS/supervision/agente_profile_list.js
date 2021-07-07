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

function obtener_campanas_agente(pk_agent) {
    var $campanasAgenteModal = $('#campanasAgenteModal');
    table = $('#campanasAgenteTable').DataTable( {
      ajax: {
          url: Urls.api_campanas_de_supervisor() + '?agent=' + pk_agent,
          dataSrc: '',
      },
      columns: [
          { 'data': 'nombre',},
          { 'data': 'id'},
          { 'data': 'objetivo'},
      ],
    } );
    $campanasAgenteModal.modal('show');
    table.destroy();
};
