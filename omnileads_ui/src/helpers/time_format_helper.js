export function formatTime (seconds) {
    var date = new Date(seconds * 1000);
    var hhLabel = 'horas';
    var mmLabel = 'minutos';
    var ssLabel = 'segundos';
    var hh = date.getUTCHours();
    var mm = date.getUTCMinutes();
    var ss = date.getSeconds();
    if (hh !== 0) {
        if (hh === 1) { hhLabel = 'hora'; }
        if (mm === 1) { mmLabel = 'minuto'; }
        if (ss === 1) { ssLabel = 'segundo'; }
        if (hh < 10) { hh = '0' + hh; }
        if (mm < 10) { mm = '0' + mm; }
        if (ss < 10) { ss = '0' + ss; }
        return `${hh} ${hhLabel}, ${mm} ${mmLabel}, ${ss} ${ssLabel}`;
    }
    if (mm !== 0) {
        if (mm === 1) { mmLabel = 'minuto'; }
        if (ss === 1) { ssLabel = 'segundo'; }
        if (mm < 10) { mm = '0' + mm; }
        if (ss < 10) { ss = '0' + ss; }
        return `${mm} ${mmLabel}, ${ss} ${ssLabel}`;
    }
    if (ss === 1) { ssLabel = 'segundo'; }
    if (ss < 10) { ss = '0' + ss; }
    return `${ss} ${ssLabel}`;
}

export function getDatetimeFormat (fecha) {
    const date = new Date(fecha);
    const months = [
        'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
        'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'
    ];

    const month = months[date.getMonth()];

    const dia = ('0' + date.getDate()).slice(-2);
    const hora = ('0' + date.getHours()).slice(-2);
    const minuto = ('0' + date.getMinutes()).slice(-2);
    const segundo = ('0' + date.getSeconds()).slice(-2);

    return `${month} ${dia}, ${date.getFullYear()} ${hora}:${minuto}:${segundo}`;
}
