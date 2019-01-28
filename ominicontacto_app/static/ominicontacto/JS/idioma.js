/**
 * Script para cambiar idioma dinámicamente, una vez que se selecciona el valor de idioma correspondiente
 realiza un submit de los cambios al sistema eliminando la necesidad del botón
 */
$('#cambiarIdiomaSelect').on('change', function(){
  $('#submitIdioma').click();
});
