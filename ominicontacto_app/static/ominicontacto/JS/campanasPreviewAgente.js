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
  var $contactoTelefono = $panelContacto.find('#contacto-telefono');
  var $contactoOtrosDatos = $panelContacto.find('#contacto-datos');

  function informarError(data) {
    alert(data['data']);
  }

  $('.obtener-contacto').each(function() {
    $(this).on('click', function(){
      var idCampana = $(this).attr('data-campana');
      var url = '/campana_preview/'+ idCampana +'/contacto/obtener/';
      $.post(url)
        .success(function (data) {
          if (data['result'] == 'Error') {
            informarError(data);
          }
          else {                // se obtienen los datos del contacto
            $panelContacto.attr('class', 'col-md-4 col-md-offset-1');
            // actualizamos el teléfono del contacto
            var contactoTelefono = data['telefono_contacto'];
            $contactoTelefono.text(contactoTelefono);

            // Limpiamos la información de algún contacto
            $contactoOtrosDatos.html("");

            // Actualizamos los datos del contacto obtenido
            for (campo in data['datos_contacto']) {
              var campoData = '<p>'+campo+': ' + data['datos_contacto'][campo] + '</p>';
              $contactoOtrosDatos.append(campoData);
            }
            console.log("Success: ", data);
          }

        })
        .fail( function (data) {
          console.log("Fail: ", data);
        })
        .error( function (data) {
          console.log("Error: ", data);
        });
    });
  });
});
