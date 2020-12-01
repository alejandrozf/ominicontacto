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
/* global gettext Urls*/
function set_url_parameters(url, parameters){
    var new_url = url;
    for (var i = 0; i < parameters.length; i++) {
        var value = parameters[i];
        new_url = new_url.replace(String(i).repeat(4), value);
    }
    return new_url;
}

// TODO - Modelar un componente que se encargue de toda esta funcionalidad

var peticion_preview_en_curso = false;

$(document).ready(function(){

    var $errorAsignacionContacto = $('#errorAsignacionContacto');

    $('#campanasPreviewTable').DataTable( {
    // Convierte a datatable la tabla de campañas preview
        language: {
            search: gettext('Buscar:'),
            paginate: {
                first: gettext('Primero'),
                previous: gettext('Anterior'),
                next: gettext('Siguiente'),
                last: gettext('Último')
            },
            lengthMenu: gettext('Mostrar _MENU_ entradas'),
            info: gettext('Mostrando _START_ a _END_ de _TOTAL_ entradas'),
        }
    } );

    // asocia el click en la campaña preview a obtener los datos de un contacto
    var $panelContacto = $('#panel-contacto');
    var $contactoTelefono = $panelContacto.find('#contacto-telefono');
    var $contactoOtrosDatos = $panelContacto.find('#contacto-datos');
    var $inputAgente = $('#pk_agente');
    var $inputContacto = $('#pk_contacto');
    var $inputCampana = $('#pk_campana');
    var $inputCampanaNombre = $('#campana_nombre');

    function informarError(data, $button) {
        $button.addClass('disabled');
        $button.attr('title', data['data']);
    }

    function validarContacto() {
        if (peticion_preview_en_curso)
            return;

        var url = Urls.validar_contacto_asignado();
        var data = {
            'pk_agente': $inputAgente.val(),
            'pk_campana': $inputCampana.val(),
            'pk_contacto': $inputContacto.val(),
        };
        peticion_preview_en_curso = true;
        $.post(url, data).success(function(data) {
            // comprobamos si el contacto todavía sigue asignado al agente
            // antes de llamar
            if (data['contacto_asignado'] == true) {
                // hacemos click en el botón del form para iniciar la
                // llamada
                var campaign_id = $('#pk_campana').val();
                var campaign_type = $('#tipo_campana').val();
                var contact_id = $('#pk_contacto').val();
                var phone = data['telefono_contacto'];
                var call_type = $('#click2call_type').val();
                var click2call = window.parent.click2call;
                click2call.call_contact(campaign_id, campaign_type, contact_id, phone, call_type);
            }
            else {
                // se muestra modal con mensaje de error
                var errorMessage = gettext('OPS, se venció el tiempo de asignación de este contacto.\
Por favor intente solicitar uno nuevo');
                $errorAsignacionContacto.html(errorMessage);
            }
        }).always(function () {
            peticion_preview_en_curso = false;
        });
    }

    $('#validar_contacto').on('click', validarContacto);

    $('.obtener-contacto').each(function() {
        $(this).on('click', function() {
            if (peticion_preview_en_curso){
                return;
            }
            peticion_preview_en_curso = true;
            var $button = $(this);
            var nombreCampana = $button.text();
            var idCampana = $button.attr('data-campana');
            var url = Urls.campana_preview_dispatcher(idCampana);
            $.post(url)
                .success(function (data) {
                    if (data['result'] != 'OK') {
                        informarError(data, $button);
                    }
                    else {                // se obtienen los datos del contacto
                        $('#validar_contacto').show();
                        $panelContacto.attr('class', 'col-md-4 col-md-offset-1');
                        // actualizamos el teléfono del contacto
                        var contactoTelefono = data['telefono_contacto'];
                        $contactoTelefono.text(contactoTelefono);
                        $inputAgente.attr('value', data['agente_id']);
                        $inputContacto.attr('value', data['contacto_id']);
                        $inputCampana.attr('value', idCampana);
                        $inputCampanaNombre.attr('value', nombreCampana);

                        // Limpiamos la información de algún contacto anterior
                        $contactoOtrosDatos.html('');

                        if (data['code'] == 'contacto-asignado'){
                            $errorAsignacionContacto.html(gettext('Contacto asignado por llamado previo.\
 Califique el contacto o liberelo para poder recibir un nuevo contacto.'));
                            $('#liberar_contacto').show();
                            $('#calificar_contacto').show();
                            var url_parameters = [idCampana, data['contacto_id'], data['agente_id']];
                            var calificar_contacto_url = Urls.calificacion_formulario_update_or_create('0000', '1111');
                            var calificar_url = set_url_parameters(calificar_contacto_url, url_parameters);
                            $('#calificar_contacto').attr('href', calificar_url);
                        }
                        else{
                            $('#liberar_contacto').hide();
                            $('#calificar_contacto').hide();
                            $errorAsignacionContacto.html('');
                        }

                        // Actualizamos los datos del contacto obtenido
                        for (var campo in data['datos_contacto']) {
                            var capitalizedCampo = campo.charAt(0).toUpperCase() + campo.slice(1);
                            var campoData = '<p><span style="font-weight: bold;">'+capitalizedCampo+': </span>' +
                    data['datos_contacto'][campo] + '</p>';
                            $contactoOtrosDatos.append(campoData);
                        }
                    }

                })
                .fail( function (data) {
                    informarError(data, $button);
                    console.log('Fail: ', data);
                })
                .error( function (data) {
                    informarError(data, $button);
                    console.log('Error: ', data);
                })
                .always( function () {
                    peticion_preview_en_curso = false;
                });
        });
    });

    $('#liberar_contacto').on('click', function(){
        if (peticion_preview_en_curso){
            return;
        }
        peticion_preview_en_curso = true;
        var url = Urls.liberar_contacto_asignado_agente();
        var data = {
            'campana_id': $inputCampana.val(),
        };
        $.post(url, data)
            .success(function(data) {
                // comprobamos si el contacto todavía sigue asignado al agente
                // antes de llamar
                if (data['status'] == 'OK') {
                    $errorAsignacionContacto.html('');
                    $contactoOtrosDatos.html(gettext('Contacto Liberado'));
                    $('#validar_contacto').hide();
                    $('#liberar_contacto').hide();
                    $('#calificar_contacto').hide();
                }
                else {
                    // se muestra modal con mensaje de error
                    var errorMessage = gettext('No se pudo liberar al contacto. Intente pedir otro.');
                    $errorAsignacionContacto.html(errorMessage);
                }
            })
            .always( function () {
                peticion_preview_en_curso = false;
            });

    });

});
