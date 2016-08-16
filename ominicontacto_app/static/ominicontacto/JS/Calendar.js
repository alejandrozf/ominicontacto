$(function () {
	$("#register").click(function () {
		var chan;
		var smart = false; 
		var pers = false;
		var flagAjax = false;
		var mensaje = '';
		var ag = $("#idagt").val();
		var phoneOrEmail = $("#phoneOrEmail").val();
		if($(".personal").prop("checked")) {
			pers = true;
		}
		if($(".smart").prop("checked")) {
			smart = true;
		}
		$(".notif").prop("checked", function () {
			chan = $("input[name=notf]:checked").val();
		});
		if(chan === "3") {
			var a = phoneOrEmail.indexOf("@");
			console.log(a);
			if(a !== -1 && a !== 0) {
				flagAjax = true;
			} else {
			  mensaje = "Verificar direccion de e-mail";
			}
		} else {
			if(!(isNaN(phoneOrEmail)) && phoneOrEmail.length > 6 && phoneOrEmail.length < 13) {
				flagAjax = true;
			} else {
				mensaje = "Verificar numero de telefono";
			}
		}
		if(flagAjax === true) {
		$.ajax({
			type: "get",
	   	 url: "/agenda/nuevo/",
	   	 contentType: "text/plain",
	   	 data: "horaEvento="+$("#horaAgenda").val()+"&fechaEvento="+$("#ctlfechaAgenda").val()+"&descripcion="+$("#calendarSubject").val()+"&agente="+ag+"&smart="+smart+"&channel="+chan+"&dirchan="+phoneOrEmail+"&personal="+pers,
	   	 success: function (msg) {
	   	 	$("#horaAgenda").val("");
	   	 	$("#ctlfechaAgenda").val("");
	   	 	$("#calendarSubject").val("");
	   	 	$(".personal").prop("checked", false);
	   	 	$(".smart").prop("checked", false);
	   	 	$(".notif").prop("checked", false);
	   	 	$("#phoneOrEmail").val("");
	   	 	mensaje = "Agenda guardada correctamente";
	   	 	$("#infoAjax").html(mensaje);
	   	 	$("#infoAjax").css("color","darkcyan");
				$("#modalMensaje").modal("show");
				ocultarModal("#modalMensaje");		
	   	 },
	   	 error: function (jqXHR, textStatus, errorThrown) {
	       debugger;
	       console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
	     }
		}); 
		} else {
			$("#infoAjax").html(mensaje);
			$("#infoAjax").css("color","red");
			$("#modalMensaje").modal("show");
			ocultarModal("#modalMensaje");
		}
	});
	function ocultarModal(modal) {
	  setTimeout(function(){$(modal).modal("hide");}, 2000);
	}
	$('#fechaAgenda').datetimepicker({
  	pickTime: false
	});
	$('#horaAgenda').datetimepicker({
  	pickDate: false,
  	format: 'HH:mm'
	});
});