#!/usr/bin/php -q

<?php

$BASE_PATH="/var/lib/asterisk/agi-bin/";

require $BASE_PATH."phpagi.php";
require_once $BASE_PATH."phpagi-asmanager.php";


//$agiWrapper = new AGI($BASE_PATH."include/phpagi/phpagi.conf");
$astman = new AGI_AsteriskManager();

$ampmgruser  = "wombat";
$ampmgrpass  = "fop222";

$oResultado = $astman->connect("localhost", $ampmgruser, $ampmgrpass);
        if($oResultado == FALSE)
                echo "Connection failed.\n";
                                
$listado = shell_exec("/usr/sbin/asterisk  -rx 'queue show' |grep Unava |awk '{print $1, $2}' FS='(' |awk '{print $1, $2}' FS='SIP' |awk '{print $1, $2}' FS='/' |awk '{print $1, $2}' FS=')'");

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
		echo "nobre: $nombre \n";
		echo "numero-sip: $numero \n";
		
		$aResponse = $astman->Originate(
							    'Local/066LOGOUT@fts-pausas/n',
                                NULL,
                                NULL,
                                NULL,
                                NULL,
                                'auto logout',
                                "AUTOLOGOUT=$numero-$nombre",
                                NULL,
                                'Hangup',
                                NULL
                                );
      echo "pepe \n"; 
    	}
}

?>
