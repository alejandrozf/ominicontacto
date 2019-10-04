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

$(function() {
   var start = moment();
   var end = moment();
   function cb(start, end) {
     $('#id_fecha').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
   }

   $('#id_fecha').on('apply.daterangepicker', function(ev, picker) {
     $(this).val(picker.startDate.format('DD/MM/YYYY') + ' - ' + picker.endDate.format('DD/MM/YYYY'));
   });

   $('#id_fecha').on('cancel.daterangepicker', function(ev, picker) {
     $(this).val('');
   });

   // Init daterange plugin
   var ranges = get_ranges($('#campana_fecha_inicio').val());
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
});