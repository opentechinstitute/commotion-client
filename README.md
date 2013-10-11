#Commotion Linux - Python Implementation
=======================================

##INTRODUCTION
This is an initial implementation of core Commotion functionality in the form of a python module, commotionc, and related scripts.  None of the code in this bundle is intended to be called directly, but rather serves as a backend for commotion-mesh-applet and nm-applet-olsrd (although if you really want to you can use fallback.py as a basic command-line interface to bring Commotion up and down). Future versions of this code will allow for full command-line control of the Commotion software stack via one unified binary.  

##PRE-REQUISITES
1. Confirm that you have a wireless adapter whose driver supports both the cfg80211 kernel interface and ibss mode. A list of drivers that support these features can be found at http://wireless.kernel.org/en/users/Drivers. 
2. Ensure that you are running an up-to-date OS and kernel.  Where possible, download and install the newest kernel your OS supports (optimally 3.5 or higher).  Many wireless drivers are embedded in the kernel, and some of these have only recently gotten full cfg80211 support.  
3. If you are running an OS that uses a version of wpasupplicant older than v. 1.0, you will need the commotion-wpasupplicant package.  Your system will only be able connect in "fallback" mode, which entirely bypasses network manager.  

##USAGE
###Step 1
Define a new mesh network profile or modify the default profile in `/etc/commotion/profiles.d/`. You can define as many different network profiles as you wish, one per file.  .profile files consist of simple parameter=value pairs, one per line.  The default `commotionwireless.net.profile` file installed by the commotion-mesh-applet package shows all available parameters:

```
ssid=commotionwireless.net 
#Network name (REQUIRED)
bssid=02:CA:FF:EE:BA:BE
#IBSS cell ID, which takes the form of a fake mac address.  If this field is omitted, it will be automatically generated via an md4 hash of the ssid and channel.
channel=5
#2.4 GHz Channel (REQUIRED)
ip=5.0.0.0
#When ipgenerate=true, ip holds the subnet from which the actual ip will be generated.  When ipgenerate=false, ip holds the actual ip that will be used for the connection (REQUIRED)
ipgenerate=true
#See not for ip parameter.  ipgenerate is automatically set to false once a permanent ip has been generated (REQUIRED)
netmask=255.0.0.0
#The subnet mask of the network (REQUIRED)
dns=8.8.8.8
#DNS server (REQUIRED)
psk=meshpassword
#The password required to connect to an IBSS-RSN encrypted mesh network.  When connecting to a network with an encrypted backhaul, this parameter is required.  When connecting to a networking without encryption, the parameter should be omitted entirely.  
```

###Step 2
Once you have either modified the default profile or installed a new one, you will need to force the various Commotion helper applets to reparse the profiles.d directory, like so:
* _commotion-mesh-applet:_ Restart commotion-mesh-applet either by logging out of your current user session and logging in again, or exiting the applet and then running it directly from the command line: `/usr/bin/gnome-applets/commotion-mesh-applet`.
* _nm-dispatcher-olsrd:_ Have network manager connect or disconnect to a network - but *NOT* the mesh network you're trying to connect to.  This will force the dispatcher script to run, which will pull the updates to the `profiles.d` directory into the appropriate connection files in `/etc/NetworkManager/system-connections/`. You can can confirm that the new Commotion settings have been accepted by looking at the appropriate network profile in the nm-applet interface, and/or the contents of `/etc/NetworkManager/system-connections/<connectionname>`

###Step 3
Click on the mesh profile you wish to connect to in the list of networks shown by commotion-mesh-applet.  If your system is capable of using the "network manager" connection path, Network Manager will activate the specified connection, and nm-applet will display an ad-hoc icon once you are connected.  If your system relies on the "fallback" connection path, Network Manager will be put to sleep when the mesh network is activated, and will remain so until the mesh connection is deactivated.  In the fallback case, all networking mechanics are handled directly by wpasupplicant and calls to ifconfig.  

###Step 4
When you wish to restore normal networking functionality, click <Disconnect> in commotion-mesh-applet.  

##*TROUBLESHOOTING NOTES*
* Log files for each Commotion component are generated in `/tmp`, with very obvious names (eg, `nm-dispatcher-olsrd.log`).  
* A great deal of information is dumped to standard out by commotion-mesh-applet, so if you're having trouble connecting you should close the applet and restart it from a command line, so that you can see its output. 
* If you are using the "network manager" connection path, you might want to keep *wpa_cli* open while you're trying to connect.  This will allow you to see whether or not the Linux client is able to successfully complete the authentication handshake with the rest of the network 
* When connecting to encrypted mesh networks, you want to see output that says "Key negotiation completed with <MAC address>" immediately after you connect.  In the fallback case, this output should be dumped to stdout by commotion-mesh-applet.  In the "network manager" connection process, this output should be shown by *wpa_cli*.  
* Some information may also be sent to `/var/log/syslog`.  
* Some drivers much more likely to properly connect to a mesh after being unloaded from and then reloaded into the kernel. Weirdly, this also applies to olsrd: If everything else seems to be working, but olsrd refuses to get routes, try unloading/reloading the driver, and reconnecting.
* If you have multiple networking cards present on your system, disable (ie, unload the drivers for) the ones that aren't capable of meshing properly.  The interface selection routines in the Linux client are currently very unintelligent, and will simply chose the first active wireless interface they encounter, even if that interface actually does not support mesh connections.  
* iwconfig and iw both lie horribly about data such as active channel and authentication status.  Don't necessarily believe what they tell you.  
