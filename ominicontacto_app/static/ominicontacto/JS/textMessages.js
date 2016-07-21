   var wsuri;
	 wsuri = "wss://172.16.20.241:8080/ws";
   //WAMP connection to the Router
   var connection = new autobahn.Connection({
     url: wsuri,
     realm: "realm1"
   });
         // fired when connection is established and session attached
         connection.onopen = function (session, details) {
           var text = document.getElementById('textSend');
        	 var tel = document.getElementById('phoneSend');
           var textThread = document.getElementById('textSendThread');
        	 var telThread = document.getElementById('phoneSendThread');

            console.log("Connected");
            // SUBSCRIBE to a topic and receive events
            function on_counter (args) {
              var smsNumber = args[0][0];
              notify(smsNumber);
              searchAndBold(smsNumber);
              //console.log("on_counter() event received with counter " + args[0]);
            }
            session.subscribe('com.example.oncounter', on_counter).then(
               function (sub) {
                  console.log('subscribed to topic');
               },
               function (err) {
                  console.log('failed to subscribe to topic', err);
               }
            );
            // Enviar a servidor
	          var btnSend = document.getElementById('sendMessage');
            var btnSendThread = document.getElementById('sendMessageFromThread');
            btnSend.onclick = function () {
               text = text.value;
               tel = tel.value;
               var mensaje = [ tel, text];
               session.publish('com.example.onhello', mensaje);
               limpiar();
            };
            btnSendThread.onclick = function () {
               textThread = text.value;
               telThread = tel.value;
               var mensaje = [ telThread, textThread];
               session.publish('com.example.onhello', mensaje);
               limpiar();
            };
         };
         //Conectar
connection.open();
var smsNvos = 0;
function notify(nro) {
  smsNvos += 1;
  localStorage.setItem("newSms", smsNvos);
  var showStoragedSms = localStorage.getItem("newSms");
  var counter = document.getElementById("newSMS");
  if(smsNvos < 2) {
    counter.innerHTML = showStoragedSms+" ("+nro+")";
  } else {
    counter.innerHTML = showStoragedSms;
  }
}
function searchAndBold(number) {
  var idToBold;
  var filasTabla = document.getElementById("cuerpoTabla").childNodes;
  for (var i = 6; i <= filasTabla.length; i++) {
    if(filasTabla[i].className == "odd" || filasTabla[i].className == "even") {
      if(filasTabla[i].childNodes[1].innerHTML==number) {
        idToBold = filasTabla[i].childNodes[1].id;
        document.getElementById(idToBold).style.fontWeight = "900";
        document.getElementById(idToBold).style.color = "green";
        return;
      }
    }
  }
}
function limpiar() {
  text.value ="";
  tel.value="";
}
