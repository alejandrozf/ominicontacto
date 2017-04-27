$(function() {
  var a = 0;
  var socket = io.connect('https://'+socketIoIp+':8082', {secure: true});
  var formAgtId = document.getElementById('idagt');
  var li = "";
  socket.on('news', function (datos) {
      if(datos) {
        if(datos.agentId === parseInt(formAgtId.value)) {
          getDialog(datos.call_id);
        }
      }
  });

  $("#endDialog").click(function () {
    var selectedRecipFb = $("input[name=dialogId]:checked","#cuerpoTablaFb").val();
    moveDialog(selectedRecipFb);
  });

  $("#cuerpoTablaFb").on("change", ".fb_username", function() {
    if(this.checked) {
      $("#messagesFb").append(li);// adjunto li al ul contenedor de dialogo
    } else {
      $("#cuerpoTablaFb").html("");
    }
  });

  $("#facebookChat").click(function() {
    resetFBMessagesCounter();
  });

  $("#sendMessageFb").click(function() {
    var textoFbaEnviar = $("#textSendFb").val();
    var selectedRecipFb = $("input[name=dialogId]:checked","#cuerpoTablaFb").val();
    var callId = $("#"+selectedRecipFb).val();
    var recipId = $("#"+callId).val();
    var jsondata = {
      message: textoFbaEnviar,
      agent_id: formAgtId.value,
      fbuser_id: selectedRecipFb,
      call_id: callId,
      recipient_id: recipId
    };

    socket.emit('responseDialog', jsondata);
    $("#textSendFb").val("");
    setTimeout(function () {getDialog(callId);}, 3000);
    /*var li = document.createElement("div");
    var textLi = document.createTextNode(textoFbaEnviar);
    li.style.listStyleType = "none";
    li.style.borderRadius = "5px";
    li.style.paddingLeft = "5px";
    li.style.marginBottom = "2px";
    li.style.boxShadow = "3px 3px #2E2E2E";
    li.style.backgroundColor = "yellowgreen";
    li.style.color = "black";
    li.appendChild(textLi);
    $("#messagesFb").append(li);*/
  });

  function removeDialog(clid) {
    $("#messagesFb").empty();
    var nodoCall_id = document.getElementById(clid);
    //var nodoCall_id = document.getElementById(clid);
    //var nodoCall_id = document.getElementById(clid);

    TDNodoCall_id = nodoCall_id.parentNode;
    TRNodoCall_id = TDNodoCall_id.parentNode;
    TRNodoCall_id.parentNode.removeChild(TRNodoCall_id);
  }

  function createDialog(mensaje) {
    if(!$("#modalFacebook").hasClass('in')) {
      a = a + 1;
      notReadMessages(a);
    }
    var json = JSON.parse(mensaje);
    var messagesCuantity = json.dialog.length;
    for(var l = 0; l < messagesCuantity; l++) {
      if(!document.getElementById(json.dialog[l].fb_username) && !document.getElementById(json.dialog[l].call_id)) {
        var inputClidHidden = document.createElement('input');//creo input para type=hidden de call_id
        inputClidHidden.id = json.dialog[l].fb_username;
        inputClidHidden.value = json.dialog[l].call_id;
        inputClidHidden.type = 'hidden';
        inputClidHidden.className = "client_id";

        var inputReidHidden = document.createElement('input');//creo input para type=hidden de recipient_id
        inputReidHidden.id = json.dialog[l].call_id;
        inputReidHidden.value = json.dialog[l].recipient_id;
        inputReidHidden.type = 'hidden';
        inputReidHidden.className = "recipient_id";

        var filaFBUsers = document.createElement('tr');//creo fila
        var radioBtnFB = document.createElement('input');//creo radiobutton
        radioBtnFB.type = 'radio';
        radioBtnFB.name = "dialogId";
        radioBtnFB.value = json.dialog[l].fb_username;
        radioBtnFB.className = "fb_username";

        var tdRadioContainerFB = document.createElement('td');//creo td para radiobutton
        tdRadioContainerFB.appendChild(radioBtnFB);//inserto el radiobtn en el td
        tdRadioContainerFB.appendChild(inputClidHidden);//inserto el input type=hidden con call_id al td
        tdRadioContainerFB.appendChild(inputReidHidden);//inserto el input type=hidden con recipient_id al td
        filaFBUsers.appendChild(tdRadioContainerFB);//inserto td de radiobtn a tr
        var tdUserFB = document.createElement('td');//creo td para texto de usuario
        var textTdFB = document.createTextNode(json.dialog[l].fb_username);
        tdUserFB.appendChild(textTdFB);//agrego texto a td de user de fb
        filaFBUsers.appendChild(tdUserFB);//agrego td que contiene el usuario de fb, a una fila de tabla
        $("#cuerpoTablaFb").append(filaFBUsers);// agrego la fila de tabla que contiene el td con el usuario de fb, a la tabla de usuarios

      }
      li = document.createElement("div");// creo li para que contenga el textNode de dialogo
      textLi = document.createTextNode(json.dialog[l].text_message);// creo textNode de dialogo
      li.style.listStyleType = "none";
      li.style.borderRadius = "5px";
      li.style.paddingLeft = "5px";
      li.style.marginBottom = "2px";
      li.style.boxShadow = "3px 3px #2E2E2E";
      var selectedRecipFb = $("input[name=dialogId]:checked","#cuerpoTablaFb").val();
      if(json.dialog[l].send_flag == 'f') {
        li.style.backgroundColor = "#819FF7";
        li.style.color = "black";
        li.appendChild(textLi);// adjunto textNode a li
        if(selectedRecipFb == json.dialog[l].fb_username) {
          $("#messagesFb").append(li);// adjunto li al div contenedor de dialogo
        }
      } else {
        li.style.backgroundColor = "yellowgreen";
        li.style.color = "black";
        li.appendChild(textLi);// adjunto textNode a li
        if(selectedRecipFb == json.dialog[l].fb_username) {
          $("#messagesFb").append(li);// adjunto li al div contenedor de dialogo
        }
      }
    }
  }

  function getDialog(clid) {
    $.ajax({
      contentType: "application/json",
      url: "http://localhost/getmessages.php?callid="+clid,
      type: "GET",
      success: function (msg) {
        if(msg !== "") {
          $("#messagesFb").empty();
          createDialog(msg);
        }
      },
      error: function (jqXHR, textStatus, errorThrown) {
        debugger;
        console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
      }
    });
  }

  function moveDialog(clid) {
    /*$.ajax({
      contentType: "application/json",
      url: "http://localhost/movemessages.php?callid="+clid,
      type: "GET",
      success: function (msg) {
        if(msg !== "") {*/
          removeDialog(clid);
        /*}
      },
      error: function (jqXHR, textStatus, errorThrown) {
        debugger;
        console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
      }
    });*/
  }

  function notReadMessages(point) {
    var values = {
      one: 'filter_1',
      two: 'filter_2',
      three: 'filter_3',
      four: 'filter_4',
      five: 'filter_5',
      six: 'filter_6',
      seven: 'filter_7',
      eight: 'filter_8',
      nine: 'filter_9',
      nineplus: 'filter_9_plus'
    };
    switch (point) {
      case 1:
        $("#fbNotReadMessagesCounter").html(values.one);
        break;
      case 2:
        $("#fbNotReadMessagesCounter").html(values.two);
        break;
      case 3:
        $("#fbNotReadMessagesCounter").html(values.three);
        break;
      case 4:
        $("#fbNotReadMessagesCounter").html(values.four);
        break;
      case 5:
        $("#fbNotReadMessagesCounter").html(values.five);
        break;
      case 6:
        $("#fbNotReadMessagesCounter").html(values.six);
        break;
      case 7:
        $("#fbNotReadMessagesCounter").html(values.seven);
        break;
      case 8:
        $("#fbNotReadMessagesCounter").html(values.eight);
        break;
      case 9:
        $("#fbNotReadMessagesCounter").html(values.nine);
        break;
      default:
        $("#fbNotReadMessagesCounter").html(values.nineplus);
        $("#fbNotReadMessagesCounter").css("color", "red");
        break;
    }
  }

  function resetFBMessagesCounter() {
    a = 0;
    $("#fbNotReadMessagesCounter").html("");
  }

});
