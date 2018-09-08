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
var tabagt;
$(function () {
  tabagt = $('#tableAgt').DataTable({
    columns: [
        {data: 'agente'},
        {data: 'estado'},
        {data: 'tiempo'},
        {data: 'acciones'},
    ],
    ordering: false,
    searching: false,
    bLengthChange: false,
    paging: false
  });
  var url = window.location.href;
  if(url.indexOf('Detalle_Campana') !== -1) {
    setInterval("actualiza_contenido_agt()", 4000);
    setInterval("actualiza_contenido_objcamp()", 4000);
    setInterval("actualiza_contenido_camp()", 4000);
    setInterval("actualiza_contenido_colas()", 4000);
    setInterval("actualiza_contenido_wombat()", 1000);
  }
});

function actualiza_contenido_agt() {
  var nomcamp = $("#nombreCamp").html();
  $.ajax({
    url: 'Controller/Detalle_Campana_Contenido.php',
    type: 'GET',
    dataType: 'html',
    data: 'nomcamp='+nomcamp+'&op=agstatus',
    success: function (msg) {
      if(msg!=="]") {
        var mje = JSON.parse(msg);
        tabagt.rows().remove().draw();
        tabagt.rows.add(mje).draw();
      } else {
        tabagt.rows().remove().draw();
      }
    },
    error: function (jqXHR, textStatus, errorThrown) {
      console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
    }
  });
}

function actualiza_contenido_objcamp() {
  var campid = $("#campId").val();
  $.ajax({
    url: 'Controller/Detalle_Campana_Contenido.php',
    type: 'GET',
    dataType: 'html',
    data: 'idcamp='+campid+'&op=objcamp',
    success: function (msg) {
      if(msg!=="]") {
        var mje = JSON.parse(msg);
        $("#gestioncampana").html(mje.gestion_campana);
        $("#objcampana").html(mje.objetivo_campana);
        var pje = (mje.gestion_campana * 100) / mje.objetivo_campana;
        pje = pje.toFixed(2);
        $("#percent").html(pje +"%");
      }
    },
    error: function (jqXHR, textStatus, errorThrown) {
      console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
    }
  });
}

function actualiza_contenido_camp() {
  var nomcamp = $("#nombreCamp").html();
  var campid = $("#campId").val();
  var tabla = document.getElementById('bodyTableCampSummary');
  $.ajax({
    url: 'https://' + OmlIp + ':' + OmlPort + '/api_supervision/llamadas_campana/' + campid + '/',
    type: 'GET',
    dataType: 'html',
    success: function (msg) {
      $("#bodyScore").html("");
      var mje = $.parseJSON(msg), trHTML = '';
      var llamadas = mje['llamadas'];
      $.each (llamadas, function (i, item) {
        if (i !== 'status') {
          trHTML += '<span class=\'label\'>' + item[0] + '</span>&nbsp;<span>' + item[1] + '</span>.&nbsp;';
        }
      });
      if (mje.hasOwnProperty('manuales')){
        var manuales = mje['manuales'];
        trHTML += '<br/><br/><h2>Llamadas Manuales</h2>';
        $.each (manuales, function (i, item) {
          if (i !== 'status') {
            trHTML += '<span class=\'label\'>' + item[0] + '</span>&nbsp;<span>' + item[1] + '</span>.&nbsp;';
          }
        });
      }
      $("#bodyScore").append(trHTML);
    },
    error: function (jqXHR, textStatus, errorThrown) {
      console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
    }
  });
  $.ajax({
    url: 'https://' + OmlIp + ':' + OmlPort + '/api_supervision/calificaciones_campana/'+ campid + '/',
    type: 'GET',
    dataType: 'html',
    success: function (msg) {
      $("#bodySummary").html("");
      var mje = $.parseJSON(msg), trHTML = '';
      $.each (mje, function (i, item) {
        if (i !== 'status') {
          trHTML += '<tr><td>' + i + '</td><td>' + item + '</td></tr>';
        }
      });
      $("#bodySummary").append(trHTML);
    },
    error: function (jqXHR, textStatus, errorThrown) {
      console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
    }
  });
}

