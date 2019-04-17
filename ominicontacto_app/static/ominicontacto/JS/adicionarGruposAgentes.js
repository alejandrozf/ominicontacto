/*
 * Funciones para que una vez que se adicione un grupo de agentes se actualice el formset de agentes
 (queue_member)
*/

function eliminarPrimeraFilaVacia(data) {
    // esta función elimina la primera fila de la tabla una vez que se han
    // añadido filas de los agentes de un grupo, si esta fila está vacía
    var $firstRow = $('.linkFormset').first();
    var $selectMember = $firstRow.find('.member>select');
    if (($selectMember.val() == "") && (data.length != 0)) {
        $firstRow.find('.deleteFormset').click();
    }
}

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
            row.find('.deleteFormset').click();
        }
    }
}
