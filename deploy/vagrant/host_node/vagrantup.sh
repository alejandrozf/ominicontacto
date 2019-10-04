#!/bin/bash

vagrant up $1
vagrant halt $1
vagrant up --no-provision $1
