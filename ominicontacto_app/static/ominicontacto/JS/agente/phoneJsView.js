
/* Copyright (C) 2018 Freetech Solutions

 This file is part of OMniLeads

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Lesser General Public License version 3, as published by
 the Free Software Foundation.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Lesser General Public License for more details.

 You should have received a copy of the GNU Lesser General Public License
 along with this program.  If not, see http://www.gnu.org/licenses/.

*/

/* global gettext OMLAPI */

var CAMPANA_TYPE_ENTRANTE = 3;

/*
 * Phone View for use with PhoneJSController
 */
class PhoneJSView {
    constructor () {
        /*Temporal Debug */ this.consultToCampEnabled = true;
        /* Streams */
        this.local_audio = $('#localAudio')[0];
        this.remote_audio = $('#remoteAudio')[0];

        /* Inputs */
        // TODO: Revisar cuales se usan y cuales no.
        this.resumeButton = $('#Resume');
        this.pauseButton = $('#Pause');
        this.pauseMenu = $('#modalPause');
        this.changeCampaignButton = $('#changeCampAssocManualCall');
        this.changeCampaignMenu = $('#modalSelectCmp');
        this.timebar = $('#timeBar');
        this.callButton = $('#call');
        this.callOffCampaignMenuButton = $('#call_off_campaign_menu');
        this.callAgentButton = $('#call_agent');
        this.callPhoneOffCampaignButton = $('#call_phone_off_campaign');
        this.callQuickOffCampaignButton = $('#call_quick_contact');
        this.numberDisplay = $('#numberToCall');
        this.redialButton = $('#redial');
        this.holdButton = $('#onHold');
        this.transferButton = $('#Transfer');
        this.conferButton = $('#Confer');
        this.dtmfButton = $('#dtmf');
        this.endTransferButton = $('#EndTransfer');
        this.transferOutMenu = $('#modalTransfer');
        this.inboundCallMenu = $('#modalReceiveCalls');
        this.tagCallButton = $('#SignCall');
        this.hangUpButton = $('#endCall');
        this.recordCall = $('#recordCall');
        this.imgRecordOffUrl = $('#recordOffUrl').val();
        this.imgRecordOnUrl = $('#recordOnUrl').val();

        this.keypad_buttons_ids = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
            'asterisk', 'hashtag'];
        this.inputs_ids = ['Resume', 'Pause', 'changeCampAssocManualCall',
            'call', 'numberToCall', 'redial', 'onHold', 'Transfer', 'dtmf',
            'Confer', 'EndTransfer', 'SignCall', 'endCall',
            'call_off_campaign_menu', 'recordCall'];
        this.modal_menus_ids = ['modalPause', 'modalSelectCmp',
            'modalTransfer', 'modalReceiveCalls', 'modalCallOffCamp',
            'modalDtmf'];

        /* Outputs */
        this.sipStatus = $('#SipStatus');
        this.callStatus = $('#CallStatus');
        this.user_status = $('#UserStatus');
        this.conferAgent = $('#ConferAgent');

        /* Other buttons & Modal menus */
        this.selectCampaignButton = $('#SelectCamp');
        this.setPauseButton = $('#setPause');
        this.tagCallMenu = $('#modalSignCall');
        this.makeTransferButton = $('#makeTransfer');
        this.makeTransferToSurveyButton = $('#makeTransferToSurvey');
        this.confirmTransferButton = $('#buttonContinueTransfer');
        this.cancelTransferButton = $('#buttonCancelTransfer');
        this.callOffCampaignMenu = $('#modalCallOffCamp');
        this.reload_video_button = $('#reload_video_id');
        this.buttonVideo = $('#buttonVideo');
        this.videoJitsi = $('#video-container');
        this.modalDtmf = $('#modalDtmf');
        this.dtmfInput = $('#dtmfInput');
        this.dtmfError = $('#dtmfError');
        this.sendDtmfButton = $('#sendDtmf');

