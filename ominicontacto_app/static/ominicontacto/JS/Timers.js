var centesimasO = 0;
var segundosO = 0;
var minutosO = 0;
var centesimasP = 0;
var segundosP = 0;
var minutosP = 0;
var centesimasT = 0;
var segundosT = 0;
var minutosT = 0;
var centesimasC = 0;
var segundosC = 0;
var minutosC = 0;

$(function () {

  $("#segsO").html(":00");
  $("#minsO").html(":00");
  $("#horaO").html("00");
  $("#segsP").html(":00");
  $("#minsP").html(":00");
  $("#horaP").html("00");
  $("#segsT").html(":00");
  $("#minsT").html(":00");
  $("#horaT").html("00");
  $("#segsC").html(":00");
  $("#minsC").html(":00");
  $("#horaC").html("00");

  function parar1 () {
    clearInterval(control1);
  }
  function parar2 () {
    clearInterval(control2);
  }
  function inicio2 () {
    control2 = setInterval(cronometro2,1000);
  }
  function inicio3 () {
    control3 = setInterval(cronometro3,1000);
  }

  function cronometro2 () {
    if (centesimasP < 59) {
      centesimasP++;
      if (centesimasP < 10) { centesimasP = "0"+centesimasP; }
      $("#segsP").html(":"+centesimasP);
    }
    if (centesimasP == 59) {
      centesimasP = -1;
    }
    if (centesimasP == 0) {
      segundosP++;
      if (segundosP < 10) { segundosP = "0"+segundosP; }
      $("#minsP").html(":"+segundosP);
    }
    if (segundosP == 59) {
      segundosP = -1;
    }
    if ( (centesimasP == 0)&&(segundosP == 0) ) {
      minutosP++;
      if (minutosP < 10) { minutosP = "0"+minutosP; }
      $("#horaP").html(""+minutosP);
    }
  }
  function cronometro3 () {
    if (centesimasT < 59) {
      centesimasT++;
      if (centesimasT < 10) { centesimasT = "0"+centesimasT; }
      $("#segsT").html(":"+centesimasT);
    }
    if (centesimasT == 59) {
      centesimasT = -1;
    }
    if (centesimasT == 0) {
      segundosT++;
      if (segundosT < 10) { segundosT = "0"+segundosT; }
      $("#minsT").html(":"+segundosT);
    }
    if (segundosT == 59) {
      segundosT = -1;
    }
    if ( (centesimasT == 0)&&(segundosT == 0) ) {
      minutosT++;
      if (minutosT < 10) { minutosT = "0"+minutosT; }
      $("#horaT").html(""+minutosT);
    }
  }

  function reinicio (horaDOM, minDOM, segDOM) {
  	clearInterval(control);
  	centesimas = 0;
  	segundos = 0;
  	minutos = 0;
  	segDOM.html(":00");
  	minDOM.html(":00");
  	horaDOM.html("00");
  }

  function inicio () {
    control = setInterval(cronometro1,1000);
  }

});
