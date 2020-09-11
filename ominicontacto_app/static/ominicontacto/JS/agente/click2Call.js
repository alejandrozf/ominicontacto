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
/* global Urls*/

class Click2CallDispatcher {
    /*
    *  Esta clase será la encargada de despachar los pedidos de click to call que ejecute el
    *  usuario. Se deshabilita mientras el UserAgent no este registrado, cuando haya una llamada
    *  en curso, etc...
    */
    constructor (oml_api, agent_id) {
        this.AGENT = 'AGENT';
        this.EXTERNAL = 'EXTERNAL';
        this.enabled = false;
        this.oml_api = oml_api;
        this.agent_id = agent_id;
    }

    enable() {
        this.enabled = true;
        $('#sumTime').css('background-color', 'palegreen');
    }

    disable() {
        this.enabled = false;
        $('#sumTime').css('background-color', 'forestgreen');
    }

    call_contact(campaign_id, campaign_type, contact_id, phone, click2call_type='click2call'){
        this.obligarCalificacion = $('#obligar-calificacion').val();
        if (this.obligarCalificacion == 'True'){
            var self = this;
            this.oml_api.llamadaCalificada(function(){self.make_call(campaign_id, campaign_type, contact_id, phone, click2call_type='click2call');}, function(call_data){self.make_disposition(call_data);});
        }
        else{
            this.make_call(campaign_id, campaign_type, contact_id, phone, click2call_type='click2call');
        }
    }

    make_call(campaign_id, campaign_type, contact_id, phone, click2call_type='click2call') {
        if (this.enabled) {
            this.oml_api.startClick2Call(this.agent_id, campaign_id, campaign_type,
                contact_id, phone, click2call_type);
        }
        else {
            console.log('Alertar al usuario que no es posible hacer una click2call');
        }
    }

    make_disposition(calldata){
        $('#obligarCalificarCall').modal('show');
        $('#obligarCalificarCall_submit').click(function(){
            var call_data_json = JSON.stringify(calldata);
            var url = Urls.calificar_llamada(encodeURIComponent(call_data_json));
            $('#dataView').attr('src', url);
            $('#obligarCalificarCall').modal('hide');
        });
    }

    call_agent(agent_id){
        this.obligarCalificacion = $('#obligar-calificacion').val();
        if (this.obligarCalificacion == 'True'){
            var self = this;
            this.oml_api.llamadaCalificada(function(){self.make_agent_call(agent_id);}, function(call_data){
                $('#modalCallOffCamp').modal('hide');
                self.make_disposition(call_data);
            });
        }
        else{
            this.make_agent_call(agent_id);
        }
    }

    make_agent_call(agent_id) {
        if (this.enabled) {
            this.oml_api.startCallOutsideCampaign(this.AGENT, agent_id);
        }
        else {
            console.log('Alertar al usuario que no es posible hacer una click2call');
        }
    }
    call_external(phone){
        this.obligarCalificacion = $('#obligar-calificacion').val();
        if (this.obligarCalificacion == 'True'){
            var self = this;
            this.oml_api.llamadaCalificada(function(){self.make_external_call(phone);}, function(call_data){
                $('#modalCallOffCamp').modal('hide');
                self.make_disposition(call_data);
            });
        }
        else{
            this.make_external_call(phone);
        }
    }

    make_external_call(phone) {
        if (this.enabled) {
            this.oml_api.startCallOutsideCampaign(this.EXTERNAL, phone);
        }
        else {
            console.log('Alertar al usuario que no es posible hacer una click2call');
        }
    }
}
