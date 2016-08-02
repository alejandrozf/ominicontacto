$(function () {
	$("#register").click(function () {
		debugger;
		var chan;
		var smart = false; 
		var pers = false;
		var flagAjax = false;
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
		if(chan === 3) {
			if(phoneOrEmail.indexOf("@")) {
				flagAjax = true;
			}
		} else {
			if(phoneOrEmail.length > 6 && phoneOrEmail.length < 13) {
				flagAjax = true;
			}
		}
		if(flagAjax === true) {
		$.ajax({
			type: "get",
	   	 url: "/agenda/nuevo/",
	   	 contentType: "text/plain",
	   	 data: "horaEvento="+$("#horaAgenda").val()+"&fechaEvento="+$("#ctlfechaAgenda").val()+"&descripcion="+$("#calendarSubject").val()+"&agt="+ag+"&smart="+smart+"&channel="+chan+"dirchan="+phoneOrEmail+"&personal="+pers,
	   	 success: function (msg) {
	   	 	debugger;
	   	 	$("#horaAgenda").html("");
	   	 	$("#ctlfechaAgenda").html("");
	   	 	$("#calendarSubject").html("");
	   	 	$(".personal").prop("checked", false);
	   	 	$(".smart").prop("checked", false);
	   	 	$(".notif").prop("checked", false);
	   	 	$("#phoneOrEmail").val();
	   	 },
	   	 error: function (jqXHR, textStatus, errorThrown) {
	                 debugger;
	                 console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
	     }
		}); 
		
		}
	});
	$('#fechaAgenda').datetimepicker({
  	pickTime: false
	});
	$('#horaAgenda').datetimepicker({
  	pickDate: false,
  	format: 'HH:mm'
	});
});