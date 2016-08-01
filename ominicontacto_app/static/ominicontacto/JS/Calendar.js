$(function () {
	$("#register").click(function () {
		$.ajax({
			type: "post",
	   	 url: "/agenda/guardar/",
	   	 contentType: "text/plain",
	   	 data: "horaEvento="+$("#horaAgenda").val()+"&fechaEvento="+$("#ctlfechaAgenda").val()+"&descripcion="+$("#calendarSubject").val();
	   	 success: function (msg) {
	   	 	debugger;
	   	 	$("#horaAgenda").html("");
	   	 	$("#ctlfechaAgenda").html("");
	   	 	$("#calendarSubject").html("");
	   	 },
	   	 error: function (jqXHR, textStatus, errorThrown) {
	                 debugger;
	                 console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
	     }
		});		
	});
	$('#fechaAgenda').datetimepicker({
  	pickTime: false
	});
	$('#horaAgenda').datetimepicker({
  	pickDate: false,
  	format: 'HH:mm'
	});
});