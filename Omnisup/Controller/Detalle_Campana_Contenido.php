<?php
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
// ini_set('display_errors', 'On');
// error_reporting(E_ALL | E_STRICT);
include $_SERVER['DOCUMENT_ROOT'] . '/Omnisup/config.php';
//include '/var/www/html/Omnisup/Controller/Campana.php';
include controllers . '/Campana.php';
//include '/var/www/html/Omnisup/Controller/Agente.php';
include controllers . '/Agente.php';
include helpers . '/time_helper.php';

function mostrarEstadoAgentes($camp) {
     $jsonString = '[';
     $Controller_Agente = new Agente();
     $resul = $Controller_Agente->traerAgentes($camp);
     $arrAgtIds = $arrAgtNoms = array();
     foreach ($resul as $key => $value) {
         if ($key == "ids") {
             foreach ($value as $ky => $vl) {
                 if ($vl) {
                     $arrAgtIds[]= $vl;
                 }
             }
         }
         if ($key == "nombres_usuario") {
             foreach ($value as $ky => $vl) {
                 if ($vl) {
                     $arrAgtNoms[]= $vl;
                 }
             }
         }
     }
     $i = 0;
     foreach ($arrAgtIds as $value) {
         $resul = $Controller_Agente->traerEstadoAgente($value);
         foreach ($resul as $key => $value) {
                 $tiempo = RestarHoras(date('H:i:s', $value->getTime()), date('H:i:s'));
                 if($value->getStatus() != "" && $tiempo != "" && $value->getId() != "") {
                    $status = explode("-", $value->getStatus());

                    $jsonString .= '{"agente": "' . $arrAgtNoms[$i] . '", ';
                    $jsonString .= '"tiempo": "' . $tiempo . '",';

                    if ($status[0] !== "PAUSE") {
                      $cssStatus = "";
                      switch ($status[0]) {
                        case 'READY':
                          $cssStatus = 'ready';
                          break;
                        case 'DIALING':
                          $cssStatus = 'dialing';
                          break;
                        case 'OFFLINE':
                          $cssStatus = 'offline';
                          break;
                        case 'ONCALL':
                          $cssStatus = 'oncall';
                          break;
                      }
                        $jsonString .= '"estado": "<label class=\'badge align-top agent-' . $cssStatus . '\'>' . $value->getStatus() . '</label>", ';
                        $jsonString .= '"acciones": "' .
                                '<a class=\'not-link\' title=\'escuchar\' href=\'#\'><i class=\'fas fa-user-secret chanspy\' id=\'' . $value->getId()  . '\'></i></a>' .
                                '<a class=\'not-link\' title=\'escuchar y susurrar\' href=\'#\'><img src=\'static/Img/spywhisper2.png\' width=\'26\' height=\'26\' class=\'chanspywhisper\' id=\'' . $value->getId()  . '\' /></a>' .
                                '<a class=\'not-link\' title=\'pausar\' href=\'#\'><i class=\'fas fa-pause pause\' id=\'' . $value->getId()  . '\'></i></a>&nbsp;' .
                                '<a class=\'not-link\' title=\'desregistrar\' href=\'#\'><i class=\'fas fa-sign-out-alt agentlogoff\' id=\'' . $value->getId()  . '\'></i></a>&nbsp;' .
                                '<a class=\'not-link\' title=\'tomar llamada\' href=\'#\'><img src=\'static/Img/takecall.png\' width=\'18\' height=\'12\' class=\'takecall\' id=\'' . $value->getId()  . '\' /></a>&nbsp;' .
                                '<a class=\'not-link\' title=\'conferencia\' href=\'#\'><i class=\'fas fa-users conference\' id=\'' . $value->getId()  . '\'></i></a>' .
                        '"},';
                    } else {
                        $jsonString .= '"estado": "<label class=\'badge align-top agent-pause\'>' . $status[1] . '</label>", ';
                        $jsonString .= '"acciones": "' .
                        '<a class=\'not-link\' title=\'escuchar\' href=\'#\'><i class=\'fas fa-user-secret chanspy\' id=\'' . $value->getId()  . '\'></i></a>' .
                        '<a class=\'not-link\' title=\'escuchar y susurrar\' href=\'#\'><img src=\'static/Img/spywhisper2.png\' width=\'26\' height=\'26\' class=\'chanspywhisper\' id=\'' . $value->getId()  . '\' /></a>' .
                        '<a class=\'not-link\' title=\'pausar\' href=\'#\'><i class=\'fas fa-pause pause\' id=\'' . $value->getId()  . '\'></i></a>&nbsp;' .
                        '<a class=\'not-link\' title=\'desregistrar\' href=\'#\'><i class=\'fas fa-sign-out-alt agentlogoff\' id=\'' . $value->getId()  . '\'></i></a>&nbsp;' .
                        '<a class=\'not-link\' title=\'tomar llamada\' href=\'#\'><img src=\'static/Img/takecall.png\' width=\'18\' height=\'12\' class=\'takecall\' id=\'' . $value->getId()  . '\' /></a>&nbsp;' .
                        '<a class=\'not-link\' title=\'conferencia\' href=\'#\'><i class=\'fas fa-users conference\' id=\'' . $value->getId()  . '\'></i></a>' .
                      '"},';
                     }
                     $i++;
                 }
         }
     }
     $jsonString = substr($jsonString, 0, -1);
     $jsonString .=  ']';
     return $jsonString;
}

