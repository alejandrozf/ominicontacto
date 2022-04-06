export function getToasConfig (title = '', text = '', icon = 'success') {
    return {
        title,
        text,
        icon,
        timer: 5000,
        showConfirmButton: false,
        showCloseButton: true,
        backdrop: false,
        position: 'top-end',
        toast: true
    };
}
