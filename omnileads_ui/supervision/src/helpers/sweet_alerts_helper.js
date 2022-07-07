export function getToasConfig (title = '', text = '', icon = 'success', footer = null, html = null) {
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
