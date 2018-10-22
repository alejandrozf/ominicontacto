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
/*      - omlAPI.js         */
/*      - phoneJsSip.js     */
/*      - phoneJsFSM.js     */
/*      - phoneJsSip.js     */
/*      - click2Call.js     */

ACW_PAUSE_ID = '0';
ACW_PAUSE_NAME = 'ACW';


class PhoneJSController {
    // Connects PhoneJS with a PhoneJSView.
    constructor(agent_id, sipExtension, sipSecret, timers, click_2_call_dispatcher) {
        this.oml_api = new OMLAPI();
        this.view = new PhoneJSView();
        this.timers = timers;
        this.phone = new PhoneJS(agent_id, sipExtension, sipSecret, KamailioIp, KamailioPort,
                                 this.view.local_audio, this.view.remote_audio);
        this.phone_fsm = new PhoneFSM();
        this.agent_config = new AgentConfig();
        this.pause_manager = new PauseManager();
        this.click_2_call_dispatcher = click_2_call_dispatcher;

        /* Local Variables */
        this.agent_id = agent_id;
        this.lastDialedNumber = undefined;
        this.call_after_campaign_selection = false;
        this.manual_campaign_id = undefined;
        this.campaign_id = null;
        this.campaign_type = null;
        this.campaign_name = '';
        /*-----------------*/


        this.subscribeToViewEvents();
        this.subscribeToFSMEvents();
        this.subscribeToPhoneEvents();

        this.oml_api.getAgentes(this.view.cargarAgentes);
        this.oml_api.getCampanasActivas(this.view.cargarCampanasActivas);
        this.phone_fsm.start();
    }

    subscribeToViewEvents() {
        var self = this;

        this.view.changeCampaignButton.click(function() {
            self.call_after_campaign_selection = false;
            self.view.changeCampaignMenu.modal("show");
        });

        this.view.selectCampaignButton.click(function() {
            self.selectManualCampaign();
        });

        this.view.numberDisplay.bind("keypress", function(event) {
            if (event.which == 13) {
                event.preventDefault();
                self.callDialedNumber();
            };
        });

        this.view.callButton.click(function(e) {
            self.callDialedNumber();
        });

        this.view.redialButton.click(function() {
            self.redial();
        });

        this.view.resumeButton.click(function() {
            self.leavePause()
        });

        this.view.pauseButton.click(function () {
            self.view.pauseMenu.modal('show');
        });

        this.view.setPauseButton.click(function() {
            var pause_id = $("#pauseType").val();
            var pause_name = $("#pauseType option:selected").html().replace(' ', '');
            self.setPause(pause_id, pause_name);
        });

        this.view.hangUpButton.click(function() {
            self.phone.hangUp();
        });

        this.view.tagCallButton.click(function() {
            self.view.tagCallMenu.modal('show');
        });

        this.view.holdButton.click(function() {
            if (self.phone_fsm.state == 'OnCall') {
                self.phone_fsm.startOnHold();
                self.phone.putOnHold();
                self.view.holdButton.html('unhold');
            } else if (self.phone_fsm.state == 'OnHold') {
                self.phone_fsm.releaseHold();
                self.phone.releaseHold();
                self.view.holdButton.html('hold');
            } else {
                phone_logger.log('Error');
            }
        }); 

        $("#SaveSignedCall").click(function() {
            // TODO: Verificar si solo se pueden marcar Entrantes, ya que para las salientes
            //       no se esta guardando un call_uuid
            var descripcion = $("#SignDescription").val(); // sign subject
            self.oml_api.marcarLlamada(descripcion, self.phone.call_uuid);
            $("#SignDescription").val(null);
            self.view.tagCallMenu.modal('hide');
        });

        $("#CallList").click(function() {
            $("#modalCallList").modal('show');
        });

        $("logout").click(function() {
            self.phone.logout();
        });

        // Transfer View events: makeTransfer, EndTransfer,
        this.view.makeTransferButton.click(function () {
            var transfer = new OutTransferData();
            if (!transfer.is_valid){
                alert('Seleccione una opción válida');
            }
            else {
                self.phone_fsm.dialTransfer();
                self.phone.dialTransfer(transfer);
            }
        });

        this.view.endTransferButton.click(function() {
            self.phone_fsm.endTransfer()
            self.phone.endTransfer();
        });

        this.subscribeToKeypadEvents();

        // TODO: a variables de instancia
        var answerCallButton = document.getElementById('answer');
        var refuseCallButton = document.getElementById('doNotAnswer');
        answerCallButton.onclick = function() {
            clearTimeout(self.ACW_pause_timeout_handler); // Por las dudas
            self.phone_fsm.acceptCall();
            self.phone.acceptCall();
            $("#modalReceiveCalls").modal('hide');
            var fromUser = self.phone.session_data.from;
            self.view.setCallStatus("Connected to " + fromUser, "orange");
            self.manageContact(self.phone.session_data);
        };

        refuseCallButton.onclick = function() {
            $("#modalReceiveCalls").modal('hide');
            self.phone_fsm.refuseCall();
            self.phone.refuseCall();
        }

    }

