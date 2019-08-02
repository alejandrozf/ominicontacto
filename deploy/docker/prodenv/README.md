###########################################################
###     OMniLeads Docker environment for production     ###
###########################################################

You can have the software running in your system with this simple steps:
  1. Install Docker CE for your SO: https://docs.docker.com/install/
  2. Install docker-compose
      As docker CE follow the installation steps: https://docs.docker.com/compose/install/
  3. Select a user that will be capable to run docker commands and be sure that it has UID=1000 and GID=1000
** For Linux Docker Host **
  4. Follow docker post-installations steps: https://docs.docker.com/install/linux/linux-postinstall/

  5. Copy the prodenv folder in the location you desire
  6. Check the .env file, read carefully what is the purpose of each variable and edit them as you desire. There are some variables that are really important and you need to change them:
    * DOCKER_HOSTNAME="the hostname of the machine used to be docker host"
    * RELEASE="the OMniLeads release you want to deploy"
    * TZ="your timezone"
    * DJANGO_PASS="the password for the web GUI"
  7. With the user you selected raise up the environment
      - docker-compose up -d

This will take some time while the images of services are downloaded. Once finished you can see 9 containers up and running with docker ps.

Wait some time until the omniapp container finish some tasks. You can see the progress with:

  * docker logs oml-omniapp

To access OMniLeads via web browser:
  1. https://DOCKER_HOSTNAME

**********************************
* Post docker-compose workaround *
**********************************

In the prodenv folder you will see after running docker-compose up -d that four folders are created:

 * recordings: will have the recordings of the calls
 * mariadb_data: will have the mysql database needed for Wombat Dialer
 * postgresql_data: will have the postgresql database needed for OMniLeads
 * sounds: will have the sounds you upload in the sounds GUI in OMniLeads

At beginning you will see that the oml-mariadb-prodenv container will be restarting. To fix this:

 * chown 1001:1001 mariadb_data
 * docker restart oml-mariadb-prodenv

*******
* FAQ *
*******

1. How do I change passwords of my services?

There are two important password services:
    - Omnileads web GUI: change the $DJANGO_PASS variable in .env file and restart the omniapp container
    - Postgresql: edit the $PGPASSWORD variable in .env file, then use the **change_postgres_pass** script located in this folder. After that do docker-compose up -d to remake containers with new $PGPASSWORD

These are typical issues you can encourage editing some variables in .env file.

2. Overlap of network settings: By default the environment will use the subnet 192.168.15.0/24 for internal docker networking. If you are using this subnet in you LAN you can change these variables with new subnet configuration (or you can change your LAN):

  DIALER_IP=192.168.15.10
  KAMAILIO_IP=192.168.15.11
  OMniLeads_IP=192.168.15.12
  SUBNET=192.168.15.0/24

2. The environment doesn't start because docker-compose says a port is in use: there are three port mappings made to access services inside containers. Change them as your convenience.

  WD_EXT_PORT=442  --> maps the 8080/tcp port in Wombat Dialer, to access WD GUI
  NGINX_EXT_PORT=444 --> maps the 443/tcp port in Omniapp to access OMniLeads GUI
  PG_EXT_PORT=445  --> maps the 5038/tcp port in Postgresql to acces OMniLeads database
