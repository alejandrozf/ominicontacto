/* Copyright (C) 2018 Freetech Solutions

 This file is part of OMniLeads

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see http://www.gnu.org/licenses/.

*/

function formatTime (seconds) {
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

function setTimerText(timer) {
    if (timer > 0) {
        $('#showPauseTimer').html(`<b>Duracion de la pausa:</b> ${formatTime(timer)}`);
    } else {
        $('#showPauseTimer').text('');
    }
}

$('#pauseType').change(function(){
    const pauseData = $(this).val().split(',');
    const timeToEndPause = parseInt(pauseData[2]);
    setTimerText(timeToEndPause);
});

const pauseData = $('#pauseType').val().split(',');
const timeToEndPause = parseInt(pauseData[2]);
setTimerText(timeToEndPause);

