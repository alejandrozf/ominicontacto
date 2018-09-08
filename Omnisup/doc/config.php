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
date_default_timezone_set("America/Argentina/Cordoba");

define('AMI_USERNAME','');
define('AMI_PASWORD','');
define('AMI_HOST','');

define('PG_USER', '');
define('PG_PASSWORD', '');
define('PG_HOST', '');
define('WD_API_USER', '');
define('WD_API_PASS', '');

define("entities", $_SERVER['DOCUMENT_ROOT'].'/Omnisup/entities');
define("helpers", $_SERVER['DOCUMENT_ROOT'].'/Omnisup/helpers');
define("models", $_SERVER['DOCUMENT_ROOT'].'/Omnisup/Model');
define("controllers", $_SERVER['DOCUMENT_ROOT'].'/Omnisup/Controller');
define("views", $_SERVER['DOCUMENT_ROOT'].'/Omnisup/View');
