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

/* global Urls */
/* global moment */
/* global gettext */
/* global get_ranges */

$(function() {
    var start = moment();
    var end = moment();
    function cb(start, end) {
        $('#id_fecha').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
    }

    $('#id_fecha').on('apply.daterangepicker', function(ev, picker) {
        $(this).val(picker.startDate.format('DD/MM/YYYY') + ' - ' + picker.endDate.format('DD/MM/YYYY'));
    });

    $('#id_fecha').on('cancel.daterangepicker', function() {
        $(this).val('');
    });

    // Init daterange plugin
    var ranges = get_ranges();
    $('#id_fecha').daterangepicker(
        {
            locale: {
                format: 'DD/MM/YYYY'
            },
            startDate: start,
            endDate: end,
            ranges: ranges,
        }, cb);

    cb(start, end);

    $('#id_agente').change(function() {
        if( $('#id_agente').val() == null) {
            $('#id_grupo_agente').removeAttr('disabled');
            $('#id_todos_agentes').removeAttr('disabled');
        } else {
            $('#id_grupo_agente').attr('disabled', true);
            $('#id_todos_agentes').attr('disabled', true);
        }
    });

    $('#id_grupo_agente').change(function() {
        if( $('#id_grupo_agente').val() == '') {
            $('#id_agente').removeAttr('disabled');
            $('#id_todos_agentes').removeAttr('disabled');
        } else {
            $('#id_agente').attr('disabled', true);
            $('#id_todos_agentes').attr('disabled', true);
        }
    });

    $('#id_todos_agentes').change(function() {
        if( $('#id_todos_agentes').prop('checked') ) {
            $('#id_agente').attr('disabled', true);
            $('#id_grupo_agente').attr('disabled', true);
        } else {
            $('#id_agente').removeAttr('disabled');
            $('#id_grupo_agente').removeAttr('disabled');
        }
    });

    $('.tiemposAgenteModal').click(function(event){
        event.preventDefault();
        var id_agente;
        id_agente = $(this).attr('id_agente');
        var fecha_desde = $(this).attr('fecha_desde');
        var fecha_hasta = $(this).attr('fecha_hasta');
        $.ajax({
            type:'POST',
            url: Urls.reportes_agente_por_fecha(),
            data:{
                'id_agente': id_agente,
                'fecha_desde': fecha_desde,
                'fecha_hasta': fecha_hasta,
            },
            success: function (data) {
                // alert(data, textStatus);
                $('#output').html(data.tbody); // append to inner html
                $('#nombre_agente').html(data.nombre_agente);
                var rep_table = $('#reporteFechaModalTable').DataTable({
                    buttons: [{
                        extend: 'csv',
                        text: 'Exportar reporte de tiempos detallado (CSV)',
                        className: 'btn btn-outline-primary'
                    }],
                    searching: false,
                    paging: false,
                    ordering: false
                });
                rep_table.buttons().container().appendTo( $('#exportButtonCol'));
            },
            error: function(xhr, status, e) {
                alert(status, e);
            }
        });
    });

    $('.tiemposPausaModal').click(function(event){
        event.preventDefault();
        var id_agente = $(this).attr('id_agente');
        var fecha_desde = $(this).attr('fecha_desde');
        var fecha_hasta = $(this).attr('fecha_hasta');
        var pausa_id = $(this).attr('pausa_id');
        $.ajax({
            type:'POST',
            url: Urls.reportes_pausa_por_fecha(),
            data:{
                'id_agente': id_agente,
                'fecha_desde': fecha_desde,
                'fecha_hasta': fecha_hasta,
                'pausa_id': pausa_id,
            },
            success: function (data) {
                //alert(data, textStatus);
                $('#output_pausa').html(data.tbody); // append to inner html
                $('#nombre_agente_pausa').html(data.nombre_agente);
                $('#nombre_pausa').html(data.pausa);
            },
            error: function(xhr, status, e) {
                alert(status, e);
            }
        });
    });

    $('#reporteFechaModal').on('hidden.bs.modal', function(event){
        $('#reporteFechaModalTable').DataTable().destroy();
    });

});
