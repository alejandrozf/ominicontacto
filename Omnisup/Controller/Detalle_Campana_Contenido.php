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
                     $jsonString .= '{"agente": "' . $arrAgtNoms[$i] . '", ';
                     $jsonString .= '"estado": "' . $value->getStatus() . '", ';
                     $jsonString .= '"tiempo": "' . $tiempo . '",';
                     $jsonString .= '"acciones": "<button type=\'button\' id=\'' . $value->getId() . '\' class=\'btn btn-primary btn-xs chanspy\' title=\'monitorear\'><span class=\'glyphicon glyphicon-eye-open\'></span></button>&nbsp;'
                                   . '                  <button type=\'button\' id=\'' . $value->getId() . '\' class=\'btn btn-primary btn-xs chanspywhisper\' title=\'hablar con agente\'><span class=\'glyphicon glyphicon-sunglasses\'></span></button>&nbsp;'
                                   . '                  <button type=\'button\' id=\'' . $value->getId() . '\' class=\'btn btn-primary btn-xs conference\' title=\'conferencia\'><span class=\'glyphicon glyphicon-user\'></span></button>"},';
                     $i++;
                 }
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
