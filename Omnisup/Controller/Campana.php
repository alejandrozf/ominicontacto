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
include $_SERVER['DOCUMENT_ROOT'] . '/Omnisup/config.php';
include models . '/Campana_Model.php';
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
