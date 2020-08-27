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
    $('.edit_url').prop('disabled', false);
}

$(function(){
    interaccionUrl();
    inicializarCampoOutr();
});

function inicializarCampoOutr() {
    var $outr = $('#id_0-outr');
    $outr.on('change', actualizarEstadoOutcid);
    actualizarEstadoOutcid();
}

function actualizarEstadoOutcid() {
    var $outr = $('#id_0-outr');
    var $outcid = $('#id_0-outcid');
    if ($outr.val() == ''){
        $outcid.prop('disabled', true);
        $outcid.val('');
    }
    else
        $outcid.prop('disabled', false);
}


