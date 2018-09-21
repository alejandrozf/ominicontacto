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

function obtenerPath() {

    $op = isset($_GET['op']) ? $_GET['op'] : "new";
    $pag = isset($_GET['page']) ? $_GET['page'] : "Detalle_Campana_Contenido";

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
