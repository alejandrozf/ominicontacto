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

$(function(){

    setInterval(function() {
    window.location.reload(true)
    }, 180000);

    $(".btn-submit").click(function (){
        var campana_id = $(this).attr("id");
        var action = $(this).attr("name");
        submit_form(campana_id, action);
    })

function submit_form(campana_id, action){
    $("#campana_id").val(campana_id);
    $("#form_estados_campanas").attr("action", action);
    $("#form_estados_campanas").submit();
}
});

function mostrar_detalle_campana(pk_campana) {
    if ($('#modal_ventana').attr('first-time') == 'true'){
        $('#modal_ventana').attr('first-time', 'false')
    }
    else{
        $('#modal_ventana').fadeOut('slow');
    }
    $('#modal_ventana').html("");
    $.get(Urls.campana_dialer_detalle_wombat(), {pk_campana: pk_campana},
            function (data) {
                $('#modal_ventana').html(data);
                $('#modal_ventana').fadeIn('slow');
            });
}
;

function mostrar_campanas_dialer_ocultas() {

    $.get(Urls.campana_dialer_mostrar_ocultas(),
            function (data) {
                $('#t_body_borradas').html(data);

            });
    }
    ;