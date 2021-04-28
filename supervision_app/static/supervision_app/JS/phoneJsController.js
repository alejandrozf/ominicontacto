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

/* Requirements:            */
/*      - config.js         */
/*      - phoneJsSip.js     */
/*      - phoneJsFSM.js     */

/* global PhoneFSM PhoneJS PhoneJSView JsSIP */
/* global spied_agent_name interpolate */
/* global gettext KamailioHost WebSocketPort WebSocketHost*/

class PhoneJSController {
    // Connects PhoneJS with a PhoneJSView.
    constructor(supervisor_id, sipExtension, sipSecret) {
        this.view = new PhoneJSView();
        this.phone = new PhoneJS(supervisor_id, sipExtension, sipSecret,
            KamailioHost, WebSocketPort, WebSocketHost,
            this.view.local_audio, this.view.remote_audio);
        this.phone_fsm = new PhoneFSM();

        this.subscribeToViewEvents();
        this.subscribeToFSMEvents();
        this.subscribeToPhoneEvents();

        this.phone_fsm.start();
    }

    subscribeToViewEvents() {
        var self = this;

        this.view.hangUpButton.click(function() {
            self.phone.hangUp();
        });

        // TODO: Ver si hace falta hacer logout cuando se va de supervision
        $('#logout').click(function() {
            self.phone.logout();
        });

    }

    subscribeToFSMEvents() {
        var self = this;
        this.phone_fsm.observe({
            onInitial: function() {
                self.view.setSipStatus('NO_ACCOUNT');
                self.view.setUserStatus('label label-success', gettext('Desconectado'));
                self.view.setStateInputStatus('Initial');
                self.phone.startSipSession();
            },
            onEnd: function() {
                self.view.setUserStatus('label label-success', gettext('Desconectado'));
                self.view.setStateInputStatus('End');
            },
            onReady: function() {
                phone_logger.log('FSM: onReady');
                self.view.setUserStatus('label label-success', gettext('Conectado'));
                self.view.setStateInputStatus('Ready');
            },
            onPaused: function() {
                phone_logger.log('FSM: onPaused');
                self.view.setUserStatus('label label-danger', self.pause_manager.pause_name);
                self.view.setStateInputStatus('Paused');
            },
            onCalling: function() {
                phone_logger.log('FSM: onCalling');
                self.view.setUserStatus('label label-success', gettext('Llamando'));
                self.view.setStateInputStatus('Calling');
            },
            onOncall: function() {
                phone_logger.log('FSM: onOncall');
                self.view.setUserStatus('label label-success', gettext('En llamado'));
                self.view.setStateInputStatus('OnCall');
            },
            onDialingtransfer: function() {
                phone_logger.log('FSM: onDialingTransfer');
                self.view.setUserStatus('label label-success', gettext('Transfiriendo'));
                self.view.setStateInputStatus('DialingTransfer');
            },
            onTransfering: function() {
                phone_logger.log('FSM: onTransfering');
                self.view.setUserStatus('label label-success', gettext('Transfiriendo'));
                self.view.setStateInputStatus('Transfering');
            },
            onReceivingcall: function() {
                phone_logger.log('FSM: onReceivingCall');
                self.view.setUserStatus('label label-success', gettext('Recibiendo llamado'));

                self.view.setStateInputStatus('ReceivingCall');
            },
            onOnhold: function() {
                phone_logger.log('FSM: onOnHold');
                self.view.setUserStatus('label label-success', gettext('En espera'));
                self.view.setStateInputStatus('OnHold');
            },
        });
    }

