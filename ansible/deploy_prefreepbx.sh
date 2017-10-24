#!/bin/bash


echo "Bienvenido al asistente de instalación de Omnileads"
echo ""
echo "Ingrese 1 si va instalar en Debian o 2 si va a instalar en SangomaOS"
echo -en "Opcion: ";read opcion
echo ""

if [ $opcion -eq 1 ]; then
    echo "Ejecutando Ansible en Debian omni-voip Pre-FreePBX"
    ansible-playbook -s /etc/ansible/pre-freepbx/omni-voip.yml -u freetech -K
    echo "Finalizó la instalación Pre-FreePBX, favor hacer las configuraciones en la GUI"

elif [ $opcion -eq 2 ]; then
    echo "Ejecutando Ansible en SangomaOS Pre-Freepbx"
    ansible-playbook -s /etc/ansible/pre-freepbx/omni-freepbx.yml -u root
    echo "Finalizó la instalación Pre-FreePBX, favor hacer las configuraciones en la GUI"

else
    echo "Parámetro inválido ingrese de nuevo"
    echo  ""
fi
