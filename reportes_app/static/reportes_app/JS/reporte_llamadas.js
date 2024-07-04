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

/* global get_ranges */


$(function() {

    initSubmitButton();
    var date_format = 'DD/MM/YYYY';

    function set_daterange_input_values(start, end) {
        $('#id_fecha').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
    }

    $('#id_fecha').on('apply.daterangepicker', function(ev, picker) {
        $(this).val(picker.startDate.format(date_format) + ' - ' + picker.endDate.format(date_format));
    });

    $('#id_fecha').on('cancel.daterangepicker', function(ev, picker) {
        $(this).val('');
    });

    // Init daterange plugin
    var ranges = get_ranges();
    $('#id_fecha').daterangepicker(
        {
            locale: {
                format: date_format
            },
            ranges: ranges,
        },
        set_daterange_input_values
    );
});

function exportarReporte(tipo_reporte){
    $('#tipo_reporte').val(tipo_reporte);
    $('#exportar_reporte').submit();
}

function mostrarLlamadasPorFecha(tipo){
    $('#modalLlamadas' + tipo).modal('show');
}

function toggleTiposDeLlamadaPorFecha(tipo, id){
    $('tr[fechas=Fechas' + tipo + '_' + id + ']').toggle();
}

function initSubmitButton() {
    $('#id_buscar_btn').click(function (params) {
        $('#submit_msg').show();
        setTimeout(function () { $('#id_buscar_btn').attr('disabled', true); }, 0);
    });
}
