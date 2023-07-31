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
/* global Urls */
const $modalDBContactos = $('#modalDBContactos');
const $selectDBContactos = $('#camp_bd_contactos');
const $modalContentDBContactos = $('#modalContentDBContactos');
const $modalTitle = $('#modalTitle');
const $cancelModal = $('#cancelModal');

$selectDBContactos.change(function () {
    try {
        $modalDBContactos.modal('hide');
        const selectText = $(this).find('option:selected').text();
        const selectValue = $(this).val() || null;
        if (selectValue) {
            $.ajax({
                url: Urls.api_contact_database_campaings(selectValue),
                method: 'GET',
                success: function (response) {
                    const { data, status } = response;
                    const { campanas } = data;
                    if (status === 'SUCCESS' && (campanas && campanas.length > 0)) {
                        let html = '<ul>';
                        campanas.forEach((c) => {
                            html += `<li>${c.nombre}</li>`;
                        });
                        html += '</ul>';
                        $modalTitle.html(`Campañas asociadas a la DB: ${selectText}`);
                        $modalContentDBContactos.html(html);
                        $modalDBContactos.modal('show');
                    }
                },
                error: function (xhr, status, error) {
                    console.error('Error:', error);
                },
            });
        }
    } catch (error) {
        console.error('===> ERROR: Al obtener info de la base de contactos');
        console.error(error);
    }
});

$cancelModal.click(function () {
    $selectDBContactos.val(null);
    $modalDBContactos.modal('hide');
});
