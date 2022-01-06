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

/* global moment get_ranges Urls gettext */


var subscribeConfirmationMessage = 'Subscribed!';

function generarReporteCSV(urlExportacion, $csvDescarga, sufijoUrl, start, end,
    $barraProgresoCSV, campanaId, taskId) {

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
            'desde': start.format('DD/MM/YYYY'),
            'hasta': end.format('DD/MM/YYYY'),
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



function exportarReporteCSV(sufijoUrl, $csvDescarga, taskId, urlExportacion, $barraProgresoCSV, $csvDescargaLink, start, end) {

    var campanaId = $('#campana_id').val();
   
    // establece conexion a websocket para obtener los status
    // y enviarlos a la barra de progreso
    const contactadosSocket = new WebSocket(
        'wss://' +
        window.location.host +
        '/consumers/reporte_grafico_campana/' +
        sufijoUrl +
        '/' +
        campanaId +
        '/' +
        taskId
    );

    contactadosSocket.onmessage = function(e) {
        var data = e.data;
        if (data == subscribeConfirmationMessage) {
            generarReporteCSV(urlExportacion, $csvDescarga, sufijoUrl, start, end,
                $barraProgresoCSV, campanaId, taskId);
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
                            ' ha sido completada completada exitosamente.')
                    });
                setTimeout(function() {
                    notification.close();
                }, 3000);
                contactadosSocket.close();
            }
        }
    };
}


$(function() {

    Notification.requestPermission();

    var calificaciones_task_id =  $('#calificaciones_task_id').val();
    var $csvCalificacionesCampanaDescarga = $('#csvCalificacionesCampanaDescarga');
    var $csvCalificacionesCampanaDescargaLink = $('#csvCalificacionesCampanaDescargaLink');
    var $barraCSVCalificacionesCampana = $('#barraProgresoCSVCalificacionesCampana');
    var urlExportacionCalificacionesCampana = Urls.api_exportar_csv_calificaciones_campana();

    var formulario_gestion_task_id =  $('#formulario_gestion_task_id').val();
    var $csvFormularioGestionCampanaDescarga = $('#csvFormularioGestionCampanaDescarga');
    var $csvFormularioGestionCampanaDescargaLink = $('#csvFormularioGestionCampanaDescargaLink');
    var $barraCSVFormularioGestionCampana = $('#barraProgresoCSVFormularioGestionCampana');
    var urlExportacionFormularioGestionCampana = Urls.api_exportar_csv_formulario_gestion_campana();

    var $fechaElegidaDesde = $('#reporte_fecha_desde_elegida');
    var $fechaElegidaHasta = $('#reporte_fecha_hasta_elegida');


    var start, end;

    if ($fechaElegidaDesde.val() == '') {
        start = moment();
        end = moment();
    } else {
        start = moment(moment(Date.parse($fechaElegidaDesde.val())));
        end = moment(moment(Date.parse($fechaElegidaHasta.val())));
    }

    function cb(start, end) {
        $('#id_fecha').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
    }

    $('#id_fecha').on('apply.daterangepicker', function(ev, picker) {
        $(this).val(picker.startDate.format('DD/MM/YYYY') + ' - ' + picker.endDate.format('DD/MM/YYYY'));
    });

    $('#id_fecha').on('cancel.daterangepicker', function(ev, picker) {
        $(this).val('');
    });

    // Init daterange plugin
    var ranges = get_ranges($('#campana_fecha_inicio').val());
    $('#id_fecha').daterangepicker({
        locale: {
            format: 'DD/MM/YYYY'
        },

        startDate: start,
        endDate: end,
        ranges: ranges,
    }, cb);

    cb(start, end);

    $csvCalificacionesCampanaDescarga.on('click', function() {
        var $self = $(this);
        exportarReporteCSV('calificados', $self, calificaciones_task_id, urlExportacionCalificacionesCampana, $barraCSVCalificacionesCampana,
            $csvCalificacionesCampanaDescargaLink, start, end);
    });

    $csvFormularioGestionCampanaDescarga.on('click', function() {
        var $self = $(this);
        exportarReporteCSV('formulario_gestion', $self, formulario_gestion_task_id, urlExportacionFormularioGestionCampana, $barraCSVFormularioGestionCampana,
            $csvFormularioGestionCampanaDescargaLink, start, end);
    });

});

