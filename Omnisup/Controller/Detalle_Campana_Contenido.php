<?php
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
                        $jsonString .= '"estado": "' . $value->getStatus() . '", ';
                        $jsonString .= '"acciones": "<button type=\'button\' id=\'' . $value->getId() . '\' class=\'btn btn-primary btn-xs chanspy\' title=\'monitorear\'><span class=\'glyphicon glyphicon-eye-open\'></span></button>&nbsp;'
                                    . '<button type=\'button\' id=\'' . $value->getId() . '\' class=\'btn btn-primary btn-xs chanspywhisper\' title=\'hablar con agente\'><span class=\'glyphicon glyphicon-sunglasses\'></span></button>&nbsp;'
                                    . '<button type=\'button\' id=\'' . $value->getId() . '\' class=\'btn btn-primary btn-xs pause\' title=\'pausar agente\'><span class=\'glyphicon glyphicon-pause\'></span></button>&nbsp;'
                                    . '<button type=\'button\' id=\'' . $value->getId() . '\' class=\'btn btn-primary btn-xs agentlogoff\' title=\'logoff agente\'><span class=\'glyphicon glyphicon-off\'></span></button>&nbsp;'
                                    . '<button type=\'button\' id=\'' . $value->getId() . '\' class=\'btn btn-primary btn-xs takecall\' title=\'tomar llamada\'><span class=\'glyphicon glyphicon-share-alt\'></span></button>&nbsp;'
                                    . '<button type=\'button\' id=\'' . $value->getId() . '\' class=\'btn btn-primary btn-xs conference\' title=\'conferencia\'><span class=\'glyphicon glyphicon-user\'></span></button>"},';
                    } else {
                        $jsonString .= '"estado": "' . $status[1] . '", ';
                        $jsonString .= '"acciones": "<button type=\'button\' id=\'' . $value->getId() . '\' class=\'btn btn-primary btn-xs chanspy\' title=\'monitorear\'><span class=\'glyphicon glyphicon-eye-open\'></span></button>&nbsp;'
                                    . '<button type=\'button\' id=\'' . $value->getId() . '\' class=\'btn btn-primary btn-xs chanspywhisper\' title=\'hablar con agente\'><span class=\'glyphicon glyphicon-sunglasses\'></span></button>&nbsp;'
                                    . '<button type=\'button\' id=\'' . $value->getId() . '\' class=\'btn btn-primary btn-xs unpause\' title=\'despausar agente\'><span class=\'glyphicon glyphicon-play\'></span></button>&nbsp;'
                                    . '<button type=\'button\' id=\'' . $value->getId() . '\' class=\'btn btn-primary btn-xs agentlogoff\' title=\'logoff agente\'><span class=\'glyphicon glyphicon-off\'></span></button>&nbsp;'
                                    . '<button type=\'button\' id=\'' . $value->getId() . '\' class=\'btn btn-primary btn-xs takecall\' title=\'tomar llamada\'><span class=\'glyphicon glyphicon-share-alt\'></span></button>&nbsp;'
                                    . '<button type=\'button\' id=\'' . $value->getId() . '\' class=\'btn btn-primary btn-xs conference\' title=\'conferencia\'><span class=\'glyphicon glyphicon-user\'></span></button>"},';
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
function mostrarLlamadasEnCola($camp) {
    $Controller_Campana = new Campana();
    $jsonString = '';
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

        echo mostrarLlamadasEnCola($_GET['nomcamp']);
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
