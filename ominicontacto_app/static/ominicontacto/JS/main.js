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
var control1 = control2 = control3 = control4 = '';
var modifyUserStat = document.getElementById("UserStatus");
$(function () {
	$("#Resume").prop("disabled",true);
	 changeStatus(2, $("#idagt").val());
	 inicio1();//cronometro de operacion
	 inicio4();// cronometro del total
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
	/* $("#newLead").click(function () {
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
	 });/**/
	 $("#webChat").click(function () {
	     $("#modalwebChat").modal('show');
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
	   inicio2();// inicio cronometro pausa
		 parar1();// pauso cronometro operacion
	   updateButton(modifyUserStat, "label label-danger", $("#pauseType option:selected").text());
	 });

	 $("#logout").click(function () {
	   changeStatus(3, $("#idagt").val());
	 });

	 $("#Resume").click(function () {
	   parar2();
		 inicio1();
	   changeStatus(1, $("#idagt").val());
	   $("#Pause").prop('disabled', false);
	   $("#Resume").prop('disabled', true);
	   var lastPause = updateButton(modifyUserStat, "label label-success", "Online");
	   var containerTag = document.getElementById("timers");
	   var pausas = document.getElementsByClassName("pausa");
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

	 function parar1() {
	 		clearInterval(control1);
	 }
	 function inicio1() {
	 		control1 = setInterval(cronometro1, 1000);
	 }
	 function parar2() {
	     clearInterval(control2);
	 }
	 function inicio2() {
	     control2 = setInterval(cronometro2, 1000);
	 }
	 function parar4() {
	     clearInterval(control4);
	 }
	 function inicio4() {
	     control2 = setInterval(cronometro4, 1000);
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
	 //*************************************CRONOMETRO DE  OPERACION***********************
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
	 //************************************CRONOMETRO DEL TOTAL----------------------------
 	 function cronometro4() {
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
   //-------------------------------------------------------------------------
	 function reinicio(horaDOM, minDOM, segDOM, controlX, cent, seg, min) {
	     clearInterval(controlX);
	     cent = 0;
	     seg = 0;
	     min = 0;
	     segDOM.html(":00");
	     minDOM.html(":00");
	     horaDOM.html("00");
	 }
});
