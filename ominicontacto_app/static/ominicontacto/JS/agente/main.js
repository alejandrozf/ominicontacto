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

/* Requirements: 			*/
/* 		- Timers.js 		*/
/*      - omlAPI.js         */
/* 		- click2Call.js     */

/* globals Timer OMLAPI KeepAliveSender Click2CallDispatcher PhoneJSController gettext */
/* globals AgendasNotifier */

/* DEBUG*/
$('#wrapperWebphone').toggleClass('active');

var USER_STATUS_OFFLINE = 1; //  Agente en estado offline
var USER_STATUS_ONLINE = 2; //  Agente en estado online
var USER_STATUS_PAUSE = 3; //  Agente en estado pausa

var phone_controller = undefined;
var click2call = undefined;
var keep_alive_sender = undefined;

var logoffEvent = undefined;
var agendas_notifier = undefined;

$(function () {
    let agendas_dates = JSON.parse($('#agendas_dates_json').val());
    agendas_notifier = new AgendasNotifier(agendas_dates);

    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(function(stream) {
            startPhoneJs();
        })
        .catch(function(err) {
            alert(gettext('No se ha podido acceder a su micrófono. \n\
Permita el acceso al mismo y recargue la página para comenzar a trabajar.'));
            return;
        });
});

function startPhoneJs() {
    var timers = {
        'operacion': new Timer('horaO', 'minsO', 'segsO'),
        'pausa': new Timer('horaP', 'minsP', 'segsP'),
        'llamada': new Timer('horaC', 'minsC', 'segsC'),
        // 'timer_total' = new Timer('horaT', 'minsT', 'segsT');
    };
    var agent_id = $('#idagt').val();
    var sipExtension = $('#sipExt').val();
    var sipSecret = $('#sipSec').val();
    var max_session_age = $('#max_session_age').val();
    var video_domain = $('#video_domain').val();

    var oml_api = new OMLAPI();

    click2call = new Click2CallDispatcher(oml_api, agent_id);
    keep_alive_sender = new KeepAliveSender(max_session_age);
    phone_controller = new PhoneJSController(
        agent_id, sipExtension, sipSecret, timers, click2call, keep_alive_sender, video_domain);

    subscribirEventosBotonesGenerales(oml_api, agent_id, timers);
    subscribirEventosBotonesOtrosMedios(oml_api);

    timers.operacion.start();

    window.addEventListener('beforeunload', preventLeaveWithoutLogoff);
}

function subscribirEventosBotonesGenerales(oml_api, agent_id) {

    $('#logout').click(function () {
        window.removeEventListener('beforeunload', preventLeaveWithoutLogoff);
    });
}

function preventLeaveWithoutLogoff(event) {
    // Cancel the event as stated by the standard.
    event.preventDefault();
    phone_controller.hangUp();
    // Chrome requires returnValue to be set.
    event.returnValue = gettext('Recuerde cerrar la sesión antes de salir de esta pantalla.');
    return gettext('Recuerde cerrar la sesión antes de salir de esta pantalla.');
}

function subscribirEventosBotonesOtrosMedios() {
    /* Subscripcion eventos botones Facebook,  */
    // $('#facebookChat').click(function() {
    //     $('#modalFacebook').modal('show');
    // });
    /* $('#newLead').click(function () {
       $.ajax({
       type: 'get',
       url: '/contacto/nuevo',
       contentType: 'text/html',
       success: function (msg) {
       $('#crm').html(msg);
       },
       error: function (jqXHR, textStatus, errorThrown) {
       console.log('Error al ejecutar => ' + textStatus + ' - ' + errorThrown);
       }
       });
       });/**/

    // $('#webChat').click(function () {
    //     $('#modalwebChat').modal('show');
    // });

    //     $('#txtSms').click(function () {
    //         $.ajax({
    //             url: '/sms/getAll/',
    //             type: 'GET',
    //             contentType: 'application/json',
    //             success: function (jsOn) {
    //                 var row;
    //                 for (var i = 0; i < jsOn.length; i++) {
    //                     if (jsOn[i].content !== '') {
    //                         row += '<tr><td id=' + jsOn[i].id + '>' + jsOn[i].remitente + '</td><td>' + jsOn[i].content +
    //                                 '</td><td><button type='button'  class='btn btn-primary btn-xs ampliarConvers' title='Ver Conversacion' value=' + jsOn[i].remitente +
    //                                 '><span class='glyphicon glyphicon-align-left'></span></button></td></tr>';
    //                     }
    //                 }
    //                 $('#cuerpoTabla').html(row);
    //             },
    //             error: function (jqXHR, textStatus, errorThrown) {
    //                 console.log('Error al ejecutar => ' + textStatus + ' - ' + errorThrown);
    //             }
    //         });
    //         $('#modalSMS').modal('show');
    //     });

    //       $('#threadMsgsTable').DataTable({
    //         paging:false,
    //         searching:false,
    //         ordering:false,
    //         info:false,
    //         language: {
    //           'emptyTable':     'Sin datos disponibles'
    //         }
    //       });

    //       $('#messagesTable').DataTable({
    //         'language': {
    //           'lengthMenu': 'Registros por pagina _MENU_',
    //           'search': 'Buscar:',
    //           'info': 'Mostrando desde _START_ hasta _END_ de _TOTAL_ registros',
    //           'infoEmpty': 'Mostrando desde 0 hasta 0 de 0 paginas',
    //           'emptyTable':     'Sin datos disponibles',
    //           'paginate': {
    //             'first':      'Primero',
    //             'last':       'Ultimo',
    //             'next':       'Siguiente',
    //             'previous':   'Anterior'
    //           }
    //         }
    //       });

    //       $('#cuerpoTabla').on('click', '.ampliarConvers',function(e) {
    //         var nroTel = $(this).val();
    //         $('#phoneSendThread').attr('value',nroTel);
    //         var datos = {'phoneNumber':nroTel};
    //         $.ajax({
    //           url: '/smsThread/',
    //           type : 'GET',
    //           contentType: 'application/json',
    //           data: datos,
    //           success: function (jsOn) {
    //             var row;
    //             for (var i=0; i < jsOn.length; i++) {
    //               if(jsOn[i].content !== '') {
    //                 var date = jsOn[i].timestamp;
    //                 date = date.substring(5, 10);
    //                 date = date.split('-');
    //                 date = date.reverse();
    //                 date = date.join('-');
    //                 row +='<tr><td>'+jsOn[i].remitente+'</td><td>'+jsOn[i].destinatario+'</td><td>'+jsOn[i].content+'</td><td>'+date+'</td></tr>';
    //               }
    //             }
    //             $('#bodyThreadMsgTable').html(row);
    //             $('#modalConvers').modal('show');
    //           },
    //           error: function (jqXHR, textStatus, errorThrown) {
    //             console.log('Error al ejecutar => ' + textStatus + ' - ' + errorThrown);
    //           }
    //         });
    //       });
}
