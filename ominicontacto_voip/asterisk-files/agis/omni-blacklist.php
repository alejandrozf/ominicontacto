#!/usr/bin/php -q

<?php

header('Content-Type: text/html; charset=UTF-8');
set_time_limit(20);
include 'phpagi.php';
$Agi = new AGI();

$Numero=$argv[1];
$Archivo = '/var/spool/asterisk/oml_backlist.txt';

$Blacklist = system("grep $Numero $Archivo|wc -l");

$Agi->set_variable('BLACKLIST',$Blacklist);

?>
