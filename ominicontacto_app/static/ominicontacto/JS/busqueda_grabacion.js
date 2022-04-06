/* eslint-disable no-undef */
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
var subscribeConfirmationMessage = 'Subscribed!';

$(function() {
    var start = moment().subtract(29, 'days');
    var end = moment();

    function cb(start, end) {
        $('#id_fecha').html(start.format('DD/MM/YYYY') + ' - ' + end.format('DD/MM/YYYY'));
    }

    $('#id_fecha').on('apply.daterangepicker', function(ev, picker) {
        $(this).val(picker.startDate.format('DD/MM/YYYY') + ' - ' + picker.endDate.format('DD/MM/YYYY'));
    });

    $('#id_fecha').on('cancel.daterangepicker', function(ev, picker) {
        $(this).val('');
    });

    var ranges = get_ranges();

    // Init daterange plugin
    $('#id_fecha').daterangepicker({
        locale: {
            format: 'DD/MM/YYYY'
        },
        autoUpdateInput: false,
        ranges: ranges,
    }, cb);

    cb(start, end);

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
    const zipSocket = new WebSocket(
        'wss://' +
        window.location.host +
        '/consumers/genera_zip_grabaciones/grabaciones/' + userId + '/zip'
    );

    zipSocket.onmessage = function(e) {
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
                        'La operación ha sido completada completada exitosamente.')
                });
            setTimeout(function() {
                notification.close();
            }, 3000);
            zipSocket.close();
        }

    };
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
        calificacion: row.find('td').eq(8).text().replace('\n', ' ').trim(),
        archivo: fileName,
        agente_username: row.find('td').eq(10).text(),
        contacto_id: row.find('td').eq(11).text(),
    };
    return res;
}