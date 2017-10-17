#!/bin/bash

echo "Ejecutando Ansible en omni-voip Pre-Freepbx"
ansible-playbook -s /etc/ansible/pre-freepbx/main.yml -u freetech -K

