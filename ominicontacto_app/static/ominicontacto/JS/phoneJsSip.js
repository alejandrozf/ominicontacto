//***************************************************
//2001, 2002 (123456)
var config = null;var textSipStatus = null;var callSipStatus = null;var iconStatus = null;var userAgent = null;var sesion = null;var opciones = null;var eventHandlers = null; var flagTransf = false; var flagInit = true; var num = null;
var sipStatus = document.getElementById('SipStatus');var callStatus = document.getElementById('CallStatus');var local = document.getElementById('localAudio');var remoto = document.getElementById('remoteAudio');var displayNumber = document.getElementById("numberToCall"); var pauseButton = document.getElementById("Pause");

$(function() {
  var estado = JSON.stringify({'status' : 'online'});
  /*$.ajax({
    url: '/status/setStat',
    type: 'POST',
    contentType: 'application/json',
    data: estado,
    succes: function (msg) {
        console.log(JSON.parse(msg));
    },
    error: function (jqXHR, textStatus, errorThrown) {
            console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
    }
  });*/
 
  $("#Pause").click(function () {
    if (flagPausa === true) {
    num = "0077UNPAUSE";
    makeCall(num);
    }
  });
  if($("#sipExt").val() && $("#sipSec").val()) {
    config = {
      uri : "sip:"+$("#sipExt").val()+"@172.16.20.219",
      ws_servers : "wss://172.16.20.219:443",
      password : $("#sipSec").val()//"123456"
    };
    userAgent = new JsSIP.UA(config);
    sesion = userAgent.start();
    setSipStatus("greydot.png", "  No account", sipStatus);
  }
  $("#UserStatus").html("Online");
  $("#sipLogout").click(function() {
    num = "0077LOGOUT";
    makeCall(num);
  });
  $("#CallList").click(function() {
    $("#modalCallList").modal('show');
  });
  $("#setPause").click(function() {
    $.ajax({
      url: '/status/setStat',
      type: 'POST',
      contentType: 'text/plain',
      content: 'pause='+$("#UserStatus").value,
      error: function (jqXHR, textStatus, errorThrown) {
              console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
      }
    });
    //console.log($("#pauseType").val());
    //num = "0077"+$("#pauseType").value.toUpperCase();
    console.log($("#UserStatus").val());
    num = "0077"+$("#UserStatus").value.toUpperCase();
    makeCall(num);
  });

  $(".key").click(function(e) {
    var numPress = "";
    if(displayNumber.value === "") {
      numPress = e.currentTarget.childNodes[0].data;
    } else {
      numPress = displayNumber.value;
      numPress += e.currentTarget.childNodes[0].data;
    }
    displayNumber.value = numPress;
  });
  $("#unregister").click(function() {
    userAgent.unregister();
    /*userAgent.on('',function() {

    });*/
   userAgent.on('unregistered', function(e) {
      setSipStatus("reddot.png", "  Unregistered", sipStatus);
    });
  });
    $("#unregister").prop('disabled', false);
    //Connects to the WebSocket server
    userAgent.on('registered', function(e) {
      num = "0077LOGIN";
      makeCall(num);
      $("#sendMessage").prop('disabled', false);
      $("#chatMessage").prop('disabled', false);
      iconStatus.parentNode.removeChild(iconStatus);
      textSipStatus.parentNode.removeChild(textSipStatus);
      setSipStatus("greendot.png", "  Registered", sipStatus);
      defaultCallState();
    });

    userAgent.on('registrationFailed', function(e) {

      setSipStatus("redcross.png", "  Registration failed", sipStatus);
    });

    userAgent.on('newMessage', function(e) {
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
        textoDeMensaje = document.createTextNode(fromUser+": "+msg);
        liMensaje.appendChild(textoDeMensaje);
        chatWindow.appendChild(liMensaje);
      }
    });

    userAgent.on('connected', function () {
      user = $("#user").val();
      var fila = document.createElement('tr');
      var celda1 = document.createElement('td');
      var celda2 = document.createElement('td');
      var celda3 = document.createElement('td');
      var imgCelda1 = document.createElement("img");
      var txtCelda2 = document.createTextNode(user);
      var radioCelda3 = document.createElement("input");
      imgCelda1.src="Img/greendot.png";
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

    userAgent.on('newRTCSession', function(e) {
		  var originHeader = "";
      e.session.on('ended',function() {
      	if($("#auto_pause").val() === "True" && originHeader !== "") {
          num = "0077ACW";
    			makeCall(num);
    			entrante = false;
    			debugger;
    			// cod que se repite en main.js.. se deberia mejorar esto
    			pauseButton.className = "btn btn-danger";
	        pauseButton.innerHTML = "Resume";
	        modifyUserStat = document.getElementById("UserStatus");
	        modifyUserStat.className = "label label-warning";
	        modifyUserStat.innerHTML = "ACW";
	        flagPausa = true;
	        parar1();
	        inicio2();
        }
        defaultCallState();
      });
      //dar solucion a la repeticion de codigo, esto ya existe en main.js
      function parar1() {
	     clearInterval(control1);
	 		}
	 		function inicio2() {
	     control2 = setInterval(cronometro2, 1000);
	 		}
	 		//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
      e.session.on('failed',function(e) {
        $("#aTransfer").prop('disabled', true);
        $("#bTransfer").prop('disabled', true);
        $("#modalReceiveCalls").modal('hide');
        Sounds("","stop");
      });
      if(e.originator=="remote") {
      	entrante = true;
      	if(e.request.headers.Origin) {
      	  originHeader = e.request.headers.Origin[0].raw;
      	}
      	if (e.request.headers.Idcliente) {
      		var leadIdHeader = e.request.headers.Idcliente[0].raw;
      	}
        var fromUser = e.request.headers.From[0].raw;
        var endPos = fromUser.indexOf("@");
        var startPos = fromUser.indexOf(":");
        fromUser = fromUser.substring(startPos+1,endPos);

        if(leadIdHeader) {
          processLeadid(leadIdHeader);	
        } else {
        	if(fromUser !== "Unknown") {
        	  processCallid(fromUser);
        	} else {
        		getBlankForm();
        	}
        } 
        
        $("#callerid").text(fromUser);
        if($("#modalWebCall").is(':visible')) {
          $("#modalReceiveCalls").modal('show');
        } else {
          $("#modalWebCall").modal('show');
          $("#modalReceiveCalls").modal('show');
        }
        Sounds("In", "play");
        var atiendoSi = document.getElementById('answer');
        var atiendoNo = document.getElementById('doNotAnswer');
        var session_incoming = e.session;
        session_incoming.on('addstream',function(e) {
          remote_stream = e.stream;
          remoto = JsSIP.rtcninja.attachMediaStream(remoto, remote_stream);
        });
        var options = {'mediaConstraints': {'audio': true,'video': false}};
        atiendoSi.onclick = function() {
          $("#modalReceiveCalls").modal('hide');
          session_incoming.answer(options);
          setCallState("Connected", "orange");
          Sounds("","stop");
        };
        atiendoNo.onclick = function() {
          $("#modalReceiveCalls").modal('hide');
          if($("#autopause").val() === "True") {
          	
          }
          userAgent.terminateSessions();
          defaultCallState();
        };
        processOrigin(originHeader, options);
        function processOrigin(origin, opt) {
			  	var options = opt;
  				switch(origin) {
  					case "Dialer":
  						var dialerTag = document.getElementById("auto_attend_DIALER");
  						if(dialerTag.value === "True") {
  							$("#modalReceiveCalls").modal('hide');
  			  			session_incoming.answer(options);
          			setCallState("Connected", "orange");
          			Sounds("","stop");
  						}
  		  			break;
  					case "Inbound":
  		  			var inboundTag = document.getElementById("auto_attend_INBOUND");
  		  			if(inboundTag.value === "True") {
  		  				$("#modalReceiveCalls").modal('hide');
  			  			session_incoming.answer(options);
          			setCallState("Connected", "orange");
          			Sounds("","stop");
  						}
  		  			break;
			  		case "ICS":
  						var icsTag = document.getElementById("auto_attend_ICS");
  						if(icsTag.value === "True") {
			  				$("#modalReceiveCalls").modal('hide');
  			  			session_incoming.answer(options);
          			setCallState("Connected", "orange");
          			Sounds("","stop");
  						}	
  		  			break;  
  				}
  			}
      } else {
        Sounds("Out", "play");
        var session_outgoing = e.session;

      }
      e.session.on("accepted", function() {
        Sounds("", "stop");
        $("#aTransfer").prop('disabled', false);
        $("#bTransfer").prop('disabled', false);
      });
      /*e.session.on("", function() {
        Souds("Out", "stop");
        $("#aTransfer").prop('disabled', true);
        $("#bTransfer").prop('disabled', true);
      });*/
        var aTransf = document.getElementById("aTransfer");
        aTransf.onclick = function() {
          flagTransf = true;
          e.session.sendDTMF("*");
          e.session.sendDTMF("2");
          setTimeout(transferir(e), 3000);
        };

        var bTransf = document.getElementById("bTransfer");
        bTransf.onclick = function() {
          flagTransf = true;
          e.session.sendDTMF("#");
          e.session.sendDTMF("#");
          setTimeout(transferir(e), 3000);
        };
        function transferir(objRTCsession) {
          objRTCsession.session.sendDTMF(displayNumber.value);
        }
    });
  $("#endCall").click(function() {
    Sounds("", "stop");
    userAgent.terminateSessions();
    defaultCallState();
  });
  $("#call").click(function(e) {
  	entrante = false;
    // esto es para enviar un Invite/llamada
    num = displayNumber.value;
    makeCall(num);
  });
  function makeCall() {
    eventHandlers = {
      'confirmed':  function(e) {
        // Attach local stream to selfView
                    local.src = window.URL.createObjectURL(sesion.connection.getLocalStreams()[0]);
                    },
      'addstream':  function(e) {
                    setCallState("Connected", "orange");
                    var stream = e.stream;
                    // Attach remote stream to remoteView
                    remoto.src = window.URL.createObjectURL(stream);
                    },
      'failed': function(data) {
                  if (data.cause === JsSIP.C.causes.BUSY) {
                    Sounds("", "stop");
                    setCallState("Ocupado, intenta mas tarde", "orange");
                    setTimeout(defaultCallState, 5000);
                  } else if (data.cause === JsSIP.C.causes.REJECTED) {
                    setCallState("Rechazo, intenta mas tarde", "orange");
                    setTimeout(defaultCallState, 5000);
                  } else if (data.cause === JsSIP.C.causes.UNAVAILABLE) {
                      setCallState("Unavailable", "red");
                      setTimeout(defaultCallState, 5000);
                  } else if (data.cause === JsSIP.C.causes.NOT_FOUND) {
                    setCallState("Error, revisa el numero discado", "red");
                    setTimeout(defaultCallState, 5000);
                  } else if (data.cause === JsSIP.C.causes.AUTHENTICATION_ERROR) {
                    setCallState("Auth error", "red");
                    setTimeout(defaultCallState, 5000);
                  } else if (data.cause === JsSIP.C.causes.MISSING_SDP) {
                    setCallState("Missing sdp", "red");
                    setTimeout(defaultCallState, 5000);
                  } else if (data.cause === JsSIP.C.causes.ADDRESS_INCOMPLETE) {
                    setCallState("Address incomplete", "red");
                    setTimeout(defaultCallState, 5000);
                  }
                }
    };
    opciones = {
      'eventHandlers': eventHandlers,
      'mediaConstraints': {
                'audio': true,
                'video': false
              }
    };
    //Mando el invite/llamada
     if(flagInit === true) {
       flagInit = false;
       sesion = userAgent.call("sip:"+num+"@172.16.20.219", opciones);
     } else {
       sesion = userAgent.call("sip:"+num+"@172.16.20.219", opciones);
       setCallState("Calling.... "+num, "yellowgreen");
       displayNumber.value = "";
     }
  }
  function setCallState(estado, color) {
    callSipStatus.parentNode.removeChild(callSipStatus);
    callSipStatus = document.createElement("em");
    var textCallSipStatus = document.createTextNode(estado);
    callSipStatus.style.color = color;
    callSipStatus.appendChild(textCallSipStatus);
    callStatus.appendChild(callSipStatus);
  }
  function defaultCallState() {
    if(callStatus.childElementCount > 0) {
      callSipStatus.parentNode.removeChild(callSipStatus);
    }
    callSipStatus = document.createElement("em");
    textCallSipStatus = document.createTextNode("Idle");
    callSipStatus.style.color = "#80FF00";
    callSipStatus.appendChild(textCallSipStatus);
    callStatus.appendChild(callSipStatus);
  }
  function setSipStatus(img, state, elem) {
    
    if(elem.childElementCount > 0) {
      var hijo1 = document.getElementById("textSipStatus");
      var hijo2 = document.getElementById("imgStatus");
      elem.removeChild(hijo1);
      elem.removeChild(hijo2);
    }
    iconStatus = document.createElement('img');
    textSipStatus = document.createTextNode(state);
    iconStatus.id = "imgStatus";
    textSipStatus.id = "textSipStatus";
    elem.style.color="white";
    iconStatus.src = "/static/ominicontacto/Img/"+img;
    elem.appendChild(iconStatus);
    elem.appendChild(textSipStatus);
  }
  function Sounds(callType, action) {
    var ring = null;
    if(action === "play") {
      if(callType === "In") {
        ring = document.getElementById('RingIn');
        ring.play();
      } else {
        ring = document.getElementById('RingOut');
        ring.play();
      }
    } else {
        ring = document.getElementById('RingIn');
        ring.pause();
        ring = document.getElementById('RingOut');
        ring.pause();
    }
  }
  function getBlankForm() {
    var url = '/contacto/list/';
    $("#dataView").attr('src', url); 
  }
  function processCallid(callerid) {
  	var url = "/contacto/"+callerid+"/list/";
  	$("#dataView").attr('src', url);
  }
  function processLeadid(leadid) {
  	var url = "/contacto/"+leadid+"/update/"; 
  	$("#dataView").attr('src', url);
  }
});
