#!/usr/bin/php -q
<?php
$conf = parse_conf("/etc/amportal.conf");

$HOST = trim($conf['DBHOST']);
$USER = trim($conf['DBUSER']);
$PASS = trim($conf['DBPASS']);
$DATA = trim($conf['DBNAME']);


$db = new mysqli("$HOST", "$USER", "$PASS", "$DATA");
if ($db->connect_errno) {
    echo "; Fallo al contenctar a MySQL: (" . $db->connect_errno . ") " . $db->connect_error;
    die();
} 

$query = "SELECT a.route_id,name,concat(match_pattern_prefix,match_pattern_pass) AS pattern FROM outbound_route_sequence a LEFT JOIN outbound_routes b ON a.route_id=b.route_id LEFT JOIN outbound_route_patterns c ON a.route_id=c.route_id ORDER BY seq";

$text = "[find-route-number]\n";
$result = $db->query($query);

if($result) {
    while($obj = $result->fetch_object()) {
        $idx = $obj->route_id."!".$obj->pattern;
        $line[$idx]="exten => _".$obj->pattern.",1,Set(RUTA=".$obj->route_id.")\n";
        $line[$idx].= "exten => _".$obj->pattern.",2,Goto(end,1)\n";
    }
    $result->close();
}

foreach($line as $ll) {
    $text.=$ll;
}

$text .= "exten => end,1,Noop(Fin de seleccion de ruta \${RUTA})\n";

$query = "SELECT route_id,GROUP_CONCAT(trunk_id ORDER BY seq) AS failover FROM outbound_route_trunks GROUP BY route_id";
$result = $db->query($query);
if($result) {
    while($obj = $result->fetch_object()) {
        $partes = preg_split("/,/",$obj->failover);
        $quito  = array_shift($partes);
        $final  = implode($partes,",");
        $text .= "exten => end,n,ExecIf($[\"\${RUTA}\" = \"".$obj->route_id."\"]?Set(FAILOVERTRUNKS=".$final."))\n";
    }
    $result->close();
}

$db->close();
$text .= "exten => end,n,Return\n\n";

echo $text;


function parse_conf($filename) {

    global $config_engine;

    $file = file($filename);

    foreach ($file as $line) {
        if (preg_match("/^\s*([\w]+)\s*=\s*\"?([^\"]*)?\"?/",$line,$matches)) {
            $matches[1] = preg_replace("/^AMP/","",$matches[1]);
            $conf[ $matches[1] ] = $matches[2];
        }
    }

    return $conf;
}


