#!/bin/bash

DOCKER="`which docker`"
DOCKER_COMPOSE="`which docker-compose`"
KAM_EXEC="$DOCKER exec -i {{ kamailio_fqdn}} bash -c"
AST_EXEC="$DOCKER exec -i {{ asterisk_fqdn }} bash -c"
OMNIAPP_EXEC="$DOCKER exec -i {{ omniapp_fqdn }} bash -c"

if [ -z $DOCKER_COMPOSE ]; then
  echo "Docker-compose not installed, exiting"
  exit 1
fi

UpCommands() {

  echo "Creating ssh keys for omniapp"
  if [ ! -f {{ omniapp_location }}/.ssh/id_rsa ]; then
    mkdir -p {{ omniapp_location }}/.ssh
    ssh-keygen -t rsa -b 4096 -f {{ omniapp_location}}/.ssh/id_rsa -t rsa -N ''
  else
    echo "SSH keys already created"
  fi
  chmod 600 {{ omniapp_location }}/.ssh/id_rsa && chown -R {{ docker_user }}. {{ deploy_location }}

  cd {{ deploy_location }}
  if [ ! -f .env ]; then
    touch .env
  fi
  echo "Creating and starting Omnileads containers "
  $DOCKER_COMPOSE -f devenv_stack.yml up -d
  ResultadoCompose=`echo $?`
  if [ "$ResultadoCompose" != 0 ]; then
    echo "There was a problem raising up some container, rerun the script"
    exit 1
  fi
  echo "Creating symlink of asterisk dialplan files"
  array=(oml_extensions_agent_session.conf oml_extensions_bridgecall.conf oml_extensions_commonsub.conf oml_extensions_modules.conf oml_extensions_postcall.conf oml_extensions_precall.conf oml_extensions.conf)
  for i in $(seq 0 6); do
    $AST_EXEC "if [ ! -f /etc/asterisk/${array[i]} ]; then ln -s /var/tmp/${array[i]} /etc/asterisk/${array[i]}; fi"
  done
  echo "Creating symlink of kamailio.cfg file"
  $KAM_EXEC "if [ ! -f /etc/kamailio/kamailio.cfg ]; then ln -s /var/tmp/kamailio.cfg /etc/asterisk/kamailio.cfg; fi"
  ast_ip=$(docker inspect -f {% raw %} "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}" {% endraw %} {{ asterisk_fqdn }})
  dialer_ip=$(docker inspect -f {% raw %} "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}" {% endraw %} {{ dialer_fqdn }})
  kam_ip=$(docker inspect -f {% raw %} "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}" {% endraw %} {{ kamailio_fqdn }})
  omni_ip=$(docker inspect -f {% raw %} "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}" {% endraw %} {{ omniapp_fqdn }})
  cat > {{ deploy_location }}/.env <<EOF

  ##############################
  #### Archivo autogenerado ####
  ##############################

  AMI_USER={{ ami_user }}
  AMI_PASSWORD={{ ami_password }}
  ASTERISK_IP=${ast_ip}
  ASTERISK_HOSTNAME={{ asterisk_fqdn }}
  ASTERISK_LOCATION=
  CALIFICACION_REAGENDA={{ schedule }}
  DIALER_IP=${dialer_ip}
  {% if devenv == 0 %}
  DJANGO_SETTINGS_MODULE=ominicontacto.settings.production
  {% else %}
  DJANGO_SETTINGS_MODULE=ominicontacto.settings.develop
  {% endif %}
  EPHEMERAL_USER_TTL=28800
  EXTERNAL_PORT={{ external_port }}
  INSTALL_PREFIX={{ install_prefix }}
  KAMAILIO_IP=${kam_ip}
  KAMAILIO_HOSTNAME={{ kamailio_fqdn }}
  KAMAILIO_LOCATION=
  NGINX_HOSTNAME={{ hostname.stdout }}
  OMNILEADS_IP=${omni_ip}
  OMNILEADS_HOSTNAME={{ omniapp_fqdn }}
  PGHOST={{ database_fqdn }}
  PGDATABASE={{ postgres_database }}
  PGUSER={{ postgres_user }}
  PGPASSWORD={{ postgres_password }}
  PYTHONPATH={{ install_prefix }}ominicontacto
  REDIS_HOSTNAME={{ redis_fqdn }}
  RTPENGINE_HOSTNAME={{ rtpengine_fqdn }}
  SESSION_COOKIE_AGE=3600
  WOMBAT_HOSTNAME={{ dialer_fqdn }}
  WOMBAT_USER={{ dialer_user }}
  WOMBAT_PASSWORD={{ dialer_password }}
EOF

  echo "Copying omniapp public key in asterisk and kamailio containers"
  ssh_key=$(cat {{ omniapp_location }}/.ssh/id_rsa.pub)
  $AST_EXEC "mkdir -p /root/.ssh/"
  $AST_EXEC "echo ${ssh_key} > /root/.ssh/authorized_keys"
  echo " Recreating omniapp container to get the IP of other containers"
  $DOCKER kill {{ omniapp_fqdn }} && $DOCKER rm {{ omniapp_fqdn }}
  $DOCKER_COMPOSE -f devenv_stack.yml create omniapp
  $DOCKER_COMPOSE -f devenv_stack.yml start omniapp
  $DOCKER restart {{ asterisk_fqdn }}
}

case "$1" in
  up)
    UpCommands
    ;;
  down)
    echo "Stopping and killing Omnileads containers "
    $DOCKER_COMPOSE -f devenv_stack.yml down
    ;;
  *)
    echo "Usage: used by omnileads-devenv.service"
    exit 1
    ;;
esac
