<?php

class NumState {

    private $number;
    private $state;

    function __construct() {
        $this->number = 0;
        $this->state = "";
    }

    function getNumber() {
        return $this->number;
    }

    function getState() {
        return $this->state;
    }

    function setNumber($number) {
        $this->number = $number;
    }

    function setState($state) {
        $this->state = $state;
    }

}
