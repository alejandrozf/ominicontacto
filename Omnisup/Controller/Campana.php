<?php

include models . '/Campana_Model.php';
include entities. '/QueueMember.php';
include entities. '/NumState.php';

class Campana {

    private $Campana_Model;

    function __construct() {
        $this->Campana_Model = new Campana_Model();
    }

    function traerCampanas($supervId=NULL) {
        $arrData = array();
        if($supervId != NULL) {
            $campanas = $this->Campana_Model->getCampaigns($supervId);
        } else {
            $campanas = $this->Campana_Model->getCampaignsForAdm();
        }
        foreach ($campanas as $clave => $valor) {
            if(is_array($valor)) {
                foreach ($valor as $cla => $val) {
                    if($cla == "id") {
                        $arrData[$val] = $v;
                    } else {
                        $v = $val;
                    }
                }
            } else {
              $arrData[] = $valor;
            }
        }
        return $arrData;
    }

    function traerCampanaDet($nomCamp) {
        $campana = $this->Campana_Model->getCampaign($nomCamp);
      	$rawArrayData = array();
      	$campana = explode(PHP_EOL, $campana);
      	foreach($campana as $clave => $valor) {
      	    $Qm = new QueueMember();
      	    $valor = explode("(", $valor);
      	    $name = str_replace(")","",$valor[0]);
      	    if($name) {
      	        $Qm->setName($name);
      	    }
      	    $val = explode(" ", $valor[1]);
      	    $exten = str_replace("SIP/","",$val[0]);
      	    if($exten) {
      	        $Qm->setExten($exten);
      	    }
      	    $val = str_replace("(","",$valor[2]);
      	    $val = str_replace(")","",$valor[2]);
      	    $status = $val;
      	    if($status) {
      	        $Qm->setStatus($status);
      	    }
      	    $rawArrayData[] = $Qm;
      	}
        return $rawArrayData;
    }

    function traerInfoReporteRealTimeCamp($NomCamp, $IdCamp) {
        $llamadasRecibidas = $this->Campana_Model->getReceivedCalls($IdCamp);
        $llamadasAtendidas = $this->Campana_Model->getAttendedCalls($IdCamp);
        $llamadasAbandonadas = $this->Campana_Model->getAbandonedCalls($IdCamp);
        $llamadasExpiradas = $this->Campana_Model->getExpiredCalls($IdCamp);
        $llamadasManuales = $this->Campana_Model->getManualCalls($IdCamp);
        $llamadasManualesAtendidas = $this->Campana_Model->getAttendedManualCalls($IdCamp);
        $llamadasManualesNoAtendidas = $this->Campana_Model->getNotAttendedManualCalls($IdCamp);
        $llamadasDetecContestador = $this->Campana_Model->getAnswererDetected($IdCamp);

        $cdadVentas = $this->Campana_Model->getSells($NomCamp);
        $arrInfo = array();

        foreach ($llamadasRecibidas as $key => $value) {
            foreach($value as $k => $v) {
                $arrInfo['received'] = $v;
            }
        }
        foreach ($llamadasAtendidas as $key => $value) {
            foreach($value as $k => $v) {
                $arrInfo['attended'] = $v;
            }
        }
        foreach ($llamadasAbandonadas as $key => $value) {
            foreach($value as $k => $v) {
                $arrInfo['abandoned'] = $v;
            }
        }
        foreach ($llamadasExpiradas as $key => $value) {
            foreach($value as $k => $v) {
                $arrInfo['expired'] = $v;
            }
        }
        foreach ($llamadasManuales as $key => $value) {
            foreach($value as $k => $v) {
                $arrInfo['manuals'] = $v;
            }
        }
        foreach ($llamadasManualesAtendidas as $key => $value) {
            foreach($value as $k => $v) {
                $arrInfo['manualsa'] = $v;
            }
        }
        foreach ($llamadasManualesNoAtendidas as $key => $value) {
            foreach($value as $k => $v) {
                $arrInfo['manualsna'] = $v;
            }
        }
        foreach ($llamadasDetecContestador as $key => $value) {
          foreach($value as $k => $v) {
              $arrInfo['answererdetected'] = $v;
          }
        }
        return $arrInfo;
    }

    function traerCalificaciones($IdCamp) {
        $cdadCalificaciones = $this->Campana_Model->getScoreCuantity($IdCamp);
        $arrCuant = $arrScore = $arrData = array();
        foreach ($cdadCalificaciones as $key => $value) {
          foreach ($value as $ky => $va) {
            if($ky == "count") {
              $arrCuant[] = $va;
            } else {
              $arrScore[] = $va;
            }
          }
        }
        $arrData = array_combine($arrScore, $arrCuant);
        return $arrData;
    }

    function traerLlamadasEnCola($NomCamp) {
        $result = $this->Campana_Model->getQueuedCalls($NomCamp);
        $rawArrayData = array();
      	$result = explode(PHP_EOL, $result);
      	foreach($result as $clave => $valor) {
            $valor = explode(": ", $valor);
            $rawArrayData[] = $valor[1];
        }
        $rawArrayData = array_filter($rawArrayData, "strlen");
        return $rawArrayData;
    }

    function traerEstadoDeCanales($NomCamp) {
        $result = $this->Campana_Model->getChannelsStatus($NomCamp);
        $datosUtiles = array();
        foreach($result as $clave => $valor) {
            if($clave == "result") {
                foreach($valor as $key => $value) {
                    if($key == "hopperState") {
                        foreach($value as $clav => $valo) {
                            if(in_array($NomCamp, $valo)) {
                                $NumState = new NumState();
                                $NumState->setNumber($valo['number']);
                                $NumState->setState($valo['state']);
                                $datosUtiles[] = $NumState;
                                $NumState = NULL;
                            }
                        }
                    }
                }
            }
        }
        return $datosUtiles;
    }

    function traerGestionCampana($IdCamp) {
        $result = $this->Campana_Model->getSpecialScore($IdCamp);
        $numGestion = "";
        foreach ($result as $key => $value) {
          if(is_array($value)) {
              foreach ($value as $ky => $vl) {
                $numGestion = $vl;
              }
          } else {
            $numGestion = $value;
          }
        }
        return $numGestion;
    }

    function traerObjetivoCampana($IdCamp) {
        $result = $this->Campana_Model->getGoalCampaign($IdCamp);
        $numObj = "";
        foreach ($result as $key => $value) {
            if(is_array($value)) {
                foreach ($value as $ky => $vl) {
                  $numObj = $vl;
                }
            } else {
              $numObj = $value;
            }
        }
        return $numObj;
    }

    function traerUserClaveSIP($userId) {
        $result = $this->Campana_Model->getSIPcredentialsByUserId($userId);
        return $result;
    }

}
