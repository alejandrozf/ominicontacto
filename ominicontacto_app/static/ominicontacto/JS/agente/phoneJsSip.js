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

/* Requirements:  * /
    - config.js
/* ----------------*/


var test;

/**********   Constants   **********/
var UNPAUSE_CODE = '0077UNPAUSE';
var LOGIN_CODE = '0077LOGIN';
var SPECIAL_CODE_PREFIX = "0077";

var DIRECT_TRANSFER = "1";
var CONSULTATIVE_TRANSFER = "2";
var CAMPAIGN_TRANSFER = "3";

var ORIGIN_INBOUND = 'IN';
var ORIGIN_DIALER = 'DIALER-FORM';
var ORIGIN_CLICK2CALL = 'CLICK2CALL';
var ORIGIN_CLICK2CALL_PREVIEW = 'CLICK2CALLPREVIEW';
var ORIGIN_MANUAL = 'Manual-Call';
var ORIGIN_INTERNAL = 'Internal';

var ORIGIN_IDS = {};
ORIGIN_IDS[ORIGIN_DIALER] = 2;
ORIGIN_IDS[ORIGIN_INBOUND] = 3;
ORIGIN_IDS[ORIGIN_CLICK2CALL] = 4;
ORIGIN_IDS[ORIGIN_CLICK2CALL_PREVIEW] = 4;
ORIGIN_IDS[ORIGIN_MANUAL] = 1;

/* NOTA: Ver si es necesario */
ORIGIN_IDS[ORIGIN_INTERNAL] = 5;    // NOTA: Ver cual es el codigo que tendran

class PhoneJS {
    constructor(agent_id, sipExtension, sipSecret, KamailioHost, WebSocketPort, WebSocketHost,
                local_audio, remote_audio) {
        /* Config */
        this.agent_id = agent_id
        this.sipExtension = sipExtension;
        this.sipSecret = sipSecret;
        this.KamailioHost = KamailioHost;
        this.WebSocketPort = WebSocketPort;
        this.WebSocketHost = WebSocketHost;

        /* Components / Colaborators */
        this.oml_api = new OMLAPI();
        this.userAgent = undefined;
        this.currentSession = undefined;

        this.local_audio = local_audio;
        this.remote_audio = remote_audio;

        /* Local Variables */
        this.callTimeoutHandler = undefined;
        this.transferTimeoutHandler = undefined;

        /* eventsCallbacks */
        this.eventsCallbacks = {
            onUserAgentRegistered: $.Callbacks(),
            onUserAgentDisconnect: $.Callbacks(),
            onUserAgentRegisterFail: $.Callbacks(),
            onAgentLogged: $.Callbacks(),
            onAgentLoginFail: $.Callbacks(),

            onAgentPaused: $.Callbacks(),
            onAgentPauseFail: $.Callbacks(),
            onAgentUnpaused: $.Callbacks(),
            onAgentUnPauseFail: $.Callbacks(),

            onCallConnected:  $.Callbacks(),
            onOutCallFailed: $.Callbacks(),
            onCallEnded: $.Callbacks(),

            onCallReceipt: $.Callbacks(),
            onTransferReceipt: $.Callbacks(),

            onTransferDialed: $.Callbacks(),

            onSessionFailed: $.Callbacks(),

        }
    }

    startSipSession() {
        var socket = new JsSIP.WebSocketInterface('wss://' + this.WebSocketHost + ':' + this.WebSocketPort + '/ws');
        var config = {
                sockets: [ socket ],
                uri: "sip:" + this.sipExtension + "@" + this.KamailioHost,
                password: this.sipSecret,
                realm: this.KamailioHost,
                hack_ip_in_contact: true,
                session_timers: false,
                register_expires: 120,
                pcConfig: {
                    rtcpMuxPolicy: 'negotiate'
                }
            };

        // Inicializar Sesion de Websocket con Kamailio  "Hacer Login"
        if (this.sipExtension && this.sipSecret) {
            this.userAgent = new JsSIP.UA(config);
            this.userAgent.start();
            this.subscribeToUserAgentEvents();
        }
    }

    logout() {
        var options = {
            all: true
        };
        this.userAgent.unregister(options);
    }