function mostrarEstadoCampana($idcamp) {
    $Controller_Campana = new Campana();
    $objresul = $Controller_Campana->traerObjetivoCampana($idcamp);
    $objresulg = $Controller_Campana->traerGestionCampana($idcamp);
    $jsonString .= '{"objetivo_campana": "' . $objresul . '","gestion_campana": "' . $objresulg . '"}';
    return $jsonString;
}

function mostrarCalificaciones($camp) {
    $Controller_Campana = new Campana();
    $resul = $Controller_Campana->traerCalificaciones($camp);
    $jsonString = '[';
    foreach ($resul as $key => $value) {
        $noSpaceKey = str_replace(' ', '', $key);
        $jsonString .= '{"cantidad": "'. $value . '", "calificacion": "' . $key . '", "tagId": "' . $noSpaceKey . '"},';
    }
    $jsonString = substr($jsonString, 0, -1);
    $jsonString .= "]";
    return $jsonString;
}
function mostrarLlamadasEnCola($camp, $idcamp) {
    $Controller_Campana = new Campana();
    $jsonString = '';
    $camp = $idcamp.'_'.$camp;
    $resul = $Controller_Campana->traerLlamadasEnCola($camp);
    $jsonString .= '[';
    $i = 1;
    foreach($resul as $clave => $valor) {
        $jsonString .= '{"nroLlam": ' . $i . ', "tiempo": "' . $valor . '"},';
        $i++;
    }
    $jsonString = substr($jsonString, 0, -1);
    $jsonString .= "]";
    return $jsonString;
}
function mostrarEstadoCanalesWombat($camp) {
  $Controller_Campana = new Campana();
  $jsonString = '';
  $resul = $Controller_Campana->traerEstadoDeCanales($camp);
  $jsonString .= '[';
  foreach ($resul as $value) {
      $ns = $value;
      if ($ns->getState() == "DIALLING") {
          $jsonString .= '{"estado": "DIALING", "numero": "' . $ns->getNumber() . '"},';
      } else {
          $jsonString .= '{"estado": "' . $ns->getState() . '", "numero": "' . $ns->getNumber() . '"},';
      }
  }
  $jsonString = substr($jsonString, 0, -1);
  $jsonString .= "]";
  return $jsonString;
}
function mostrarUserPassSip($userID) {
  $Controller_Campana = new Campana();
  $resul = $Controller_Campana->traerUserClaveSIP($userID);
  $jsonString = '';
  $user = $pass = $timestamp = "";
  foreach ($resul as $key => $value) {
      if(is_array($value)) {
          foreach($value as $cla => $val) {
              if($cla == "sip_extension") {
                  $user = $val;
              } elseif($cla == "timestamp") {
                $timestamp = $val;
              } else {
                  $pass = $val;
              }
          }
      } else {
          if($key == "sip_extension") {
              $user = $value;
          } else {
              $pass = $value;
          }
      }
  }
  $jsonString .= '{"sipuser": "' . $timestamp .':' . $user . '", "sippass": "' . $pass .'"}';
  return $jsonString;
}

if ($_GET['nomcamp']) {

    if ($_GET['op'] == 'agstatus') {

        echo mostrarEstadoAgentes($_GET['nomcamp']);
    } else if ($_GET['op'] == 'queuedcalls') {

        echo mostrarLlamadasEnCola($_GET['nomcamp'], $_GET['idcamp']);
    } else if ($_GET['op'] == 'wdstatus') {

        echo mostrarEstadoCanalesWombat($_GET['nomcamp']);
    }
} else if ($_GET['idcamp']) {

  if ($_GET['op'] == 'objcamp') {

    echo mostrarEstadoCampana($_GET['idcamp']);
  }
}

if($_GET['supId']) {
    echo mostrarUserPassSip($_GET['supId']);
}
