<?php

include $_SERVER['DOCUMENT_ROOT'] . '/Omnisup/config.php';
include controllers . '/Agente.php';

if (isset($_GET['sip']) && isset($_GET['sipext']) && isset($_GET['action'])) {
    $sipext = explode(":", $_GET['sipext']);
    $accion = "";
    switch($_GET['action']) {
        case 'spy':
        $accion = "CHANSPY";
        break;
        case 'confer':
        $accion = "CHANCONFER";
        break;
        case 'spywhisper':
        $accion = "CHANSPYWISHPER";
        break;
        case 'takecall':
        $accion = "CHANTAKECALL";
        break;
        case 'pauseagent':
        $accion = "AGENTPAUSE";
        break;
        case 'unpauseagent':
        $accion = "AGENTUNPAUSE";
        break;
        case 'logoutagent':
        $accion = "AGENTLOGOUT";
        break;
    }
    $Controller_Agente = new Agente();//"AGENTLOGOUT"/"AGENTUNPAUSE"/"AGENTPAUSE"/"CHANTAKECALL"/"CHANSPYWISHPER"/"CHANSPY"/"CHANCONFER"
    $res = $Controller_Agente->ejecutarAccion($_GET['sip'], $sipext[1], $accion);
    echo $res;
}
header('location: ../index.php?page=Lista_Agentes');
