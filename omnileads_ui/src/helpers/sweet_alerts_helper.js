import Swal from 'sweetalert2';
export const ICONS = {
    SUCCESS: 'success',
    ERROR: 'error',
    WARNING: 'warning',
    INFO: 'info'
};
export const POSITIONS = {
    TOP: 'top',
    TOP_START: 'top-start',
    TOP_END: 'top-end',
    CENTER: 'center',
    CENTER_START: 'center-start',
    CENTER_END: 'center-end',
    BOTTOM: 'bottom',
    BOTTOM_START: 'bottom-start',
    BOTTOM_END: 'bottom-end'
};

export function getToasConfig (
    title = '',
    text = '',
    icon = 'success',
    footer = null,
    html = null
) {
    return {
        title,
        text,
        html,
        icon,
        footer,
        timer: 5000,
        showConfirmButton: false,
        showCloseButton: true,
        backdrop: false,
        position: 'top-end',
        toast: true
    };
}

export function toasConfig ({
    title = '',
    text = '',
    html = null,
    icon = ICONS.SUCCESS,
    footer = null,
    timer = 5000,
    showConfirmButton = false,
    showCloseButton = true,
    position = POSITIONS.TOP_END,
    toast = true
}) {
    return {
        title,
        text,
        html,
        icon,
        footer,
        timer,
        showConfirmButton,
        showCloseButton,
        position,
        toast
    };
}

export function fireNotification (config) {
    return Swal.fire(toasConfig(config));
}
