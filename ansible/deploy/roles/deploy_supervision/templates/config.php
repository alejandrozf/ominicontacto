<?php
date_default_timezone_set("America/Argentina/Cordoba");

define('AMI_USERNAME','omnisup');
define('AMI_PASWORD','omnisup123');
define('AMI_HOST','127.0.0.1');
define('PG_USER', 'kamailio');
define('PG_PASSWORD', 'kamailiorw');
define('PG_HOST', $_SERVER['SERVER_ADDR'].':10443');
define('OML_HOST', $_SERVER['SERVER_ADDR'].':11443');
define('WD_API_USER', 'demoadmin');
define('WD_API_PASS', 'demo');
define("entities", $_SERVER['DOCUMENT_ROOT'].'/Omnisup/entities');
define("helpers", $_SERVER['DOCUMENT_ROOT'].'/Omnisup/helpers');
define("models", $_SERVER['DOCUMENT_ROOT'].'/Omnisup/Model');
define("controllers", $_SERVER['DOCUMENT_ROOT'].'/Omnisup/Controller');
define("views", $_SERVER['DOCUMENT_ROOT'].'/Omnisup/View');
