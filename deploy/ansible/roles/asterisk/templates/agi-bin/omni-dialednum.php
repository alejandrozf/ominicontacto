#!/usr/bin/php -q

<?php

header('Content-Type: text/html; charset=UTF-8');
set_time_limit(20);
include 'phpagi.php';
$Agi = new AGI();

$Numero=$argv[1];
$idCamp=$argv[2];

$Archivo = "{{ asterisk_location }}/var/spool/asterisk/oml_'$idCamp'_dialednum.txt";

$omlDialedNum = system("grep $Numero $Archivo|wc -l");

$Agi->set_variable('OMLDIALEDNUM',$omlDialedNum);

?>
