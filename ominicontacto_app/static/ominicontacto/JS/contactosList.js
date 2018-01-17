$(document).ready(function(){
  $('#agenteContactosTable').DataTable( {
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
  } );
});
