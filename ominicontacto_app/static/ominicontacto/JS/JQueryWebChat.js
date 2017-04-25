var user, mensaje;
//var KamailioIp = "172.16.20.14";
$(function() {
	var configuration = {
      uri : "sip:"+$("#sipExt").val()+"@"+KamailioIp,
      ws_servers : "wss://"+KamailioIp+":443",
      password : $("#sipSec").val(),
      session_timers: false
    };
  var ua = new JsSIP.UA(configuration);
  var sesion = ua.start();

 // 	debugger;
    $("#sendMessage").prop('disabled', false);
    $("#chatMessage").prop('disabled', false);
    $("#modalAccountConfig").modal('hide');
    //Connects to the WebSocket server

    ua.on('registered', function(e) {
      console.log("peer registered");
    });
    ua.on('newMessage', function(e) {
      var chatWindow = document.getElementById("messages");
      var liMensaje = "";
      var textoDeMensaje = "";
      var msg = e.message.content;
      if(e.originator == "remote") {
        fromUser = e.request.headers.From[0].raw;
        endPos = fromUser.indexOf("@");
        startPos = fromUser.indexOf(":");
        fromUser = fromUser.substring(startPos+1,endPos);
        liMensaje = document.createElement("li");
        textoDeMensaje = document.createTextNode(fromUser+": "+msg);
        liMensaje.appendChild(textoDeMensaje);
        chatWindow.appendChild(liMensaje);
      } else {
        fromUser = document.getElementById("user");
        liMensaje = document.createElement("li");
        var msgToSend = document.getElementById("chatMessage").value;
        liMensaje = document.createElement("li");
        textoDeMensaje = document.createTextNode(fromUser.value+": "+msgToSend);
        liMensaje.appendChild(textoDeMensaje);
        chatWindow.appendChild(liMensaje);
      }
    });

    ua.on('connected', function () {
      user = $("#user").val();
      var fila = document.createElement('tr');
      var celda1 = document.createElement('td');
      var celda2 = document.createElement('td');
      var celda3 = document.createElement('td');
      var imgCelda1 = document.createElement("img");
      var txtCelda2 = document.createTextNode(user);
      var radioCelda3 = document.createElement("input");
      imgCelda1.src="../static/ominicontacto/Img/greendot.png";
      radioCelda3.type="checkbox";
      radioCelda3.id=user;
      celda3.style.textAlign='right';
      celda1.appendChild(imgCelda1);
      celda2.appendChild(txtCelda2);
      celda3.appendChild(radioCelda3);
      fila.appendChild(celda1);
      fila.appendChild(celda2);
      fila.appendChild(celda3);
      document.getElementById("tbodyContacts").appendChild(fila);
    });
var chatId =  $("#conversationId").val();
  $("#sendMessage").click(function() {
    mensaje = $("#chatMessage").val();
    var receiver = '1007';
    user = $("#user").val();
    if(mensaje !== "") {
        ua.sendMessage("sip:"+receiver+"@"+KamailioIp, mensaje);
      $("#chatMessage").val("");
    }

    $.ajax({

		  url: '/chat/mensaje',
    	type: 'GET',
    	contentType: 'application/json',
    	data: "sender="+user+"&to="+receiver+"&mensaje="+mensaje+"&chat="+chatId,
    	succes: function (msg) {
        console.log(JSON.parse(msg));
    	},
    	error: function (jqXHR, textStatus, errorThrown) {
        console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
    	}

    });
  });
});