        this.startKeypad();
        this.startTransferMenu();

        this.session_data = undefined;
    }

    setCallSessionData(session_data) {
        this.session_data = session_data;
    }

    startKeypad() {
        var self = this;
        $('.key').click(function(e) {
            var pressed_key = e.currentTarget.childNodes[0].data;
            var dialedNumber = self.numberDisplay.val();
            self.numberDisplay.val(dialedNumber + pressed_key);
        });
    }

    startTransferMenu() {
        var self = this;
        var transfToCamp = document.getElementById('transfToCamp');
        var transfToNum = document.getElementById('transfToNum');
        var transfToQuickNum = document.getElementById('transfToQuickNum');

        this.transferButton.click(function() {
            $('#blindTransf').prop('checked', false);
            $('#consultTransf').prop('checked', false);

            $('#transfToNum').prop('disabled', true);
            $('#transfToAgent').prop('disabled', true);
            $('#transfToCamp').prop('disabled', true);
            $('#transfToQuickNum').prop('disabled', true);

            $('#campToTransfer').prop('disabled', true);
            $('#numberToTransfer').prop('disabled', true);
            $('#agentToTransfer').prop('disabled', true);
            $('#quickNumToTransfer').prop('disabled', true);

            self.transferOutMenu.modal('show');
            var oml_api = new OMLAPI();
            $('#agentToTransfer').find('option').remove();
            oml_api.getAgentes(self.cargarAgentes);
            if (self.session_data.survey) {
                $('#transferToSurveyContainer').show();
            }
            else {
                $('#transferToSurveyContainer').hide();
            }
        });

        $('#blindTransf').change(function() {
            if (this.checked) {
                $('#transfToNum').prop('disabled', false);
                $('#transfToAgent').prop('disabled', false);
                if (self.session_data.is_off_campaign) {
                    $('#transfToCamp').prop('disabled', true);
                    $('#campToTransfer').prop('disabled', true);
                    $('#transfToCamp').prop('checked', false);
                }
                else {
                    $('#transfToCamp').prop('disabled', false);
                    $('#campToTransfer').prop('disabled', false);
                    $('#transfToCamp').prop('checked', true);
                }
                $('#transfToQuickNum').prop('disabled', false);
            }
        });

        $('#consultTransf').change(function() {
            if (this.checked) {
                $('#transfToNum').prop('disabled', false);
                $('#transfToAgent').prop('disabled', false);
                if (self.consultToCampEnabled){  // Eliminar condicional al habilitar permanente
                    $('#transfToCamp').prop('disabled', false);
                    $('#campToTransfer').prop('disabled', false);
                }
                else {
                    $('#transfToCamp').prop('disabled', true);
                    $('#campToTransfer').prop('disabled', true);
                }
                $('#transfToCamp').prop('checked', false);
                $('#transfToQuickNum').prop('disabled', false);
            }
        });

        $('#transfToNum').change(function() {
            if (this.checked) {
                $('#numberToTransfer').prop('disabled', false);
                $('#campToTransfer').prop('disabled', true);
                $('#agentToTransfer').prop('disabled', true);
                $('#quickNumToTransfer').prop('disabled', true);
                $('#transfToQuickNum').prop('checked', false);
            }
        });

        $('#transfToCamp').change(function() {
            if (this.checked) {
                $('#campToTransfer').prop('disabled', false);
                $('#numberToTransfer').prop('disabled', true);
                $('#agentToTransfer').prop('disabled', true);
                $('#quickNumToTransfer').prop('disabled', true);
            }
        });

        $('#transfToAgent').change(function() {
            if (this.checked) {
                $('#agentToTransfer').prop('disabled', false);
                $('#campToTransfer').prop('disabled', true);
                $('#numberToTransfer').prop('disabled', true);
                $('#quickNumToTransfer').prop('disabled', true);
                $('#transfToQuickNum').prop('checked', false);
            }
        });

        $('#transfToQuickNum').change(function() {
            if (this.checked) {
                $('#agentToTransfer').prop('disabled', true);
                $('#campToTransfer').prop('disabled', true);
                $('#numberToTransfer').prop('disabled', true);
                $('#quickNumToTransfer').prop('disabled', false);
                $('#transfToNum').prop('checked', false);
            }
        });
    }

    disable(elements) {
        this.setDisabledProp(elements, true);
    }

    enable(elements) {
        this.setDisabledProp(elements, true);
    }

    setDisabledProp(elements, property) {
        for (var i=0; i < elements.length; i++) {
            var element = elements[i];
            element.prop('disabled', property);
        }
    }

    setSipStatus(status_code) {
        var text = SIP_STATUSES[status_code].text;
        var icon = SIP_STATUSES[status_code].icon;

        this.sipStatus.children().remove();
        var iconStatus = document.createElement('img');
        iconStatus.id = 'imgStatus';
        iconStatus.src = '../static/ominicontacto/Img/' + icon;
        $(this.sipStatus).append(iconStatus);
        var textSipStatus = document.createElement('em');
        textSipStatus.id = 'textSipStatus';
        textSipStatus.append(document.createTextNode(text));
        $(this.sipStatus).append(textSipStatus);
    }

    setCallStatus(text, color) {
        this.callStatus.children().remove();
        var callSipStatus = document.createElement('em');
        var textCallSipStatus = document.createTextNode(text);
        callSipStatus.style.color = color;
        callSipStatus.id = 'dial_status';
        callSipStatus.append(textCallSipStatus);
        this.callStatus.append(callSipStatus);
    }

    setConferenceAgent(text, color) {
        this.conferAgent.children().remove();
        var conferAgentEM = document.createElement('em');
        var textConferAgent = document.createTextNode(text);
        conferAgentEM.style.color = color;
        conferAgentEM.id = 'confer_agent';
        conferAgentEM.append(textConferAgent);
        this.conferAgent.append(conferAgentEM);
    }

    cargarAgentes(agentes) {
        agentes.sort(ordenAgentes);
        for (var i = 0; i < agentes.length; i++) {
            var id = agentes[i].id;
            var full_name = agentes[i].full_name;
            var status = agentes[i].status;
            if (status == 'READY') {
                $('#agentToTransfer').append('<option value=\'' + id + '\'>' + full_name + ': ' + status + '</option>');
            }
            else {
                $('#agentToTransfer').append('<option disabled="disabled" value=\'' + id + '\'>' + full_name + ': ' + status + '</option>');
            }
        }
    }

    cargarCampanasActivas(campanas) {
        for (var i = 0; i < campanas.length; i++) {
            if (campanas[i].type == CAMPANA_TYPE_ENTRANTE) {
                var id = campanas[i].id;
                var nombre = campanas[i].nombre;
                $('#campToTransfer').append('<option value=\'' + id + '\'>' + nombre + '</option>');            }
        }
    }

    setUserStatus(class_name, inner_html){
        this.updateButton(this.user_status, class_name, inner_html);
    }

    updateButton(button_object, class_name, inner_html) {
        button_object.className = class_name;
        var lastval = button_object.html();
        button_object.html(inner_html);
        return lastval;
    }

    getDialedNumber() {
        return this.numberDisplay.value;
    }

    setStateInputStatus(state_name) {
        var status_config = this.getStateConfig(state_name);
        this.setKeypadButtonsEnabled(status_config.keypad_enabled);
        this.setInputsEnabled(status_config.enabled_buttons);
        this.setStateColors(status_config.color);
    }

    setKeypadButtonsEnabled(enabled) {
        for (var i=0; i<this.keypad_buttons_ids.length; i++) {
            var id = this.keypad_buttons_ids[i];
            $('#' + id).prop('disabled', !enabled);
        }
    }

    setInputsEnabled(enabled_ones) {
        for (var i=0; i<this.inputs_ids.length; i++) {
            var id = this.inputs_ids[i];
            $('#' + id).prop('disabled', enabled_ones.indexOf(id) == -1);
        }
    }

    setStateColors(color) {
        this.timebar.css('background-color', color);
    }


    toogleVisibilityRecordButtons(sessionData) {
        // si no se recibe desde Asterisk un nombre para el archivo de grabación
        // significa que la llamada pertenece a un campaña no está configurada
        // para grabar llamadas
        var recordingFile = sessionData.remote_call.rec_filename;
        if (recordingFile == '') {
            this.tagCallButton.attr('disabled', true);
        }
        else {
            this.recordCall.attr('disabled', true);
        }
    }

    closeAllModalMenus() {
        for (var i = 0; i < this.modal_menus_ids.length; i++) {
            var id = this.modal_menus_ids[i];
            $('#' + id).modal('hide');
        }
    }

    getStateConfig(state_name) {
        return PHONE_STATUS_CONFIGS[state_name];
    }

    showHideVideo(){
        this.videoJitsi.toggle();
    }
}