    hangUp(play_stop_sound=true) {
        if (play_stop_sound) {
            this.Sounds("", "stop");
        }
        this.userAgent.terminateSessions();
    }

    /******  Eventos User Agent  *******/
    subscribeToUserAgentEvents() {
        var self = this;
        /* -- SIP registration events -- */
        //Connects to the WebSocket server
        this.userAgent.on("registered", function(e) { // cuando se registra la entidad SIP
            phone_logger.log('User Agent: registered');
            self.eventsCallbacks.onUserAgentRegistered.fire();
        });
        this.userAgent.on("registrationFailed", function(e) { // cuando falla la registracion
            phone_logger.log('User Agent: registrationFailed');
            self.eventsCallbacks.onUserAgentRegisterFail.fire();
        });
        this.userAgent.on("unregistered", function(e) {phone_logger.log('User Agent: unregistered');});

        /* -- WebSocket connection events -- */
        this.userAgent.on("disconnected", function(e) {
            phone_logger.log('User Agent: disconnected');
            self.eventsCallbacks.onUserAgentDisconnect.fire();
        });
        this.userAgent.on("connected", function(e) {phone_logger.log('User Agent: connected');});

        /*      --  New incoming or outgoing call event  --
           La sesion se crea al: Llamar, recibir llamada, des/Pausar, Hacer Login
           Si el originator es 'local': Llamar, des/pausar, login
           Si es 'remote': Puede ser recibir llamada, click2Call, Recibir transferencia
        */
        this.userAgent.on("newRTCSession", function(e) {
            phone_logger.log('newRTCSession');
            // TODO: En realidad pueden caer varias sessiones a la vez.
            //       Si ya existe alguna debería rechazarse la siguiente hasta saber manejar
            //       multiples
            self.invite_request = e.request;
            self.currentSession = e.session;
            self.session_data = new SessionData(self.currentSession,
                                                self.local_call,
                                                self.invite_request,
                                                e.originator);

            if (self.session_data.is_remote) {
                self.Sounds("In", "play");
                if (self.session_data.is_transfered) {
                    self.eventsCallbacks.onTransferReceipt.fire(self.session_data); // Pasar un TransferData?
                }
                else {
                    self.eventsCallbacks.onCallReceipt.fire(self.session_data); // Pasar un ReceivedCallData?
                }
            }

            // Session Events
            self.currentSession.on("failed", function(e) {
                phone_logger.log('session: failed');
                self.Sounds("", "stop");
                if (self.session_data.is_call) {
                    self.eventsCallbacks.onSessionFailed.fire();
                }
            });

            self.currentSession.on("confirmed", function(e) {
                // Aca si puedo decir que esta establecida
                phone_logger.log('session: confirmed');
                if (self.session_data.is_call) {
                    var phone_number = self.session_data.is_remote?
                                            self.session_data.from :
                                            self.local_call.numberToCall;
                    self.eventsCallbacks.onCallConnected.fire(phone_number);
                }
            });

            self.currentSession.on("accepted", function() { // cuando se establece una llamada
                phone_logger.log('session: accepted');
                self.Sounds("", "stop");
            });

            // Llamada puede ser por: REGISTER - LOGIN, (UN)PAUSA, Manual
            //                        IN, Dialer, Preview, Click2Call, Transfer.
            self.currentSession.on("ended", function() { // Cuando Finaliza la llamada
                phone_logger.log('session: ended');
                if (self.session_data.is_call){
                    phone_logger.log('PhoneJS: onCallEnded');
                    self.eventsCallbacks.onCallEnded.fire();
                }
            });
            // TODO: SACAR ESTO, SOLO ESTA PARA DEBUG
            self.currentSession.on("addstream", function() {phone_logger.log('session: addstream')});
            self.currentSession.on("succeeded", function() {phone_logger.log('session: succeeded')});
        });
    };

    subscribeToSessionConnectionEvents() {
        var self = this;
        this.currentSession.connection.addEventListener('addstream', function (event) {
            phone_logger.log('currentSession.connection: addstream');
            self.remote_audio.srcObject = event.stream;
        });
    }

    /* FUNCTIONS */

    makeLoginCall(pause_id) {
        phone_logger.log("----------\nLogin Call");
        this.makeCall(LOGIN_CODE);
    }

