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
  var $inputAgente = $('#pk_agente');
  var $inputContacto = $('#pk_contacto');

  function informarError(data, $button) {
    $button.addClass('disabled');
    $button.attr('title', data['data']);
  }

  $('.obtener-contacto').each(function() {
    $(this).on('click', function() {
      var $button = $(this);
      var idCampana = $button.attr('data-campana');
      var url = '/campana_preview/'+ idCampana +'/contacto/obtener/';
      $.post(url)
        .success(function (data) {
          if (data['result'] == 'Error') {
            informarError(data, $button);

          }
          else {                // se obtienen los datos del contacto
            $panelContacto.attr('class', 'col-md-4 col-md-offset-1');
            // actualizamos el teléfono del contacto
            var contactoTelefono = data['telefono_contacto'];
            $contactoTelefono.text(contactoTelefono);
            $inputAgente.attr('value', data['agente_id']);
            $inputContacto.attr('value', data['contacto_id']);

            // Limpiamos la información de algún contacto
            $contactoOtrosDatos.html("");

            // Actualizamos los datos del contacto obtenido
            for (campo in data['datos_contacto']) {
              capitalizedCampo = campo.charAt(0).toUpperCase() + campo.slice(1);
              var campoData = '<p><span style="font-weight: bold;">'+capitalizedCampo+': </span>' +
                  data['datos_contacto'][campo] + '</p>';
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
