$(document).ready(function(){
  $('#campanasPreviewTable').DataTable( {
    // Convierte a datatable la tabla de campañas preview
    language: {
      search: "Buscar:",
      paginate: {
        first: "Primero",
        previous: "Anterior",
        next: "Siguiente",
        last: "Último"
      },
      lengthMenu: "Mostrar _MENU_ entradas",
      info: "Mostrando _START_ a _END_ de _TOTAL_ entradas",
    }
  } );

  // asocia el click en la campaña preview a obtener los datos de un contacto
  var $panelContacto = $('#panel-contacto');
  var $contactoNombre = $panelContacto.find('#panel-contacto-nombre');
  var $contactoTelefono = $panelContacto.find('#panel-contacto-telefono');

  $('.obtener-contacto').each(function() {
    $(this).on('click', function(){
      var idCampana = $(this).attr('data-campana');
      var url = '/campana_preview/'+ idCampana +'/contacto/obtener/';
      $.post(url)
        .success(function (data) {
          $panelContacto.attr('class', 'col-md-4 col-md-offset-1');
          var contactoNombre = data['datos_contacto'][0] + ' ' + data['datos_contacto'][1];
          var contactoTelefono = data['telefono_contacto'];
          $contactoNombre.text(contactoNombre);
          $contactoTelefono.text(contactoTelefono);
          console.log("Success: ", data);
        })
        .fail( function (data) {
          console.log("Fail: ", data);
        })
        .error( function (data) {
          console.log("Error: ", data);
        });
    })
  });
});
