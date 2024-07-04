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

/* global moment get_ranges Urls gettext*/

var subscribeConfirmationMessage = 'Subscribed!';

$(function() {

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
    var ranges = get_ranges();
    $('#id_fecha').daterangepicker(
        {
            locale: {
                format: date_format
            },
            ranges: ranges,
        },
        set_daterange_input_values
    );

    const checkGeneral = $('#check-general');
    checkGeneral.on('click', function() {
        cambiaEstadoChecks(checkGeneral.prop('checked'));
    });

    $('.check-auditoria').on('click', function() {
        if (!$('#check-auditoria').prop('checked')) {
            checkGeneral.prop('checked', false);
        }
    });

    $('#csvDescarga').on('click', function() {
        wsProcess();
    });
});

function cambiaEstadoChecks(estado) {
    $('.check-auditoria').prop('checked', estado);
}

function filtrar_pagina(pagina) {
    $('#id_pagina').val(pagina);
    $('#form-buscar-gestiones').submit();
}

function generarReporteCSV() {
    var buttonDescarga = $('#csvDescarga');
    var check_mostrar_detalles = $('#check-mostrar-detalles').is(':checked');
    buttonDescarga.val(gettext('Descargar archivo de auditoria (CSV)'));
    buttonDescarga.attr('class', 'btn btn-outline-secondary btn-sm disabled');
    buttonDescarga.attr('disabled', true);
    $.ajax({
        type: 'POST',
        url: Urls.api_auditoria_archivo(),
        dataType: 'json',
        data: {
            calificaciones_id: JSON.stringify(prepareData()),
            mostrar_detalles: check_mostrar_detalles
        },
        success: function(msg) {
            console.log(msg);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown);
        }
    });
    $('#barraProgresoCSV').toggle();

}

function wsProcess() {
    var $barraProgresoCSV = $('#barraProgresoCSV');
    var $csvDescarga = $('#csvDescarga');
    var $csvDescargaLink = $('#csvDescargaLink');
    const userId = $('#user_id').val();
    const url = `wss://${window.location.host}/consumers/genera_csv_auditoria/calificados/${userId}/csv`;
    const rws = new ReconnectingWebSocket(url, [], {
        connectionTimeout: 8000,
        maxReconnectionDelay: 3000,
        minReconnectionDelay: 1000,
    });
    rws.addEventListener('message', function(e) {
        var data = e.data;
        if (data == subscribeConfirmationMessage) {
            generarReporteCSV();
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
                            'La exportación a .csv del reporte ha sido ' +
                            'completada exitosamente.')
                    });
                setTimeout(function() {
                    notification.close();
                }, 3000);
                rws.close();
            }
        }
    });
}

function prepareData() {
    var res = [];
    $('.check-auditoria:checked').each(function() {
        const id = $(this).val();
        res.push(id);
    });
    return res;
}

function initSubmitButton() {
    $('#id_buscar_btn').click(function (params) {
        $('#submit_msg').show();
        setTimeout(function () { $('#id_buscar_btn').attr('disabled', true); }, 0);
    });
}
