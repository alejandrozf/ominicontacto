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
   $(function() {
     var start = moment();
     var end = moment();
     function cb(start, end) {
       $('#id_fecha').html(start.format('DD/MM/YYYY') + ' - ' + end.format('DD/MM/YYYY'));
     }

     $('#id_fecha').on('apply.daterangepicker', function(ev, picker) {
       $(this).val(picker.startDate.format('DD/MM/YYYY') + ' - ' + picker.endDate.format('DD/MM/YYYY'));
     });

     $('#id_fecha').on('cancel.daterangepicker', function(ev, picker) {
       $(this).val('.calificacionContacto');
     });

     var localeData = moment.localeData();
     var calendar = localeData._calendar;
     ranges = get_ranges();
     // Init daterange plugin
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

     $(".btn-submit").click(function (){
       var action = $(this).attr("name");
       var pk_contacto = $(this).attr("pk_contacto");
       var pk_agente = $(this).attr("agente");
       var tipo_campana = $(this).attr("tipo_campana");
       var campana_nombre = $(this).attr("campana_nombre");
       var pk_campana = $(this).attr("pk_campana");
       submit_form(pk_contacto, pk_agente, action, tipo_campana, campana_nombre, pk_campana);
     })

     function submit_form(pk_contacto, pk_agente, action, tipo_campana, campana_nombre, pk_campana){
       $("#pk_contacto").val(pk_contacto);
       $("#pk_agente").val(pk_agente);
       $("#tipo_campana").val(tipo_campana);
       $("#pk_campana").val(pk_campana);
       $("#campana_nombre").val(campana_nombre);
       $("#form_llamar").attr("action", action);
       $("#form_llamar").submit();
     }
});
