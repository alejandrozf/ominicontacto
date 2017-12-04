$(document).ready(function(){

  var $errorAsignacionContacto = $('#errorAsignacionContacto');

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
  var $inputCampana = $('#pk_campana');
  var $inputCampanaNombre = $('#campana_nombre');

  function informarError(data, $button) {
    $button.addClass('disabled');
    $button.attr('title', data['data']);
  }

  $('#validar_contacto').on('click', function(){
    var url = "/campana_preview/validar_contacto_asignado/";
    var data = {
      'pk_agente': $inputAgente.val(),
      'pk_campana': $inputCampana.val(),
      'pk_contacto': $inputContacto.val(),
    };
    $.post(url, data).success(function(data) {
      // comprobamos si el contacto todavía sigue asignado al agente
      // antes de llamar
      if (data['contacto_asignado'] == true) {
        // hacemos click en el botón del form para iniciar la
        // llamada
        $('#llamar_contacto').trigger('click');
      }
      else {
        // se muestra modal con mensaje de error
        var errorMessage = "Ha sido desconectado del contacto asignado, pruebe obtener otro"
        $errorAsignacionContacto.html(errorMessage);
      }
    });
  });

  $('.obtener-contacto').each(function() {
    $(this).on('click', function() {
      var $button = $(this);
      var nombreCampana = $button.text();
      var idCampana = $button.attr('data-campana');
      var url = '/campana_preview/'+ idCampana +'/contacto/obtener/';
      $.post(url)
        .success(function (data) {
          if (data['result'] != 'OK') {
            informarError(data, $button);

          }
          else {                // se obtienen los datos del contacto
            $panelContacto.attr('class', 'col-md-4 col-md-offset-1');
            // actualizamos el teléfono del contacto
            var contactoTelefono = data['telefono_contacto'];
            $contactoTelefono.text(contactoTelefono);
            $inputAgente.attr('value', data['agente_id']);
            $inputContacto.attr('value', data['contacto_id']);
            $inputCampana.attr('value', idCampana);
            $inputCampanaNombre.attr('value', nombreCampana);
            $errorAsignacionContacto.html('');

            // Limpiamos la información de algún contacto anterior
            $contactoOtrosDatos.html('');

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
