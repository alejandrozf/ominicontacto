<?php

include $_SERVER['DOCUMENT_ROOT'] . '/Omnisup/config.php';
//include '/var/www/html/Omnisup/Controller/Campana.php';
include controllers . '/Campana.php';
//include '/var/www/html/Omnisup/Controller/Agente.php';
include controllers . '/Agente.php';
include helpers . '/time_helper.php';

function mostrarEstadoAgentes($camp) {
    $Controller_Campana = new Campana();
    $Controller_Agente = new Agente();
    $jsonString = '';
    $resul = $Controller_Campana->traerCampanaDet($camp);
    $jsonString .= '[';
    foreach($resul as $Obj) {
        $Qm = $Obj;
        $pausa = $Controller_Agente->traerTipoPausa(trim(str_replace(')', '', $Qm->getExten())));
        $horaini = explode(' ', $pausa[3]);
        $tiempo = RestarHoras(date('H:i:s',$horaini[0]), date('H:i:s'));
        if($Qm->getName()) {
            $jsonString .= '{"agente": "' . trim($Qm->getName()) . '",';
            $status = $Qm->getStatus();
            $status = trim($status);
            if($status == "Not in use") {
                $jsonString .= '"estado": "Libre",';
                $jsonString .= '"tiempo": "---",';
            } else if($status == "paused") {
                $jsonString .= '"estado": "Pausa - ' . $pausa[2] . '",';
                $jsonString .= '"tiempo": "' . trim($tiempo) . '",';
            } else if($status == "In use") {
                $jsonString .= '"estado": "Llamada",';
                $jsonString .= '"tiempo": "---",';
            } else if($status == "in call") {
                $jsonString .= '"estado": "Llamada",';
                $jsonString .= '"tiempo": "---",';
            } else {
                $jsonString .= '"estado": "Desconectado",';
                $jsonString .= '"tiempo": "---",';
            }
            $jsonString .= '"acciones": "<button type=\'button\' id=\'' . $Qm->getExten() . '\' class=\'btn btn-primary btn-xs chanspy\' title=\'monitorear\'><span class=\'glyphicon glyphicon-eye-open\'></span></button>&nbsp;'
                  . '                  <button type=\'button\' id=\'' . $Qm->getExten() . '\' class=\'btn btn-primary btn-xs chanspywhisper\' title=\'hablar con agente\'><span class=\'glyphicon glyphicon-sunglasses\'></span></button>&nbsp;'
                  . '                  <button type=\'button\' id=\'' . $Qm->getExten() . '\' class=\'btn btn-primary btn-xs conference\' title=\'conferencia\'><span class=\'glyphicon glyphicon-user\'></span></button>"},';
                  /*. '                  <button type=\'button\' id=\'' . $Qm->getExten() . '\' class=\'btn btn-primary btn-xs info\' placeholder=\'conferencia\'><span class=\'glyphicon glyphicon-info-sign\'></span></button>&nbsp;'
                  . '                  <button type=\'button\' id=\'' . $Qm->getExten() . '\' class=\'btn btn-primary btn-xs agentlogoff\' placeholder=\'desconectar agente\'><span class=\'glyphicon glyphicon-off\'></span></button>"},';*/
       }
    }
    $jsonString = substr($jsonString, 0, -1);
    $jsonString .=  ']';
    return $jsonString;
}

function mostrarEstadoCampana($nomcamp,$idcamp) {
    $Controller_Campana = new Campana();
    $jsonString = '';
    $resul = $Controller_Campana->traerInfoReporteRealTimeCamp($nomcamp, $idcamp);
    $objresul = $Controller_Campana->traerObjetivoCampana($idcamp);
    $objresulg = $Controller_Campana->traerGestionCampana($idcamp);
    $jsonString .= '{';
    foreach($resul as $clave => $valor) {
        if($clave == "received") {
            $jsonString .= '"recibidas": "' . $valor . '",';
        }
        if($clave == "attended") {
            $jsonString .= '"atendidas": "' . $valor . '",';
        }
        if($clave == "abandoned") {
            $jsonString .= '"abandonadas": "' . $valor . '",';
        }
        if($clave == "expired") {
            $jsonString .= '"expiradas": "' . $valor . '",';
        }
        if($clave == "manuals") {
            $jsonString .= '"manuales": "' . $valor . '",';
        }
        if($clave == "manualsa") {
            $jsonString .= '"manualesatendidas": "' . $valor . '",';
        }
        if($clave == "manualsna") {
            $jsonString .= '"manualesnoatendidas": "' . $valor . '",';
        }
        if($clave == "answererdetected") {
            $jsonString .= '"contestador_detectado": "' . $valor . '",';
        }
    }

    $jsonString .= '"objetivo_campana": "' . $objresul . '",';
    $jsonString .= '"gestion_campana": "' . $objresulg . '",';
    $jsonString = substr($jsonString, 0, -1);
    $jsonString .= "}";
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
      $jsonString .= '{"estado": "' . $ns->getState() . '", "numero": "' . $ns->getNumber() . '"},';
  }
  $jsonString = substr($jsonString, 0, -1);
  $jsonString .= "]";
  return $jsonString;
}
function mostrarUserPassSip($userID) {
  $Controller_Campana = new Campana();
  $resul = $Controller_Campana->traerUserClaveSIP($userID);
  $jsonString = '';
  $user = $pass = "";
  foreach ($resul as $key => $value) {
      if(is_array($value)) {
          foreach($value as $cla => $val) {
              if($cla == "sip_extension") {
                  $user = $val;
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
  $jsonString .= '{"sipuser": "' . $user . '", "sippass": "' . $pass .'"}';
  return $jsonString;
}
if ($_GET['nomcamp']) {
    if($_GET['op'] == 'agstatus') {
        echo mostrarEstadoAgentes($_GET['nomcamp']);
    } else if ($_GET['op'] == 'campstatus') {
        echo mostrarEstadoCampana($_GET['nomcamp'], $_GET['CampId']);
    } else if ($_GET['op'] == 'queuedcalls') {
        echo mostrarLlamadasEnCola($_GET['nomcamp']);
    } else if($_GET['op'] == 'wdstatus') {
        echo mostrarEstadoCanalesWombat($_GET['nomcamp']);
    } else if($_GET['op'] == 'scorestatus') {
        echo mostrarCalificaciones($_GET['CampId']);
    }
}
if($_GET['supId']) {
    echo mostrarUserPassSip($_GET['supId']);
}
