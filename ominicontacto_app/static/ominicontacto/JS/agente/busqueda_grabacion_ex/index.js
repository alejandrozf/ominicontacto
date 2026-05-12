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

    const reconnectGracePeriodMs = 15000;
    let elapsedIntervalId = null;
    let reconnectTimeoutId = null;
    let loadingStartTime = null;
    let currentTaskId = null;
    let requestInFlight = false;
    let requestResolved = false;
    let resultFetchInProgress = false;
    let initialRequestSent = false;

    function getLoadingElements() {
        return {
            $button: $('#id_buscar_btn'),
            $status: $('#recordings_search_loading_status'),
            $spinner: $('#recordings_search_loading_spinner'),
            $message: $('#recordings_search_loading_message'),
            $elapsed: $('#recordings_search_loading_elapsed'),
        };
    }

    function formatElapsed(milliseconds) {
        const totalSeconds = Math.floor(milliseconds / 1000);
        const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, '0');
        const seconds = String(totalSeconds % 60).padStart(2, '0');
        return `${minutes}:${seconds}`;
    }

    function generateTaskId() {
        if (window.crypto && typeof window.crypto.randomUUID === 'function') {
            return window.crypto.randomUUID();
        }
        return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    }

    function stopElapsedCounter() {
        if (elapsedIntervalId !== null) {
            window.clearInterval(elapsedIntervalId);
            elapsedIntervalId = null;
        }
        loadingStartTime = null;
    }

    function clearReconnectTimeout() {
        if (reconnectTimeoutId !== null) {
            window.clearTimeout(reconnectTimeoutId);
            reconnectTimeoutId = null;
        }
    }

    function startElapsedCounter() {
        const { $elapsed } = getLoadingElements();
        stopElapsedCounter();
        loadingStartTime = Date.now();
        $elapsed.text('00:00');
        elapsedIntervalId = window.setInterval(function () {
            $elapsed.text(formatElapsed(Date.now() - loadingStartTime));
        }, 1000);
    }

    function updateStatus(customMessage, isError) {
        const { $status, $spinner, $message } = getLoadingElements();
        if (!$status.length) {
            return;
        }

        $status.removeClass('hidden');
        $message.text(customMessage);
        if (isError) {
            $status.addClass('recordings-search-loading-status--error');
            $spinner.addClass('hidden');
            return;
        }

        $status.removeClass('recordings-search-loading-status--error');
        $spinner.removeClass('hidden');
    }

    function sendResumeRequest() {
        if (!requestInFlight || requestResolved || !currentTaskId) {
            return;
        }
        try {
            rws.send(JSON.stringify({
                'type': 'search_recordings.resume',
                'task_id': currentTaskId,
            }));
        } catch (error) {
            startReconnectTimeout();
        }
    }

    async function fetchTaskResult() {
        const { $status } = getLoadingElements();
        if (!currentTaskId || !$status.length || resultFetchInProgress) {
            return;
        }

        resultFetchInProgress = true;
        updateStatus($status.data('fetching-result-text'), false);

        try {
            const response = await fetch(
                `${$status.data('result-url')}?task_id=${encodeURIComponent(currentTaskId)}`,
                {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    credentials: 'same-origin',
                }
            );

            if (response.status === 202) {
                window.setTimeout(fetchTaskResult, 1000);
                return;
            }

            if (!response.ok) {
                const errorPayload = await response.json();
                throw new Error(errorPayload.error_message || $status.data('connection-error-text'));
            }

            const result = await response.json();
            requestResolved = true;
            setLoading(false);
            applyFragments(result.fragments);
        } catch (error) {
            setLoading(false, error.message || $status.data('connection-error-text'));
        } finally {
            // eslint-disable-next-line require-atomic-updates
            resultFetchInProgress = false;
        }
    }

    function updateStatusFromServer(status, errorMessage) {
        const { $status } = getLoadingElements();
        if (!$status.length) {
            return;
        }
        if (status === 'queued') {
            updateStatus($status.data('queued-text'), false);
            return;
        }
        if (status === 'running') {
            updateStatus($status.data('running-text'), false);
            return;
        }
        if (status === 'done') {
            fetchTaskResult();
            return;
        }
        if (status === 'failed') {
            setLoading(false, errorMessage || $status.data('connection-error-text'));
        }
    }

    function setLoading(value, customMessage) {
        const { $button, $status } = getLoadingElements();
        if (!$button.length || !$status.length) {
            clearReconnectTimeout();
            stopElapsedCounter();
            return;
        }
        if (value) {
            clearReconnectTimeout();
            requestInFlight = true;
            requestResolved = false;
            resultFetchInProgress = false;
            $button.prop('disabled', true);
            updateStatus(customMessage || $status.data('loading-text'), false);
            startElapsedCounter();
            return;
        }

        clearReconnectTimeout();
        $button.prop('disabled', false);
        stopElapsedCounter();
        requestInFlight = false;
        resultFetchInProgress = false;
        if (!customMessage) {
            requestResolved = true;
            currentTaskId = null;
        }

        if (customMessage) {
            currentTaskId = null;
            updateStatus(customMessage, true);
            return;
        }
        $status.addClass('hidden');
    }

    function startReconnectTimeout() {
        const { $status } = getLoadingElements();
        clearReconnectTimeout();
        reconnectTimeoutId = window.setTimeout(function () {
            if (requestInFlight && !requestResolved) {
                currentTaskId = null;
                setLoading(false, $status.data('connection-error-text'));
            }
        }, reconnectGracePeriodMs);
    }

    const $form = $('#form-buscar-grabacion');
    const websocketProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const rws = new ReconnectingWebSocket(
        `${websocketProtocol}://${window.location.host}/channels/background-tasks`,
        [],
        {
            connectionTimeout: 8000,
            maxReconnectionDelay: 3000,
            minReconnectionDelay: 1000,
            // debug: true,
        }
    );

    function applyFragments(fragments) {
        if (!fragments) {
            return;
        }
        Object.entries(fragments).forEach(([fragment, content]) => {
            $(fragment).html(content);
        });
    }

    function sendSearchRequest() {
        currentTaskId = generateTaskId();
        setLoading(true);
        try {
            rws.send(JSON.stringify({
                'type': 'search_recordings.request',
                'task_id': currentTaskId,
                'data': $form.serialize(),
            }));
        } catch (error) {
            currentTaskId = null;
            setLoading(false, getLoadingElements().$status.data('connection-error-text'));
        }
    }

    $form.submit(function (event) {
        event.preventDefault();
        sendSearchRequest();
    });

    rws.addEventListener('message', function (event) {
        const message = JSON.parse(event.data);
        if (
            message.task_id
            && currentTaskId
            && message.task_id !== currentTaskId
        ) {
            return;
        }
        if (message.type === 'search_recordings.status') {
            if (!requestInFlight) {
                return;
            }
            updateStatusFromServer(message.status, message.error_message);
            return;
        }
        if (message.type === 'search_recordings.respond') {
            if (!requestInFlight) {
                return;
            }
            setLoading(false);
            applyFragments(message.result.fragments);
            // console.log(JSON.stringify(message, null, 2))
        }
    });

    rws.addEventListener('open', function () {
        if (requestInFlight && !requestResolved) {
            clearReconnectTimeout();
            updateStatus(getLoadingElements().$status.data('loading-text'), false);
            sendResumeRequest();
            return;
        }
        if (!initialRequestSent) {
            initialRequestSent = true;
            sendSearchRequest();
        }
    });

    rws.addEventListener('close', function () {
        const { $button, $status } = getLoadingElements();
        if (requestInFlight && !requestResolved && $button.prop('disabled') && $status.length) {
            updateStatus($status.data('reconnecting-text'), false);
            startReconnectTimeout();
        }
    });

    rws.addEventListener('error', function () {
        const { $button, $status } = getLoadingElements();
        if (requestInFlight && !requestResolved && $button.prop('disabled') && $status.length) {
            updateStatus($status.data('reconnecting-text'), false);
            startReconnectTimeout();
        }
    });

    $('#pagination').on('click', '.page-link', function () {
        $('#id_pagina').val(this.dataset.page);
        sendSearchRequest();
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
