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
            /* Maneja el submit del ordenamiento.*/
            $(".orden").click(function (){
                var sentido_orden = $(this).attr('data-sentido-orden');
                $("#id_sentido_orden").val(sentido_orden);
                var url = $(this).attr('data-url');
                $("#form-orden-campos").attr('action', url);
                $("#form-orden-campos").submit();
            });
    
            /* Maneja la adicion de un item a la lista */
            $("#agregar_lista").click(function (){
                $('#value_item_error').hide();
                $('#repeticion_item_error').hide();
                var item = $('#id_value_item').val();
                var list = $('#id_list_values').val();
                if (item == ''){
                    $('#value_item_error').show();
                }
                else {
                    var lista = [];
                    $('#id_list_values').find('option').each(function(){  lista.push($(this).val()); });
                    if (lista.indexOf(item)== -1){
                        $('#id_list_values').append($("<option>").val(item).html(item));
                        $('#id_value_item').val("");
                        lista.push(item);
                        $("#id_values_select").val(JSON.stringify(lista));        
                    }
                    else {
                        $('#repeticion_item_error').show();
                    }
                    
                }
            });

            $("#eliminar_lista").click(function (){
                var list_values = document.getElementById("id_list_values");
                var opt_seleccionados = list_values.selectedOptions;
                var z = 0;
                var length = opt_seleccionados.length;
                 while (z < length) {
                    var child = opt_seleccionados[0];
                        list_values.removeChild(child);
                    z++;
                   }
            });
            $("#id_tipo").change(function() {
                if( $("#id_tipo").val() == 3 ) {

                    $("#lista_control").slideDown('fast');
                    $("#separador_lista_control").slideDown('fast');
                    $("#id_value_item").removeAttr('disabled');
                    $("#id_list_values").removeAttr('disabled');
                    $("#agregar_lista").removeAttr('disabled');
                    $("#eliminar_lista").removeAttr('disabled');
                } else {
                    $("#lista_control").slideUp('fast');
                    $("#separador_lista_control").slideUp('fast');
                    $("#id_value_item").attr('disabled', true);
                    $("#id_list_values").attr('disabled', true);
                    $("#agregar_lista").attr('disabled', true);
                    $("#eliminar_lista").attr('disabled', true);

                }
            });

            /**/

    });