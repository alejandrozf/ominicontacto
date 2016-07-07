  $(document).ready(function() {
      $("#threadMsgsTable").DataTable({
        paging:false,
        searching:false,
        ordering:false,
        info:false,
        language: {
          "emptyTable":     "Sin datos disponibles"
        }
      });
      $('#messagesTable').DataTable({
        "language": {
          "lengthMenu": "Registros por pagina _MENU_",
          "search": "Buscar:",
          "info": "Mostrando desde _START_ hasta _END_ de _TOTAL_ registros",
          "infoEmpty": "Mostrando desde 0 hasta 0 de 0 paginas",
          "emptyTable":     "Sin datos disponibles",
          "paginate": {
            "first":      "Primero",
            "last":       "Ultimo",
            "next":       "Siguiente",
            "previous":   "Anterior"
          }
        }
      });
      $("#cuerpoTabla").on('click', '.ampliarConvers',function(e) {
        debugger;
        var nroTel = $(this).val();
        $("#phoneSendThread").attr('value',nroTel);
        var datos = JSON.stringify({'phoneNumber' : nroTel});
        $.ajax({
          url: '/smsThread',
          type : 'POST',
          contentType: 'application/json',
          data: datos,
          success: function (jsOn) {
            debugger;
            var row;
            for (var i=0; i < jsOn.length; i++) {
              if(jsOn[i].content !== "") {
                var date = jsOn[i].timestamp;
                date = date.substring(5, 10);
                date = date.split("-");
                date = date.reverse();
                date = date.join("-");
                row +="<tr><td>"+jsOn[i].remitente+"</td><td>"+jsOn[i].destinatario+"</td><td>"+jsOn[i].content+"</td><td>"+date+"</td></tr>";
              }
            }
            $("#bodyThreadMsgTable").html(row);
            $("#modalConvers").modal('show');
          },
          error: function (jqXHR, textStatus, errorThrown) {
            debugger;
            console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
          }
        });
      });
  });
