/*
 * Funcion que impide la posibilidad de dar valor al campo que indica la url de sitio externo
 si se ha seleccionado una interaccion de tipo formulario.
*/

function interaccionUrl(){
    var $tipoInteraccion = $('input:radio[name ="0-tipo_interaccion"]');
    if ($tipoInteraccion.length > 0) {
        // vista de creación de la campaña
        if ( $('input:radio[name ="0-tipo_interaccion"]:checked').val() == 2){
            $('#id_0-sitio_externo').prop('disabled', false);
        }
        else{
            $('#id_0-sitio_externo').prop('disabled', true);
        }
    }
}

$(function(){
    interaccionUrl();
});
