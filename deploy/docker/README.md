#########################################################
### DevEnv. Omnileads Docker container for developers ###
#########################################################

You can have the software running in your system with this simple steps:
  1. Install Docker CE for Ubuntu: https://docs.docker.com/install/linux/docker-ce/ubuntu/
  2. Install docker-compose
      As docker CE follow the installation steps: https://docs.docker.com/compose/install/
  3. Follow docker post-installations steps: https://docs.docker.com/install/linux/linux-postinstall/

NOTE: never raise up containers with root user or root privileges

  4. Change the TZ environment file in the devenv-stack.yml to raise up containers with the timezone you want
  5. Go to deploy/docker/devenv/ and run:
      - ./docker-manage up

This will create and start the containers and open de django-server shell. There are another options for this script:
  * start: use it every time you boot your computer. This will restart some services inside containers and will also open the django-server shell
  * killrun: to kill the django-server inside omniapp container
  * run: this just will open the django-server shell
  * stop: stop all containers
  * down: stop and kill all containers

The devenv-stack file links the OML repository into the container so any change you make in the repository will be reflected in the devenv inmediately

To access omnileads via web browser:
  1. Edit you /etc/hosts file with:
      172.16.0.6 omniapp
  2. Acces with your favorite browser:
      https://omniapp

#########################################################
###                   PBX-emulator                    ###
#########################################################

Adittionally with omnileads container is the pbx-emulator, this an emulation of a PSTN provider, so you can make calls via Omnileads and have different results of the call based on what you dialed.

************************
*Dialplan configuration*
************************

  - Any number dialed finished with 0: PSTN is going to send you a BUSY signal
  - Any number dialed finished with 1: PSTN is going to answer your call and playback audios
  - Any number dialed finished with 2: PSTN will anwer your call, play short audio then hangup. This will emulate a calle hangup
  -  Any number dialed finished with 3: PSTN will answer your call after 35 seconds
  - Any number dialed finished with 5: PSTN will make you wait 120 seconds and then hangup. This will emulate a NO_ANSWER
  - Any number dialed finished with 9: PSTN will simulate a congestion

***************
*Inbound calls*
***************
You can simulate inbound calls registering an extension from the pbx-emulator. You can use the softphone you want. This are the extensions credentials:

  username: 01155001122
  secret: OMLtraining72
  domanin: 172.16.0.7

After registering the extension you can call this numbers for receiving the call to a Omnileads inbound campaign (check manuals to configure inbound campaign and inbound routing)

  0117766001[1-9] => you will receive the call with a random numeric CID
  0117766002[1-9] => you will receive the call with the word “unknown” as CID

Also you will have these two numbers to call from Omnileads to your softphone: 01155001122, 01155001133

*********************
*Trunk configuration*
*********************

Use this trunk configuration in you Omnileads environment to connect with the pbx-emulator

  type=friend
  host=172.16.0.7
  defaultuser=01177660010
  secret=OMLtraining72
  qualify=yes
  insecure=invite
  context=from-pstn
  disallow=all
  allow=alaw

And this in the register chain:

  01177660010:OMLtraining72@172.16.0.7
