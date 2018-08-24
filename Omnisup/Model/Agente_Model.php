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
                FROM ominicontacto_app_agenteprofile AP JOIN queue_member_table AC
                ON AP.id = AC.member_id JOIN ominicontacto_app_user AU ON AP.user_id = AU.id AND AP.is_inactive = 'f'
                AND AP.borrado = 'f' AND AC.id_campana LIKE :cpname";
        try {
          $cpname = "%$campName";
          $cnn = new PDO($this->argPdo, PG_USER, PG_PASSWORD);
          $query = $cnn->prepare($sql);
          $query->bindParam(':cpname', $cpname );
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

    function ExecAction($agt, $exten, $action) {
        try {
            $this->agi->connect(AMI_HOST, AMI_USERNAME, AMI_PASWORD);
        } catch (Exception $ex) {
            return "problemas de Conexion AMI: " . $ex;
        }
        //"AGENTLOGOUT"/"AGENTUNPAUSE"/"AGENTPAUSE"/"CHANTAKECALL"/"CHANSPYWISHPER"/"CHANSPY"/"CHANCONFER"
        $res = $this->agi->Originate("SIP/$exten", $action, 'oml-sup-actions', 1, NULL, NULL, '25000', NULL, "OMLAGENTID=".$agt, NULL, NULL, NULL);
        $this->agi->disconnect();
        return $res;
    }
}
