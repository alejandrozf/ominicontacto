<?php

include models . '/Agente_Model.php';

class Agente {

    private $Agente_Model;
    private $keyWords;

    function __construct() {
        $this->keyWords = array('Host', 'Dyn', 'Forcerport', 'Comedia', 'ACL', 'Port');
        $this->Agente_Model = new Agente_Model();
    }

    function traerAgentes() {
        $peers = $stringData = $peersOk = $peersUnk = $peersUnr = array();
        $agentes = $this->Agente_Model->getAgents();
        foreach ($agentes as $clave => $valor) {
            if ($clave == "data") {
                $datos = explode(PHP_EOL, $valor);
                foreach ($datos as $cla => $val) {
                    if ($cla > 1 && $cla < count($datos) - 2) {
                        if (strpos($val, "OK")) {
                            $val = explode(" ", $val);
                            $peers[] = $val[0];
                            $peersOk[] = $val[0];
                        } elseif (strpos($val, "UNKNOWN")) {
                            $val = explode(" ", $val);
                            $peers[] = $val[0];
                            $peersUnk[] = $val[0];
                        } elseif (strpos($val, "UNREACHABLE")) {
                            $val = explode(" ", $val);
                            $peers[] = $val[0];
                            $peersUnr[] = $val[0];
                        }
                    }
                }
            }
        }
        $stringData['peers'] = $peers;
        $stringData['Ok'] = $peersOk;
        $stringData['Unk'] = $peersUnk;
        $stringData['Unr'] = $peersUnr;
        return $stringData;
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
