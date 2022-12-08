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
