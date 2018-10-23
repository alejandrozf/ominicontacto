#!/usr/bin/php -q

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
include "{{ install_prefix }}Omnisup/config.php";
require ('phpagi.php') ;
//creando nueva instancia AGI
$agi = new AGI() ;
ob_implicit_flush(true) ;
set_time_limit(30) ;

$tipo_llamada=$argv[1];
$id_cliente=$argv[2];
$tel_cliente=$argv[3];
$grabacion=$argv[4];
$agente_id=$argv[5];
$campana=$argv[6];
$fecha=$argv[7];
$uid=$argv[8];
$duracion=$argv[9];
$string_connection="host=" . PG_HOST . " port=5432 password=" . PG_PASSWORD ." user=" . PG_USER;
$connection=pg_connect($string_connection)
or die('NO HAY CONEXION: ' . pg_last_error());

$query ="INSERT INTO ominicontacto_app_grabacion (fecha,tipo_llamada,id_cliente,tel_cliente,grabacion,agente_id,campana_id,uid,duracion) VALUES ('$fecha','$tipo_llamada','$id_cliente','$tel_cliente','$grabacion','$agente_id','$campana','$uid','$duracion');";

echo"$query\n";

$result=pg_query($connection, $query) or die('ERROR AL INSERTAR DATOS: ' . pg_last_error());

pg_close ($connection);
?>