    makePauseCall(pause_id) {
        phone_logger.log("---------- \nPause Call");
        this.makeCall(SPECIAL_CODE_PREFIX + pause_id);
    }

    makeUnpauseCall() {
        phone_logger.log("----------\nUnpause Call");
        this.makeCall(UNPAUSE_CODE);
    }

    putOnHold() {
        phone_logger.log("----------\nset Hold");
        this.currentSession.hold();
    }

    releaseHold() {
        phone_logger.log("----------\nrelease Hold");
        this.currentSession.unhold();
    }

    // TODO: En principio sólo se va a usar para Login, Pause y Unpause.
    //       Más adelante tal vez se use para llamadas fuera de campaña entre agentes.
    makeCall(numberToCall) {
        var self = this;
        this.local_call = new LocalCall(numberToCall);
        phone_logger.log('makeCall: ' + numberToCall);

        // Luego de 60 segundos sin respuesta, stop al ringback y cuelga discado
        // TODO: Cancelar el timeout una vez recibida respuesta ('accepted', failed', )
        this.callTimeoutHandler = setTimeout(function() {self.hangUp();}, 61000);

        var eventHandlers = {
            // TODO: Verificar si no hay otros posibles eventos.
            // Asegurarse de que cualquier finalizacion termina llamando al clearTimeout(...)
            'confirmed': function(e) {
                phone_logger.log('makeCall: confirmed');
                clearTimeout(self.callTimeoutHandler);
                if (self.local_call.is_unpause) {
                    self.eventsCallbacks.onAgentUnpaused.fire();
                }
                else if (self.local_call.is_login) {
                    self.eventsCallbacks.onAgentLogged.fire();
                }
                else if (self.local_call.is_pause) {
                    self.eventsCallbacks.onAgentPaused.fire();
                }
            },/**/
            'addstream': function(e) {
                phone_logger.log('makeCall: addstream');
                clearTimeout(self.callTimeoutHandler);
            },
            'succeeded': function(e) {
                phone_logger.log('makeCall: succeeded');
                clearTimeout(self.callTimeoutHandler);
            },
            'failed': function(data) {
                phone_logger.log('makeCall: failed - ' + numberToCall);
                clearTimeout(self.callTimeoutHandler);
                if (self.local_call.is_login) {
                    self.eventsCallbacks.onAgentLoginFail.fire(self);
                } else if (self.local_call.is_unpause) {
                    self.eventsCallbacks.onAgentUnPauseFail.fire(self);
                } else if (self.local_call.is_pause) {
                    self.eventsCallbacks.onAgentPauseFail.fire(self);
                }
                // TODO: Este caso no se va a dar más para llamadas de campañas
                // Probablemente quede solo para llamadas internas entre agentes 
                else {
                    // (self.local_call.is_internal_call)
                    self.eventsCallbacks.onOutCallFailed.fire(data.cause);
                    if (data.cause === JsSIP.C.causes.BUSY) {
                        self.Sounds("", "stop");
                        self.Sounds("", "play");
                    }
                }
            },
            // TODO: SACAR ESTO, SOLO ESTA PARA DEBUG
            'accepted': function(asd) { phone_logger.log('makeCall: accepted'); },
            'ended': function(asd) { phone_logger.log('makeCall: ended'); },
        };
        var opciones = {
            'eventHandlers': eventHandlers,
            'mediaConstraints': {
                'audio': true,
                'video': false
            },
            pcConfig: {
                rtcpMuxPolicy: 'negotiate'
            },
        };

        // Finalmente Mando el invite/llamada
        this.userAgent.call('sip:' + numberToCall + '@' + this.KamailioHost, opciones);
        this.subscribeToSessionConnectionEvents();
    }

