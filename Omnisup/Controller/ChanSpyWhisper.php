<?php

include $_SERVER['DOCUMENT_ROOT'] . '/Omnisup/config.php';
include controllers . '/Agente.php';

if (isset($_GET['sip']) && isset($_GET['sipext'])) {
    $Controller_Agente = new Agente();
    $res = $Controller_Agente->espiaryHablarAgente($_GET['sip'], $_GET['sipext']);
    echo $res;
}
header('location: ../index.php?page=Lista_Agentes');
