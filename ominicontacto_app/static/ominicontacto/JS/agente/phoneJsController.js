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
/*      - jitsi_external_api.js     */

/* global click2call gettext interpolate JsSIP OMLAPI PhoneJSView PhoneJS KamailioHost */
/* global WebSocketPort WebSocketHost PhoneFSM USER_STATUS_PAUSE USER_STATUS_ONLINE Urls*/
/* global JitsiMeetExternalAPI PHONE_STATUS_CONFIGS */

var ACW_PAUSE_ID = '0';
var ACW_PAUSE_NAME = 'ACW';


class PhoneJSController {
    // Connects PhoneJS with a PhoneJSView.
    constructor(agent_id, sipExtension, sipSecret, timers, click_2_call_dispatcher, keep_alive_sender, video_domain, notification_agent) {
        this.oml_api = new OMLAPI();
        this.view = new PhoneJSView();
        this.timers = timers;
        this.phone = new PhoneJS(agent_id, sipExtension, sipSecret, KamailioHost, WebSocketPort, WebSocketHost, this.view.local_audio, this.view.remote_audio);
        this.phone_fsm = new PhoneFSM();
        this.notification_agent = notification_agent;
        this.agent_config = new AgentConfig();
        this.pause_manager = new PauseManager();
        this.click_2_call_dispatcher = click_2_call_dispatcher;
        this.keep_alive_sender = keep_alive_sender;

        /* Local Variables */
        this.agent_id = agent_id;
        this.video_domain = video_domain;
        this.lastDialedCall = undefined;
        this.call_after_campaign_selection = false;
        this.manual_campaign_id = undefined;
        this.campaign_id = null;
        this.campaign_type = null;
        this.campaign_name = '';
        this.llamada_calificada = null;
        /*-----------------*/

        this.disableOnHold();

        this.subscribeToViewEvents();
        this.subscribeToFSMEvents();
        this.subscribeToPhoneEvents();
        this.subscribeToAgentNotificationEvents();

        this.oml_api.getAgentes(this.view.cargarAgentes);
        this.oml_api.getCampanasActivas(this.view.cargarCampanasActivas);

        this.phone_fsm.start();
    }


    markRecordCallButtonReady (self, $img, $recordCallButton) {
        // cambia icono y mensaje del botón de grabacion bajo demanda
        // para mostrar que está listo para grabar
        $img.attr('src', self.view.imgRecordOffUrl);
        $recordCallButton.attr('title', gettext('Grabar llamada'));
    }

    markRecordCallButtonRecording (self, $img, $recordCallButton) {
        // cambia icono y mensaje del botón de grabacion bajo demanda
        // para mostrar que está grabando
        $img.attr('src', self.view.imgRecordOnUrl);
        $recordCallButton.attr('title', gettext('Parar grabación llamada'));
    }