    subscribeToKeypadEvents() {
        /* Botones de telefono */
        /* Solo deberian tener esta funcionalidad mientras se esta onCall */
        var self = this;
        $(".key").click(function(e) {
            var pressed_key = e.currentTarget.childNodes[0].data;
            if (self.phone_fsm.state == 'OnCall'){
                self.phone.currentSession.sendDTMF(pressed_key);
            }            
        });
    }

    subscribeToFSMEvents() {
        var self = this;
        this.phone_fsm.observe({
            onInitial: function() {
                self.view.setSipStatus("NO_ACCOUNT");
                self.view.setUserStatus("label label-success", "Online");
                self.view.closeAllModalMenus();
                self.view.setInputDisabledStatus('Initial');
                self.phone.startSipSession();
                self.click_2_call_dispatcher.disable();
            },
            onEnd: function() {
                self.view.setUserStatus("label label-success", "Offline");
                self.view.closeAllModalMenus();
                self.view.setInputDisabledStatus('End');
                self.click_2_call_dispatcher.disable();
            },
            onReady: function() {
                phone_logger.log('FSM: onReady')
                self.view.setUserStatus("label label-success", "Online");
                self.view.closeAllModalMenus();
                self.view.setInputDisabledStatus('Ready');
                self.click_2_call_dispatcher.enable();
            },
            onPaused: function() {
                phone_logger.log('FSM: onPaused')
                self.view.setUserStatus("label label-danger", self.pause_manager.pause_name);
                self.view.closeAllModalMenus();
                self.view.setInputDisabledStatus('Paused');
                self.click_2_call_dispatcher.enable();
            },
            onCalling: function() {
                phone_logger.log('FSM: onCalling')
                self.view.setUserStatus("label label-success", "Calling");
                self.view.closeAllModalMenus();
                self.view.setInputDisabledStatus('Calling');
                self.click_2_call_dispatcher.disable();
            },
            onOncall: function() {
                phone_logger.log('FSM: onOncall')
                self.view.setUserStatus("label label-success", "OnCall");
                self.view.closeAllModalMenus();
                self.view.setInputDisabledStatus('OnCall');
                self.click_2_call_dispatcher.disable();
            },
            onDialingtransfer: function() {
                phone_logger.log('FSM: onDialingTransfer')
                self.view.setUserStatus("label label-success", "Transfering");
                self.view.closeAllModalMenus();
                self.view.setInputDisabledStatus('DialingTransfer');
                self.click_2_call_dispatcher.disable();
            },
            onTransfering: function() {
                phone_logger.log('FSM: onTransfering')
                self.view.setUserStatus("label label-success", "Transfering");
                self.view.closeAllModalMenus();
                self.view.setInputDisabledStatus('Transfering');
                self.click_2_call_dispatcher.disable();
            },
            onReceivingcall: function() {
                phone_logger.log('FSM: onReceivingCall')
                self.view.setUserStatus("label label-success", "ReceivingCall");
                self.view.closeAllModalMenus();
                self.view.setInputDisabledStatus('ReceivingCall');
                self.click_2_call_dispatcher.disable();
            },
            onOnhold: function() {
                phone_logger.log('FSM: onOnHold')
                self.view.setUserStatus("label label-success", "OnHold");
                self.view.closeAllModalMenus();
                self.view.setInputDisabledStatus('OnHold');
                self.click_2_call_dispatcher.disable();
            },
        });
    }

