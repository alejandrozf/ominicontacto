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
/*
 * Phone View for use with PhoneJSController 
 */
class PhoneJSView {
    constructor () {
        /* Streams */
        this.local_audio = $('#localAudio')[0];
        this.remote_audio = $('#remoteAudio')[0];

        /* Inputs */
        this.callButton = $("#call");
        this.hangUpButton = $("#endCall");

        /* Outputs */
        this.timebar = $('#timeBar');
        this.sipStatus = $('#SipStatus');
        this.callStatus = $('#CallStatus');
        this.user_status = $("#UserStatus");
    }

    setSipStatus(status_code) {
        var text = SIP_STATUSES[status_code].text;
        var icon = SIP_STATUSES[status_code].icon;

        this.sipStatus.children().remove()
        var iconStatus = document.createElement('img');
        iconStatus.id = "imgStatus";
        iconStatus.src = "../../static/ominicontacto/Img/" + icon;
        $(this.sipStatus).append(iconStatus);
        var textSipStatus = document.createElement('em');
        textSipStatus.id = "textSipStatus";
        textSipStatus.append(document.createTextNode(text));
        $(this.sipStatus).append(textSipStatus);
    };

    setCallStatus(text, color) {
        this.callStatus.children().remove();
        var callSipStatus = document.createElement("em");
        var textCallSipStatus = document.createTextNode(text);
        callSipStatus.style.color = color;
        callSipStatus.id = "dial_status";
        callSipStatus.append(textCallSipStatus);
        this.callStatus.append(callSipStatus);
    }

    setUserStatus(class_name, inner_html){
        this.updateButton(this.user_status, class_name, inner_html);
    };

    updateButton(button_object, class_name, inner_html) {
        button_object.className = class_name;
        var lastval = button_object.html();
        button_object.html(inner_html);
        return lastval;
    };

    setStateInputStatus(state_name) {
        var not_in_call = CALL_STATUSES.indexOf(state_name) == -1
        this.hangUpButton.prop('disabled', not_in_call);
        var status_color = STATUS_COLOR[state_name];
        this.setStateColors(status_color);
    }

    setStateColors(color) {
        this.timebar.css('background-color', color);
    }

}

SIP_STATUSES = {
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
}

var CALL_STATUSES = ['Calling', 'OnCall', 'Transfering', 'OnHold']

var STATUS_COLOR = {
    'Initial': '#888888',
    'End':  '#888888',
    'Ready': '#ECEEEA',
    'Paused': '#e0b93d',
    'Calling': '#bfef7a',
    'OnCall': '#8fc641',
    'OnHold': '#9ab97b',
    'DialingTransfer': '#bfef7a',
    'Transfering': '#bfef7a',
    'ReceivingCall': '#bfef7a',
}
