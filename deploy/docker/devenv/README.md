###########################################################
### DevEnv. Omnileads Docker environment for developers ###
###########################################################

You can have the software running in your system with this simple steps:
  1. Install Docker CE for your SO: https://docs.docker.com/install/
  2. Install docker-compose
      As docker CE follow the installation steps: https://docs.docker.com/compose/install/
  3. Follow docker post-installations steps: https://docs.docker.com/install/linux/linux-postinstall/

NOTE: never raise up containers with root user or root privileges

  4. Open he ansible inventory file and:
    * Uncomment the line below [devenv-container] to let ansible know you want to deploy a devenv
        [devenv-container]
        #localhost ansible_connection=local
      * Uncomment the following variables and change the values as you wish       
          #postgres_password=my_very_strong_pass
          #admin_pass=my_very_strong_pass
          #mysql_root_password=my_very_strong_pass
          #TZ=America/Argentina/Cordoba
  5. Check the network assgined to devenv in group_vars/docker_devenv_vars.yml. By default the subnet 172.20.0.0/24 is assgined to the environment. Change the subnet and the IP's assigned to some containers if you need it.
  6. Go to deploy/ansible and run:
      - sudo ./deploy.sh --docker-deploy --iface=<your_iface>
    where your_iface is the network interface of your LAN o WLAN 

This will deploy the required settings for the environment. Once finished you can use docker ps to see that you have 10 containers up and running.
A new service is created for raising up or down the environment. Init the service:

  * service omnileads-devenv start

Wait some time until the omniapp container finish some tasks. You can see the progress with:

  * docker attach oml-omniapp

The devenv_stack file links the OML repository into the container so any change you make in the repository will be reflected in the devenv inmediately

To access omnileads via web browser:
  1. https://YOUR_HOSTNAME


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
  domanin: pbx-emulator

After registering the extension you can call this numbers for receiving the call to a Omnileads inbound campaign (check manuals to configure inbound campaign and inbound routing)

  0117766001[1-9] => you will receive the call with a random numeric CID
  0117766002[1-9] => you will receive the call with the word “unknown” as CID

Also you will have these two numbers to call from Omnileads to your softphone: 01155001122, 01155001133

*********************
*Trunk configuration*
*********************

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

******************************
*Outbound route configuration*
******************************

With the previous sip trunk created you must create an outbound route for outbound calls.
You can customize the parameters values for your needs but we recommend, for quickly setup of develop enviromment, to type any value for field 'name', leave defaults values for fields 'Ring time' and 'Dial options' and type "X." for field "Dial pattern". Then select the trunk previously created for field 'Trunks sequence' and save the outbound route.
