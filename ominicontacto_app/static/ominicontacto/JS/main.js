var a = 0;
var holdFlag = false;
var centesimasO = 0;
var segundosO = 0;
var minutosO = 0;
var centesimasP = 0;
var segundosP = 0;
var minutosP = 0;
var centesimasT = 0;
var segundosT = 0;
var minutosT = 0;
var flagPause = 0;
var control = control2 = control3 = '';
var modifyUserStat = document.getElementById("UserStatus");
$(function () {
	$("#Resume").prop("disabled",true);
	 /*$("#id_registrar").click(function () {
	 	 $.ajax({
	 	 	 type: "post",
	 	 	 url: "/contacto/nuevo",
	 	 	 contentType: "application/json",
	 	 	 data: "",
	 	 	 success: function (msg) {
	   	 	 debugger;
	   	 	 $("#crm").html(msg);
	   	 },
	   	 error: function (jqXHR, textStatus, errorThrown) {
	       debugger;
	       console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
	     }
	 	 });
	 });*/
	 changeStatus(2, $("#idagt").val());

	 /*
	 ESTADO_OFFLINE = 1    """Agente en estado offline"""
	 ESTADO_ONLINE = 2    """Agente en estado online"""
	 ESTADO_PAUSA = 3    """Agente en estado pausa"""
	 */
	 function changeStatus(status, idagente) {
		 $.ajax({
	   	 type: "get",
	   	 url: "/agente/cambiar_estado?estado="+status+"&pk_agente="+idagente,
	   	 contentType: "text/html",
	   	 success: function (msg) {

	   	 },
	   	 error: function (jqXHR, textStatus, errorThrown) {
	                 debugger;
	                 console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
	     }
	   });
	 }

	 $("#facebookChat").click(function() {
     $("#modalFacebook").modal('show');
   });
	 $("#newLead").click(function () {
	   $.ajax({
	   	 type: "get",
	   	 url: "/contacto/nuevo",
	   	 contentType: "text/html",
	   	 success: function (msg) {
	   	 	$("#crm").html(msg);
	   	 },
	   	 error: function (jqXHR, textStatus, errorThrown) {
	                 debugger;
	                 console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
	     }
	   });
	 });
	 $("#webChat").click(function () {
	     $("#modalwebChat").modal('show');
	 });
	// como informo a un servidro de presencia que mi endpoint camibia de status
	 //$("#modalWebCall").modal('show');
	 $("#webCall").click(function () {
	     $("#modalWebCall").modal('show');
	 });
	 function updateButton(btn,clsnm,inht) {
	 	 btn.className = clsnm;
	 	 var lastval = btn.innerHTML;
	 	 btn.innerHTML = inht;
	 	 return lastval;
	 }
	 $("#setPause").click(function () {
		 changeStatus(3, $("#idagt").val());
	 	 $("#Pause").prop('disabled', true);
	 	 $("#Resume").prop('disabled', false);
     $("#modalPause").modal('hide');
     updateButton(modifyUserStat, "label label-danger", $("#pauseType option:selected").text());
//     inicio2();
   });
	 $("#logout").click(function () {
		 changeStatus(3, $("#idagt").val());
	 });

   $("#Resume").click(function () {
		 changeStatus(1, $("#idagt").val());
   	  $("#Pause").prop('disabled', false);
	 	  $("#Resume").prop('disabled', true);
	  //  parar2();
	    //updateButton(pauseButton, "btn btn-warning btn-sm", "Pause");
	    var lastPause = updateButton(modifyUserStat, "label label-success", "Online");
	    var containerTag = document.getElementById("timers");
	    var pausas = document.getElementsByClassName("pausa");
	    if (pausas.length) { // Si ya existe pausa, ver si se repite
	      var arrPausas = [];
	      for (var i = 0; i < pausas.length; i++) {
	        arrPausas[i] = pausas[i].id;
	      }
	      var found = arrPausas.indexOf(lastPause);
	        if (found != -1) { // Si se repite, suma los tiempos
	          horaToSum = $("#horaP").html();
	          minsToSum = $("#minsP").html().replace(":", "");
	          segsToSum = $("#segsP").html().replace(":", "");
	          horap = document.getElementById("hora" + lastPause);
	          minsp = document.getElementById("mins" + lastPause);
	          segsp = document.getElementById("segs" + lastPause);
	          horap = horap.innerHTML;
	          minsp = minsp.innerHTML.replace(":", "");
	          segsp = segsp.innerHTML.replace(":", "");
	          horap = Number(horap) + Number(horaToSum);
	          minsp = Number(minsp) + Number(minsToSum);
	          segsp = Number(segsp) + Number(segsToSum);
	          if (horap < 10) {
	            horap = String(horap) + "0";
	          }
	          if (minsp < 10) {
	            minsp = ":0" + String(minsp);
	          } else {
	            minsp = ":" + String(minsp);
	          }
	          if (segsp < 10) {
	            segsp = ":0" + String(segsp);
	          } else {
	            segsp = ":" + String(segsp);
	          }
	          document.getElementById("hora" + lastPause).innerHTML = horap;
	          document.getElementById("mins" + lastPause).innerHTML = minsp;
	          document.getElementById("segs" + lastPause).innerHTML = segsp;
	          lastPause = "";
	        } else { //si NO se repite, crea un marcador nuevo siempre y cndo no sea el estado = Online
	          if(lastPause != "Online") {
	            var descTxtContainerTag = document.createTextNode(lastPause + " ");
	            var ContainerSegs = document.createTextNode($("#segsP").html());
				      var ContainerMins = document.createTextNode($("#minsP").html());
	    			  var ContainerHora = document.createTextNode($("#horaP").html());
	          	var labelSegs = document.createElement("label");
				      var labelMins = document.createElement("label");
				      var labelHora = document.createElement("label");
	            var statusTag = document.createElement("span");
				      labelSegs.id = "segs" + lastPause;
	            labelMins.id = "mins" + lastPause;
	            labelHora.id = "hora" + lastPause;
	            labelSegs.appendChild(ContainerSegs);
	            labelMins.appendChild(ContainerMins);
	            labelHora.appendChild(ContainerHora);
	            statusTag.id = lastPause;
	            statusTag.className = "label label-default pausa";
	            statusTag.appendChild(descTxtContainerTag);
	            statusTag.appendChild(labelHora);
	            statusTag.appendChild(labelMins);
	            statusTag.appendChild(labelSegs);
	            containerTag.innerHTML += "&nbsp;";
	            containerTag.appendChild(statusTag);
	          }
	        }
	      } else { //Si NO existe pausa, creala siempre y cuando no sea el statusAgente = ONLINE
	        if(lastPause != "Online") {
	          var descTxtContainerTag = document.createTextNode(lastPause + " ");
	          var ContainerSegs = document.createTextNode($("#segsP").html());
	          var ContainerMins = document.createTextNode($("#minsP").html());
	          var ContainerHora = document.createTextNode($("#horaP").html());
	          var labelSegs = document.createElement("label");
	          var labelMins = document.createElement("label");
	          var labelHora = document.createElement("label");
	          var statusTag = document.createElement("span");
	          labelSegs.id = "segs" + lastPause;
	          labelMins.id = "mins" + lastPause;
	          labelHora.id = "hora" + lastPause;
	          labelSegs.appendChild(ContainerSegs);
	          labelMins.appendChild(ContainerMins);
	          labelHora.appendChild(ContainerHora);
	          statusTag.id = lastPause;
	          statusTag.className = "label label-default pausa";
	          statusTag.appendChild(descTxtContainerTag);
	          statusTag.appendChild(labelHora);
	          statusTag.appendChild(labelMins);
	          statusTag.appendChild(labelSegs);
	          containerTag.innerHTML += "&nbsp;";
	          containerTag.appendChild(statusTag);
	        }
	      }
	   //   reinicio($("#horaP"), $("#minsP"), $("#segsP"));
	  });

	 $("#Pause").click(function () {
	 	$("#modalPause").modal('show');
	  $("#pauseTime").html();
	 });
	 $("#onHold").click(function (){
	 	 if(holdFlag === false) {
	 	   $("#onHold").html("unhold");
	 	   holdFlag = true;
	 	 } else {
	 	 	 $("#onHold").html("hold");
	 	 	 holdFlag = false;
	 	 }
	 });
	 $("#txtSms").click(function () {
	     $.ajax({
	         url: '/sms/getAll/',
	         type: 'GET',
	         contentType: 'application/json',
	         success: function (jsOn) {
	             var row;
	             for (var i = 0; i < jsOn.length; i++) {
	                 if (jsOn[i].content !== "") {
	                     row += "<tr><td id=" + jsOn[i].id + ">" + jsOn[i].remitente + "</td><td>" + jsOn[i].content +
	                             "</td><td><button type='button'  class='btn btn-primary btn-xs ampliarConvers' title='Ver Conversacion' value=" + jsOn[i].remitente +
	                             "><span class='glyphicon glyphicon-align-left'></span></button></td></tr>";
	                 }
	             }
	             $("#cuerpoTabla").html(row);
	         },
	         error: function (jqXHR, textStatus, errorThrown) {
	             debugger;
	             console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
	         }
	     });
	     $("#modalSMS").modal("show");
	 });

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
	     var nroTel = $(this).val();
	     $("#phoneSendThread").attr('value',nroTel);
	     var datos = {'phoneNumber':nroTel};
	     $.ajax({
	       url: '/smsThread/',
	       type : 'GET',
	       contentType: 'application/json',
	       data: datos,
	       success: function (jsOn) {
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

	 $("#segsP").html(":00");
	 $("#minsP").html(":00");
	 $("#horaP").html("00");

	 function parar2() {
	     clearInterval(control2);
	 }
	 function inicio2() {
	     control2 = setInterval(cronometro2, 1000);
	 }

//************************************CRONOMETRO DE PAUSAS----------------------------
	 function cronometro2() {
	     if (centesimasP < 59) {
	         centesimasP++;
	         if (centesimasP < 10) {
	             centesimasP = "0" + centesimasP;
	         }
	         $("#segsP").html(":" + centesimasP);
	     }
	     if (centesimasP == 59) {
	         centesimasP = -1;
	     }
	     if (centesimasP == 0) {
	         segundosP++;
	         if (segundosP < 10) {
	             segundosP = "0" + segundosP;
	         }
	         $("#minsP").html(":" + segundosP);
	     }
	     if (segundosP == 59) {
	         segundosP = -1;
	     }
	     if ((centesimasP == 0) && (segundosP == 0)) {
	         minutosP++;
	         if (minutosP < 10) {
	             minutosP = "0" + minutosP;
	         }
	         $("#horaP").html("" + minutosP);
	     }
	 }

	 function reinicio(horaDOM, minDOM, segDOM) {
	     clearInterval(control);
	     centesimasP = 0;
	     segundosP = 0;
	     minutosP = 0;
	     segDOM.html(":00");
	     minDOM.html(":00");
	     horaDOM.html("00");
	 }

});
