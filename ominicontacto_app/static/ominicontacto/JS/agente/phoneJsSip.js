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
/* globals JsSIP phone_logger */

/**********   Constants   **********/
var UNPAUSE_CODE = '0077UNPAUSE';
var LOGIN_CODE = '0077LOGIN';
var SPECIAL_CODE_PREFIX = '0077';

var DIRECT_TRANSFER = '1';
var CONSULTATIVE_TRANSFER = '2';
var CAMPAIGN_TRANSFER = '3';

var ORIGIN_INBOUND = 'IN';
var ORIGIN_DIALER = 'DIALER-FORM';
var ORIGIN_CLICK2CALL = 'CLICK2CALL';
var ORIGIN_CLICK2CALL_PREVIEW = 'CLICK2CALLPREVIEW';
var ORIGIN_MANUAL = 'Manual-Call';
var ORIGIN_OFF_CAMPAIGN = 'withoutCamp';
var ORIGIN_AGENT_CALL = 'agentCall';

/* TODO: Revisar utilidad y borrar
var ORIGIN_IDS = {};
ORIGIN_IDS[ORIGIN_MANUAL] = 1;
ORIGIN_IDS[ORIGIN_DIALER] = 2;
ORIGIN_IDS[ORIGIN_INBOUND] = 3;
ORIGIN_IDS[ORIGIN_CLICK2CALL_PREVIEW] = 4;
ORIGIN_IDS[ORIGIN_CLICK2CALL] = 6;

ORIGIN_IDS[ORIGIN_OFF_CAMPAIGN] = 5?;    // NOTA: Ver cual es el codigo que tendran
ORIGIN_IDS[ORIGIN_AGENT_CALL] = 5?;    // NOTA: Ver cual es el codigo que tendran
/**/

var DESTINATION_AGENT = 1;
var DESTINATION_EXTERNAL = 2;

