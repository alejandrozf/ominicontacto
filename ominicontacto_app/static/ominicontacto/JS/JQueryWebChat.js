var sesion = null;
var ua = null;
var user = '';
var configuration = null;

$(function() {
  $("#conf").click(function() {
    $("#modalAccountConfig").modal('show');
  });
  $("#register").click(function() {
    $("#sendMessage").prop('disabled', false);
    $("#chatMessage").prop('disabled', false);
    $("#modalAccountConfig").modal('hide');
    //Connects to the WebSocket server
    ua = new JsSIP.UA(configuration);
    sesion = ua.start();

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
        fromUser = e.request.headers.From[0];
        endPos = fromUser.indexOf("@");
        startPos = fromUser.indexOf(":");
        fromUser = fromUser.substring(startPos+1,endPos);
        liMensaje = document.createElement("li");
        var msgToSend = document.getElementById("chatMessage").value;
        liMensaje = document.createElement("li");
        textoDeMensaje = document.createTextNode(fromUser+": "+msgToSend);
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
      //imgCelda1.src="Img/greendot.png";
      imgCelda1.src="{% static 'ominicontacto/Img/greendot.png' %}";
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
  });
  $("#sendMessage").click(function() {
    var mensaje = $("#chatMessage").val();
    user = $("#user").val();
    if(mensaje !== "") {
      if ($("#uri").val() === "2002") {
        ua.sendMessage("sip:2001@172.16.20.219", mensaje);
      } if ($("#uri").val() === "2001") {
        ua.sendMessage("sip:2002@172.16.20.219", mensaje);
      }
      $("#chatMessage").val("");
    }
  });
  $("#saveConf").click(function() {
    // esto seria un sip para recibir y realizar llamadas
    configuration = {
      uri : "sip:"+$("#uri").val()+"@172.16.20.219",
      ws_servers : "ws://172.16.20.219:80",
      password : "123456"
    };
  });
});