    subscribeToPhoneEvents() {
        var self = this;

        /** User Agent **/
        this.phone.eventsCallbacks.onUserAgentRegistered.add(function () {
            self.view.setSipStatus("REGISTERED");
            self.view.setCallStatus("Login Attempt..", "yellowgreen");
            self.phone.makeLoginCall();
        });

        this.phone.eventsCallbacks.onUserAgentRegisterFail.add(function () {
            self.view.setSipStatus("REGISTER_FAIL");
            self.phone_fsm.failedRegistration();
        });

        this.phone.eventsCallbacks.onUserAgentDisconnect.add(function () {
            self.view.setSipStatus("NO_SIP");
            // TODO: Definir acciones a tomar.
        });

        this.phone.eventsCallbacks.onAgentLogged.add(function() {
            self.phone_fsm.registered();
            self.view.setCallStatus("Agent logged in", "orange");
        });
        this.phone.eventsCallbacks.onAgentLoginFail.add(function() {
            self.view.setCallStatus("Agent not logged in, contact your administrator", "red");
            self.phone_fsm.failedRegistration();
        });

        /** Pauses **/
        this.phone.eventsCallbacks.onAgentPaused.add(function() {
            self.view.setCallStatus("Agent paused", "orange");
        });
        this.phone.eventsCallbacks.onAgentPauseFail.add(function() {
            self.view.setCallStatus("Cannot pause agent, contact your administrator", "red");
            self.phone_fsm.unpause();
            // Arrancar de nuevo timer de operacion
            self.timers.pause.stop();
            self.timers.operacion.start();
            self.pause_manager.leavePause();
        });
        this.phone.eventsCallbacks.onAgentUnpaused.add(function() {
            self.view.setCallStatus("Idle", "black");
        });
        this.phone.eventsCallbacks.onAgentUnPauseFail.add(function() {
            self.view.setCallStatus("Cannot unpause agent, contact your administrator", "red");
            self.phone_fsm.startPause();
            // Arrancar de nuevo timer de pausa
            self.timers.operacion.stop();
            self.timers.pause.start();
        });

        /** Calls **/
        this.phone.eventsCallbacks.onTransferDialed.add(function(transfer_data) {
            phone_logger.log('onTransferDialed')
            if (transfer_data.is_blind) {
                self.phone_fsm.blindTransfer();
                // La llamada se terminará sola luego de mandar los DTMF correspondientes
            } else {
                self.phone_fsm.consultativeTransfer();
            }
        });

        this.phone.eventsCallbacks.onTransferReceipt.add(function(session_data) {
            self.phone_fsm.receiveCall();
            $("#extraInfo").html(session_data.transfer_type_str);
            $("#modalReceiveCalls").modal('show');
        });
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
                $("#modalReceiveCalls").modal('hide');
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
            else { phone_logger.log(`No se sabe volver desde: ${self.phone_fsm.state}`)}

            self.timers.llamada.stop();

            if (self.pause_manager.pause_enabled) {
                self.phone_fsm.startPause();
                self.timers.pausa.start();
            } else {
                self.timers.operacion.start();
            }
        });

        // Outbound Call
        this.phone.eventsCallbacks.onCallConnected.add(function(numberToCall) {
            phone_logger.log('onCallConnected from: ' + self.phone_fsm.state);
            self.view.setCallStatus("Connected to " + numberToCall, "orange");
            if (self.phone_fsm.state == 'Calling') {
                self.phone_fsm.connectCall();
            }
            else {
                // Analizar si hace falta atender el evento si es inbound.
            }
            self.timers.llamada.start();
            self.timers.pausa.stop();           // Ver antes si estaba en pausa 
            self.timers.operacion.start();
        });

        this.phone.eventsCallbacks.onOutCallFailed.add(function(cause) {
            self.setCallFailedStatus(cause);
            // El fallo de llamada saliente tambien dispara el onSessionFailed
        });

        this.phone.eventsCallbacks.onCallEnded.add(function() {
            if (self.phone_fsm.state == 'DialingTransfer') {
                self.phone.cancelDialTransfer();
            }
            self.view.setCallStatus("Idle", "black");
            self.phone_fsm.endCall();
            self.saveCall();
            self.timers.llamada.stop();
            self.timers.llamada.restart();
            self.callEndTransition();
        });
    }

    callEndTransition() {
        var return_to_pause = this.pause_manager.pause_enabled && !this.pause_manager.in_ACW_pause;
        var pause_id = return_to_pause? this.pause_manager.pause_id: undefined;
        var pause_name = return_to_pause? this.pause_manager.pause_name: undefined;

        if (this.agent_config.auto_pause) {
            var self = this;
            this.setPause(ACW_PAUSE_ID, ACW_PAUSE_NAME);
            if (this.agent_config.auto_unpause > 0) {
                var m_seconds = this.agent_config.auto_unpause * 1000;
                this.ACW_pause_timeout_handler = setTimeout(
                    function() {self.autoLeaveACWPause(return_to_pause, pause_id, pause_name);},
                    m_seconds
                );
            } else {
                this.timers.operacion.start();
                this.phone.cleanLastCallData();
            }
        } else {
            this.timers.operacion.start();
            this.phone.cleanLastCallData();
        }
    }

    autoLeaveACWPause(return_to_pause, pause_id, pause_name) {
        this.ACW_pause_timeout_handler = undefined;
        if (return_to_pause) {
            this.setPause(pause_id, pause_name);
        }else {
            this.leavePause();
        }
    }

    setPause(pause_id, pause_name) {
        if (this.phone_fsm.state == 'Paused') {
            this.phone_fsm.changePause();
        } else {
            this.phone_fsm.startPause();
        }
        this.pause_manager.setPause(pause_id, pause_name)
        this.view.setUserStatus("label label-danger", pause_name);
        this.view.setCallStatus("Pausing.... " + pause_name, "yellowgreen");

        this.oml_api.changeStatus(USER_STATUS_PAUSE, this.agent_id);
        this.timers.pausa.start();
        this.timers.operacion.stop();

        this.phone.makePauseCall(pause_id);
    }

    leavePause() {
        clearTimeout(this.ACW_pause_timeout_handler);
        this.pause_manager.leavePause();
        this.oml_api.changeStatus(USER_STATUS_ONLINE, this.agent_id);
        this.phone.makeUnpauseCall();
        this.timers.pausa.stop();
        this.timers.operacion.start();
        this.phone_fsm.unpause();
        this.view.setCallStatus("Unpausing....", "yellowgreen");
    }

    callDialedNumber() {
        this.is_inbound = false;

        var dialedNumber = this.view.numberDisplay.value;
        if (dialedNumber == "") {
            this.view.numberDisplay.css('border-color', 'red');
            return;
        }
        this.view.numberDisplay.css('border-color', 'black');

        if (this.manual_campaign_id == undefined) {
            this.call_after_campaign_selection = true;
            $("#modalSelectCmp").modal("show");
            return;
        }

        this.makeDialedNumberCall();
    }

    makeDialedNumberCall() {
        clearTimeout(this.ACW_pause_timeout_handler);
        // Dialed number OK and Campaign selected
        var dialedNumber = this.view.numberDisplay.val();
        this.lastDialedNumber = dialedNumber;

        this.phone.makeCall(dialedNumber,
                            this.manual_campaign_id,
                            this.manual_campaign_type);
        this.getNewContactForm(this.manual_campaign_id,
                                      this.agent_id,
                                      dialedNumber);
        this.view.numberDisplay.val("");
        this.view.setCallStatus("Calling.... " + dialedNumber, "yellowgreen");
        this.phone_fsm.startCall();
    }

    redial() {
        // TODO: Ver por que falla!!!
        if (this.lastDialedNumber !== undefined) {
            this.view.numberDisplay.val(this.lastDialedNumber);
            this.makeDialedNumberCall();
        }
        else {
            phone_logger.log('Redial button should be disabled.')
        }
    }

    selectManualCampaign() {
        $("#modalSelectCmp").modal("hide");
        this.manual_campaign_id = $("#cmpList").val();
        this.manual_campaign_type = $("#cmpList option:selected").attr('campana_type');
        var nombrecamp = $("#cmpList option:selected").html().trim();
        $("#campAssocManualCall").html(nombrecamp);
        
        if (this.call_after_campaign_selection) {
            this.makeDialedNumberCall();
        }
    }

    setCallFailedStatus(cause) {
        switch(cause){
            case JsSIP.C.causes.BUSY:
                this.view.setCallStatus("Number busy, try later", "orange");
                break;
            case JsSIP.C.causes.REJECTED:
                this.view.setCallStatus("Rejected, try later", "orange");
                break;
            case JsSIP.C.causes.UNAVAILABLE:
                this.view.setCallStatus("Unavailable, contact your administrator", "red");
                break;
            case JsSIP.C.causes.NOT_FOUND:
                this.view.setCallStatus("Error, check the number dialed", "red");
                break;
            case JsSIP.C.causes.AUTHENTICATION_ERROR:
                this.view.setCallStatus("Authentication error, contact your administrator", "red");
                break;
            case JsSIP.C.causes.MISSING_SDP:
                this.view.setCallStatus("Error, Missing sdp", "red");
                break;
            case JsSIP.C.causes.ADDRESS_INCOMPLETE:
                this.view.setCallStatus("Address incomplete", "red");
                break;
            case JsSIP.C.causes.SIP_FAILURE_CODE:
                this.view.setCallStatus("Service Unavailable, contact your administrator", "red");
                break;
            case JsSIP.C.causes.USER_DENIED_MEDIA_ACCESS:
                this.view.setCallStatus("WebRTC Error: User denied media access", "red");
                break;
            default:
                this.view.setCallStatus("Error: Call failed", "red");
        }
    }

    manageCallReceipt(session_data) {
        if (this.forcesAutoAttend(session_data)) {
            clearTimeout(this.ACW_pause_timeout_handler);   // Por las dudas
            this.phone_fsm.acceptCall();
            this.phone.acceptCall();
            this.manageContact(session_data);
        } else {
            var from = session_data.from;
            $("#callerid").text(from);
            $("#modalReceiveCalls").modal('show');
        }
    }

    forcesAutoAttend(session_data) {
        if (session_data.is_click2call) {
            return true;
        }
        if (session_data.is_dialer && this.agent_config.auto_attend_DIALER) {
            return true;
        }
        if (session_data.is_inbound && this.agent_config.auto_attend_IN) {
            return true;
        }
        return false;
    }

    manageContact(session_data) {
        var from = session_data.from;
        if (session_data.requires_crm_treatment){
            // Definir pasos a seguir con CRM
            // var linkaddress = e.request.headers.Sitioexterno[0].raw;
            // self.getIframe(linkaddress);
        } else {
            var campaign_id = session_data.campaign_id;
            var contact_id = session_data.contact_id;
            if (campaign_id !== undefined && campaign_id != '') {
                if (contact_id !== undefined && contact_id != '') {
                    this.getContactForm(campaign_id, contact_id, this.agent_id);
                } else {
                    this.getNewContactForm(campaign_id, this.agent_id, from);
                }
            }
        }
        // Muestra el formulario correspondiente, o abre el link del CRM

    }

    saveCall() {
        var duracion = this.timers.llamada.get_time_str();
        var numero_telefono = undefined;
        if (this.phone.session_data.is_local_call) {
            numero_telefono = this.lastDialedNumber;
        } else {
            numero_telefono = this.phone.session_data.from;
        }
        var tipo_llamada = this.phone.session_data.call_type_id;
        phone_logger.log(`saveCall: tipo:${tipo_llamada}, numero: ${numero_telefono}`);
        this.oml_api.guardarDuracionLlamada(duracion,
                                            this.agent_id,
                                            numero_telefono,
                                            tipo_llamada,
                                            function(msg){$("#call_list").html(msg);});
    }

    getContactForm(campid, contactid, agentid) {
        // var url = "/formulario/" + campid + "/calificacion/" + contactid + "/update/" + agentid + "/calificacion/";
        var url = `/formulario/${campid}/calificacion/${contactid}/update/${agentid}/calificacion/`;
        $("#dataView").attr('src', url);
    }

    getNewContactForm(idcamp, idagt, tel) {
        // Elimino los caracteres no numericos
        var telephone = tel.replace(/\D+/g, '');
        telephone = telephone == '' ? 0 : telephone;
        var url = `/formulario/${idcamp}/calificacion/${idagt}/create/${telephone}/`;
        // var url = "/formulario/" + idcamp + "/calificacion/" + idagt + "/create/" + telephone + "/";
        $("#dataView").attr('src', url);
    }

    getIframe(url) {
        $("#dataView").attr('src', url);
    }

}

