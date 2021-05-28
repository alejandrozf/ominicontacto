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

$('#addAllSupervisors').change(function() {
    if(this.value == 1){
        // Update campaign
        if(this.checked) {
            $('input[name="supervisors"]').each( function () { this.checked = true; });
        }else{
            $('input[name="supervisors"]').each( function () { this.checked = false; });
        }
    }else{
        // Create campaign
        if(this.checked) {
            $('input[name="4-supervisors"]').each( function () { this.checked = true; });
        }else{
            $('input[name="4-supervisors"]').each( function () { this.checked = false; });
        }
    }
});