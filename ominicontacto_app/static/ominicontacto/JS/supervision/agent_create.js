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

$(function () {
    const AGENT_TYPE = '5';
    const CAMP_ACTIVA = 2;
    const CAMP_PAUSADA = 5;
    const rol = $('#id_0-rol');
    const labelGroup = $('label[for="id_0-grupo"]');
    const group = $('#id_0-grupo');
    const campaignType = $('#id_1-campaign_type');
    const campaignsByType = $('#id_1-campaigns_by_type');

    function getCampaingsByType (type) {
        return new Promise((resolve, reject) => {
            try {
                $.ajax({
                    url: `${Urls.api_campanas_de_supervisor()}?type=${type}&status=[${CAMP_ACTIVA},${CAMP_PAUSADA}]`,
                    type: 'GET',
                    dataType: 'json',
                    success: (response) => {
                        resolve(response);
                    },
                    error: (xhr, status, error) => {
                        console.error('===> ERROR AJAX');
                        console.error(error);
                        resolve([]);
                    },
                });
            } catch (error) {
                console.error('===> ERROR al obtener campanas por tipo');
                console.error(error);
                resolve([]);
            }
        });
    }

    function handleGroupByRol (rol) {
        if (rol === AGENT_TYPE) {
            group.show();
            labelGroup.show();
        } else {
            group.hide();
            group.val('');
            labelGroup.hide();
        }
    }

    function updateSelect (datos) {
        campaignsByType.empty();
        $.each(datos, function (_, { id, nombre }) {
            campaignsByType.append(
                $('<option>', {
                    value: id,
                    text: nombre,
                })
            );
        });
    }

    handleGroupByRol(rol.val());

    rol.change(function () {
        handleGroupByRol($(this).val());
    });

    campaignType.change(async function () {
        const type = $(this).val();
        const opciones = await getCampaingsByType(type);
        updateSelect(opciones);
    });
});

function obtener_campanas_agente(pk_agent) {
    var $campanasAgenteModal = $('#campanasAgenteModal');
    var filter = '?status=[2,5,6]&agent=' + pk_agent;
    var table = $('#campanasAgenteTable').DataTable( {
        ajax: {
            url: Urls.api_campanas_de_supervisor() + filter,
            dataSrc: '',
        },
        columns: [
            { 'data': 'id'},
            { 'data': 'nombre',},
            { 'data': 'objetivo'},
        ],
        paging: false,
    } );
    $campanasAgenteModal.modal('show');
    table.destroy();
}