    subscribeToViewEvents() {
        var self = this;

        this.view.changeCampaignButton.click(function() {
            self.call_after_campaign_selection = false;
            self.view.changeCampaignMenu.modal('show');
        });

        this.view.selectCampaignButton.click(function() {
            self.selectManualCampaign();
        });

        this.view.numberDisplay.bind('keypress', function(event) {
            if (event.which == 13) {
                event.preventDefault();
                self.callDialedNumber();
            }
        });

        this.view.callButton.click(function(e) {
            self.callDialedNumber();
        });

        this.view.redialButton.click(function() {
            self.redial();
        });

        this.view.recordCall.click(function () {
            var $recordCallButton = self.view.recordCall;
            var $img = $recordCallButton.find('img');
            var recordUrlStatus = $img.attr('src');

            if (recordUrlStatus == self.view.imgRecordOffUrl) {
                self.markRecordCallButtonRecording(self, $img, $recordCallButton);
                self.recordCall();
            }
            else {
                self.markRecordCallButtonReady(self, $img, $recordCallButton);
                self.stopRecordCall();
            }
        });

        this.view.resumeButton.click(function() {
            self.leavePause();
        });

        if ($('#pauseType').find('option').length > 0){
            this.view.pauseButton.click(function () {
                self.view.pauseMenu.modal('show');
            });
        }
        else {
            this.view.pauseButton.click(function () {
                alert('No tiene pausas definidas.');
            });
        }

        this.view.setPauseButton.click(function() {
            var pause_id = $('#pauseType').val();
            var pause_name = $('#pauseType option:selected').html().replace(' ', '');
            clearTimeout(self.ACW_pause_timeout_handler);
            self.setPause(pause_id, pause_name);
        });

        this.view.hangUpButton.click(function() {
            self.hangUp();
            self.view.holdButton.html('hold');
        });

        this.view.tagCallButton.click(function() {
            self.view.tagCallMenu.modal('show');
        });

        this.view.holdButton.click(function() {
            if (self.phone_fsm.state == 'OnCall') {
                self.phone_fsm.startOnHold();
                self.phone.putOnHold();
                self.view.holdButton.html('unhold');
                self.oml_api.eventHold();
            } else if (self.phone_fsm.state == 'OnHold') {
                self.phone_fsm.releaseHold();
                self.phone.releaseHold();
                self.view.holdButton.html('hold');
                self.oml_api.eventHold();
            } else {
                phone_logger.log('Error');
            }
        });

        /* Off Campaign */
        this.view.callOffCampaignMenuButton.click(function() {
            self.view.callOffCampaignMenu.modal('show');
            if ($('#agente_off_camp').find('option').length == 0){
                self.view.callAgentButton.prop('disabled', true);
            }
        });

        this.view.callAgentButton.click(function() {
            var agent_id = $('#agente_off_camp').val();
            click2call.call_agent(agent_id);
        });

        this.view.callPhoneOffCampaignButton.click(function() {
            var phone = $('#phone_off_camp').val();
            click2call.call_external(phone);
        });

        this.view.callQuickOffCampaignButton.click(function() {
            var phone = $('#lista_rapida_off_camp').val();
            click2call.call_external(phone);
        });

        $('#SaveSignedCall').click(function() {
            if (self.phone.session_data.remote_call) {
                var descripcion = $('#SignDescription').val(); // sign subject
                var call_id = self.phone.session_data.remote_call.call_id;
                self.oml_api.marcarLlamada(descripcion, call_id);
                $('#SignDescription').val(null);
                self.view.tagCallMenu.modal('hide');
            }
        });

        $('#CallList').click(function() {
            $('#modalCallList').modal('show');
        });

        $('#logout').click(function() {
            self.phone.logout();
        });

        // Transfer View events: makeTransfer, EndTransfer,
        this.view.makeTransferButton.click(function () {
            var transfer = new OutTransferData();
            if (!transfer.is_valid){
                alert(gettext('Seleccione una opción válida'));
            }
            else {
                self.phone_fsm.dialTransfer();
                self.phone.dialTransfer(transfer);
                $('#numberToTransfer').val('');
            }
        });

        this.view.makeTransferToSurveyButton.click(function() {
            self.phone_fsm.dialTransfer();
            self.phone.dialTransfer(new SurveyTransferData());
        });

        this.view.endTransferButton.click(function() {
            self.phone_fsm.endTransfer();
            self.phone.endTransfer();
        });

        this.view.conferButton.click(function() {
            self.phone.confer();
        });

        this.subscribeToKeypadEvents();

        // TODO: a variables de instancia
        var answerCallButton = document.getElementById('answer');
        answerCallButton.onclick = function() {
            clearTimeout(self.ACW_pause_timeout_handler); // Por las dudas
            self.phone_fsm.acceptCall();
            self.phone.acceptCall();
            $('#modalReceiveCalls').modal('hide');
            var fromUser = self.phone.session_data.from;
            var message = interpolate(gettext('Conectado a %(fromUser)s'), {fromUser:fromUser}, true);
            self.view.setCallStatus(message, 'orange');
            self.manageContact(self.phone.session_data);
        };
        
        // filters doNotAnswer and doNotAnswerX
        $('[id^=doNotAnswer]').click(function() {
            $('#modalReceiveCalls').modal('hide');
            self.phone.refuseCall();
        });

        this.view.reload_video_button.click(function() {
            self.reloadVideo();
        });

        this.view.buttonVideo.click(function() {
            self.view.showHideVideo();
        });
    }

    subscribeToKeypadEvents() {
        /* Botones de telefono */
        /* Solo deberian tener esta funcionalidad mientras se esta onCall */
        var self = this;
        $('.key').click(function(e) {
            var pressed_key = e.currentTarget.childNodes[0].data;
            if (self.phone_fsm.state == 'OnCall' || self.phone_fsm.state == 'Transfering'){
                self.phone.currentSession.sendDTMF(pressed_key);
            }
        });
    }

