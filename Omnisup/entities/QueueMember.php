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
