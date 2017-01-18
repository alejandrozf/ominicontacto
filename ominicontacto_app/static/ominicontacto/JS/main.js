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
var flagPause = false;
var control = control2 = control3 = '';
$(function () {
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
	 inicio1();
	 inicio3();
	// como informo a un servidro de presencia que mi endpoint camibia de status
	 //$("#modalWebCall").modal('show');
	 $("#webCall").click(function () {
	     $("#modalWebCall").modal('show');
	 });
	 function updateButton(btn,clsnm,inht) {
	 	 btn.className = clsnm;
	 	 btn.innerHTML = inht;
	 }
	 $("#Pause").click(function () {
	 	if (flagPause === false) {
	    $("#modalPause").modal('show');
	    $("#pauseTime").html();
	  } else {
	    flagPause = false;
	    inicio1();
	    parar2();
	    updateButton(pauseButton, "btn btn-warning", "Pause");
	    modifyUserStat = document.getElementById("UserStatus");
	    modifyUserStat.className = "label label-success";
	    var lastPause = modifyUserStat.innerHTML;
	    var containerTag = document.getElementById("timers");
	    var pausas = document.getElementsByClassName("pausa");
	   }
	 	 
	 });
	 $("#setPause").click(function () {
	     if (flagPause === false) {
	     	   updateButton(pauseButton, "btn btn-danger", "Resume");
	         /*pauseButton.className = "btn btn-danger";
	         pauseButton.innerHTML = "Resume";*/
	         $("#modalPause").modal('hide');
	         modifyUserStat = document.getElementById("UserStatus");
	         modifyUserStat.className = "label label-warning";
	         modifyUserStat.innerHTML = $("#pauseType").val();
	         //flagPause = true;
	         parar1();
	         inicio2();
	     } 
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
	
	 function inicio1() {
	     control1 = setInterval(cronometro1, 1000);
	 }
	 function cronometro1() {
	     if (centesimasO < 59) {
	         centesimasO++;
	         if (centesimasO < 10) {
	             centesimasO = "0" + centesimasO;
	         }
	         $("#segsO").html(":" + centesimasO);
	     }
	     if (centesimasO == 59) {
	         centesimasO = -1;
	     }
	     if (centesimasO == 0) {
	         segundosO++;
	         if (segundosO < 10) {
	             segundosO = "0" + segundosO;
	         }
	         $("#minsO").html(":" + segundosO);
	     }
	     if (segundosO == 59) {
	         segundosO = -1;
	     }
	     if ((centesimasO == 0) && (segundosO == 0)) {
	         minutosO++;
	         if (minutosO < 10) {
	             minutosO = "0" + minutosO;
	         }
	         $("#horaO").html("" + minutosO);
	     }
	 }
	 $("#segsO").html(":00");
	 $("#minsO").html(":00");
	 $("#horaO").html("00");
	 $("#segsP").html(":00");
	 $("#minsP").html(":00");
	 $("#horaP").html("00");
	 $("#segsT").html(":00");
	 $("#minsT").html(":00");
	 $("#horaT").html("00");
	
	 function parar1() {
	     clearInterval(control1);
	 }
	 function parar2() {
	     clearInterval(control2);
	 }
	 function inicio2() {
	     control2 = setInterval(cronometro2, 1000);
	 }
	 function inicio3() {
	     control3 = setInterval(cronometro3, 1000);
	 }
	
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
	 function cronometro3() {
	     if (centesimasT < 59) {
	         centesimasT++;
	         if (centesimasT < 10) {
	             centesimasT = "0" + centesimasT;
	         }
	         $("#segsT").html(":" + centesimasT);
	     }
	     if (centesimasT == 59) {
	         centesimasT = -1;
	     }
	     if (centesimasT == 0) {
	         segundosT++;
	         if (segundosT < 10) {
	             segundosT = "0" + segundosT;
	         }
	         $("#minsT").html(":" + segundosT);
	     }
	     if (segundosT == 59) {
	         segundosT = -1;
	     }
	     if ((centesimasT == 0) && (segundosT == 0)) {
	         minutosT++;
	         if (minutosT < 10) {
	             minutosT = "0" + minutosT;
	         }
	         $("#horaT").html("" + minutosT);
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
	
	 function inicio() {
	     control = setInterval(cronometro1, 1000);
	 }
});
