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
/* TODO: este código debería estar en un archivo separado  */

function makeClick2Call(campaign_id, campaign_type, contact_id, phone, call_type) {
    // Utilizar click2call manager para intentar llamar.
    // Ver si tengo acceso
    if (window.parent.hasOwnProperty('click2call')){
        var click2call = window.parent.click2call;
        click2call.call_contact(campaign_id, campaign_type, contact_id, phone, call_type);
    } else {
        // console.log('Alertar al usuario que no es posible hacer una click2call');
    }
};
