<?php

include models . '/Agente_Model.php';

class Agente {

    private $Agente_Model;
    private $keyWords;

    function __construct() {
        $this->keyWords = array('Host', 'Dyn', 'Forcerport', 'Comedia', 'ACL', 'Port');
        $this->Agente_Model = new Agente_Model();
    }

    function traerAgentes($campName) {
        $result = $this->Agente_Model->getAgents($campName);
        return $result;
        // $arrClaves = $arrExtSip = $arrUserId = $arrGrupoId = array();
        // foreach ($result as $clave => $valor) {
        //     if ($clave == "id") {
        //         $arrClaves[] = 2;
        //     }
        //     if ($clave == "sip_extension") {
        //         $arrExtSip[] = $valor;
        //     }
        //     if ($clave == "grupo_id") {
        //         $arrGrupoId[] = $valor;
        //     }
        //     if ($clave == "user_id") {
        //         $arrUserId[] = $valor;
        //     }
        // }
        // $arrResult['ids'] = $arrClaves;
        // $arrResult['extesiones'] = $arrExtSip;
        // $arrResult['ids_grupo'] = $arrGrupoId;
        // $arrResult['ids_user'] = $arrUserId;
        // return $arrResult;
    }


    function traerEstadoAgente($idAgent) {
        $agente = $this->Agente_Model->getAgentStatus($idAgent);
        return $agente;
      	// $rawArrayData = array();
      	// $agente = explode(PHP_EOL, $agente);
      	// foreach($agente as $clave => $valor) {
      	//     $Qm = new QueueMember();
      	//     $valor = explode("(", $valor);
      	//     $name = str_replace(")","",$valor[0]);
      	//     if($name) {
      	//         $Qm->setName($name);
      	//     }
      	//     $val = explode(" ", $valor[1]);
      	//     $exten = str_replace("SIP/","",$val[0]);
      	//     if($exten) {
      	//         $Qm->setExten($exten);
      	//     }
      	//     $val = str_replace("(","",$valor[2]);
      	//     $val = str_replace(")","",$valor[2]);
      	//     $status = $val;
      	//     if($status) {
      	//         $Qm->setStatus($status);
      	//     }
      	//     $rawArrayData[] = $Qm;
      	// }
        // return $rawArrayData;
    }

    function traerTipoPausa($agent) {
        $data = $this->Agente_Model->getPauseAgents($agent);
        foreach ($data as $clave => $valor) {
            if ($clave == 'data') {
                $arrData = explode(":", $valor);
            }
        }
        return $arrData;
    }

    function espiarAgente($agt, $ext) {
        $res = $this->Agente_Model->ChanSpy($agt, $ext);
        echo $res;
    }

    function espiaryHablarAgente($agt, $ext) {
        $res = $this->Agente_Model->ChanSpyWhisper($agt, $ext);
        echo $res;
    }

    function Conferencia($agt, $ext) {
        $res = $this->Agente_Model->Conference($agt, $ext);
        echo $res;
    }

    function Desregistrar($agt, $arrNomsColas) {
        $res = $this->Agente_Model->AgentLogoff($agt, $arrNomsColas);
        echo $res;
    }

}
