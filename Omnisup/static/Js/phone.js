$(function () {
  var sipStatus = document.getElementById('SipStatus');
  var modifyUserStat = document.getElementById("UserStatus");
  var callStatus = document.getElementById('CallStatus');
  var userAgent;
  var sipSession;
  var num;
  var flagLogin = 0;
  var local = document.getElementById('localAudio');
  var remoto = document.getElementById('remoteAudio');
  var config = {
  };
  var userAgent;
  var sipSession;
  $.ajax({
    url: 'Controller/Detalle_Campana_Contenido.php',
    type: 'GET',
    dataType: 'html',
    data: 'supId='+$("#userId").val(),
    success: function (msg) {
      var msg = JSON.parse(msg);
      if(msg!=="]") {
        config.uri= 'sip:' + msg.sipuser + '@' + KamailioIp;
        config.ws_servers= 'wss://' + KamailioIp+":"+ KamailioPort;
        config.password= msg.sippass;
        config.hack_ip_in_contact= true;
        config.session_timers= false;

        userAgent = new JsSIP.UA(config);
        sipSession = userAgent.start();

        $("#sipUser").val(msg.sipuser);
        $("#sipPass").val(msg.sippass);

        userAgent.on('registered', function(e) { // cuando se registra la entidad SIP
          setSipStatus("greendot.png", "  Registered", sipStatus);
          defaultCallState();
        });

        userAgent.on('unregistered', function(e) {  // cuando se desregistra la entidad SIP
          setSipStatus("reddot.png", "  Unregistered", sipStatus);
          $("#Pause").prop('disabled',true);
          $("#Resume").prop('disabled',true);
        });

        userAgent.on('registrationFailed', function(e) {  // cuando falla la registracion
          setSipStatus("redcross.png", "  Registration failed", sipStatus);
        });
        //
        userAgent.on('newRTCSession', function(e) {       // cuando se crea una sesion RTC
          var originHeader = "";
          e.session.on("ended",function() {               // Cuando Finaliza la llamada
            var callerOrCalled = "";
            if(entrante) {
            	callerOrCalled = fromUser;
            } else {
              callerOrCalled =  num;
            }
            defaultCallState();
          });
          e.session.on("failed",function(e) {  // cuando falla el establecimiento de la llamada
            $("#modalReceiveCalls").modal('hide');
            Sounds("","stop");
          });
          if(e.originator=="remote") {         // Origen de llamada Remoto
            entrante = true;
            fromUser = e.request.headers.From[0].raw;
            var endPos = fromUser.indexOf("@");
            var startPos = fromUser.indexOf(":");
            fromUser = fromUser.substring(startPos+1,endPos);
            Sounds("In", "play");
            var atiendoSi = document.getElementById('answer');
            var atiendoNo = document.getElementById('doNotAnswer');
            var session_incoming = e.session;
            //atiende automaticamente
            $("#modalReceiveCalls").modal('hide');
            session_incoming.answer(options);
            setCallState("Connected", "orange");
            Sounds("","stop");
            //-----------------------
            session_incoming.on('addstream',function(e) {       // al cerrar el canal de audio entre los peers
              lastPause = $("#UserStatus").html();
              remote_stream = e.stream;
              remoto = JsSIP.rtcninja.attachMediaStream(remoto, remote_stream);
            });
            var options = {'mediaConstraints': {'audio': true, 'video': false}};

            atiendoSi.onclick = function() {
              $("#modalReceiveCalls").modal('hide');
              session_incoming.answer(options);
              setCallState("Connected", "orange");
              Sounds("","stop");
            };

            atiendoNo.onclick = function() {
              $("#modalReceiveCalls").modal('hide');
              userAgent.terminateSessions();
              defaultCallState();
            };
          }

          e.session.on("accepted", function() { 			// cuando se establece una llamada
            Sounds("", "stop");
            lastPause = $("#UserStatus").html();
          });
        });
      }
    },
    error: function (jqXHR, textStatus, errorThrown) {
      console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
    }
  });

  $("#tableAgBody").on('click', '.chanspy', function () {
    var id = this.id;
    var sipExt = $("#sipUser").val();
    $.ajax({
      url: 'Controller/actionListener.php',
      type: 'GET',
      dataType: 'html',
      data: 'sip=' + id + '&sipext=' + sipExt + "&action=spy",
      success: function (msg) {
      },
      error: function (jqXHR, textStatus, errorThrown) {
        debugger;
        console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
      }
    });
  });

  $("#tableAgBody").on('click', '.chanspywhisper', function () {
    var id = this.id;
    var sipExt = $("#sipUser").val();
    $.ajax({
      url: 'Controller/actionListener.php',
      type: 'GET',
      dataType: 'html',
      data: 'sip=' + id + '&sipext=' + sipExt + "&action=spywhisper",
      success: function (msg) {
      },
      error: function (jqXHR, textStatus, errorThrown) {
        debugger;
      console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
      }
    });
  });

  $("#tableAgBody").on('click', '.conference', function () {
    var id = this.id;
    var sipExt = $("#sipUser").val();
    $.ajax({
      url: 'Controller/actionListener.php',
      type: 'GET',
      dataType: 'html',
      data: 'sip=' + id + '&sipext=' + sipExt + "&action=confer",
      success: function (msg) {
      },
      error: function (jqXHR, textStatus, errorThrown) {
        debugger;
        console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
      }
    });
  });

  $("#tableAgBody").on('click', '.agentlogoff', function () {
    var id = this.id;
    var sipExt = $("#sipUser").val();
    $.ajax({
      url: 'Controller/actionListener.php',
      type: 'GET',
      dataType: 'html',
      data: 'sip=' + id + '&sipext=' + sipExt + "&action=logoutagent",
      success: function (msg) {
      },
      error: function (jqXHR, textStatus, errorThrown) {
        debugger;
        console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
      }
    });
  });

  $("#tableAgBody").on('click', '.pause', function () {
    var id = this.id;
    var sipExt = $("#sipUser").val();
    $.ajax({
      url: 'Controller/actionListener.php',
      type: 'GET',
      dataType: 'html',
      data: 'sip=' + id + '&sipext=' + sipExt + "&action=pauseagent",
      success: function (msg) {
        $(".btn.btn-primary.btn-xs.pause").removeClass("pause").addClass("unpause");
        $(".glyphicon.glyphicon-pause").removeClass("glyphicon-pause").addClass("glyphicon-play");
      },
      error: function (jqXHR, textStatus, errorThrown) {
        debugger;
        console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
      }
    });
  });

  $("#tableAgBody").on('click', '.unpause', function () {
    var id = this.id;
    var sipExt = $("#sipUser").val();
    $.ajax({
      url: 'Controller/actionListener.php',
      type: 'GET',
      dataType: 'html',
      data: 'sip=' + id + '&sipext=' + sipExt + "&action=unpauseagent",
      success: function (msg) {
        $(".btn.btn-primary.btn-xs.unpause").removeClass("unpause").addClass("pause");
        $(".glyphicon.glyphicon-play").removeClass("glyphicon-play").addClass("glyphicon-pause");
      },
      error: function (jqXHR, textStatus, errorThrown) {
        debugger;
        console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
      }
    });
  });

  $("#tableAgBody").on('click', '.takecall', function () {
    var id = this.id;
    var sipExt = $("#sipUser").val();
    $.ajax({
      url: 'Controller/actionListener.php',
      type: 'GET',
      dataType: 'html',
      data: 'sip=' + id + '&sipext=' + sipExt + "&action=takecall",
      success: function (msg) {
      },
      error: function (jqXHR, textStatus, errorThrown) {
        debugger;
        console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
      }
    });
  });

  $("#endCall").click(function() {
    Sounds("", "stop");
    userAgent.terminateSessions();
    defaultCallState();
  });
  //


  function makeCall(extraHds=null) {
    eventHandlers = {
      'confirmed':  function(e) {
                    local.src = window.URL.createObjectURL(sipSession.connection.getLocalStreams()[0]);
                },
      'addstream':  function(e) {
                    var stream = e.stream;
                    remoto.src = window.URL.createObjectURL(stream);
                },
      'failed': function(data) {
                if (data.cause === JsSIP.C.causes.BUSY) {
                  Sounds("", "stop");
                  Sounds("", "play");
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
                } else if (data.cause === "SIP Failure Code") {
      		  setCallState("JsSIP SIP Failure code (500)", "red");
                  setTimeout(defaultCallState, 5000);
                }
            }
    };
    var opciones = {
      'eventHandlers': eventHandlers,
      'mediaConstraints': {
              'audio': true,
              'video': false
      }
    };
    if(extraHds !== null) {
      opciones.extraHeaders = [extraHds];
    }
    sipSession = userAgent.call("sip:"+num+"@"+KamailioIp, opciones);
  }

  function setCallState(estado, color) {
    if(callStatus.childElementCount > 0) {
      callSipStatus.parentNode.removeChild(callSipStatus);
    }
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
    $("#aTransfer").prop('disabled', true);
    $("#bTransfer").prop('disabled', true);
    $("#onHold").prop('disabled', true);
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
    iconStatus.src = "/Omnisup/static/Img/"+img;
    elem.appendChild(iconStatus);
    elem.appendChild(textSipStatus);
  }

  function Sounds(callType, action) {
    var ring = null;
    if(action === "play") {
      if(callType === "In") {
        ring = document.getElementById('RingIn');
        ring.play();
      } else if(callType === "Out") {
        ring = document.getElementById('RingOut');
        ring.play();
      } else {
      	ring = document.getElementById('RingBusy');
        ring.play();
      }
    } else {
      ring = document.getElementById('RingIn');
      ring.pause();
      ring = document.getElementById('RingOut');
      ring.pause();
      ring = document.getElementById('RingBusy');
      ring.pause();
    }
  }

  $("#webphone").click(function () {
    $("#modalWebCall").modal('show');
  });
});