function actualiza_contenido_colas() {
  var nomcamp = $("#nombreCamp").html();
  var idcamp = $("#campId").val();
  $.ajax({
    url: 'Controller/Detalle_Campana_Contenido.php',
    type: 'GET',
    dataType: 'html',
    data: 'nomcamp='+nomcamp+'&idcamp='+idcamp+'&op=queuedcalls',
    success: function (msg) {
      if(msg!=="]") {
        var mje = JSON.parse(msg);
        var tabla = document.getElementById('tableQueuedCalls');
        if($("#tableQueuedCalls").children().length > 0) {
          while(tabla.firstChild) {
            tabla.removeChild(tabla.firstChild);
          }
        }
        for (var i = 0; i < mje.length; i++) {
          var tdTimeContainer = document.createElement('td');
          var tdTimeLabel = document.createElement('td');
          var rowTime = document.createElement('tr');

          var spanTime = document.createElement('span');

          spanTime.className = 'icon far fa-clock';
          var textTimeContainer = document.createTextNode(mje[i].nroLlam);
          var textTimeLabel = document.createTextNode(mje[i].tiempo);

          tdTimeContainer.appendChild(spanTime);
          tdTimeContainer.appendChild(textTimeLabel);
          tdTimeLabel.appendChild(textTimeContainer);
          rowTime.appendChild(tdTimeLabel);
          rowTime.appendChild(tdTimeContainer);
          tabla.appendChild(rowTime);
        }
      } else {
        var tabla = document.getElementById('tableQueuedCalls');
        if($("#tableQueuedCalls").children().length > 0) {
          while(tabla.firstChild) {
            tabla.removeChild(tabla.firstChild);
          }
        }
      }
    },
    error: function (jqXHR, textStatus, errorThrown) {
      console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
    }
  });
}

function actualiza_contenido_wombat() {
  var nomcamp = $("#nombreCamp").html();
  $.ajax({
    url: 'Controller/Detalle_Campana_Contenido.php',
    type: 'GET',
    dataType: 'html',
    data: 'nomcamp='+nomcamp+'&op=wdstatus',
    success: function (msg) {
      if(msg!=="]") {
        var mje = JSON.parse(msg);
        var tabla = document.getElementById('tableChannelsWombat');
        if($("#tableChannelsWombat").children().length > 0) {
          while(tabla.firstChild) {
            tabla.removeChild(tabla.firstChild);
          }
        }
        for (var i = 0; i < mje.length; i++) {
          var tdStatContainer = document.createElement('td');
          var tdTelContainer = document.createElement('td');
          var row = document.createElement('tr');

          var spanStatus = document.createElement('span');

          var statusTag;
          switch(mje[i].estado) {
            case "CONNECTED":
            statusTag = 'connected';
            break;
            case "DIALING":
            statusTag = 'calling';
            break;
            default:
            statusTag = 'shortcall';
            break;
          }
          spanStatus.className = 'badge badge-outline line-' + statusTag;

          var textStatContainer = document.createTextNode(mje[i].estado);
          var textTelContainer = document.createTextNode(mje[i].numero);

          spanStatus.appendChild(textStatContainer);
          tdTelContainer.appendChild(textTelContainer);
          tdStatContainer.appendChild(spanStatus);
          row.appendChild(tdStatContainer);
          row.appendChild(tdTelContainer);
          tabla.appendChild(row);
        }
      } else {
        var tabla = document.getElementById('tableChannelsWombat');
        if($("#tableChannelsWombat").children().length > 0) {
          while(tabla.firstChild) {
            tabla.removeChild(tabla.firstChild);
          }
        }
      }
    },
    error: function (jqXHR, textStatus, errorThrown) {
      console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
    }
  });
}
