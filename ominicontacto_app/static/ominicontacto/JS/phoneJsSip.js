var lastDialedNumber, entrante, config, textSipStatus, callSipStatus, iconStatus, userAgent, sesion, opciones, eventHandlers, flagHold = true;
var flagTransf = false,flagInit = true, num = null, headerIdCamp, headerNomCamp, calltypeId, flagPausa = 0, fromUser, wId, lastPause, uid = "";
var agentIdHeaderVal, campaignIdHeaderVal;
var sipStatus = document.getElementById('SipStatus');
var callStatus = document.getElementById('CallStatus');
var local = document.getElementById('localAudio');
var remoto = document.getElementById('remoteAudio');
var displayNumber = document.getElementById("numberToCall");
var pauseButton = document.getElementById("Pause");

function updateButton(btn,clsnm,inht) {
	 	 btn.className = clsnm;
	 	 var lastval = btn.innerHTML;
	 	 btn.innerHTML = inht;
	 	 return lastval;
}

$(function() {

	var idTipoCamp = $("#cmpList option:selected").attr('campana_type');
	$("#modalWebCall").modal('show');
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

	function getCampActivas(status, idagente) {
		$.ajax({
			type: "get",
			url: "/service/campana/activas/",
			contentType: "text/html",
			success: function (msg) {
				for (var i = 0; i < msg.campanas.length; i++) {
					$("#campToTransfer").append("<option value='" + msg.campanas[i].id + "'>" + msg.campanas[i].nombre + "</option>");
				}
			},
			error: function (jqXHR, textStatus, errorThrown) {
					console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
			}
		});
	}

	function getAgentes(status, idagente) {
		$.ajax({
			type: "get",
			url: "/service/agente/otros_agentes_de_grupo/",
			contentType: "text/html",
			success: function (msg) {
				for (var i = 0; i < msg.agentes.length; i++) {
					$("#agentToTransfer").append("<option value='" + msg.agentes[i].id + "'>" + msg.agentes[i].full_name + "</option>");
				}
			},
			error: function (jqXHR, textStatus, errorThrown) {
					console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
			}
		});
	}

	var modifyUserStat = document.getElementById("UserStatus");
	$("#redial").prop('disabled', true);
	$('#modalSelectCmp').modal('hide');
  var estado = JSON.stringify({'status' : 'online'});

	 $("#SignCall").click(function () {
	   $("#modalSignCall").modal('show');
	 });

	 $("#SaveSignedCall").click(function () {
	 	 var desc = $("#SignDescription").val();// sign subject
		 var URl = "grabacion/marcar/";
		 var data2 =  {"uid": uid, "descripcion": desc};
	 	 $.ajax({
	 	   url: URl,
	 	   type: 'POST',
       dataType: 'json',
       data: data2,
       succes: function (msg) {

	     },
    	 error: function (jqXHR, textStatus, errorThrown) {
         console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
    	 }
	 	 });
	   $("#modalSignCall").modal('hide');
	   campid = idagt = desc = null;
	 });

  $("#Resume").click(function() {
  	num = "0077UNPAUSE";
    makeCall();
  });

  $("#setPause").click(function() {
  	var pausa = $("#pauseType").val().toUpperCase();
  	if(pausa.indexOf(' ')) {
  		pausa = pausa.replace(' ','');
  	}
    num = "0077" + pausa;
    makeCall();
  });

  if($("#sipExt").val() && $("#sipSec").val()) {
    config = {
      uri : "sip:"+$("#sipExt").val()+"@"+KamailioIp,
      ws_servers : "wss://"+KamailioIp+":"+ KamailioPort,
      password : $("#sipSec").val(),
      hack_ip_in_contact: true,
      session_timers: false,
			pcConfig: {
				rtcpMuxPolicy: 'negotiate'}
    };
    userAgent = new JsSIP.UA(config);
    sesion = userAgent.start();
  }

  $("#CallList").click(function() {
    $("#modalCallList").modal('show');
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

  //Connects to the WebSocket server
  userAgent.on('registered', function(e) { // cuando se registra la entidad SIP
		getAgentes();
		getCampActivas();
    setSipStatus("greydot.png", "  No account", sipStatus);
  	updateButton(modifyUserStat, "label label-success", "Online");
    num = "0077LOGIN";
    makeCall();
    $("#sendMessage").prop('disabled', false);
    $("#chatMessage").prop('disabled', false);
    iconStatus.parentNode.removeChild(iconStatus);
    textSipStatus.parentNode.removeChild(textSipStatus);
    setSipStatus("greendot.png", "  Registered", sipStatus);
    defaultCallState();
  });

  userAgent.on('registrationFailed', function(e) {  // cuando falla la registracion
    setSipStatus("redcross.png", "  Registration failed", sipStatus);
  });

  userAgent.on('newRTCSession', function(e) {       // cuando se crea una sesion RTC

		var objLastPause = {};
		objLastPause.LastStatusAgent = $("#UserStatus").html();
		objLastPause.LastStatusAgentClass = $("#UserStatus").attr('class');
		objLastPause.LastBtnStatusPause = $("#Pause").prop('disabled');
		objLastPause.LastBtnStatusResume = $("#Resume").prop('disabled');
		objLastPause.LastBtnStatusSipLogout = $("#sipLogout").prop('disabled');
	  var originHeader = "";

    function saveCall(callerOrCalled) {
    	$.ajax({
          type: "get",
	   	    url: "/duracion/llamada/",
	   	    contentType: "text/html",
	   	    data : "duracion=" + $("#horaC").html() + $("#minsC").html() + $("#segsC").html() + "&agente="+$("#idagt").val()+"&numero_telefono="+callerOrCalled+"&tipo_llamada="+calltypeId,
	   	    success: function (msg) {
	   	 	    $("#call_list").html(msg);
	   	    },
	   	    error: function (jqXHR, textStatus, errorThrown) {
	          debugger;
	          console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
	        }
        });
    }
    function originToId(origin) {
      var id = '';
			var origin = origin;
			if (origin) {
				if (origin.search("DIALER") === 0) {
					origin = "DIALER";
				}
			}
      switch(origin) {
				case "CLICK2CALL":
  			  id = 5;
  		  	break;
  		  case "DIALER":
  			  id = 2;
  		  	break;
  			case "IN":
  		    id = 3;
  		  	break;
			  case "ICS":
  				id = 1;
  				break;
 				default:
  			  id = 4;
  			  break;
  		}
  	  return id;
    }
    function reinicio(horaDOM, minDOM, segDOM, controlX, cent, seg, min) {
	    clearInterval(controlX);
	    cent = 0;
	    seg = 0;
	    min = 0;
	    segDOM.html(":00");
	    minDOM.html(":00");
	    horaDOM.html("00");
  	}
    //dar solucion a la repeticion de codigo, esto ya existe en main.js
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
	 	function parar3() {
	     clearInterval(control3);
	 	}
	 	function inicio3() {
	 	  control3 = setInterval(cronometro3, 1000);
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
	 	//****************************CRONOMETRO DE Pausas***********************************
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
	 //****************************CRONOMETRO DE LLAMADA***********************************
	 function cronometro3() { // Cronometro embebido en el webphone
	     if (centesimasC < 59) {
	         centesimasC++;
	         if (centesimasC < 10) {
	             centesimasC = "0" + centesimasC;
	         }
	         $("#segsC").html(":" + centesimasC);
	     }
	     if (centesimasC == 59) {
	         centesimasC = -1;
	     }
	     if (centesimasC == 0) {
	         segundosC++;
	         if (segundosC < 10) {
	             segundosC = "0" + segundosC;
	         }
	         $("#minsC").html(":" + segundosC);
	     }
	     if (segundosC == 59) {
	         segundosC = -1;
	     }
	     if ((centesimasC == 0) && (segundosC == 0)) {
	         minutosC++;
	         if (minutosC < 10) {
	             minutosC = "0" + minutosC;
	         }
	         $("#horaC").html("" + minutosC);
	     }
	 }
	 	//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    e.session.on("failed",function(e) {  // cuando falla el establecimiento de la llamada
      $("#Transfer").prop('disabled', true);
      $("#onHold").prop('disabled', true);
      $("#modalReceiveCalls").modal('hide');
      Sounds("","stop");
    });
      if(e.originator=="remote") {         // Origen de llamada Remoto
        entrante = true;
      	if(e.request.headers.Wombatid) {
      		wId = e.request.headers.Wombatid[0].raw;
      	}
      	if(e.request.headers.Origin) {
      	  originHeader = e.request.headers.Origin[0].raw;
      	}
      	if (e.request.headers.Idcliente) {
      		var leadIdHeader = e.request.headers.Idcliente[0].raw;
      	}
      	if (e.request.headers.Idcamp) {
      		var CampIdHeader = e.request.headers.Idcamp[0].raw;
      		$("#idCamp").val(CampIdHeader);
      	}

        if(e.request.headers.Uidgrabacion) {
	        uid = e.request.headers.Uidgrabacion[0].raw;
        }
        fromUser = e.request.headers.From[0].raw;
        var endPos = fromUser.indexOf("@");
        var startPos = fromUser.indexOf(":");
        fromUser = fromUser.substring(startPos+1,endPos);

        if(CampIdHeader) {
        	if(leadIdHeader) {
						if(originHeader === "DIALER-FORM") {
							getData(CampIdHeader, leadIdHeader, $("#idagt").val(), wId);
						} else if (originHeader === "DIALER-SITIOEXTERNO") {
							var linkaddress = e.request.headers.Sitioexterno[0].raw;
							getIframe(linkaddress);
						} else if (originHeader === "DIALER-JSON") {

						} else if (originHeader === "CLICK2CALL") {
                getData(CampIdHeader, leadIdHeader, $("#idagt").val(), 0);
            }
             else if (originHeader === "CLICK2CALLPREVIEW") {
               getData(CampIdHeader, leadIdHeader, $("#idagt").val(), 0);
						}
        	} else {
        		if(fromUser !== "Unknown") {
              getFormManualCalls(CampIdHeader, $("#idagt").val(), fromUser);
        		} else {
        			getBlankFormCamp(CampIdHeader);
        		}
        	}
        }

        $("#callerid").text(fromUser);
        Sounds("In", "play");
        var atiendoSi = document.getElementById('answer');
        var atiendoNo = document.getElementById('doNotAnswer');
        var session_incoming = e.session;

        session_incoming.on('addstream',function(e) {       // al cerrar el canal de audio entre los peers
        	$("#Pause").prop('disabled',true);
        	$("#Resume").prop('disabled',true);
        	$("#sipLogout").prop('disabled',true);
        	lastPause = $("#UserStatus").html();
        	updateButton(modifyUserStat, "label label-primary", "OnCall");
          remote_stream = e.stream;
          remoto = JsSIP.rtcninja.attachMediaStream(remoto, remote_stream);
        });

        var options = {'mediaConstraints': {'audio': true, 'video': false}};
        calltypeId = originToId(originHeader);
        processOrigin(originHeader, options, fromUser);

        atiendoSi.onclick = function() {
          $("#modalReceiveCalls").modal('hide');
          session_incoming.answer(options);
          setCallState("Connected to " +fromUser , "orange");
          Sounds("","stop");
				};

        atiendoNo.onclick = function() {
          $("#modalReceiveCalls").modal('hide');
          if($("#autopause").val() === "True") {
          }
          userAgent.terminateSessions();
          defaultCallState();
				};

    function processOrigin(origin, opt, from) {
	    var options = opt;
	    var origin = origin;
	    if (origin) {
	      if (origin.search("DIALER") === 0) {
	        origin = "DIALER";
	      }

				if (origin !== "CLICK2CALL" && origin !== "CLICK2CALLPREVIEW") {
				  if (document.querySelector("#auto_attend_" + origin).value == "True") {
					  session_incoming.answer(options);
					  setCallState("Connected to " + from, "orange");
					  Sounds("","stop");
				  } else {
					  $("#modalReceiveCalls").modal('show');
				  }
				} else {
					session_incoming.answer(options);
					setCallState("Connected to " + from, "orange");
					Sounds("","stop");
			  }
	    }
    }

      } else {
      	calltypeId = originToId(null);
        Sounds("Out", "play");
        var session_outgoing = e.session;
      }

      e.session.on("accepted", function() { 			// cuando se establece una llamada
        Sounds("", "stop");
        $("#Transfer").prop('disabled', false);
        $("#onHold").prop('disabled', false);

        if (num.substring(4,0) != "0077") {
					inicio3();
	       	$("#Pause").prop('disabled',true);
	       	$("#Resume").prop('disabled',true);
	       	$("#sipLogout").prop('disabled',true);
	       	lastPause = $("#UserStatus").html();
	       	updateButton(modifyUserStat, "label label-primary", "OnCall");
		    }
				if (fromUser) {
					inicio3();
				}
      });

			var clickHold = document.getElementById("onHold");
	  	clickHold.onclick = function () {
				if(flagHold) {
	  	 		flagHold = false;
					e.session.sendDTMF("*");
		      e.session.sendDTMF("2");
		      setTimeout(transferirHold(e), 1000);
	  	 	} else {
	  	 	  flagHold = true;
					e.session.sendDTMF("*");
		      e.session.sendDTMF("1");
	  	 	}
			};

		var one = document.getElementById("1");
		one.onclick = function() {
			e.session.sendDTMF('1');
		};

		var two = document.getElementById("2");
		two.onclick = function() {
			e.session.sendDTMF('2');
		};

		var three = document.getElementById("3");
		three.onclick = function() {
			e.session.sendDTMF('3');
		};

		var four = document.getElementById("4");
		four.onclick = function() {
			e.session.sendDTMF('4');
		};

		var five = document.getElementById("5");
		five.onclick = function() {
			e.session.sendDTMF('5');
		};

		var six = document.getElementById("6");
		six.onclick = function() {
			e.session.sendDTMF('6');
		};

		var seven = document.getElementById("7");
		seven.onclick = function() {
			e.session.sendDTMF('7');
		};

		var eight = document.getElementById("8");
		eight.onclick = function() {
			e.session.sendDTMF('8');
		};

		var nine = document.getElementById("9");
		nine.onclick = function() {
			e.session.sendDTMF("9");
		};
		var dash = document.getElementById("#");
		dash.onclick = function() {
			e.session.sendDTMF("#");
		};
		var ast = document.getElementById("*");
		ast.onclick = function() {
			e.session.sendDTMF("*");
		};

		var makeTransfer = document.getElementById("makeTransfer");
		var blindTransf = document.getElementById("blindTransf");
		var consultTransf = document.getElementById("consultTransf");
		var transfToAgent = document.getElementById("transfToAgent");
		var transfToNum = document.getElementById("transfToNum");
		var transfToCamp = document.getElementById("transfToCamp");
		$("#Transfer").click(function () {
			$("#modalTransfer").modal("show");
		});

		$("#blindTransf").change(function () {
			if (this.checked) {
				$("#campToTransfer").prop('disabled', false);
				transfToCamp.checked = true;
				transfToCamp.disabled = false;
			}
		});

		$("#consultTransf").change(function () {
			if (this.checked) {
				$("#campToTransfer").prop('disabled', true);
				transfToCamp.checked = false;
				transfToCamp.disabled = true;
			} else {
				$("#campToTransfer").prop('disabled', false);
				transfToCamp.checked = true;
			}
		});

		$("#transfToNum").change(function () {
			if (this.checked) {
				$("#numberToTransfer").prop('disabled', false);
				$("#campToTransfer").prop('disabled', true);
				$("#agentToTransfer").prop('disabled', true);
			}
		});

		$("#transfToCamp").change(function () {
			if (this.checked) {
				$("#campToTransfer").prop('disabled', false);
				$("#numberToTransfer").prop('disabled', true);
				$("#agentToTransfer").prop('disabled', true);
			}
		});

		$("#transfToAgent").change(function () {
			if (this.checked) {
				$("#agentToTransfer").prop('disabled', false);
				$("#campToTransfer").prop('disabled', true);
				$("#numberToTransfer").prop('disabled', true);
			}
		});

		makeTransfer.onclick = function () {
		  flagTransf = true;
			if (blindTransf.checked) {
				e.session.sendDTMF("#");
				e.session.sendDTMF("#");
				if (transfToAgent.checked) {
					if ($("select[id=agentToTransfer]").val()) {
						agentIdHeaderVal = $("select[id=agentToTransfer]").val();
						setTimeout(function () {
							e.session.sendDTMF("0");
							e.session.sendDTMF("0");
							e.session.sendDTMF("0");
							e.session.sendDTMF("0");
							e.session.sendDTMF(agentIdHeaderVal);
						}, 2500);
					}
				} else if (transfToCamp.checked) {
					if ($("select[id=campToTransfer]").val()) {
						campaignIdHeaderVal = $("select[id=campToTransfer]").val();
						setTimeout(function () {
							e.session.sendDTMF("9");
							e.session.sendDTMF("9");
							e.session.sendDTMF("9");
							e.session.sendDTMF("9");
							e.session.sendDTMF(campaignIdHeaderVal);
						}, 2500);
				  }
				} else if (transfToNum.checked) {
				  if ($("#numberToTransfer").val()) {
						var i = 0;
	          setTimeout(function () {
							while(i < $("#numberToTransfer").val().length) {
								e.session.sendDTMF($("#numberToTransfer").val()[i]);
								i++;
							}
						}, 2500);
				  }
				}
			} else if (consultTransf.checked) {
				e.session.sendDTMF("*");
				e.session.sendDTMF("2");
				if (transfToAgent.checked == true) {
					if ($("select[id=agentToTransfer]").val()) {
						agentIdHeaderVal = $("select[id=agentToTransfer]").val();
						setTimeout(function () {
							e.session.sendDTMF("1");
							e.session.sendDTMF("1");
							e.session.sendDTMF("1");
							e.session.sendDTMF("1");
							e.session.sendDTMF(agentIdHeaderVal);
						}, 2500);
					}
				} else if (transfToNum.checked) {
					if ($("#numberToTransfer").val()) {
						var i = 0;
						setTimeout(function () {
							while(i < $("#numberToTransfer").val().length) {
								e.session.sendDTMF($("#numberToTransfer").val()[i]);
								i++;
							}
						}, 2500);
					}
				}
			}
		};

    function transferir(objRTCsession, transferDst) {
      objRTCsession.session.sendDTMF(transferDst);
    }

		function transferirHold(objRTCsession) {
      objRTCsession.session.sendDTMF('*098');
    }

		e.session.on("ended", function() {               // Cuando Finaliza la llamada
			parar3();
			reinicio($("#horaC"), $("#minsC"), $("#segsC"), control3, centesimasC, segundosC, minutosC);
			if(entrante) {
				if(fromUser) { // fromUser es para entrantes
					if(lastPause === "Online" && fromUser.substring(4,0) != "0077") {
						saveCall(fromUser);
						num = '';
						fromUser = "";
						$("#Pause").prop('disabled',false);
						$("#Resume").prop('disabled',true);
						$("#sipLogout").prop('disabled',false);
						updateButton(modifyUserStat, "label label-success", "Online");
					} else if(lastPause === "OnCall") {
						saveCall(fromUser);
						num = '';
						fromUser = "";
						$("#Pause").prop('disabled',false);
						$("#Resume").prop('disabled',true);
						$("#sipLogout").prop('disabled',false);
						updateButton(modifyUserStat, "label label-success", "Online");
					} else {
						fromUser = "";
						$("#Pause").prop('disabled',true);
						$("#Resume").prop('disabled',false);
						$("#sipLogout").prop('disabled',false);
						updateButton(modifyUserStat, "label label-danger", lastPause);
					}
					if (fromUser.substring(4,0) != "0077") {
							if ($("#auto_pause").val() == "True") {//Si es un agente predictivo
								changeStatus(3, $("#idagt").val());
						    num = "00770";
						    makeCall();
						    entrante = false;
								$("#Pause").prop('disabled',true);
								$("#Resume").prop('disabled',false);
								$("#sipLogout").prop('disabled',false);
								updateButton(modifyUserStat, "label label-danger", "ACW");
								parar1();
								inicio2();
								if ($("#auto_unpause").val() != 0) {
							    var timeoutACW = $("#auto_unpause").val();
							    timeoutACW = timeoutACW * 1000;
							    var toOnline = function() {
							      num = "0077UNPAUSE";
							      if ($("#UserStatus").html() === "ACW") {
                      if ($("#dial_status").html().substring(9,0) !== "Connected" && $("#dial_status").html().substring(7,0) !== "Calling")
							        {
                        makeCall();
							          $("#Resume").trigger('click');
                      }
							      }
							    };

							    setTimeout(toOnline, timeoutACW);
							  }
							} // si no es agente predictivo....
					}
				}
			} else { // si NO es una llamada entrante
			  if (num) { // num para salientes
				  if (num.substring(4,0) != "0077") {
						saveCall(num);
						if (lastPause != "Online") {
							num = '';
							$("#Pause").prop('disabled',true);
							$("#Resume").prop('disabled',false);
							$("#sipLogout").prop('disabled',false);
							updateButton(modifyUserStat, "label label-danger", lastPause);
						} else {
							$("#Pause").prop('disabled',false);
							$("#Resume").prop('disabled',true);
							$("#sipLogout").prop('disabled',false);
							updateButton(modifyUserStat, "label label-success", lastPause);
						}
            if ($("#auto_pause").val() == "True") {//Si es un agente predictivo
              //if (entrante == false) { funcionalidad oml-52
							  changeStatus(3, $("#idagt").val());
					      num = "00770";
					      makeCall();
					      entrante = false;
							  $("#Pause").prop('disabled',true);
							  $("#Resume").prop('disabled',false);
							  $("#sipLogout").prop('disabled',false);
							  updateButton(modifyUserStat, "label label-danger", "ACW");
                if($("#auto_unpause").val() != 0) {
								  var timeoutACW = $("#auto_unpause").val();
								  timeoutACW = timeoutACW * 1000;
                  var toOnline = function() {
									  num = "0077UNPAUSE";
									  if($("#UserStatus").html() === "ACW") {
										  if ($("#dial_status").html().substring(9,0) !== "Connected" && $("#dial_status").html().substring(7,0) !== "Calling") {
										    makeCall();
										    $("#Resume").trigger('click');
									    }
									  }
                  };
								  setTimeout(toOnline, timeoutACW);
                }
              //} funcionalidad oml-52
            }
					}
		   }
		 }
		 defaultCallState();
    });

  });

	$("#numberToCall").bind("keypress", function(event) {
		if(event.which == 13) {
			event.preventDefault();
			entrante = false;
			if(displayNumber.value != "") {
				displayNumber.style.borderColor = "black";
	      num = displayNumber.value;
	      lastDialedNumber = num;
				if($("#campAssocManualCall").html() == "") {
					$("#modalSelectCmp").modal("show");
				} else {
					headerIdCamp = $("#cmpList").val();
			  	$("#idCamp").val(headerIdCamp);
					var nombrecamp = $("#cmpList option:selected").html();
					nombrecamp = nombrecamp.substring(1);
			  	headerNomCamp = $("#idCamp").val() + '_' + nombrecamp;
			    $("#redial").prop('disabled', false);
			  	makeCall();
				}
			} else {
	      displayNumber.style.borderColor = "red";
			}
		}
	});

  $("#redial").click(function () {// esto es para enviar un Invite/llamada
  	entrante = false;
  	num = lastDialedNumber;
		if($("#campAssocManualCall").html() == "") {
  	  $("#modalSelectCmp").modal("show");
    } else {
			makeCall();
			Sounds("Out", "play");
			setTimeout(function () {//luego de 60 segundos, stop al ringback y cuelga discado
				Sounds("", "stop");
				userAgent.terminateSessions();
				defaultCallState();
			}, 61000);
		}
  });

  $("#endCall").click(function() {
    Sounds("", "stop");
    userAgent.terminateSessions();
    defaultCallState();
  });

  $("#call").click(function(e) {
  	entrante = false;
		if(displayNumber.value != "") {
			displayNumber.style.borderColor = "black";
      num = displayNumber.value;
      lastDialedNumber = num;
			if($("#campAssocManualCall").html() == "") {
				$("#modalSelectCmp").modal("show");
			} else {
				headerIdCamp = $("#cmpList").val();
		  	$("#idCamp").val(headerIdCamp);
				var nombrecamp = $("#cmpList option:selected").html();
				nombrecamp = nombrecamp.substring(1);
				headerNomCamp = $("#idCamp").val() + '_' + nombrecamp;
		    $("#redial").prop('disabled',false);
		  	makeCall();
				getFormManualCalls($("#idCamp").val(), $("#idagt").val(), num);
				setTimeout(function () {//luego de 60 segundos, stop al ringback y cuelga discado
					Sounds("", "stop");
			    userAgent.terminateSessions();
			    defaultCallState();
				}, 61000);
			}
		} else {
      displayNumber.style.borderColor = "red";
		}
  });

	$("#changeCampAssocManualCall").click(function () {
		$("#modalSelectCmp").modal("show");
	});

  $("#SelectCamp").click(function () {
    if(displayNumber.value != "") {
			$("#modalSelectCmp").modal("hide");
	  	headerIdCamp = $("#cmpList").val();
	  	$("#idCamp").val(headerIdCamp);
			var nombrecamp = $("#cmpList option:selected").html();
			nombrecamp = nombrecamp.substring(1);
			headerNomCamp = $("#idCamp").val() + '_' + nombrecamp;
			var idTipoCamp = $("#campana_type").val();
	    $("#redial").prop('disabled',false);
			$("#campAssocManualCall").html(headerNomCamp);
			getFormManualCalls($("#idCamp").val(), $("#idagt").val(), displayNumber.value);
	  	makeCall();
			setTimeout(function () {//luego de 60 segundos, stop al ringback y cuelga discado
				Sounds("", "stop");
		    userAgent.terminateSessions();
		    defaultCallState();
			}, 61000);
    } else {
			$("#modalSelectCmp").modal("hide");
			headerIdCamp = $("#cmpList").val();
	  	$("#idCamp").val(headerIdCamp);
			var nombrecamp = $("#cmpList option:selected").html();
			nombrecamp = nombrecamp.substring(1);
			headerNomCamp = $("#idCamp").val() + '_' + nombrecamp;
	    $("#redial").prop('disabled', false);
			$("#campAssocManualCall").html(headerNomCamp);
		}
  });

  function makeCall() {
    eventHandlers = {
      'confirmed':  function(e) {
        // Attach local stream to selfView
                    local.src = window.URL.createObjectURL(sesion.connection.getLocalStreams()[0]);
                    },
      'addstream':  function(e) {
										if(num.substring(4,0) != "0077"){
											setCallState("Connected to " + num, "orange");
										} else {
											setCallState("Connected", "orange");
										}
                    var stream = e.stream;
                    // Attach remote stream to remoteView
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
		idTipoCamp = $("#cmpList option:selected").attr('campana_type');
    opciones = {
      'eventHandlers': eventHandlers,
      'mediaConstraints': {
                'audio': true,
                'video': false
              },
      'extraHeaders':['Idcamp:' + headerIdCamp, 'Nomcamp:' + headerNomCamp, 'Tipocamp:'+idTipoCamp],
			pcConfig: {rtcpMuxPolicy: 'negotiate'}
    };
    //Mando el invite/llamada
     if(flagInit === true) {
       flagInit = false;
       sesion = userAgent.call("sip:"+num+"@"+KamailioIp, opciones);
     } else {
       sesion = userAgent.call("sip:"+num+"@"+KamailioIp, opciones);
       setCallState("Calling.... "+num, "yellowgreen");
       displayNumber.value = "";
     }
		 idTipoCamp = null;
  }

  function setCallState(estado, color) {
    callSipStatus.parentNode.removeChild(callSipStatus);
    callSipStatus = document.createElement("em");
    var textCallSipStatus = document.createTextNode(estado);
    callSipStatus.style.color = color;
		callSipStatus.id = "dial_status";
    callSipStatus.appendChild(textCallSipStatus);
    callStatus.appendChild(callSipStatus);
  }

  function defaultCallState() {
    if(callStatus.childElementCount > 0) {
      callSipStatus.parentNode.removeChild(callSipStatus);
    }
    callSipStatus = document.createElement("em");
    textCallSipStatus = document.createTextNode("Idle");
		callSipStatus.id = "dial_status";
    callSipStatus.appendChild(textCallSipStatus);
    callStatus.appendChild(callSipStatus);
    $("#Transfer").prop('disabled', true);
    $("#onHold").prop('disabled', false);
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
    iconStatus.src = "../static/ominicontacto/Img/"+img;
    elem.appendChild(iconStatus);
    elem.appendChild(textSipStatus);
  }

  function Sounds(callType, action) {
    var ring = null;
    if(action === "play") {
      if(callType === "In") {
        ring = document.getElementById('RingIn');
        ring.play();
				ring.onended = function () {
					ring.play();
				};
      } else if(callType === "Out") {
        ring = document.getElementById('RingOut');
        ring.play();
				ring.onended = function () {
					ring.play();
				};
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

  function getBlankFormCamp(campid) {
    var url = '/campana/'+campid+'/formulario_nuevo/';
    $("#dataView").attr('src', url);
  }

  /** DEPRECATED?? **/
	function processCallid(callerid) {
  	var url = "/campana/selecciona/";
  	$("#dataView").attr('src', url);
  }

  function getData(campid, leadid, agentid, wombatId) {
    var url = "/formulario/"+campid+"/calificacion/"+leadid+"/update/"+agentid+"/"+wombatId+"/calificacion/";
    $("#dataView").attr('src', url);
  }

	function getFormManualCalls(idcamp, idagt, tel) {
    // Elimino los caracteres no numericos
    var telephone = tel.replace( /\D+/g, '');
    telephone = telephone == ''? 0 : telephone;
		var url = "/campana_manual/" + idcamp + "/calificacion/" + idagt + "/create/" + telephone + "/";
		$("#dataView").attr('src', url);
	}

	function getIframe(url) {
		$("#dataView").attr('src', url);
		/*tipo_interac; //= 2 "sitioexterno"
		// 1 "url comun"
		campana.sitio_externo.url
		sitio_externo;
		nombre;
		fecha_inicio;
		fecha_fin;
		calificacion*/
	}

  function sendStatus(pauseType,agent,statusAg) {
  	$.ajax({
      type: "get",
	   	url: "///",
	   	contentType: "text/html",
	   	data : "agente=" + agent + "&estado="+statusAg+"&tipo_pausa="+pauseType,
	   	success: function (msg) {

	   	},
	   	error: function (jqXHR, textStatus, errorThrown) {
	      debugger;
	      console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
	    }
    });
  }

});
