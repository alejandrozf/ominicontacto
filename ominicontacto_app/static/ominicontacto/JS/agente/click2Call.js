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

// url_name = 'agente_llamar_contacto'
// url(r'^agente/llamar/$',

class Click2CallDispatcher {
	constructor (oml_api) {
		this.enabled = false;
		this.oml_api = oml_api;
	}

	enable() {
		this.enabled = true;
	};

	disable() {
		this.enabled = false;
	};

	call(agent_id, contact_id, campaign_type, campaign_id, campaign_name, phone) {
		if (this.enabled) {
			// Cargar los datos en el form.
	        // $("#click2call_form").submit();
		}
		else {
			console.log('Alertar al usuario que no es posible hacer una click2call');
		}
	}
}