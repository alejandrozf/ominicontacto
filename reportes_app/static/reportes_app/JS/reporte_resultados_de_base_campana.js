/* Copyright (C) 2018 Freetech Solutions

 This file is part of OMniLeads

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Lesser General Public License version 3, as published by
 the Free Software Foundation.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Lesser General Public License for more details.

 You should have received a copy of the GNU Lesser General Public License
 along with this program.  If not, see http://www.gnu.org/licenses/.

*/

/* global moment get_ranges Urls gettext */


var subscribeConfirmationMessage = 'Subscribed!';

function generarReporteCSV(urlExportacion, $csvDescarga, sufijoUrl,
    $barraProgresoCSV, campanaId, taskId, allData) {

    // realiza request a endpoint q genera el csv
    // en background
    $csvDescarga.val(gettext('Descargar Reporte de ' + sufijoUrl + '(CSV)'));
    $csvDescarga.attr('class', 'btn btn-outline-secondary btn-sm disabled');
    $csvDescarga.attr('disabled', true);
    
    // generar el csv
    $.ajax({
        type: 'POST',
        url: urlExportacion,
        dataType: 'json',
        data: {
            'task_id': taskId,
            'campana_id': campanaId,
            'all_data': allData
        },
        success: function(msg) {
            console.log(msg);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown);
        }
    });
    $barraProgresoCSV.toggle();

}

function exportarReporteCSV(sufijoUrl, $csvDescarga, urlExportacion,
    $barraProgresoCSV, $csvDescargaLink, allData) {

    var campanaId = $('#campana_id').val();
    var taskId = $('#task_id').val();

    // establece conexion a websocket para obtener los status
    // y enviarlos a la barra de progreso
    const url = `wss://${window.location.host}/consumers/reporte_resultados_de_base_campana/${sufijoUrl}/${campanaId}/${taskId}`;
    const rws = new ReconnectingWebSocket(url, [], {
        connectionTimeout: 8000,
        maxReconnectionDelay: 3000,
        minReconnectionDelay: 1000,
    });
    rws.addEventListener('message', function(e) {
        var data = e.data;
        if (data == subscribeConfirmationMessage) {
            generarReporteCSV(
                urlExportacion,
                $csvDescarga,
                sufijoUrl,
                $barraProgresoCSV,
                campanaId,
                taskId,
                allData
            );
        } else {
            $barraProgresoCSV.find('.progress-bar').width(data + '%');
            $barraProgresoCSV.find('.progress-bar').text(data + '%');
            if (data == '100') {
                $csvDescargaLink.attr('class', 'btn btn-outline-primary btn-sm');
                $csvDescarga.remove();
                if (!('Notification' in window)) {
                    console.log('Web Notification not supported');
                    return;
                }

                var notification = new Notification(
                    gettext('Exportación completa'), {
                        body: gettext(
                            'La exportación a .csv del reporte de ' +
                            sufijoUrl +
                            ' ha sido completada exitosamente.')
                    });
                setTimeout(function() {
                    notification.close();
                }, 3000);
                rws.close();
            }
        }
    });
}


$(function() {
    Notification.requestPermission();

    // URL Api to generate report
    var urlApiExportacion = Urls.api_exportar_csv_resultados_base_contactados();

    // Contactaciones
    var $csvContactadosDescarga = $('#csvContactacionesDescarga');
    var $csvContactadosDescargaLink = $('#csvContactacionesDescargaLink');
    var $barraCSVContactados = $('#barraProgresoCSVContactaciones');
    $csvContactadosDescarga.on('click', function() {
        var $self = $(this);
        exportarReporteCSV(
            'resultados_de_base_contactados',
            $self,
            urlApiExportacion,
            $barraCSVContactados,
            $csvContactadosDescargaLink,
            0
        );
    });

    // Todas las contactaciones
    var $csvTodosContactadosDescarga = $('#csvTodasContactacionesDescarga');
    var $csvTodosContactadosDescargaLink = $('#csvTodasContactacionesDescargaLink');
    var $barraCSVTodosContactados = $('#barraProgresoCSVTodasContactaciones');
    $csvTodosContactadosDescarga.on('click', function() {
        var $self = $(this);
        exportarReporteCSV(
            'resultados_de_base_contactados_todos',
            $self,
            urlApiExportacion,
            $barraCSVTodosContactados,
            $csvTodosContactadosDescargaLink,
            1
        );
    });
});
