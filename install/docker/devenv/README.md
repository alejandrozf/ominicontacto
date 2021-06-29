# DevEnv. Omnileads Docker environment for developers

This environment can be deployed in any linux distro. Linux distro tested by our team is Ubuntu 18.04.

## Prerequisites

1. Install Docker CE for your distro: https://docs.docker.com/install/
2. Install docker-compose
    As docker CE follow the installation steps: https://docs.docker.com/compose/install/
3. Follow docker post-installations steps: https://docs.docker.com/install/linux/linux-postinstall/

## Deploy of stack

1. Create the .env file, coyping the .env.template
```sh
  $ cp .env.template .env
```
**Note:** Check the network assigned to devenv in SUBNET variable. By default the subnet 192.168.15.0/24 is assgined to the environment. Change the subnet if it clashes with your WLAN o LAN subnet
3. Raise up the environment
```sh
  $ docker-compose up -d
```
This will take some time while it download the docker images. Once finished you can use **docker ps** to see that you have 10 containers up and running.

## Setting default admin user password

**Note:** the next command must be run only once, when environment is raised up at first time

```sh
  $ docker-compose exec app bash or docker exec -it omlapp bash
  $ python3 manage.py cambiar_admin_password
```
This will set the admin password to default value: 'admin'. So you can login using that credentials: `admin/admin`

## Initializing environment

You can also use the command inicializar_entorno to have some data written in your environment.

```sh
  $ docker-compose exec app bash or docker exec -it omlapp bash
  $ python3 manage.py inicializar_entorno
```
You will have the trunk with the pbxemulator and an agent with this credentials:
`agent/agent1*`

## Services you can access

* First is the web server available. To access omnileads via web browser: **https://YOUR_HOSTNAME** or **https://YOUR_IP**
* Second, the postgresql database, you can access it with this credentials:
```sh
  PGHOST=YOUR_HOSTNAME
  PGDATABASE=the one you used in inventory
  PGUSER=the one you used in inventory
  PGPASSWORD=the one you used in inventory
  PGPORT=4444
```
* Third, Wombat Dialer web server. To access it: **http://YOUR_HOSTNAME:4442/wombat**

## Configuring wombat dialer

You only need to do this if you are going to work with Predictive Dialer campaigns

When you enter to **http://YOUR_HOSTNAME:4442** you go to Wombat Dialer to begin its configuration. Check our official documentation to check this: https://documentacion-omnileads.readthedocs.io/es/stable/maintance.html#configuracion-del-modulo-de-discador-predictivo

---
**Note:** when configuring AMI connection in Wombat Dialer, the server address is `acd`.
---

## Updating images

The images of the different services can be updated using the script `download_images.sh`. The script will always pull the latest develop of all services from the Freetech Solutions dockerhub.

## Logs and others useful stuff

From **docker ps** command you can take the container name that is assigned for each container.

* To see logs of any container:
```sh
  $ docker logs $(container_name)
```
* To go into the shell of a container
```sh
  $ docker exec -it $(container_name) bash //some containers does not have bash installed, use sh instead
```
* To capture the stdout of the logs of any container you can use
```sh
  $ docker attach $(container_name)
```
* To turn down the environment, destroying all containers.
```sh
  $ docker-compose down
```
* To clean the database, do this after turning down the environment:
```sh
  $ docker volume rm devenv_postgresql_data
```

## Adding a package to project requirements

1. Add package to requirements.txt file
2. Go to omlappbuilder container and install the requirements packages:
```sh
  $ docker exec -it omlappbuilder sh
  $ pip3 install -r requirements.txt
```  

## Changing code

The docker-compose file links the OML repository into the container so any change you make in the *django code* will be reflected in the devenv inmediately.
On the other hand after changing asterisk code or configuration file, is necessary to go into the asterisk container and execute *asterisk -rx "module reload"*

# PBX-emulator

Adittionally with omnileads container is the pbx-emulator, this an emulation of a PSTN provider, so you can make calls via Omnileads and have different results of the call based on what you dialed.

## Dialplan configuration

  - Any number dialed finished with 0: PSTN is going to send you a BUSY signal
  - Any number dialed finished with 1: PSTN is going to answer your call and playback audios
  - Any number dialed finished with 2: PSTN will anwer your call, play short audio then hangup. This will emulate a calle hangup
  -  Any number dialed finished with 3: PSTN will answer your call after 35 seconds
  - Any number dialed finished with 5: PSTN will make you wait 120 seconds and then hangup. This will emulate a NO_ANSWER
  - Any number dialed finished with 9: PSTN will simulate a congestion

## Inbound calls

You can simulate inbound calls:

A) Registering an extension from the pbx-emulator. You can use the softphone you want. This are the extensions credentials:

  username: 01155001122
  secret: OMLtraining72
  domain: YOUR_HOSTNAME

(Change "YOUR_HOSTNAME" with the hostname or your machine)

B) With sipp utility, this option permit to execute many inbound calls from pbx-emulator to OMniLeads. Here we can to perform a stress test also:

```sh
docker exec -it pbx-emulator sipp -sn uac localhost:5060 -s stress -r 1 -d 60000 -l 10
```

For more details run:

```sh
sipp --help
```

You can call this numbers for receiving the call to a Omnileads inbound campaign (check manuals to configure inbound campaign and inbound routing)

  0117766001[1-9] => you will receive the call with a random numeric CID
  0117766002[1-9] => you will receive the call with the word “unknown” as CID

Also you will have these two numbers to call from Omnileads to your softphone: 01155001122, 01155001133