    dialTransfer(transfer) {
        var self = this;
        if (transfer.is_blind) {
            this.currentSession.sendDTMF("#");
            this.currentSession.sendDTMF("#");
            if (transfer.is_to_agent) {
                if (transfer.destination) {             // TODO: Remove Line
                    this.transferTimeoutHandler = setTimeout(function() {
                        self.currentSession.sendDTMF("0");
                        self.currentSession.sendDTMF("0");
                        self.currentSession.sendDTMF("0");
                        self.currentSession.sendDTMF("0");
                        self.currentSession.sendDTMF(transfer.destination);
                        self.eventsCallbacks.onTransferDialed.fire(transfer);
                    }, 2500);
                }
            } else if (transfer.is_to_campaign) {
                if (transfer.destination) {             // TODO: Remove Line
                    this.transferTimeoutHandler = setTimeout(function() {
                        self.currentSession.sendDTMF("9");
                        self.currentSession.sendDTMF("9");
                        self.currentSession.sendDTMF("9");
                        self.currentSession.sendDTMF("9");
                        self.currentSession.sendDTMF(transfer.destination);
                        self.eventsCallbacks.onTransferDialed.fire(transfer);
                    }, 2500);
                }
            } else if (transfer.is_to_number) {
                if (transfer.destination) {
                    var i = 0;
                    this.transferTimeoutHandler = setTimeout(function() {
                        while (i < transfer.destination.length) {
                            self.currentSession.sendDTMF(transfer.destination[i]);
                            i++;
                        }
                        self.eventsCallbacks.onTransferDialed.fire(transfer);
                    }, 2500);
                }
            }
        } else if (transfer.is_consultative) {
            this.currentSession.sendDTMF("*");
            this.currentSession.sendDTMF("2");
            if (transfer.is_to_agent) {
                if (transfer.destination) {
                    this.transferTimeoutHandler = setTimeout(function() {
                        self.currentSession.sendDTMF("1");
                        self.currentSession.sendDTMF("1");
                        self.currentSession.sendDTMF("1");
                        self.currentSession.sendDTMF("1");
                        self.currentSession.sendDTMF(transfer.destination);
                        self.eventsCallbacks.onTransferDialed.fire(transfer);
                    }, 2500);
                }
            } else if (transfer.is_to_number) {
                if (transfer.destination) {
                    var i = 0;
                    this.transferTimeoutHandler = setTimeout(function() {
                        while (i < transfer.destination.length) {
                            self.currentSession.sendDTMF(transfer.destination[i]);
                            i++;
                        }
                        self.eventsCallbacks.onTransferDialed.fire(transfer);
                    }, 2500);
                }
            }
        }
    }

    cancelDialTransfer() {
        clearTimeout(this.transferTimeoutHandler);
    }

    endTransfer () {
        this.currentSession.sendDTMF("*");
        this.currentSession.sendDTMF("1");
    }

    acceptCall() {
        var options = {
            'mediaConstraints': {
                'audio': true,
                'video': false
            }
        };
        this.currentSession.answer(options);
        this.subscribeToSessionConnectionEvents();
        this.Sounds("", "stop");
    }

    refuseCall() {
        this.hangUp(false);
        this.Sounds("", "stop");
    }

    ///----------

    Sounds(callType, action) {
        // Los "catch" son por si se da el caso de que el agente no haya interactuado con la pagina.
        var ring = null;
        if (action === "play") {
            if (callType === "In") {
                ring = document.getElementById('RingIn');
                ring.play().catch(function() { });
                ring.onended = function() {
                    ring.play().catch(function() { });
                };
            } else if (callType === "Out") {
                ring = document.getElementById('RingOut');
                ring.play().catch(function() { });
                ring.onended = function() {
                    ring.play().catch(function() { });
                };
            } else {
                ring = document.getElementById('RingBusy');
                ring.play().catch(function() { });
            }
        } else {
            ring = document.getElementById('RingIn');
            ring.pause();
            ring = document.getElementById('RingOut');
            ring.pause();
            ring = document.getElementById('RingBusy');
            ring.pause();
        }
    }

    cleanLastCallData() {
        self.currentSession = undefined;
        self.session_data = undefined;
        self.local_call = undefined;
    }

};

class LocalCall {
    constructor (numberToCall) {
        this.numberToCall = numberToCall;
        this.is_unpause = numberToCall == UNPAUSE_CODE;
        this.is_login = numberToCall == LOGIN_CODE;
        this.is_pause = !this.is_unpause && !this.is_login &&
                        numberToCall.startsWith(SPECIAL_CODE_PREFIX);
        // TODO: Ver utilidad en caso de llamada entre agentes.
        // this.is_internal_call = !numberToCall.startsWith(SPECIAL_CODE_PREFIX);
    }
}

