# DevEnv. Omnileads Docker environment for developers

This environment can be deployed in any linux distro. Linux distro tested by our team is Ubuntu 18.04.

## Prerequisites

1. Install Docker CE for your distro: https://docs.docker.com/install/
2. Install docker-compose
    As docker CE follow the installation steps: https://docs.docker.com/compose/install/
3. Follow docker post-installations steps: https://docs.docker.com/install/linux/linux-postinstall/

## Deploy using ansible

1. Open he ansible inventory file located in `deploy/ansible/inventory` and:
  * Uncomment the line below [devenv-container] to let ansible know you want to deploy a devenv
```sh
  [devenv-container]
  #localhost ansible_connection=local
```
  * Uncomment the following variables and change the values as you wish       
```sh
    #postgres_user=omnileads
    #postgres_password=my_very_strong_pass
    #admin_pass=my_very_strong_pass
    #ami_user=omnileadsami
    #ami_password=5_MeO_DMT
    #dialer_user=demoadmin
    #dialer_password=demo
    #TZ=America/Argentina/Cordoba
```
2. Check the network assgined to devenv in group_vars/docker_devenv_vars.yml. By default the subnet 172.20.0.0/24 is assgined to the environment. Change the subnet if it clashes with your WLAN o LAN subnet
3. Go to deploy/ansible and run:
```sh
  $ sudo ./deploy.sh --docker-deploy --iface=<your_iface> //where your_iface is the network interface of your LAN o WLAN
```
This will deploy the required settings for the environment.

## Raising up the environment

After ansible ends, do this to raise up the enviroment:
```sh
  $ cd ~/omnileads/prodenv
  $ docker-compose up -d
```
This will take some time while it download the docker images. Once finished you can use **docker ps** to see that you have 10 containers up and running.

## Services you can access

* First is the web server available. To access omnileads via web browser: **https://YOUR_HOSTNAME**
* Second, the postgresql database, you can access it with this credentials:
```sh
  PGHOST=YOUR_HOSTNAME
  PGDATABASE=the one you used in inventory
  PGUSER=the one you used in inventory
  PGPASSWORD=the one you used in inventory
  PGPORT=4444
```
* Third, Wombat Dialer web server. To access it: **http://YOUR_HOSTNAME:4442**

## Configuring wombat dialer

You only need to do this if you are going to work with Predictive Dialer campaigns

When you enter to **http://YOUR_HOSTNAME:4442** you go to Wombat Dialer to begin its configuration. Check our official documentation to check this: https://documentacion-omnileads.readthedocs.io/es/stable/maintance.html#configuracion-del-modulo-de-discador-predictivo

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
  $ cd ~/omnileads/prodenv
  $ docker-compose down
```
* To clean the database, do this after turning down the environment:
```sh
  $ docker volume rm devenv_postgresql_data
```

# Changing .env variables value

The .env file inside `~/omnileads/devenv` contains variables used by containers. For example the django admin password. You can modify all variables except the PGPASSWORD doing these:

1. Modify the variable you want to.
2. Logout from your user's session and login again
3. Raise down the environment and raise it up again.

# Changing code

The docker-compose file links the OML repository into the container so any change you make in the *django code* will be reflected in the devenv inmediately.
On the other hand after changing asterisk code or configuration file, is necessary to go into the asterisk container and execute *asterisk -rx "module reload"*

# Updating environment

Sometimes you will need to update the environment for any change we make, for that you will have to run the deploy using ansible again.

1. If you don't want to change any of the variables from inventory you must check that your shell sources the `/etc/profile.d/`. In ubuntu we check a WA for that, adding this in the `/etc/bash.bashrc` file
```sh
  if [ -d /etc/profile.d ]; then
    for i in /etc/profile.d/*.sh; do
      if [ -r $i ]; then
        . $i
      fi
    done
    unset i
  fi
```
2. You can change the variables without deploying with ansible, editing the .env file located in `~/omnileads/prodenv/.env`
3. Check the RELEASES.txt file, to see the latest version of docker images, and what changes they bring.

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

You can simulate inbound calls registering an extension from the pbx-emulator. You can use the softphone you want. This are the extensions credentials:

  username: 01155001122
  secret: OMLtraining72
  domain: YOUR_HOSTNAME

(Change "YOUR_HOSTNAME" with the hostname or your machine)

After registering the extension you can call this numbers for receiving the call to a Omnileads inbound campaign (check manuals to configure inbound campaign and inbound routing)

  0117766001[1-9] => you will receive the call with a random numeric CID
  0117766002[1-9] => you will receive the call with the word “unknown” as CID

Also you will have these two numbers to call from Omnileads to your softphone: 01155001122, 01155001133

## Trunk configuration

Use this trunk configuration in you Omnileads environment to connect with the pbx-emulator

  type=friend
  host=pbx-emulator
  defaultuser=01177660010
  secret=OMLtraining72
  qualify=yes
  insecure=invite
  context=from-pstn
  disallow=all
  allow=alaw

And this in the register chain:

  01177660010:OMLtraining72@pbx-emulator

## Outbound route configuration

With the previous sip trunk created you must create an outbound route for outbound calls.
You can customize the parameters values for your needs but we recommend, for quickly setup of develop enviromment, to type any value for field 'name', leave defaults values for fields 'Ring time' and 'Dial options' and type "X." for field "Dial pattern". Then select the trunk previously created for field 'Trunks sequence' and save the outbound route.
