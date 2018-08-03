<?php

class QueueMember {

    private $id;
    private $exten;
    private $name;
    private $callsTaken;
    private $logoff;
    private $status;
    private $time;

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

    function getTime() {
        return $this->time;
    }

    function getId() {
        return $this->id;
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

    function setTime($time) {
        $this->time = $time;
    }

    function setId($id) {
        $this->id = $id;
    }
}