/* TODO: Esta SessionData es muy especifica para el PhoneJsController de OML.
 *       Ver de generalizarla y extenderla para cada Controller particular
/**/
class SessionData {
    constructor (session, local_call, invite_request, originator) {
        this.RTCSession = session;
        this.local_call = local_call;
        this.invite_request = invite_request;
        this.originator = originator;
        // TODO: En un futuro todas seran inbound. local_call y remote_call pueden pasar a
        // ser call nomas
        if (this.is_remote) {
            this.remote_call = this.setRemoteCallInfo(invite_request);
        }
    }

    setRemoteCallInfo(invite_request) {
        var call_data = {}
        call_data.id_campana = invite_request.headers.Idcamp[0].raw;
        call_data.campana_type = invite_request.headers.Omlcamptype[0].raw;
        call_data.telefono = invite_request.headers.Omloutnum[0].raw;
        if (!this.is_internal_call) {
            call_data.call_id = invite_request.headers.Omlcallid[0].raw;
        }
        call_data.call_type = invite_request.headers.Omlcalltypeidtype[0].raw;
        if (invite_request.headers.Idcliente)
            call_data.id_contacto = invite_request.headers.Idcliente[0].raw;
        else
            call_data.id_contacto = '';
        if (invite_request.headers.Omlrecfilename)
            call_data.rec_filename = invite_request.headers.Omlrecfilename[0].raw;
        else
            call_data.rec_filename = '';
        if (invite_request.headers.Omlcallwaitduration)
            call_data.call_wait_duration = invite_request.headers.Omlcallwaitduration[0].raw;
        else
            call_data.call_wait_duration = '';

        // Extra ICS Headers.
        if (invite_request.headers.Ics)
            call_data.ics = invite_request.headers.Ics[0].raw;
        if (invite_request.headers.Idcontactics)
            call_data.id_contacto_ics = invite_request.headers.Idcontactics[0].raw;
        if (invite_request.headers.Namecontactics)
            call_data.nombre_contacto_ics = invite_request.headers.Namecontactics[0].raw;

        return call_data;
    }

    get is_remote () {
        return this.originator == 'remote';
    }

    get is_transfered () {
        return false || this.invite_request.headers.Transfer;
    }

    get transfer_type () {
        // Directa, asistida, campaña
        return this.invite_request.headers.Transfer[0].raw;
    }

    get transfer_type_str () {
        switch (this.transfer_type) {
            case DIRECT_TRANSFER:
                return "Transf. directa";
                break;
            case CONSULTATIVE_TRANSFER:
                return "Transf. asistida";
                break;
            case CAMPAIGN_TRANSFER:
                return "Transf. a campaña";
                break;
        }
    }

    get is_internal_call () {
        return this.originator == 'local' &&
               this.local_call !== undefined &&
               this.local_call.is_internal_call;
    }

    get origin() {
        // IN, DIALER-FORM, CLICK2CALLPREVIEW, CLICK2CALL
        if (this.invite_request.headers.Origin) {
            return this.invite_request.headers.Origin[0].raw;
        }
    }

    get is_dialer() {
        return this.origin.indexOf('DIALER') == 0;
    }
    get is_click2call() {
        return this.origin.indexOf('CLICK2CALL') == 0;
    }
    get is_inbound() {
        return this.origin == 'IN';
    }

    get contact_id() {
        if (this.invite_request.headers.Idcliente) {
            return this.invite_request.headers.Idcliente[0].raw;
        }
    }

    get campaign_id() {
        if (this.invite_request.headers.Idcamp) {
            return this.invite_request.headers.Idcamp[0].raw;
        }
    }

    get from() {
        var fromUser = this.invite_request.headers.From[0].raw;
        var endPos = fromUser.indexOf("@");
        var startPos = fromUser.indexOf(":");
        return fromUser.substring(startPos + 1, endPos);
    }

    get call_type_id() {
        if (this.is_internal_call)
            return ORIGIN_IDS[ORIGIN_INTERNAL];
        return ORIGIN_IDS[this.origin];
    }

    get is_call() {
        return this.is_internal_call || this.is_remote;
    }
}
