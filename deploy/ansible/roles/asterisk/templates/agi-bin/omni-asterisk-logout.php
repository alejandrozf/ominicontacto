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
#$BASE_PATH="/opt/omnileads/asterisk/var/lib/asterisk/agi-bin/";

#require $BASE_PATH."phpagi.php";
require ('phpagi.php') ;
#require_once $BASE_PATH."phpagi-asmanager.php";
require_once ('phpagi-asmanager.php') ;


//$agiWrapper = new AGI($BASE_PATH."include/phpagi/phpagi.conf");
$astman = new AGI_AsteriskManager();

$ampmgruser  = AMI_USERNAME;
$ampmgrpass  = AMI_PASSWORD;
$ampmgrhost = AMI_HOST;

$oResultado = $astman->connect($ampmgrhost, $ampmgruser, $ampmgrpass);
        if($oResultado == FALSE)
                echo "Connection failed.\n";

$listado = shell_exec("sudo asterisk  -rx 'queue show' |grep Unava |awk '{print $1, $2}' FS='(' |awk '{print $1, $2}' FS='SIP' |awk '{print $1, $2}' FS='/' |awk '{print $1, $2}' FS=')'");

if (empty($listado)) {
    echo '$var es o bien 0, vacía, o no se encuentra definida en absoluto';
}

else
{
$listado = explode("\n",$listado);
//$listado = explode(" ",$listado);

foreach($listado as $valor)
		{
		echo "valor: $valor\n";
		$salida = explode ("    ", $valor);
		$nombre = trim($salida[1]," ");
		$numero = trim($salida[2]," ");
		echo "nombre: $nombre \n";
		echo "numero-sip: $numero \n";

		$aResponse = $astman->Originate(
				'Local/066LOGOUT@oml-agent-actions/n',
                                NULL,
                                NULL,
                                NULL,
                                'hangup',
				NULL,
				'5000',
                                'auto logout',
                                "AUTOLOGOUT=$numero-$nombre",
                                NULL,
                                NULL,
                                NULL
                                );
      printf ($aResponse) ;
    	}
}

?>
