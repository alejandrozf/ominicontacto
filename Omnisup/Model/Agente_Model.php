<?php
//include $_SERVER['DOCUMENT_ROOT'] . '/Omnisup/config.php';
include_once entities . '/Phpagi_asmanager.php';

class Agente_Model {

    private $command;
    private $agi;
    private $argPdo;

    function __construct() {
        $this->argPdo = 'pgsql:host=' . PG_HOST . ';dbname=kamailio;port=5432';
        $this->command = "sip show peers";
        $this->agi = new Phpagi_asmanager();
    }

    function getAgents($campName) {
        $sql = "SELECT AP.id, AU.username, AP.sip_extension, AP.grupo_id, AP.user_id
        FROM ominicontacto_app_agenteprofile AP JOIN ominicontacto_app_campana AC
        ON AP.reported_by_id = AC.reported_by_id JOIN ominicontacto_app_user AU ON AP.user_id = AU.id
        AND  AP.is_inactive = 'f' AND AP.borrado = 'f' AND AC.nombre LIKE :cpname";
        try {
          $cnn = new PDO($this->argPdo, PG_USER, PG_PASSWORD);
          $query = $cnn->prepare($sql);
          $query->bindParam(':cpname', $campName);
          $query->execute();
          $result = $query->fetchAll(PDO::FETCH_ASSOC);
          $cnn = NULL;
        } catch (PDOException $e) {
            $result= "Database Error: " . $e;
        }
        return $result;
    }

    function getAgentStatus($agentId) {
        try {
            $this->agi->connect(AMI_HOST, AMI_USERNAME, AMI_PASWORD);
        } catch (Exception $ex) {
            return "problemas de Conexion AMI: " . $ex;
        }
        $this->agi->Events('off');
        $this->command = "OML/AGENT/" . $agentId . "/STATUS";
        $data = $this->agi->database_show($this->command);
        return $data;
    }

    function getPauseAgents($agt) {
        try {
            $this->agi->connect(AMI_HOST, AMI_USERNAME, AMI_PASWORD);
        } catch (Exception $ex) {
            return "problemas de Conexion AMI: " . $ex;
        }
        $this->agi->Events('off');
        $this->command = "database show PAUSECUSTOM/AGENT/" . $agt;
        $data = $this->agi->Command($this->command);
        $this->agi->disconnect();
        return $data;
    }

    function ChanSpy($agt, $exten) {
        try {
            $this->agi->connect(AMI_HOST, AMI_USERNAME, AMI_PASWORD);
        } catch (Exception $ex) {
            return "problemas de Conexion AMI: " . $ex;
        }
        $this->agi->Originate("SIP/$exten", "001$agt", 'from-oml', 1, NULL, NULL, '25000', "supervision", NULL, NULL);
        $this->agi->disconnect();
    }

    function ChanSpyWhisper($agt, $exten) {
        try {
            $this->agi->connect(AMI_HOST, AMI_USERNAME, AMI_PASWORD);
        } catch (Exception $ex) {
            return "problemas de Conexion AMI: " . $ex;
        }
        $this->agi->Originate('SIP/' . $exten, "002$agt", 'from-oml', 1, NULL, NULL, '25000', "supervision", NULL, NULL);
        $this->agi->disconnect();
    }

    function Conference($agt, $exten) {
        try {
            $this->agi->connect(AMI_HOST, AMI_USERNAME, AMI_PASWORD);
        } catch (Exception $ex) {
            return "problemas de Conexion AMI: " . $ex;
        }
        $this->agi->Originate('SIP/' . $exten, "006$agt", 'from-oml', 1, NULL, NULL, '25000', "supervision", NULL, NULL);
        $this->agi->disconnect();
    }

    function AgentLogoff($agt, $queueName) {
        try {
            $this->agi->connect(AMI_HOST, AMI_USERNAME, AMI_PASWORD);
        } catch (Exception $ex) {
            return "problemas de Conexion AMI: " . $ex;
        }
        foreach ($queueName as $value) {
            $this->agi->Events('off');
            $this->command = "queue remove member sip/" . $agt . " from ". $value;
            $this->agi->Command($this->command);
        }
        $this->agi->disconnect();
    }
}
