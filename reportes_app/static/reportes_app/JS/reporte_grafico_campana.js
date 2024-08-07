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



function exportarReporteCSV(sufijoUrl, $csvDescarga, urlExportacion, $barraProgresoCSV, $csvDescargaLink, start, end) {

    var campanaId = $('#campana_id').val();
    var taskId = $('#task_id').val();

    // establece conexion a websocket para obtener los status
    // y enviarlos a la barra de progreso
    const url = `wss://${window.location.host}/consumers/reporte_grafico_campana/${sufijoUrl}/${campanaId}/${taskId}`;
    const rws = new ReconnectingWebSocket(url, [], {
        connectionTimeout: 8000,
        maxReconnectionDelay: 3000,
        minReconnectionDelay: 1000,
    });
    rws.addEventListener('message', function(e) {
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
                rws.close();
            }
        }
    });
}


$(function() {

    Notification.requestPermission();

    var $csvContactadosDescarga = $('#csvContactadosDescarga');
    var $csvContactadosDescargaLink = $('#csvContactadosDescargaLink');
    var $barraCSVContactados = $('#barraProgresoCSVContactados');
    var urlExportacionContactados = Urls.api_exportar_csv_contactados();


    var $csvCalificadosDescarga = $('#csvCalificadosDescarga');
    var $csvCalificadosDescargaLink = $('#csvCalificadosDescargaLink');
    var $barraCSVCalificados = $('#barraProgresoCSVCalificados');
    var urlExportacionCalificados = Urls.api_exportar_csv_calificados();

    var $csvDescargaNoAtendidos = $('#csvNoAtendidosDescarga');
    var $csvNoAtendidosDescargaLink = $('#csvNoAtendidosDescargaLink');
    var $barraCSVNoAtendidos = $('#barraProgresoCSVNoAtendidos');
    var urlExportacionNoAtendidos = Urls.api_exportar_csv_no_atendidos();

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

    initSubmitButton();
    var date_format = 'DD/MM/YYYY';

    function set_daterange_input_values(start, end) {
        $('#id_fecha').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
    }

    $('#id_fecha').on('apply.daterangepicker', function(ev, picker) {
        $(this).val(picker.startDate.format(date_format) + ' - ' + picker.endDate.format(date_format));
    });

    $('#id_fecha').on('cancel.daterangepicker', function(ev, picker) {
        $(this).val('');
    });

    // Init daterange plugin
    var ranges = get_ranges($('#campana_fecha_inicio').val());
    $('#id_fecha').daterangepicker(
        {
            locale: {
                format: date_format
            },

            startDate: start,
            endDate: end,
            ranges: ranges,
        },
        set_daterange_input_values
    );

    set_daterange_input_values(start, end);

    $csvContactadosDescarga.on('click', function() {
        var $self = $(this);
        exportarReporteCSV('contactados', $self, urlExportacionContactados, $barraCSVContactados,
            $csvContactadosDescargaLink, start, end);
    });

    $csvCalificadosDescarga.on('click', function() {
        var $self = $(this);
        exportarReporteCSV('calificados', $self, urlExportacionCalificados, $barraCSVCalificados,
            $csvCalificadosDescargaLink, start, end);
    });

    $csvDescargaNoAtendidos.on('click', function() {
        var $self = $(this);
        exportarReporteCSV('no_atendidos', $self, urlExportacionNoAtendidos, $barraCSVNoAtendidos,
            $csvNoAtendidosDescargaLink, start, end);
    });

});

function initSubmitButton() {
    $('#id_buscar_btn').click(function (params) {
        $('#submit_msg').show();
        setTimeout(function () { $('#id_buscar_btn').attr('disabled', true); }, 0);
    });
}
