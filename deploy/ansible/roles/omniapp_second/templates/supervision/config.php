<?php
date_default_timezone_set("America/Argentina/Cordoba");

define('AMI_USERNAME','{{ sup_ami_user }}');
define('AMI_PASSWORD','{{ sup_ami_password }}');
define('AMI_HOST','{{ asterisk_fqdn }}');
define('PG_DB', '{{ postgres_database }}');
define('PG_USER', '{{ postgres_user }}');
define('PG_HOST', '{{ database_fqdn }}');
define('OMNI_HOST', $_SERVER['SERVER_NAME']);
define('OMNI_HOST_LOGOUT', OMNI_HOST .'/accounts/logout/');
define('WD_API_HOST', '{{ dialer_fqdn }}');
define('WD_API_USER', 'demoadmin');
define('WD_API_PASS', 'demo');
define("entities", $_SERVER['DOCUMENT_ROOT'].'/Omnisup/entities');
define("helpers", $_SERVER['DOCUMENT_ROOT'].'/Omnisup/helpers');
define("models", $_SERVER['DOCUMENT_ROOT'].'/Omnisup/Model');
define("controllers", $_SERVER['DOCUMENT_ROOT'].'/Omnisup/Controller');
define("views", $_SERVER['DOCUMENT_ROOT'].'/Omnisup/View');
define("black_path","{{ asterisk_location }}/var/spool/asterisk");
