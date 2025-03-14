
function tableToDataTable(columns) {
    $('table.table').each(function(){
        try {
            $(this).DataTable({
                paging: false,
                searching: false,
                columns,
                order: [[0, 'desc']]
            });
        } catch (error) { /**/ }
    });
}