var PHONE_STATUS_CONFIGS = {
    'Initial': {
        keypad_enabled: false,
        enabled_buttons: [],
        color: '#888888',
    },
    'End': {
        keypad_enabled: false,
        enabled_buttons: [],
        color: '#888888',
    },
    'LoggingToAsterisk': {
        keypad_enabled: false,
        enabled_buttons: [],
        color: '#888888',
    },
    'Ready': {
        keypad_enabled: true,
        enabled_buttons: ['Pause', 'changeCampAssocManualCall', 'call', 'numberToCall', 'redial',
            'call_off_campaign_menu'],
        color: '#ECEEEA',
    },
    'Pausing': {
        keypad_enabled: false,
        enabled_buttons: [],
        color: '#e0b93d',
    },
    'Paused': {
        keypad_enabled: true,
        enabled_buttons: ['Pause', 'Resume', 'changeCampAssocManualCall', 'call', 'numberToCall',
            'redial', 'call_off_campaign_menu'],
        color: '#e0b93d',
    },
    'Calling': {
        keypad_enabled: false,
        enabled_buttons: ['endCall'],
        color: '#bfef7a',
    },
    'OnCall': {
        keypad_enabled: true,
        enabled_buttons: ['onHold', 'Transfer', 'dtmf','endCall', 'SignCall', 'recordCall'],
        color: '#8fc641',
    },
    'DialingTransfer': {
        keypad_enabled: false,
        enabled_buttons: [],
        color: '#bfef7a',
    },
    'Transfering': {
        keypad_enabled: true,
        enabled_buttons: ['EndTransfer', 'SignCall', 'endCall', 'Confer', 'recordCall'],
        color: '#bfef7a',
    },
    'ReceivingCall': {
        keypad_enabled: false,
        enabled_buttons: [],
        color: '#bfef7a',
    },
    'OnHold': {
        keypad_enabled: false,
        enabled_buttons: ['onHold', 'endCall'],
        color: '#9ab97b',
    },
};

var SIP_STATUSES = {
    'NO_ACCOUNT': {text: gettext('Desconectado') , icon: 'greydot.png'},
    'REGISTERED': {text: gettext('Registrado') , icon: 'greendot.png'},
    'UNREGISTERED': {text: gettext('No Registrado') , icon: 'reddot.png'},
    'NO_SIP': {
        text: gettext('El SIP Proxy no responde, contacte a su administrador') ,
        icon: 'redcross.png'
    },
    'REGISTER_FAIL': {
        text: gettext('Fallo en la registración, contacte a su administrador') ,
        icon: 'redcross.png'
    },
};

function ordenAgentes(ag1, ag2){
    // READY va Primero
    if (ag1.status == 'READY' && ag2.status != 'READY')
        return -1;
    if (ag2.status == 'READY' && ag1.status != 'READY')
        return 1;
    // Si ambos o ninguno estan READY, orden por id
    return Number(ag1.id) - Number(ag2.id);
}
