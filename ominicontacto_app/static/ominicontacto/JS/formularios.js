/*
 * Script que realiza bindings a todos los botones de mostrar/ocultar en la lista de formularios,
 * en cada click actualiza el estado del atributo 'oculto' de formulario en cuestión en BD y modifica convenientemente
 * la UI del elemento
 */

function actualizarFormulario(id, $this, mostrarOcultos) {
  var url = Urls.formulario_mostrar_ocultar(id);
  $.post(url).success(function(data) {
    actualizarNodoFormulario($this, data, mostrarOcultos);
  });
}

function actualizarNodoFormulario($this, data, mostrarOcultos) {
  var oculto = data.oculto;

  if (mostrarOcultos == "True" && oculto == false) {
    // cambiar icono a "ocultar"
    var $span = $this.find('span');
    $span.attr('class', 'icon icon-eye');
    $span.text(gettext('Ocultar'));
  }
  else {
    if (mostrarOcultos == "True" && oculto == true) {
      // cambiar icono a "mostrar"
      var $span = $this.find('span');
      $span.attr('class', 'icon icon-eye-slash');
      $span.text(gettext('Mostrar'));
    }
    else {
      // sólo se muestran los 'visibles', se elimina el nodo
      // directamente
      $this.parent().remove();
    }
  }
}


$('.mostrarOcultar').each(function (index, value) {
  var $this = $(this);
  var id = $this.attr('id');
  var mostrarOcultos = $this.attr('data-mostrar-ocultos');
  $this.on('click', function () {
    actualizarFormulario(id, $this, mostrarOcultos);
  });
});
