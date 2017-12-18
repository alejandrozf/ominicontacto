<?php

function obtenerPath() {

    $op = isset($_GET['op']) ? $_GET['op'] : "new";
    $pag = isset($_GET['page']) ? $_GET['page'] : "Lista_Campanas";

    $path = "";

    $arraypags = array("Main" => "View/Main", "Lista_Agentes" => "View/Lista_Agentes", "Lista_Campanas" => "View/Lista_Campanas",
                       "Detalle_Campana" => "View/Detalle_Campana", "Detalle_Campana_Contenido" => "Controller/Detalle_Campana_Contenido",
        );

    if (array_key_exists($pag, $arraypags)) {
        $path = "$arraypags[$pag].php";
    } else {
        $path = "views/Inexistente.php";
    }
    return $path;
}
