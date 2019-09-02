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

$(function(){
    setInterval(function() {requestEstadisticasEntrantes();}, 5000);
});

function requestEstadisticasEntrantes() {
    // {% url 'api_supervision_campanas_entrantes'%}
    var url = Urls.api_supervision_campanas_entrantes();
    $.ajax({type: 'get',
        url: url,
        contentType: 'text/html',
        success: function(msg) {
            cargarEstadisticasEntrantes(msg.data);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown);
        }
    });
}

function cargarEstadisticasEntrantes(estadisticas) {
    var tabla = $('#table-campanas');
    tabla.html('');
    Object.keys(estadisticas).forEach(function(id_campana) {
        var datos_campana = estadisticas[id_campana];
        $('#table-campanas').html();
        tabla.append('<tr>' +
                       '<td>' + datos_campana['nombre'] + '</td>' +
                       '<td>' + datos_campana['recibidas'] + '</td>' +
                       '<td>' + datos_campana['atendidas'] + '</td>' +
                       '<td>' + datos_campana['abandonadas'] + '</td>' +
                       '<td>' + datos_campana['abandonadas_anuncio'] + '</td>' +
                       '<td>' + datos_campana['t_promedio_espera'].toFixed(1) + gettext(' segundos') +'</td>' +
                       '<td>' + datos_campana['expiradas'] + '</td>' +
                       '<td>' + datos_campana['en_cola'] + '</td>' +
                       '<td>' + datos_campana['gestiones'] + '</td>' +
                     '</tr>');
    });
}
