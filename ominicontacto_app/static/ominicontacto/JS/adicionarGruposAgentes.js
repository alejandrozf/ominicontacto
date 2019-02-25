/*
 * Funciones para que una vez que se adicione un grupo de agentes se actualice el formset de agentes
 (queue_member)
*/


function obtenerAgentesGrupos() {
    var $grupoSelect = $('#gruposAgentes').find('select');
    var idGrupo = $grupoSelect.val();
    // obtenemos los datos de los agentes asignados al grupo
    return Urls.grupo_agentes_activos_list(idGrupo);
}

function asociarDatosRow(row) {
    // adicionamos la data a la nueva fila
    var elemData = row.attr('data');
    if (elemData) {
        var elemDataParsed = JSON.parse(elemData);
        var selectionMemberNode = '.member>select option[value='+ elemDataParsed.id + ']';
        var $fieldMemberRow = row.find(selectionMemberNode);
        $fieldMemberRow.prop('selected', true);
    }
    // cuando se adiciona desde API la fila chequeamos si no duplica a alguna ya existente,
    // en ese caso la eliminamos
    if (elemData) {
        var $members = $('.member:visible').find('select');
        var rowMemberVal = row.find('select').val();
        var count = 0;
        $members.each(function () {
            if ($(this).val() == rowMemberVal) {
                count = count + 1;
            }
        });
        if (count > 1) {
            row.remove();
        }
    }
}