    subscribeToFSMEvents() {
        var self = this;
        this.phone_fsm.observe({
            onInitial: function() {
                self.view.setSipStatus('NO_ACCOUNT');
                self.view.setUserStatus('label label-success', gettext('Conectado'));
                self.view.closeAllModalMenus();
                self.view.setStateInputStatus('Initial');
                self.phone.startSipSession();
                self.click_2_call_dispatcher.disable();
                self.keep_alive_sender.deactivate();
            },
            onEnd: function() {
                self.view.setUserStatus('label label-success', gettext('Desconectado'));
                self.view.closeAllModalMenus();
                self.view.setStateInputStatus('End');
                self.click_2_call_dispatcher.disable();
                self.keep_alive_sender.deactivate();
            },
            onLoggingtoasterisk: function() {
                phone_logger.log('FSM: onLoggingToAsterisk');
            },
            onReady: function() {
                phone_logger.log('FSM: onReady');
                self.view.setUserStatus('label label-success', gettext('Conectado'));
                self.view.closeAllModalMenus();
                self.view.setStateInputStatus('Ready');
                self.click_2_call_dispatcher.enable();
                self.keep_alive_sender.deactivate();
                self.callOfCampPrivilege();
            },
            onPausing: function() {
                phone_logger.log('FSM: onPausing');
                self.view.closeAllModalMenus();
                self.view.setStateInputStatus('Pausing');
                self.keep_alive_sender.deactivate();
            },
            onPaused: function() {
                phone_logger.log('FSM: onPaused');
                self.view.setUserStatus('label label-danger', self.pause_manager.pause_name);
                self.view.closeAllModalMenus();
                self.view.setStateInputStatus('Paused');
                self.click_2_call_dispatcher.enable();
                self.keep_alive_sender.deactivate();
                self.callOfCampPrivilege();
            },
            onChangePause: function() {
                phone_logger.log('FSM: onChangePause');
                self.view.setUserStatus('label label-danger', self.pause_manager.pause_name);
                self.view.closeAllModalMenus();
                self.view.setStateInputStatus('Paused');
                self.click_2_call_dispatcher.enable();
                self.keep_alive_sender.deactivate();
            },

            onCalling: function() {
                phone_logger.log('FSM: onCalling');
                self.view.setUserStatus('label label-success', gettext('Llamando'));
                self.view.closeAllModalMenus();
                self.view.setStateInputStatus('Calling');
                self.click_2_call_dispatcher.disable();
                self.keep_alive_sender.activate();
            },
            onOncall: function() {
                phone_logger.log('FSM: onOncall');
                self.view.setUserStatus('label label-success', gettext('En llamado'));
                self.view.closeAllModalMenus();
                self.view.setStateInputStatus('OnCall');
                self.view.toogleVisibilityRecordButtons(self.phone.session_data);
                self.click_2_call_dispatcher.disable();

                self.view.setCallSessionData(self.phone.session_data);

                if (self.phone.session_data.remote_call &&
                    self.phone.session_data.remote_call.force_disposition) {
                    self.click_2_call_dispatcher.last_call_configures_force_disposition = true;
                    self.click_2_call_dispatcher.last_call_forces_disposition =
                        self.phone.session_data.remote_call.force_disposition == 'True';
                }
                else {
                    self.click_2_call_dispatcher.last_call_configures_force_disposition = false;
                }

                self.keep_alive_sender.activate();
            },
            onDialingtransfer: function() {
                phone_logger.log('FSM: onDialingTransfer');
                self.view.setUserStatus('label label-success', gettext('Transfiriendo'));
                self.view.closeAllModalMenus();
                self.view.setStateInputStatus('DialingTransfer');
                self.click_2_call_dispatcher.disable();
                self.keep_alive_sender.activate();
            },
            onTransfering: function() {
                phone_logger.log('FSM: onTransfering');
                self.view.setUserStatus('label label-success', gettext('Transfiriendo'));
                self.view.closeAllModalMenus();
                self.view.setStateInputStatus('Transfering');
                self.view.toogleVisibilityRecordButtons(self.phone.session_data);
                self.click_2_call_dispatcher.disable();
                self.keep_alive_sender.activate();
            },
            onReceivingcall: function() {
                phone_logger.log('FSM: onReceivingCall');
                self.view.setUserStatus('label label-success', gettext('Recibiendo llamado'));
                self.view.closeAllModalMenus();
                self.view.setStateInputStatus('ReceivingCall');
                self.click_2_call_dispatcher.disable();
                self.keep_alive_sender.activate();
            },
            onOnhold: function() {
                phone_logger.log('FSM: onOnHold');
                self.view.setUserStatus('label label-success', gettext('En espera'));
                self.view.closeAllModalMenus();
                self.view.setStateInputStatus('OnHold');
                self.click_2_call_dispatcher.disable();
                self.keep_alive_sender.activate();
            },
        });
    }

