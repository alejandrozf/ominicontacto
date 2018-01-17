$(document).ready(function(){

  var $inputContacto = $('#pk_contacto');

  function conectar_contactos_llamadas() {
    $('.contacto-lista').each(function() {
      $(this).on('click', function() {
        var $button = $(this);
        var pk_contacto = $button.data('contacto');
        $inputContacto.attr('value', pk_contacto);
        $('#lista_llamar_contacto').trigger('click');
      });
    });
  }

  $('#agenteContactosTable')
    .on( 'draw.dt', function () { conectar_contactos_llamadas();})
    .DataTable( {
      // Convierte a datatable la tabla de contactos
      language: {
        search: "Buscar: ",
        paginate: {
          first: "Primero ",
          previous: "Anterior ",
          next: " Siguiente",
          last: " Último"
        },
        lengthMenu: "Mostrar _MENU_ entradas",
        info: "Mostrando _START_ a _END_ de _TOTAL_ entradas",
      }
    });
});