class PhoneJS {
    constructor(agent_id, sipExtension, sipSecret, KamailioHost, WebSocketPort, WebSocketHost, local_audio, remote_audio) {
        /* Config */
        this.agent_id = agent_id;
        this.sipExtension = sipExtension;
        this.sipSecret = sipSecret;
        this.KamailioHost = KamailioHost;
        this.WebSocketPort = WebSocketPort;
        this.WebSocketHost = WebSocketHost;

        /* Components / Colaborators */
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

        };
    }

    startSipSession() {
        var socket = new JsSIP.WebSocketInterface('wss://' + this.WebSocketHost + ':' + this.WebSocketPort + '/ws' );
        var config = {
            sockets: [ socket ],
            uri: 'sip:' + this.sipExtension + '@' + this.KamailioHost,
            password: this.sipSecret,
            realm: this.KamailioHost,
            hack_ip_in_contact: true,
            session_timers: false,
            register_expires: 120,
            pcConfig: {
                rtcpMuxPolicy: 'negotiate'
            }
        };

        // Inicializar Sesion de Websocket con Kamailio  'Hacer Login'
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
        this.userAgent.terminateSessions();
        this.userAgent.unregister(options);
    }

    hangUp(play_stop_sound=true) {
        if (play_stop_sound) {
            this.Sounds('', 'stop');
        }
        this.userAgent.terminateSessions();
    }

    /******  Eventos User Agent  *******/
    subscribeToUserAgentEvents() {
        var self = this;
        /* -- SIP registration events -- */
        //Connects to the WebSocket server
        this.userAgent.on('registered', function(e) { // cuando se registra la entidad SIP
            phone_logger.log('User Agent: registered');
            self.eventsCallbacks.onUserAgentRegistered.fire();
        });
        this.userAgent.on('registrationFailed', function(e) { // cuando falla la registracion
            phone_logger.log('User Agent: registrationFailed');
            self.eventsCallbacks.onUserAgentRegisterFail.fire();
        });
        this.userAgent.on('unregistered', function(e) {phone_logger.log('User Agent: unregistered');});

        /* -- WebSocket connection events -- */
        this.userAgent.on('disconnected', function(e) {
            phone_logger.log('User Agent: disconnected');
            self.eventsCallbacks.onUserAgentDisconnect.fire();
        });
        this.userAgent.on('connected', function(e) {phone_logger.log('User Agent: connected');});

        /*      --  New incoming or outgoing call event  --
           La sesion se crea al: Llamar, recibir llamada, des/Pausar, Hacer Login
           Si el originator es 'local': Llamar, des/pausar, login
           Si es 'remote': Puede ser recibir llamada, click2Call, Recibir transferencia
        */
        this.userAgent.on('newRTCSession', function(e) {
            phone_logger.log('newRTCSession');
            // Si cae una nueva session mientras hay otra activa se la rechaza.
            if (self.currentSession !== undefined){
                e.session.terminate();
                return;
            }


            self.invite_request = e.request;
            self.currentSession = e.session;
            self.session_data = new SessionData(self.currentSession,
                self.local_call,
                self.invite_request,
                e.originator);

            // Session Events
            self.currentSession.on('failed', function(e) {
                phone_logger.log('session: failed');
                self.Sounds('', 'stop');
                if (self.session_data.is_call) {
                    self.eventsCallbacks.onSessionFailed.fire();
                }
            });

            self.currentSession.on('confirmed', function(e) {
                // Aca si puedo decir que esta establecida
                phone_logger.log('session: confirmed');
                if (self.session_data.is_call) {
                    var phone_number = self.session_data.is_remote?
                        self.session_data.from :
                        self.local_call.numberToCall;
                    self.eventsCallbacks.onCallConnected.fire(phone_number);
                }
            });

            self.currentSession.on('accepted', function() { // cuando se establece una llamada
                phone_logger.log('session: accepted');
                self.Sounds('', 'stop');
            });

            // Llamada puede ser por: REGISTER - LOGIN, (UN)PAUSA, Manual
            //                        IN, Dialer, Preview, Click2Call, Transfer.
            self.currentSession.on('ended', function() { // Cuando Finaliza la llamada
                phone_logger.log('session: ended');
                if (self.session_data.is_call){
                    phone_logger.log('PhoneJS: onCallEnded');
                    self.eventsCallbacks.onCallEnded.fire();
                }
                else {
                    self.cleanLastCallData();
                }
            });
            // TODO: SACAR ESTO, SOLO ESTA PARA DEBUG
            self.currentSession.on('addstream', function() {phone_logger.log('session: addstream');});
            self.currentSession.on('succeeded', function() {phone_logger.log('session: succeeded');});

            if (self.session_data.is_remote) {
                self.Sounds('In', 'play');
                if (self.session_data.is_transfered) {
                    self.eventsCallbacks.onTransferReceipt.fire(self.session_data); // Pasar un TransferData?
                }
                else {
                    self.eventsCallbacks.onCallReceipt.fire(self.session_data); // Pasar un ReceivedCallData?
                }
            }

        });
    }

    subscribeToSessionConnectionEvents() {
        var self = this;
        this.currentSession.connection.addEventListener('addstream', function (event) {
            phone_logger.log('currentSession.connection: addstream');
            self.remote_audio.srcObject = event.stream;
        });
    }

    /* FUNCTIONS */

    putOnHold() {
        phone_logger.log('----------\nset Hold');
        this.currentSession.hold();
    }

    releaseHold() {
        phone_logger.log('----------\nrelease Hold');
        this.currentSession.unhold();
    }

    dialTransfer(transfer) {
        var self = this;
        if (transfer.is_blind) {
            this.currentSession.sendDTMF('#');
            this.currentSession.sendDTMF('#');
            if (transfer.is_to_agent) {
                if (transfer.destination) {             // TODO: Remove Line
                    this.transferTimeoutHandler = setTimeout(function() {
                        self.currentSession.sendDTMF('0');
                        self.currentSession.sendDTMF('0');
                        self.currentSession.sendDTMF('0');
                        self.currentSession.sendDTMF('0');
                        self.currentSession.sendDTMF(transfer.destination);
                        self.eventsCallbacks.onTransferDialed.fire(transfer);
                    }, 2500);
                }
            } else if (transfer.is_to_campaign) {
                if (transfer.destination) {             // TODO: Remove Line
                    this.transferTimeoutHandler = setTimeout(function() {
                        self.currentSession.sendDTMF('9');
                        self.currentSession.sendDTMF('9');
                        self.currentSession.sendDTMF('9');
                        self.currentSession.sendDTMF('9');
                        self.currentSession.sendDTMF(transfer.destination);
                        self.eventsCallbacks.onTransferDialed.fire(transfer);
                    }, 2500);
                }
            } else if (transfer.is_to_number || transfer.is_quick_contact) {
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
            this.currentSession.sendDTMF('*');
            this.currentSession.sendDTMF('2');
            if (transfer.is_to_agent) {
                if (transfer.destination) {
                    this.transferTimeoutHandler = setTimeout(function() {
                        self.currentSession.sendDTMF('1');
                        self.currentSession.sendDTMF('1');
                        self.currentSession.sendDTMF('1');
                        self.currentSession.sendDTMF('1');
                        self.currentSession.sendDTMF(transfer.destination);
                        self.eventsCallbacks.onTransferDialed.fire(transfer);
                    }, 2500);
                }
            } else if (transfer.is_to_number || transfer.is_quick_contact) {
                if (transfer.destination) {
                    i = 0;
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
        this.currentSession.sendDTMF('*');
        this.currentSession.sendDTMF('1');
    }

    confer () {
        this.currentSession.sendDTMF('*');
        this.currentSession.sendDTMF('3');
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
        this.Sounds('', 'stop');
    }

    refuseCall() {
        this.hangUp(false);
        this.Sounds('', 'stop');
    }

    ///----------

    Sounds(callType, action) {
        // Los 'catch' son por si se da el caso de que el agente no haya interactuado con la pagina.
        var ring = null;
        if (action === 'play') {
            if (callType === 'In') {
                ring = document.getElementById('RingIn');
                ring.play().catch(function() { });
                ring.onended = function() {
                    ring.play().catch(function() { });
                };
            } else if (callType === 'Out') {
                ring = document.getElementById('RingOut');
                ring.play().catch(function() { });
                ring.onended = function() {
                    ring.play().catch(function() { });
                };
            } else if (callType === 'Welcome') {
                ring = document.getElementById('Welcome');
                ring.play().catch(function() { });
                ring.onended = function() {
                    ring.pause();
                };
            }
            else {
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
        this.currentSession = undefined;
        this.session_data = undefined;
        this.local_call = undefined;
    }

}

class LocalCall {
    constructor (numberToCall) {
        this.numberToCall = numberToCall;
        this.is_unpause = numberToCall == UNPAUSE_CODE;
        this.is_login = numberToCall == LOGIN_CODE;
        this.is_pause = !this.is_unpause && !this.is_login &&
                        numberToCall.startsWith(SPECIAL_CODE_PREFIX);

        // NOTA: En caso de que se agreguen maneras locales de generar llamadas podria ser asi
        // this.is_other_internal_call = !numberToCall.startsWith(SPECIAL_CODE_PREFIX);
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
        if (this.is_remote) {
            this.remote_call = this.setRemoteCallInfo(invite_request);
        }
    }

    setRemoteCallInfo(invite_request) {
        var call_data = {};
        if (invite_request.headers.Idcamp)
            call_data.id_campana = invite_request.headers.Idcamp[0].raw;
        if (invite_request.headers.Omlcamptype)
            call_data.campana_type = invite_request.headers.Omlcamptype[0].raw;
        if (invite_request.headers.Omloutnum)
            call_data.telefono = invite_request.headers.Omloutnum[0].raw;
        if (this.is_remote && invite_request.headers.Omlcallid) {
            call_data.call_id = invite_request.headers.Omlcallid[0].raw;
        }
        if (invite_request.headers.Omlcalltypeidtype)
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
        if (invite_request.headers.Omldialerid)
            call_data.dialer_id = invite_request.headers.Omldialerid[0].raw;

        // For outside campaign calls
        if (invite_request.headers.withoutCamp)
            call_data.outside_campaign = true;

        // Extra ICS Headers.
        if (invite_request.headers.Ics)
            call_data.ics = invite_request.headers.Ics[0].raw;
        if (invite_request.headers.Idcontactics)
            call_data.id_contacto_ics = invite_request.headers.Idcontactics[0].raw;
        if (invite_request.headers.Namecontactics)
            call_data.nombre_contacto_ics = invite_request.headers.Namecontactics[0].raw;

        if (invite_request.headers.Omlvideo){
            call_data.video_channel = invite_request.headers.Omlvideo[0].raw;
        }


        // Campaign agent behaviour configuration
        if (invite_request.headers['Force-Disposition']){
            call_data.force_disposition = invite_request.headers['Force-Disposition'][0].raw;
        }
        if (invite_request.headers['Auto-Unpause']){
            call_data.auto_unpause = invite_request.headers['Auto-Unpause'][0].raw;
        }
        if (this.is_inbound && invite_request.headers['Auto-Attend-Inbound']){
            call_data.auto_attend = invite_request.headers['Auto-Attend-Inbound'][0].raw;
        }
        if (this.is_dialer && invite_request.headers['Auto-Attend-Dialer']){
            call_data.auto_attend = invite_request.headers['Auto-Attend-Dialer'][0].raw;
        }

        this.setDialplanCallData(invite_request.headers, call_data);
        return call_data;
    }

    setDialplanCallData(headers, call_data){
        for (var header in headers) {
            if (header.startsWith('Omlcrm')) {
                var value = headers[header][0].raw;
                call_data[header] = value;
            }
        }
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
            return 'Transf. directa';
        case CONSULTATIVE_TRANSFER:
            return 'Transf. asistida';
        case CAMPAIGN_TRANSFER:
            return 'Transf. a campaña';
        default:
            return undefined;
        }
    }

    get from_agent_name() {
        if (this.invite_request.headers.Omlfromagent)
            return this.invite_request.headers.Omlfromagent[0].raw;
        return '';
    }

    get origin() {
        // IN, DIALER-FORM, CLICK2CALLPREVIEW, CLICK2CALL
        if (this.invite_request.headers.Origin) {
            return this.invite_request.headers.Origin[0].raw;
        }
        else
            return undefined;
    }

    get is_dialer() {
        return this.origin != undefined && this.origin.indexOf('DIALER') == 0;
    }
    get is_click2call() {
        return this.origin != undefined && this.origin.indexOf('CLICK2CALL') == 0;
    }
    get is_inbound() {
        return this.origin == 'IN';
    }

    get is_off_campaign() {
        if (this.origin == ORIGIN_OFF_CAMPAIGN)
            return true;
        if (this.campaign_id == '0' || this.remote_call.campana_type == '0')
            return true;
        return false;
    }

    get is_from_agent(){
        return this.origin == ORIGIN_AGENT_CALL;
    }

    get contact_id() {
        if (this.invite_request.headers.Idcliente) {
            return this.invite_request.headers.Idcliente[0].raw;
        }
        else
            return undefined;
    }

    get campaign_id() {
        if (this.invite_request.headers.Idcamp) {
            return this.invite_request.headers.Idcamp[0].raw;
        }
        else
            return undefined;
    }

    get from() {
        if (this.is_from_agent) {
            var from_agent_name = this.from_agent_name;
            if (from_agent_name)
                return from_agent_name;
        }
        return this.remote_call.telefono;
    }

    get is_call() {
        return this.is_off_campaign || this.is_remote;
    }
}
