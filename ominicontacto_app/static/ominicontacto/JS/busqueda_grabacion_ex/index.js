/* global Urls */
/* global get_ranges */
/* global gettext */

$(document).ready(function () {

    const $fecha = $('#id_fecha');
    $fecha.on('apply.daterangepicker', function (ev, picker) {
        $(this).val(picker.startDate.format('DD/MM/YYYY') + ' - ' + picker.endDate.format('DD/MM/YYYY'));
    });
    $fecha.on('cancel.daterangepicker', function (ev, picker) {
        $(this).val('');
    });
    $fecha.daterangepicker(
        {
            locale: { format: 'DD/MM/YYYY' },
            ranges: get_ranges(),
        },
        function (start, end, label) {
            $(this).html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
        }
    );

    $('select.form-control').each(function () {
        $(this).select2();
    });

    const $btnProgress = $('#id_buscar_btn > span');
    function setLoading(value) {
        if (value) {
            $btnProgress.text('...');
        } else {
            $btnProgress.text('');
        }
    }

    const $barraProgresoZip = $('#barraProgresoZip');
    const $checkGeneral = $('#check-general');
    const $check_mostrar_datos_contacto = $('#check-mostrar-datos-contacto');
    const $zipDescargaLink = $('#zipDescargaLink');
    const $zipGrabaciones = $('#zipGrabaciones');

    const $form = $('#form-buscar-grabacion');
    const rws = new ReconnectingWebSocket(
        `wss://${window.location.host}/channels/background-tasks`,
        [],
        {
            connectionTimeout: 8000,
            maxReconnectionDelay: 3000,
            minReconnectionDelay: 1000,
            // debug: true,
        }
    );

    $form.submit(function (event) {
        event.preventDefault();
        setLoading(true);
        rws.send(JSON.stringify({
            'type': 'search_recordings.request',
            'data': $form.serialize(),
        }));
    });

    rws.addEventListener('message', function (event) {
        const message = JSON.parse(event.data);
        if (message.type === 'search_recordings.respond') {
            setLoading(false);
            if (message.result.fragments) {
                $barraProgresoZip.hide();
                $zipDescargaLink.hide();
                $zipGrabaciones.show();
                $checkGeneral.prop('checked', false);
                Object.entries(message.result.fragments).forEach(([fragment, content]) => {
                    $(fragment).html(content);
                });
            }
            // console.log(JSON.stringify(message, null, 2))
        }
    });

    // rws.addEventListener('open', function (event) {
    //     setLoading(true);
    //     rws.send(JSON.stringify({
    //         'type': 'search_recordings.request',
    //         'data': $form.serialize(),
    //     }));
    // });

    $('#pagination').on('click', '.page-link', function () {
        setLoading(true);
        $('#id_pagina').val($(this).text());
        rws.send(JSON.stringify({
            'type': 'search_recordings.request',
            'data': $form.serialize(),
        }));
    });

    $('#descripcionModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var uid_val = button.data('uid');
        var modal = $(this);
        var URL = Urls.grabacion_descripcion(uid_val);
        $.get(
            URL,
            function (data) {
                $('#descripcionModalLabel').text(data.result);
                $('#descripcion-text').text(data.descripcion);
            }
        ).fail(function (data) {
            $('#descripcionModalLabel').text(gettext('Error'));
            $('#descripcion-text').text(gettext('Ha ocurrido un error al intentar conectarse'));
        });
    });

    $checkGeneral.on('click', function () {
        $('.check-grabacion').prop('checked', $checkGeneral.prop('checked'));
    });

    $('#table-body').on('click', '.check-grabacion', function () {
        if (!$('#check-grabacion').prop('checked')) {
            $checkGeneral.prop('checked', false);
        }
    });

    $zipGrabaciones.on('click', function () {
        if ($('.check-grabacion:checked').length === 0) {
            return;
        }
        let final = false;
        // establece conexion a websocket para obtener los status
        // y enviarlos a la barra de progreso
        const rws_tmp = new ReconnectingWebSocket(
            `wss://${window.location.host}/consumers/genera_zip_grabaciones/grabaciones/${$('#user_id').val()}/zip`,
            [],
            {
                connectionTimeout: 8000,
                maxReconnectionDelay: 3000,
                minReconnectionDelay: 1000,
                // debug: true,
            }
        );
        rws_tmp.addEventListener('message', function (e) {
            const data = e.data;
            if (data == 'Subscribed!') {
                generarZip();
            } else if (!final) {
                $barraProgresoZip.find('.progress-bar').width(data + '%').text(data + '%');
                if (data == '100') {
                    final = true;
                }
            } else {
                $zipGrabaciones.hide();
                $zipDescargaLink.attr('href', Urls.api_grabacion_archivo() + '?filename=/zip/' + data);
                $zipDescargaLink.show();
                rws_tmp.close();
            }
        });
    });

    function generarZip() {
        $.ajax({
            type: 'POST',
            url: Urls.api_grabacion_descarga_masiva(),
            dataType: 'json',
            data: {
                files: JSON.stringify(prepareData()),
                mostrar_datos_contacto: $check_mostrar_datos_contacto.is(':checked')
            },
            success: function (msg) {
                console.log(msg);
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.log(gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown);
            }
        });
        $barraProgresoZip.show();
    }

    function prepareData() {
        return $('.check-grabacion:checked').map(function () {
            const row = $('#tr-' + $(this).val());
            return {
                fecha: row.find('td').eq(2).text(),
                tipo_llamada: row.find('td').eq(3).text(),
                telefono_cliente: row.find('td').eq(4).text(),
                agente: row.find('td').eq(5).text(),
                campana: row.find('td').eq(6).text(),
                archivo: row.find('audio > source').attr('src').split('filename=/')[1],
                calificacion: row.find('td').eq(8).find('a').map(function (_, e) { return e.innerText.trim(); }).toArray().join(', '),
                agente_username: row.find('td').eq(10).text(),
                contacto_id: row.find('td').eq(11).text(),
            };
        }).get();
    }
});