    subscribeToPhoneEvents() {
        var self = this;

        /** User Agent **/
        this.phone.eventsCallbacks.onUserAgentRegistered.add(function () {
            self.phone_fsm.registered();
            self.phone_fsm.logToAsteriskOk();
            self.view.setSipStatus('REGISTERED');
            self.view.setCallStatus(gettext('Supervisor registrado'), 'orange');
        });

        this.phone.eventsCallbacks.onUserAgentRegisterFail.add(function () {
            self.view.setSipStatus('REGISTER_FAIL');
            self.phone_fsm.failedRegistration();
        });

        this.phone.eventsCallbacks.onUserAgentDisconnect.add(function () {
            self.view.setSipStatus('NO_SIP');
            self.phone.cleanLastCallData();
            // TODO: Definir acciones a tomar.
        });

        /** Calls **/
        this.phone.eventsCallbacks.onCallReceipt.add(function(session_data) {
            self.phone_fsm.receiveCall();
            self.manageCallReceipt(session_data);
        });

        this.phone.eventsCallbacks.onSessionFailed.add(function() {
            // Se dispara al fallar Call Sessions
            phone_logger.log('Volviendo a Ready o a Pause:');
            if (self.phone_fsm.state == 'ReceivingCall') {
                phone_logger.log('Desde ReceivingCall!');
                self.phone_fsm.refuseCall();
                $('#modalReceiveCalls').modal('hide');
            } else if (self.phone_fsm.state == 'OnCall') {
                phone_logger.log('Desde OnCall!');
                self.phone_fsm.endCall();
                self.phone.cleanLastCallData();
            } else if (self.phone_fsm.state == 'Transfering') {
                phone_logger.log('Desde Transfering!');
                self.phone_fsm.transferAccepted();
                self.phone.cleanLastCallData();
            } else if (self.phone_fsm.state == 'Calling') {
                phone_logger.log('Desde Calling!');
                self.phone_fsm.endCall();
                self.phone.cleanLastCallData();
            }
            else { phone_logger.log('No se sabe volver desde: ' + self.phone_fsm.state); }

        });

        // Outbound Call
        this.phone.eventsCallbacks.onCallConnected.add(function(numberToCall) {
            phone_logger.log('onCallConnected from: ' + self.phone_fsm.state);
            var message = '';
            if (numberToCall == undefined && spied_agent_name != undefined){
                message = interpolate(gettext('Conectado a %(fromUser)s'), {fromUser:spied_agent_name}, true);
            }
            else {
                message = interpolate(gettext('Conectado a %(fromUser)s'), {fromUser:numberToCall}, true);
            }
            self.view.setCallStatus(message, 'orange');
            if (self.phone_fsm.state == 'Calling') {
                self.phone_fsm.connectCall();
            }
            else {
                // Analizar si hace falta atender el evento si es inbound.
            }
        });

        this.phone.eventsCallbacks.onOutCallFailed.add(function(cause) {
            self.setCallFailedStatus(cause);
            // El fallo de llamada saliente tambien dispara el onSessionFailed
        });

        this.phone.eventsCallbacks.onCallEnded.add(function() {
            self.view.setCallStatus(gettext('Disponible'), 'black');
            self.phone_fsm.endCall();
            self.callEndTransition();
        });
    }

    callEndTransition() {
        this.phone.cleanLastCallData();
    }

    setCallFailedStatus(cause) {
        switch(cause){
        case JsSIP.C.causes.BUSY:
            this.view.setCallStatus(gettext('Ocupado, intente maás tarde'), 'orange');
            break;
        case JsSIP.C.causes.REJECTED:
            this.view.setCallStatus(gettext('Rechazado, intente maás tarde'), 'orange');
            break;
        case JsSIP.C.causes.UNAVAILABLE:
            this.view.setCallStatus(gettext('No disponible, contacte a su administrador'), 'red');
            break;
        case JsSIP.C.causes.NOT_FOUND:
            this.view.setCallStatus(gettext('Error, verifique el número marcado'), 'red');
            break;
        case JsSIP.C.causes.AUTHENTICATION_ERROR:
            this.view.setCallStatus(
                gettext('Error de autenticación, contacte a su administrador'), 'red');
            break;
        case JsSIP.C.causes.MISSING_SDP:
            this.view.setCallStatus(gettext('Error, Falta SDP'), 'red');
            break;
        case JsSIP.C.causes.ADDRESS_INCOMPLETE:
            this.view.setCallStatus(gettext('Dirección incompleta'), 'red');
            break;
        case JsSIP.C.causes.SIP_FAILURE_CODE:
            this.view.setCallStatus(
                gettext('Servicio no disponible, contacte a su administrador'), 'red');
            break;
        case JsSIP.C.causes.USER_DENIED_MEDIA_ACCESS:
            this.view.setCallStatus(
                gettext('Error WebRTC: El usuario no permite acceso al medio'), 'red');
            break;
        default:
            this.view.setCallStatus(gettext('Error: Llamado fallido'), 'red');
        }
    }

    manageCallReceipt(session_data) {
        this.phone_fsm.acceptCall();
        this.phone.acceptCall();
        var message = gettext('Conectado a llamada');
        this.view.setCallStatus(message, 'orange');
        // TODO: VER que hacer con el session_data
    }

    is_on_call() {
        return this.phone.currentSession !== undefined;
    }

}

class PhoneJsLogger {
    constructor(log_to_console) {
        this.log_to_console = log_to_console;
    }
    log(text){
        if (this.log_to_console)
            console.log(text);
    }
}
var phone_logger = new PhoneJsLogger(true);