class PauseManager {
    constructor() {
        this.pause_id = undefined;
        this.pause_name = undefined;
        this.pause_enabled = false;
    }
    setPause(id, name) {
        this.pause_id = id;
        this.pause_name = name;
        this.pause_enabled = true;
    }
    leavePause() {
        //this.pause_id = undefined;
        //this.pause_name = undefined;
        this.pause_enabled = false;
    }
    get in_ACW_pause() {
        return this.pause_enabled && this.pause_id == ACW_PAUSE_ID;
    }
}

class OutTransferData {
    constructor() {
        var blindTransf = document.getElementById("blindTransf");
        var consultTransf = document.getElementById("consultTransf");
        var transfToAgent = document.getElementById("transfToAgent");
        var transfToCamp = document.getElementById("transfToCamp");
        var transfToNum = document.getElementById("transfToNum");

        this.is_blind = blindTransf.checked
        this.is_consultative = consultTransf.checked

        this.is_to_agent = transfToAgent.checked
        if (this.is_to_agent)
            this.destination = $("select[id=agentToTransfer]").val()
        this.is_to_campaign = transfToCamp.checked
        if (this.is_to_campaign)
            this.destination = $("select[id=campToTransfer]").val()
        this.is_to_number = transfToNum.checked
        if (this.is_to_number)
            this.destination = $("#numberToTransfer").val()
    }

    get is_valid() {
        return (this.is_blind || (this.is_consultative && !this.is_to_campaign)) &&
            (this.is_to_agent || this.is_to_number || this.is_to_campaign) &&
            this.destination != '' && this.destination != undefined
    }
}

class AgentConfig {
    constructor() {
        this.auto_pause = $('#auto_pause').val() == 'True';
        this.auto_unpause = Number($('#auto_unpause').val());
        this.auto_attend_DIALER = $('#auto_attend_DIALER').val() == 'True';
        this.auto_attend_IN = $('#auto_attend_IN').val() == 'True';
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
