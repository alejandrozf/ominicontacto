#!/bin/bash

echo "Ejecutando Ansible en omni-voip Pre-Freepbx"
ansible-playbook -s /etc/ansible/pre-freepbx/omni-debian -u freetech -K

ansible-playbook -s /etc/ansible/pre-freepbx/omni-freepbx.yml -u root
