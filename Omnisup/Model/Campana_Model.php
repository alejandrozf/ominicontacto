<?php
// ini_set('display_errors', 'On');
// error_reporting(E_ALL | E_STRICT);
//include $_SERVER['DOCUMENT_ROOT'] . '/Omnisup/config.php';
include_once entities . '/Phpagi_asmanager.php';

class Campana_Model {

    private $command;
    private $agi;
    private $argPdo;

    function __construct() {
        $this->argPdo = 'pgsql:host=' . PG_HOST . ';dbname=kamailio;port=5432';
        $this->agi = new Phpagi_asmanager();
    }

    function getCampaignsForAdm() {
      $sql = "select distinct nombre, ac.id from ominicontacto_app_campana ac
      where estado = 2";
      try {
        $cnn = new PDO($this->argPdo, PG_USER, PG_PASSWORD);
        $query = $cnn->prepare($sql);
        $query->execute();
        $result = $query->fetchAll(PDO::FETCH_ASSOC);
        $cnn = NULL;
      } catch (PDOException $e) {
          $result= "Database Error: " . $e;
      }
      return $result;
    }

    function getCampaigns($userId) {
      $sql = "select nombre, ac.id from ominicontacto_app_campana ac join ominicontacto_app_supervisorprofile sp on ac.reported_by_id = sp.user_id
              where estado = 2 and sp.id = :id
              union
              select nombre, ac.id from ominicontacto_app_campana ac join ominicontacto_app_campana_supervisors cs on ac.id = cs.campana_id
              join ominicontacto_app_supervisorprofile sp on sp.user_id = cs.user_id
              where ac.estado = 2 and sp.id = :id";
      try {
        $cnn = new PDO($this->argPdo, PG_USER, PG_PASSWORD);
        $query = $cnn->prepare($sql);
        $query->bindParam(':id', $userId);
        $query->execute();
        $result = $query->fetchAll(PDO::FETCH_ASSOC);
        $cnn = NULL;
      } catch (PDOException $e) {
          $result= "Database Error: " . $e;
      }
      return $result;
    }

    function getQueuedCalls($CampName) {
        $cmd = "sudo asterisk  -rx 'queue show " . $CampName . "' |grep wait |awk '{print $2}' FS='\(' |awk '{print $1}' FS=','";
        $data = shell_exec($cmd);
        return $data;
    }

    function getChannelsStatus($CampName) {
         $process = curl_init("http://" . PG_HOST . ":8080/wombat/api/live/calls/");
         curl_setopt($process, CURLOPT_HEADER, 0);
         curl_setopt($process, CURLOPT_USERPWD, WD_API_USER . ":" . WD_API_PASS);
         curl_setopt($process, CURLOPT_POST, 1);
         curl_setopt($process, CURLOPT_POSTFIELDS, $CampName);
         curl_setopt($process, CURLOPT_RETURNTRANSFER, TRUE);
         $res = curl_exec($process);
         curl_close($process);
         $res = json_decode($res, true);
         return $res;
    }

    function getSIPcredentialsByUserId($userId) {
        $sql = "select sip_extension, sip_password, timestamp FROM ominicontacto_app_supervisorprofile where id = :id";
        try {
            $cnn = new PDO($this->argPdo, PG_USER, PG_PASSWORD);
            $query = $cnn->prepare($sql);
            $query->bindParam(':id', $userId);
            $query->execute();
            $result = $query->fetchAll(PDO::FETCH_ASSOC);
            $cnn = NULL;
        } catch (PDOException $e) {
            $result= "Database Error: " . $e;
        }
        return $result;
    }

    function getGoalCampaign($CampId) {
         $sql = "select objetivo from ominicontacto_app_campana where id = :cmpid";
         try {
           $cnn = new PDO($this->argPdo, PG_USER, PG_PASSWORD);
           $query = $cnn->prepare($sql);
           $query->bindParam(':cmpid', $CampId);
           $query->execute();
           $result = $query->fetchAll(PDO::FETCH_ASSOC);
          $cnn = NULL;
          } catch (PDOException $e) {
             $result= "Database Error: " . $e;
         }
         return $result;
     }

     function getSpecialScore($CampId) {
       $sql = "select count(*) FROM ominicontacto_app_campana cd JOIN ominicontacto_app_opcioncalificacion oc ON cd.id=oc.campana_id JOIN
                ominicontacto_app_calificacioncliente cc ON oc.id = cc.opcion_calificacion_id AND EXTRACT(DAY from fecha) = :dia
                AND EXTRACT(MONTH from fecha) = :mes AND EXTRACT(YEAR from fecha) = :ano AND cd.id= :cpmid AND es_venta = 't'";
       $day = date("d");
       $month = date("m");
       $year = date("Y");
       try {
           $cnn = new PDO($this->argPdo, PG_USER, PG_PASSWORD);
           $query = $cnn->prepare($sql);
           $query->bindParam(':dia', $day);
           $query->bindParam(':mes', $month);
           $query->bindParam(':ano', $year);
           $query->bindParam(':cpmid', $CampId);
           $query->execute();
           $result = $query->fetchAll(PDO::FETCH_ASSOC);
           $cnn = NULL;
       } catch (PDOException $e) {
           $result= "Database Error: " . $e;
       }
       return $result;
     }
}
