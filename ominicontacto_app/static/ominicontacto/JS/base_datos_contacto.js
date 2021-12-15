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
function getColumsNameOfDBContactos() {
    return $('#db_metadata_columnas').val().split(' ');
}

function checkAllOptions() {
    getColumsNameOfDBContactos().forEach(element => {
        document.getElementById(`check_${element}`).checked = true;
    });
}

function cleanAllOptions() {
    getColumsNameOfDBContactos().forEach(element => {
        document.getElementById(`check_${element}`).checked = false;
    });
}

$(function () {
    $('#btnToShowBDInfo').click(function () {
        getColumsNameOfDBContactos().forEach(element => {
            var headElement = document.getElementById(`db_metadata_head_${element}`);
            var elementsByClass = document.getElementsByClassName(`db_metadata_body_${element}`);
            if (document.getElementById(`check_${element}`).checked) {
                headElement.classList.remove('d-none');
                for (const e of elementsByClass) {
                    e.classList.remove('d-none');
                }
            } else {
                headElement.classList.add('d-none');
                for (const e of elementsByClass) {
                    e.classList.add('d-none');
                }
            }
        });
        $('#modalToShowMoreDBInfo').modal('hide');
    });

    $('#selectAllData').click(function () {
        if ($(this).is(':checked')) {
            checkAllOptions();
        } else {
            cleanAllOptions();
        }
    });
});