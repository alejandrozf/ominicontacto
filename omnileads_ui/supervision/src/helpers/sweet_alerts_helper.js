export function getToasConfig (title = '', text = '', icon = 'success', footer = null) {
    return {
        title,
        text,
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
