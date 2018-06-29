<?php

include $_SERVER['DOCUMENT_ROOT'] . '/Omnisup/config.php';
include controllers . '/Agente.php';

if (isset($_GET['sip']) && isset($_GET['sipext'])) {
    $Controller_Agente = new Agente();
    $sipext = explode(":", $_GET['sipext']);
    $res = $Controller_Agente->espiarAgente($_GET['sip'], $sipext[1]);
    echo $res;
}
header('location: ../index.php?page=Lista_Agentes');
