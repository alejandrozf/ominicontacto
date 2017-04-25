$(function() {
  var a = 0;
  var socket = io.connect('http://'+socketIoIp+':8082');
  var formAgtId = document.getElementById('idagt');
  socket.on('news', function (datos) {
    debugger;
      if(datos) {
        if(datos.agentId === parseInt(formAgtId.value)) {
          getDialog(datos.call_id);
        }
      }
  });

  $("#cuerpoTablaFb").on("change", ".fb_username", function() {
    if(this.checked) {
      debugger;

      $("#messagesFb").append(li);// adjunto li al ul contenedor de dialogo
    } else {
      $("#cuerpoTablaFb").html("");
    }
  });

  $("#facebookChat").click(function() {
    resetFBMessagesCounter();
  });

  $("#sendFbMessage").click(function() {
    debugger;
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
    var li = document.createElement("li");
    var textLi = document.createTextNode("yo: " + textoFbaEnviar);
    li.appendChild(textLi);
    $("#messagesFb").append(li);
  });

  var li = "";
  function createDialog(mensaje) {
    if(!$("#modalFacebook").hasClass('in')) {
      a = a + 1;
      notReadMessages(a);
    }
    var json = JSON.parse(mensaje);
    for(var l = 0; l < json.dialog.length; l++) {
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
        filaFBUsers.appendChild(tdUserFB);
        $("#cuerpoTablaFb").append(filaFBUsers);
      }
      li = document.createElement("li");// creo li para que contenga el textNode de dialogo
      textLi = document.createTextNode(json.dialog[l].text_message);// creo textNode de dialogo
      li.appendChild(textLi);// adjunto textNode a li
    }
  }

  function getDialog(clid) {
    $.ajax({
      contentType: "application/json",
      url: "http://localhost/testfb.php?callid="+clid,
      type: "GET",
      success: function (msg) {
        if(msg !== "") {
          createDialog(msg);
        }
      },
      error: function (jqXHR, textStatus, errorThrown) {
        debugger;
        console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
      }
    });
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
