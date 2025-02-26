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
                Object.entries(message.result.fragments).forEach(([fragment, content]) => {
                    $(fragment).html(content);
                });
            }
            // console.log(JSON.stringify(message, null, 2))
        }
    });

    rws.addEventListener('open', function (event) {
        setLoading(true);
        rws.send(JSON.stringify({
            'type': 'search_recordings.request',
            'data': $form.serialize(),
        }));
    });

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
});
