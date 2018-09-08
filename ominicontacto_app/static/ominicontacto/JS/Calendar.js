/* Copyright (C) 2018 Freetech Solutions

 This file is part of OMniLeads

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see http://www.gnu.org/licenses/.

*/
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
  	'format': 'DD/MM/YYYY'
	});
	$('#horaAgenda').datetimepicker({
  	'format': 'HH:mm'
	});
});