<?php

class QueueMember {

    private $exten;
    private $name;
    private $callsTaken;
    private $logoff;
    private $status;

    function __construct() {
        $this->exten = 0;
        $this->name = "";
        $this->callsTaken = 0;
        $this->logoff = false;
        $this->status = "";
    }

    function getExten() {
        return $this->exten;
    }

    function getName() {
        return $this->name;
    }

    function getCallsTaken() {
        return $this->callsTaken;
    }

    function getLogoff() {
        return $this->logoff;
    }

    function getStatus() {
        return $this->status;
    }

    function setExten($exten) {
        $this->exten = $exten;
    }

    function setName($name) {
        $this->name = $name;
    }

    function setCallsTaken($callsTaken) {
        $this->callsTaken = $callsTaken;
    }

    function setLogoff($logoff) {
        $this->logoff = $logoff;
    }

    function setStatus($status) {
        $this->status = $status;
    }

}
