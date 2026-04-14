var AgentAlert = (function () {
    var BOX_ID = 'agent-alert-box';
    var OVERLAY_ID = 'agent-alert-overlay';
    var ESC_NAMESPACE = '.agentAlertEsc';
    var DRAG_NAMESPACE = '.agentAlertDrag';

    var alerts = [];
    var currentIndex = -1;
    var autoCloseTimeout = null;

    function show(options) {
        options = options || {};

        alerts.push({
            title: options.title || 'Alerta',
            message: options.message || '',
            type: options.type || 'info',
            duration: Number(options.duration) || 0,
            closeText: options.closeText || 'Cerrar',
            closeOnOverlay: options.closeOnOverlay === true,
            closeOnEscape: options.closeOnEscape !== false,
            draggable: options.draggable !== false
        });

        if (currentIndex === -1) {
            currentIndex = 0;
        }

        render();
    }

    function render() {
        clearAutoClose();
        unbindEscape();
        unbindDrag();

        $('#' + BOX_ID).remove();
        $('#' + OVERLAY_ID).remove();

        if (alerts.length === 0) {
            currentIndex = -1;
            return;
        }

        if (currentIndex < 0) {
            currentIndex = 0;
        }

        if (currentIndex > alerts.length - 1) {
            currentIndex = alerts.length - 1;
        }

        var alert = alerts[currentIndex];

        var $overlay = $('<div>', {
            id: OVERLAY_ID,
            class: 'agent-alert-overlay'
        });

        var $box = $('<div>', {
            id: BOX_ID,
            class: 'agent-alert ' + getTypeClass(alert.type),
            role: 'dialog',
            'aria-modal': 'true',
            tabindex: -1
        });

        var $header = $('<div>', {
            class: 'agent-alert__header'
        });

        var $body = $('<div>', {
            class: 'agent-alert__body'
        }).text(alert.message);

        var $actions = $('<div>', {
            class: 'agent-alert__actions'
        });

        var $prev = $('<button>', {
            type: 'button',
            class: 'agent-alert__nav',
            text: '◀',
            'aria-label': 'Anterior'
        });

        var $next = $('<button>', {
            type: 'button',
            class: 'agent-alert__nav',
            text: '▶',
            'aria-label': 'Siguiente'
        });

        if (currentIndex === 0) {
            $prev.prop('disabled', true);
        }

        if (currentIndex === alerts.length - 1) {
            $next.prop('disabled', true);
        }

        var $close = $('<button>', {
            type: 'button',
            class: 'agent-alert__close',
            text: alert.closeText,
            'aria-label': alert.closeText
        });

        $prev.on('click', prev);
        $next.on('click', next);
        $close.on('click', closeCurrent);

        if (alert.closeOnOverlay) {
            $overlay.on('click', closeCurrent);
        }

        $actions.append($prev, $next, $close);
        $box.append($header, $body, $actions);

        $('body').append($overlay, $box);

        updateHeaderCounter();

        if (alert.draggable) {
            makeDraggable($box, $header);
        }

        if (alert.closeOnEscape) {
            bindEscape();
        }

        if (alert.duration > 0) {
            autoCloseTimeout = setTimeout(closeCurrent, alert.duration);
        }

        $box.focus();
    }

    function updateHeaderCounter() {
        if (currentIndex < 0 || alerts.length === 0) {
            return;
        }

        var alert = alerts[currentIndex];
        var total = alerts.length;
        var text = alert.title;

        if (total > 1) {
            text += ' (' + (currentIndex + 1) + ' de ' + total + ')';
        }

        $('.agent-alert__header').text(text);
    }

    function next() {
        if (currentIndex < alerts.length - 1) {
            currentIndex++;
            render();
        }
    }

    function prev() {
        if (currentIndex > 0) {
            currentIndex--;
            render();
        }
    }

    function closeCurrent() {
        if (currentIndex < 0 || alerts.length === 0) {
            closeAll();
            return;
        }

        alerts.splice(currentIndex, 1);

        if (alerts.length === 0) {
            closeAll();
            return;
        }

        if (currentIndex > alerts.length - 1) {
            currentIndex = alerts.length - 1;
        }

        render();
    }

    function closeAll() {
        alerts = [];
        currentIndex = -1;

        clearAutoClose();
        unbindEscape();
        unbindDrag();

        $('#' + BOX_ID).remove();
        $('#' + OVERLAY_ID).remove();
        $('body').css('user-select', '');
    }

    function clearAutoClose() {
        if (autoCloseTimeout) {
            clearTimeout(autoCloseTimeout);
            autoCloseTimeout = null;
        }
    }

    function bindEscape() {
        $(document).off('keydown' + ESC_NAMESPACE);
        $(document).on('keydown' + ESC_NAMESPACE, function (e) {
            if (e.key === 'Escape' || e.keyCode === 27) {
                closeCurrent();
            }
        });
    }

    function unbindEscape() {
        $(document).off('keydown' + ESC_NAMESPACE);
    }

    function makeDraggable($element, $handle) {
        var isDragging = false;
        var offsetX = 0;
        var offsetY = 0;

        $handle.on('mousedown' + DRAG_NAMESPACE, function (e) {
            if (e.which !== 1) {
                return;
            }

            isDragging = true;

            var offset = $element.offset();
            offsetX = e.pageX - offset.left;
            offsetY = e.pageY - offset.top;

            $element.addClass('agent-alert--dragging');
            $element.css({
                top: offset.top,
                left: offset.left,
                transform: 'none'
            });

            $('body').css('user-select', 'none');
            e.preventDefault();
        });

        $(document).on('mousemove' + DRAG_NAMESPACE, function (e) {
            if (!isDragging) {
                return;
            }

            $element.css({
                left: e.pageX - offsetX,
                top: e.pageY - offsetY
            });
        });

        $(document).on('mouseup' + DRAG_NAMESPACE, function () {
            if (!isDragging) {
                return;
            }

            isDragging = false;
            $element.removeClass('agent-alert--dragging');
            $('body').css('user-select', '');
        });
    }

    function unbindDrag() {
        $(document).off(DRAG_NAMESPACE);
        $('.agent-alert__header').off(DRAG_NAMESPACE);
    }

    function getTypeClass(type) {
        switch (type) {
        case 'success':
            return 'agent-alert--success';
        case 'warning':
            return 'agent-alert--warning';
        case 'error':
            return 'agent-alert--error';
        default:
            return 'agent-alert--info';
        }
    }

    return {
        show: show,
        closeCurrent: closeCurrent,
        closeAll: closeAll
    };
})();