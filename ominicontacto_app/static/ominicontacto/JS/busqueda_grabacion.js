/* eslint-disable no-undef */
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

/* global get_ranges */


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

    $('.check-grabacion').on('click', function() {
        if (!$('#check-grabacion').prop('checked')) {
            checkGeneral.prop('checked', false);
        }
    });

    $('#zipGrabaciones').on('click', function() {
        wsProcess();
    });
});

function cambiaEstadoChecks(estado) {
    console.log('entro');
    $('.check-grabacion').prop('checked', estado);
}

function filtrar_pagina(pagina) {
    $('#id_pagina').val(pagina);
    $('#form-buscar-grabacion').submit();
}

function generarZip() {
    var buttonZip = $('#zipGrabaciones');
    var check_mostrar_datos_contacto = $('#check-mostrar-datos-contacto').is(':checked');
    buttonZip.val(gettext('Descargar archivo de grabaciones (ZIP)'));
    buttonZip.attr('class', 'btn btn-outline-secondary btn-sm disabled');
    buttonZip.attr('disabled', true);

    $.ajax({
        type: 'POST',
        url: Urls.api_grabacion_descarga_masiva(),
        dataType: 'json',
        data: {
            files: JSON.stringify(prepareData()),
            mostrar_datos_contacto: check_mostrar_datos_contacto
        },
        success: function(msg) {
            console.log(msg);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown);
        }
    });
    $('#barraProgresoZip').toggle();

}

function wsProcess() {
    var final = false;
    prepareData();
    // establece conexion a websocket para obtener los status
    // y enviarlos a la barra de progreso
    const userId = $('#user_id').val();
    const url = `wss://${window.location.host}/consumers/genera_zip_grabaciones/grabaciones/${userId}/zip`;
    const rws = new ReconnectingWebSocket(url, [], {
        connectionTimeout: 8000,
        maxReconnectionDelay: 3000,
        minReconnectionDelay: 1000,
    });
    rws.addEventListener('message', function(e) {
        var data = e.data;
        if (data == subscribeConfirmationMessage) {
            generarZip();
        } else if (!final) {

            $barraProgresoCSV = $('#barraProgresoZip');
            $barraProgresoCSV.find('.progress-bar').width(data + '%');
            $barraProgresoCSV.find('.progress-bar').text(data + '%');
            if (data == '100') {
                final = true;
            }
        } else {
            $('#zipDescargaLink').attr('href', Urls.api_grabacion_archivo() + '?filename=/zip/' + data);
            $('#zipDescargaLink').attr('class', 'btn btn-outline-primary btn-sm');
            $('#zipGrabaciones').toggle();
            if (!('Notification' in window)) {
                console.log('Web Notification not supported');
                return;
            }

            var notification = new Notification(
                gettext('Operación completa'), {
                    body: gettext(
                        'La operación ha sido completada exitosamente.')
                });
            setTimeout(function() {
                notification.close();
            }, 3000);
            rws.close();
        }

    });
}

function prepareData() {
    var res = [];
    $('.check-grabacion:checked').each(function() {
        const id = $(this).val();
        const row = $('#tr-' + id);
        res.push(extractRowData(row));
    });
    return res;
}

function extractRowData(row) {
    const url = row.find('td').eq(7).find('a').eq(0).attr('href');
    const spt = url.split('filename=/');
    const fileName = spt[1];
    const res = {
        fecha: row.find('td').eq(2).text(),
        tipo_llamada: row.find('td').eq(3).text(),
        telefono_cliente: row.find('td').eq(4).text(),
        agente: row.find('td').eq(5).text(),
        campana: row.find('td').eq(6).text(),
        calificacion: row.find('td').eq(8).find('a').map(function(_, e) { return e.innerText.trim();}).toArray().join(', '),
        archivo: fileName,
        agente_username: row.find('td').eq(10).text(),
        contacto_id: row.find('td').eq(11).text(),
    };
    return res;
}

function initSubmitButton() {
    $('#id_buscar_btn').click(function (params) {
        $('#submit_msg').show();
        setTimeout(function () { $('#id_buscar_btn').attr('disabled', true); }, 0);
    });
}
