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

     // Init daterange plugin
     $('#id_fecha').daterangepicker(
       {
         locale: {
           format: 'DD/MM/YYYY'
         },

         startDate: start,
         endDate: end,
         ranges: {
           'Hoy': [moment(), moment()],
           'Ayer': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
           'Ultimos 7 Días': [moment().subtract(6, 'days'), moment()],
           'Ultimos 30 Días': [moment().subtract(29, 'days'), moment()],
           'Este Mes': [moment().startOf('month'), moment().endOf('month')],
           'Ultimo Mes': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
         },

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