    subscribeToPhoneEvents() {
        var self = this;

        /** User Agent **/
        this.phone.eventsCallbacks.onUserAgentRegistered.add(function () {
            self.view.setSipStatus('REGISTERED');
            self.phone_fsm.registered();

            if (self.phone_fsm.state == 'LoggingToAsterisk') {
                self.view.setCallStatus(gettext('Conectando a asterisk  ..'), 'yellowgreen');
                var login_ok = function(){self.goToReadyAfterLogin();};
                var login_error = function(){
                    self.view.setCallStatus(gettext('Agente no conectado a asterisk, contacte a su administrador'), 'red');
                    self.phone_fsm.logToAsteriskError();
                };
                self.oml_api.asteriskLogin(login_ok, login_error);
            }
            if (self.phone_fsm.state == 'Ready')
                self.view.setCallStatus(gettext('Agente conectado.'), 'yellowgreen');
            if (self.phone_fsm.state == 'Paused') {
                self.view.setCallStatus(gettext('Agente en pausa.'), 'orange');
                self.setPause(self.pause_manager.pause_id, self.pause_manager.pause_name);
            }
        });

        this.phone.eventsCallbacks.onUserAgentUnregistered.add(function () {
            self.view.setSipStatus('UNREGISTERED');
            self.view.setCallStatus(gettext('Agente Desconectado'), 'red');
            $.growl.error({
                title: gettext('Atención!'),
                message: gettext('Ha perdido la conexión!'),
                duration: 15000,
            });
            self.phone_fsm.unregistered();
        });

        this.phone.eventsCallbacks.onUserAgentRegisterFail.add(function () {
            self.view.setSipStatus('REGISTER_FAIL');
            self.phone_fsm.failedRegistration();
        });

        this.phone.eventsCallbacks.onUserAgentDisconnect.add(function () {
            self.view.setSipStatus('NO_SIP');
            // TODO: Definir acciones a tomar.
            // Si pierde conexión, en cada intento fallido de reconexión se dispara este evento.
        });

        /** Calls **/
        this.phone.eventsCallbacks.onTransferDialed.add(function(transfer_data) {
            phone_logger.log('onTransferDialed');
            if (transfer_data.is_blind) {
                self.phone_fsm.blindTransfer();
                // La llamada se terminará sola luego de mandar los DTMF correspondientes
            } else {
                self.phone_fsm.consultativeTransfer();
            }
        });

        this.phone.eventsCallbacks.onTransferReceipt.add(function(session_data) {
            self.phone_fsm.receiveCall();
            $('#numberAni').html(session_data.from);
            $('#callerid').html(session_data.from_agent_name);
            $('#extraInfo').html(session_data.transfer_type_str);
            $('#modalReceiveCalls').modal('show');
            self.oml_api.eventRinging();
        });

        this.phone.eventsCallbacks.onCallReceipt.add(function(session_data) {
            if (self.phone_fsm.state == 'LoggingToAsterisk'){
                // Assume logged ok.
                self.goToReadyAfterLogin();
                // Delay to allow going to Ready State
                setTimeout(function(){
                    self.phone_fsm.receiveCall();
                    self.manageCallReceipt(session_data);
                }, 100);
            }
            else if (self.phone_fsm.state == 'Pausing') {
                self.phone.refuseCall();
            }
            else {
                self.phone_fsm.receiveCall();
                self.manageCallReceipt(session_data);
            }
        });

        this.phone.eventsCallbacks.onSessionFailed.add(function() {

            // La call session puede haber fallado al hacer un refuseCall
            if (self.phone_fsm.state == 'Pausing') {
                // Elimino la callData de la llamada rechazada
                self.phone.cleanLastCallData();
                return;
            }

            // Se dispara al fallar Call Sessions
            phone_logger.log('Volviendo a Ready o a Pause:');
            if (self.phone_fsm.state == 'ReceivingCall') {
                phone_logger.log('Desde ReceivingCall!');
                self.phone_fsm.refuseCall();
                $('#modalReceiveCalls').modal('hide');
                self.phone.cleanLastCallData();
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
            else { phone_logger.log('No se sabe volver desde: ' + self.phone_fsm.state);}

            self.timers.llamada.stop();

            if (self.pause_manager.pause_enabled) {
                self.phone_fsm.startPause();
                self.timers.pausa.start();
            } else {
                self.timers.operacion.start();
            }
        });

        this.phone.eventsCallbacks.onRingingEnd.add(function() {
            if (self.phone_fsm.state == 'Ready') {
                self.oml_api.eventRinging(false);
            } 
        });

        // Outbound Call
        this.phone.eventsCallbacks.onCallConnected.add(function(numberToCall) {
            phone_logger.log('onCallConnected from: ' + self.phone_fsm.state);
            var message = interpolate(gettext('Conectado a %(fromUser)s'), {fromUser:numberToCall}, true);
            self.view.setCallStatus(message, 'orange');
            if (self.phone_fsm.state == 'Calling') {
                self.phone_fsm.connectCall();
            }
            else {
                // Analizar si hace falta atender el evento si es inbound.
            }
            self.timers.llamada.start();
            self.timers.pausa.stop();           // Ver antes si estaba en pausa
            self.timers.operacion.start();

            self.loadVideoInFrame();
        });

        this.phone.eventsCallbacks.onOutCallFailed.add(function(cause) {
            self.setCallFailedStatus(cause);
            // El fallo de llamada saliente tambien dispara el onSessionFailed
        });

        this.phone.eventsCallbacks.onCallEnded.add(function() {
            if (self.phone_fsm.state == 'DialingTransfer') {
                self.phone.cancelDialTransfer();
            }
            self.view.setCallStatus(gettext('Disponible'), 'black');
            self.phone_fsm.endCall();
            self.timers.llamada.stop();
            self.timers.llamada.restart();
            self.callEndTransition();
            self.updateCallHistory();
            self.view.holdButton.html('hold');
            // mostramos al botón de grabación bajo demanda de llamada
            // como listo para grabar (aunque en este punto va a estar
            // deshabilitado)
            var $recordCallButton = self.view.recordCall;
            var $img = $recordCallButton.find('img');
            self.markRecordCallButtonReady(self, $img, $recordCallButton);
            self.unloadVideo();
        });
    }

    subscribeToAgentNotificationEvents() {
        var self = this;
        this.notification_agent.eventsCallbacks.onNotificationForzarDespausa.add(function(args){
            if (args['calificada'])
                if (self.phone_fsm.state == 'Paused')
                    self.leavePause();
                else
                    self.llamada_calificada = true;
            else
                self.llamada_calificada = false;
        });
        
        this.notification_agent.eventsCallbacks.onNotificationPhoneJsLogout.add(function(args){
            self.phone.logout();
            self.view.setSipStatus('UNREGISTERED');
            var message = gettext('Se ha detectado un nuevo inicio de sesión con su usuario.\
                            La sesión actual será suspendida. Por favor, contacte con su Administrador');
            self.view.setCallStatus(message, 'red');
            alert(message);
            
        });

    }

    goToReadyAfterLogin() {
        // If state is not LoggingToAsterisk I assume agent already went to ready
        if (this.phone_fsm.state == 'LoggingToAsterisk') {
            this.view.setSipStatus('REGISTERED');
            this.phone_fsm.logToAsteriskOk();
            this.view.setCallStatus(gettext('Agente conectado'), 'yellowgreen');
            this.phone.Sounds('Welcome', 'play');
        }
    }

    callEndTransition() {
        var return_to_pause = this.pause_manager.pause_enabled && !this.pause_manager.in_ACW_pause;
        var pause_id = return_to_pause? this.pause_manager.pause_id: undefined;
        var pause_name = return_to_pause? this.pause_manager.pause_name: undefined;

        // Al finalizar la llamada se manda el agente a Pausa forzada.
        var self = this;
        var call_auto_unpause = this.phone.session_data.remote_call.auto_unpause;
        this.phone.cleanLastCallData();
        this.setPause(ACW_PAUSE_ID, ACW_PAUSE_NAME);

        // Si se fuerza la calificación no se sale automaticamente de Pausa forzada
        if (this.click_2_call_dispatcher.disposition_forced){
            if (this.llamada_calificada){
                this.autoLeaveACWPause(return_to_pause, pause_id, pause_name);
                this.llamada_calificada = null;
            }  
            else
                return;
        }
        if (call_auto_unpause != undefined) {
            if (call_auto_unpause > 0) {
                let m_seconds = call_auto_unpause * 1000;
                this.ACW_pause_timeout_handler = setTimeout(
                    function() {self.autoLeaveACWPause(return_to_pause, pause_id, pause_name);},
                    m_seconds
                );
            }
            // else { Stay in ACW Pause }:
        }
        else if (this.agent_config.auto_unpause > 0) {
            let m_seconds = this.agent_config.auto_unpause * 1000;
            this.ACW_pause_timeout_handler = setTimeout(
                function() {self.autoLeaveACWPause(return_to_pause, pause_id, pause_name);},
                m_seconds
            );
        }
        // else { Stay in ACW Pause }:
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
        this.pause_manager.setPause(pause_id, pause_name);
        this.view.setUserStatus('label label-danger', pause_name);
        var message = interpolate(gettext('Obteniendo pausa: %(pause_name)s'),
            {pause_name: pause_name}, true);
        this.view.setCallStatus(message, 'yellowgreen');

        this.timers.pausa.start();
        this.timers.operacion.stop();

        var self = this;
        var pause_ok = function(){
            self.phone_fsm.pauseSet();
            self.view.setCallStatus(gettext('Agente en pausa'), 'orange');
        };
        var pause_error = function(){
            var message = gettext('No se puede realizar la pausa, contacte a su administrador');
            self.view.setCallStatus(message, 'red');
            self.phone_fsm.pauseAborted();
            // Arrancar de nuevo timer de operacion
            self.timers.pausa.stop();
            self.timers.operacion.start();
            self.pause_manager.leavePause();
        };
        this.oml_api.makePause(pause_id, pause_ok, pause_error);
    }

    leavePause(){
        if (this.click_2_call_dispatcher.disposition_forced){
            var self = this;
            if (self.verificando_calificacion_por_pausa){
                return;
            }
            self.verificando_calificacion_por_pausa = true;
            this.oml_api.llamadaCalificada(
                function(){
                    self.doLeavePause();
                    self.verificando_calificacion_por_pausa = false;
                },
                function(calldata){
                    click2call.make_disposition(calldata);
                    self.verificando_calificacion_por_pausa = false;
                },
                function(idcalificacion){
                    click2call.make_sales_form(idcalificacion);
                    self.verificando_calificacion_por_pausa = false;
                },
                function(){
                    self.verificando_calificacion_por_pausa = false;
                    alert(gettext('No se pudo salir de la pausa.'));
                }
            );
        }
        else {
            this.doLeavePause();
        }
    }


    doLeavePause() {
        clearTimeout(this.ACW_pause_timeout_handler);
        var pause_id = this.pause_manager.pause_id;
        this.pause_manager.leavePause();

        /** Pauses **/
        var self = this;
        var unpause_ok = function(){
            self.view.setCallStatus(gettext('Disponible'), 'black');
        };
        var unpause_error = function(){
            var message = gettext('No se puede liberar la pausa, contacte a su administrador');
            self.view.setCallStatus(message, 'red');
            self.phone_fsm.startPause();
            // Arrancar de nuevo timer de pausa
            self.timers.operacion.stop();
            self.timers.pausa.start();
        };
        this.oml_api.makeUnpause(pause_id, unpause_ok, unpause_error);
        this.timers.pausa.stop();
        this.timers.operacion.start();
        this.phone_fsm.unpause();
        this.view.setCallStatus(gettext('Liberando pausa...'), 'yellowgreen');
    }

    callDialedNumber() {
        var dialedNumber = this.view.numberDisplay.value;
        if (dialedNumber == '') {
            this.view.numberDisplay.css('border-color', 'red');
            return;
        }
        this.view.numberDisplay.css('border-color', 'black');

        if (this.manual_campaign_id == undefined) {
            this.call_after_campaign_selection = true;
            $('#modalSelectCmp').modal('show');
            return;
        }

        this.makeDialedNumberCall();
    }

    makeDialedNumberCall() {
        clearTimeout(this.ACW_pause_timeout_handler);
        // Dialed number OK and Campaign selected
        var dialedNumber = this.view.numberDisplay.val();
        this.getSelectContactForm(this.manual_campaign_id, dialedNumber);
    }

    redial() {
        if (this.lastDialedCall !== undefined) {
            // Ejecutar un click2call para el redial para ese contacto.
            var campaign_id = this.lastDialedCall.id_campana;
            var campaign_type = this.lastDialedCall.campana_type;
            var contact_id = this.lastDialedCall.id_contacto;
            var phone = this.lastDialedCall.telefono;
            this.click_2_call_dispatcher.call_contact(campaign_id, campaign_type, contact_id, phone, 'contactos');
            this.view.numberDisplay.val(this.lastDialedNumber);
        }
        else {
            phone_logger.log('Redial button should be disabled!!');
        }
    }

    selectManualCampaign() {
        $('#modalSelectCmp').modal('hide');
        this.manual_campaign_id = $('#cmpList').val();
        this.manual_campaign_type = $('#cmpList option:selected').attr('campana_type');
        var nombrecamp = $('#cmpList option:selected').html().trim();
        $('#campAssocManualCall').html(nombrecamp);

        if (this.call_after_campaign_selection) {
            this.makeDialedNumberCall();
        }
    }

    hangUp() {
        this.phone.hangUp();
    }

    recordCall() {
        // TODO: mover a modulo phoneJsSip.js
        this.phone.currentSession.sendDTMF('*4');
    }

    stopRecordCall() {
        // TODO: mover a modulo phoneJsSip.js
        this.phone.currentSession.sendDTMF('*5');
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
        if (this.pause_manager.pause_enabled && (session_data.is_dialer || session_data.is_inbound)){
            // Rechazar llamada por race condition
            this.phone.refuseCall();
        }
        if (this.forcesAutoAttend(session_data)) {
            clearTimeout(this.ACW_pause_timeout_handler);   // Por las dudas
            this.phone_fsm.acceptCall();
            this.phone.acceptCall();
            var fromUser = session_data.from;
            var message = interpolate(gettext('Conectado a %(fromUser)s'), {fromUser:fromUser}, true);
            this.view.setCallStatus(message, 'orange');
            this.manageContact(session_data);
            if (session_data.is_click2call) {
                // Seteo datos para redial
                this.lastDialedCall = session_data.remote_call;
            }
        } else {
            var from = session_data.from;
            $('#callerid').text(from);
            $('#omlcampname').text(session_data.remote_call['Omlcampname']);
            $('#omldid').text(session_data.remote_call['Omldid']);
            $('#omlinroutename').text(session_data.remote_call['Omlinroutename']);
            $('#modalReceiveCalls').modal('show');
            this.oml_api.eventRinging();
        }
    }

    forcesAutoAttend(session_data) {
        if (session_data.is_click2call) {
            return true;
        }
        if (session_data.is_dialer){
            if (session_data.remote_call.auto_attend){
                return session_data.remote_call.auto_attend == 'True';
            }
            else if (this.agent_config.auto_attend_DIALER) {
                return true;
            }
        }
        if (session_data.is_inbound){
            if (session_data.remote_call.auto_attend){
                return session_data.remote_call.auto_attend == 'True';
            }
            else if (this.agent_config.auto_attend_IN) {
                return true;
            }
        }
        if (session_data.is_off_campaign) {
            return true;
        }
        return false;
    }

    manageContact(session_data) {
        var call_data = session_data.remote_call;
        if (session_data.is_from_agent || session_data.is_off_campaign)
            return;
        this.getQualificationForm(call_data);
    }

    updateCallHistory() {
        var self = this;
        setTimeout(function() {
            self.oml_api.updateCallHistory(function(msg){$('#call_list').html(msg);});
        }, 2000);
    }

    getQualificationForm(call_data) {
        // 'calificar_llamada'
        var call_data_json = JSON.stringify(call_data);
        var url = Urls.calificar_llamada(encodeURIComponent(call_data_json));
        $('#dataView').attr('src', url);
    }

    getSelectContactForm(id_camp, tel) {
        // Elimino los caracteres no numericos
        var telephone = tel.replace(/\D+/g, '');
        telephone = telephone == '' ? 0 : telephone;
        // {% url 'identificar_contacto_a_llamar' %}
        var url = Urls.identificar_contacto_a_llamar(id_camp, telephone);
        $('#dataView').attr('src', url);
    }

    getIframe(url) {
        $('#dataView').attr('src', url);
    }

    loadVideoInFrame() {
        var options = {
            'width': 640,
            'height': 420,
            'parentNode': $('#video-container')[0],
            'configOverwrite': {
                'enableNoAudioDetection': false,
                'enableNoisyMicDetection': false,
                'startWithAudioMuted': true,
                'startWithVideoMuted': false,
                'startSilent': true,
                'hideLobbyButton': true,
                'requireDisplayName': false,
                'enableWelcomePage': false,
                'enableInsecureRoomNameWarning': false,
            },
            'interfaceConfigOverwrite': {
                'MOBILE_APP_PROMO': false,
                'SHOW_CHROME_EXTENSION_BANNER': false,
                'HIDE_KICK_BUTTON_FOR_GUESTS': true,
                'HIDE_INVITE_MORE_HEADER': true,
                'SHOW_JITSI_WATERMARK': false,
                'ENFORCE_NOTIFICATION_AUTO_DISMISS_TIMEOUT': 100,
                'TOOLBAR_BUTTONS': ['camera', 'fullscreen', 'chat', 'desktop'],
            }
        };

        if (this.phone.session_data.remote_call.video_channel) {
            var video_channel = this.phone.session_data.remote_call.video_channel;
            if (video_channel) {
                options.roomName = video_channel;
                this.jitsi_api = new JitsiMeetExternalAPI(this.video_domain, options);
                var jitsi_api = this.jitsi_api;
                this.jitsi_api.addEventListener('readyToClose', function(a){
                    jitsi_api.dispose();
                    this.view.buttonVideo.hide();
                });
                this.view.buttonVideo.show();
                this.view.reload_video_button.show();
            }
        }
    }

    unloadVideo() {
        if (this.jitsi_api) {
            this.jitsi_api.dispose();
            this.jitsi_api = undefined;
        }
        this.view.reload_video_button.hide();
        this.view.buttonVideo.hide();
    }

    reloadVideo() {
        if (this.jitsi_api) {
            this.unloadVideo();
        }
        this.loadVideoInFrame();
    }

    callOfCampPrivilege(){
        if (this.agent_config.call_off_camp){
            this.view.callOffCampaignMenuButton.prop('disabled', true);
        }
        else {
            this.view.callOffCampaignMenuButton.prop('disabled', false);
        }
    }

    disableOnHold() {
        if (this.agent_config.on_hold){
            var filter_on_call = PHONE_STATUS_CONFIGS['OnCall'].enabled_buttons.filter(function(value, index, arr){
                return value != 'onHold';
            });
            var filter_on_hold = PHONE_STATUS_CONFIGS['OnHold'].enabled_buttons.filter(function(value, index, arr){
                return value != 'onHold';
            });
            PHONE_STATUS_CONFIGS['OnCall'].enabled_buttons = filter_on_call;
            PHONE_STATUS_CONFIGS['OnHold'].enabled_buttons = filter_on_hold;
        }
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

class KeepAliveSender {
    constructor(max_session_age) {
        this.oml_api = new OMLAPI();
        this.interval = max_session_age / 2;
        this.interval_handler = undefined;
    }
    activate() {
        if (this.interval_handler == undefined) {
            var self = this;
            this.interval_handler = setInterval(function() { self.sendKeepAlive(); }, this.interval * 1000);
        }
    }
    deactivate() {
        if (this.interval_handler != undefined) {
            clearInterval(this.interval_handler);
            this.interval_handler = undefined;
        }
    }
    sendKeepAlive() {
        this.oml_api.sendKeepAlive();
    }
}

class OutTransferData {
    constructor() {
        var blindTransf = document.getElementById('blindTransf');
        var consultTransf = document.getElementById('consultTransf');
        var transfToAgent = document.getElementById('transfToAgent');
        var transfToCamp = document.getElementById('transfToCamp');
        var transfToNum = document.getElementById('transfToNum');
        var transfToQuickNum = document.getElementById('transfToQuickNum');

        this.is_blind = blindTransf.checked;
        this.is_consultative = consultTransf.checked;

        this.is_to_agent = transfToAgent.checked;
        if (this.is_to_agent)
            this.destination = $('select[id=agentToTransfer]').val();
        this.is_to_campaign = transfToCamp.checked;
        if (this.is_to_campaign)
            this.destination = $('select[id=campToTransfer]').val();
        this.is_to_number = transfToNum.checked;
        if (this.is_to_number)
            this.destination = $('#numberToTransfer').val();
        this.is_quick_contact = transfToQuickNum.checked;
        if (this.is_quick_contact)
            this.destination = $('select[id=quickNumToTransfer]').val();
    }

    get is_valid() {
        return (this.is_blind || (this.is_consultative && !this.is_to_campaign)) &&
            (this.is_to_agent || this.is_to_number || this.is_to_campaign || this.is_quick_contact) &&
            this.destination != '' && this.destination != undefined;
    }
}

class SurveyTransferData {
    constructor() {
        this.is_blind = true;
        this.is_to_number = true;
        this.destination = '098*';
    }
}

class AgentConfig {
    constructor() {
        this.auto_unpause = Number($('#auto_unpause').val());
        this.auto_attend_DIALER = $('#auto_attend_DIALER').val() == 'True';
        this.auto_attend_IN = $('#auto_attend_IN').val() == 'True';
        this.call_off_camp = $('#call_off_camp').val() == 'False';
        this.on_hold = $('#on_hold').val() == 'False';
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
