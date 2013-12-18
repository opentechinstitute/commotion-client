#/usr/bin/python

import dbus.mainloop.glib ; dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
import fcntl
import glob
import hashlib
import os
import pprint
import pyjavaproperties
import random
import re
import socket
import struct
import subprocess
import syslog
import tempfile
import time

class CommotionCore():

    def __init__(self, src='commotionc'):
        self.olsrdconf = '/etc/olsrd/olsrd.conf'
        self.profiledir = '/etc/commotion/profiles.d/'
        self.logname = src


    def _generate_ip(self, base, netmask, interface):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #First two lines adapted from stackoverflow.com/questions/159137/getting-mac-address
        hwiddata = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('32s', interface[:15])) 
        netmaskaddr = socket.inet_aton(netmask)
        baseaddr = socket.inet_aton(base)
        hwaddr = hwiddata[20:24] #Extract only the last four 1-byte hex values of the returned mac address
        finaladdr = []
        for i in range (4):
             finaladdr.append((ord(hwaddr[i]) & ~ord(netmaskaddr[i])) | (ord(baseaddr[i]) & ord(netmaskaddr[i])))
        return socket.inet_ntoa(''.join([chr(item) for item in finaladdr]))

    def log(self, msg):
        syslog.openlog(self.logname)
        syslog.syslog(msg)
        syslog.closelog()

    def getInterface(self, preferred=None):
        interface = None
        for wireless in glob.iglob('/sys/class/net/*/wireless'): #Reformat as a list comprehension
            driver = os.listdir(os.path.join('/sys/class/net', wireless.split('/')[4], 'device/driver/module/drivers'))
            if driver[0].split(':')[1] in ('ath5k', 'ath6kl', 'ath9k', 'ath9k_htc', 'b43', 'b43legacy', 'carl9170', 'iwlegacy', 'iwlwifi', 'mac80211_hwsim', 'orinoco', 'p54pci', 'p54spi', 'p54usb', 'rndis_wlan', 'rt61pci', 'rt73usb', 'rt2400pci', 'rt2500pci', 'rt2500usb', 'rt2800usb', 'rtl8187', 'wl1251', 'wl12xx', 'zd1211rw'):
                 interface = wireless.split('/')[4]
                 if preferred == interface:
                     return preferred
        if preferred:
            if interface:
                self.log("WARNING: Specified interface " + preferred + " does not support cfg80211 (ibss encryption), or ibss mode, or both!  Interface " + interface + " does, however.  Consider changing the interface setting in /etc/commotion/commotionc.conf")
            else: 
                self.log('WARNING: No available wireless interfaces have support for both ibss mode and cfg80211 (ibss encryption)')
            return preferred
        elif interface:
            self.log("Mesh-compatible interface found! (" + interface + ")")
            return interface
        else: 
            self.log('WARNING: No available wireless interfaces have support for both ibss mode and cfg80211 (ibss encryption)')
            return wireless.split('/')[4]
            #interface = subprocess.check_output(['/sbin/iw', 'dev']).split()
            #interface = interface[interface.index('Interface') + 1]
            #subprocess.check_output(['iw', 'list'])
        
    def readProfile(self, profname):
        f = os.path.join(self.profiledir, profname + '.profile')
        p = pyjavaproperties.Properties()
        p.load(open(f))
        profile = dict()
        profile['filename'] = f
        profile['mtime'] = os.path.getmtime(f)
        for k,v in p.items():
            profile[k] = v
        for param in ('ssid', 'channel', 'ip', 'netmask', 'dns', 'ipgenerate'): ##Also validate ip, dns, bssid, channel?
            if param not in profile:
                self.log('Error in ' + f + ': missing or malformed ' + param + ' option') ## And raise some sort of error?
        if profile['ipgenerate'] in ('True', 'true', 'Yes', 'yes', '1'): # and not profile['randomip']
            self.log('Randomly generating static ip with base ' + profile['ip'] + ' and subnet ' + profile['netmask'])
            profile['ip'] = self._generate_ip(profile['ip'], profile['netmask'], self.getInterface())
            self.updateProfile(profname, {'ipgenerate': 'false', 'ip': profile['ip']})
        if not 'bssid' in profile: #Include note in default config file that bssid parameter is allowed, but should almost never be used
            self.log('Generating BSSID from hash of ssid and channel')
            bssid = hashlib.new('md4', ssid).hexdigest()[-8:].upper() + '%02X' %int(profile['channel']) #or 'md5', [:8]
            profile['bssid'] = ':'.join(a+b for a,b in zip(bssid[::2], bssid[1::2]))

        conf = os.path.join(re.sub('(.*)\profiles.d.*', r'\1olsrd.d', self.profiledir), profname + '.conf') #Unify this syntax by making profiledir just /etc/commotion?
        if os.path.exists(conf):
            self.log('profile has custom olsrd.conf: "' + conf + '"')
            profile['conf'] = conf
        else:
            self.log('using built in olsrd.conf: "' + self.olsrdconf + '"')
            profile['conf'] = self.olsrdconf
        return profile


    def readProfiles(self):
        '''get all the available mesh profiles and return as a dict'''
        profiles = dict()
        self.log('Reading profiles:')
        for f in glob.glob(self.profiledir + '*.profile'):
            profname = os.path.split(re.sub('\.profile$', '', f))[1]
            self.log('reading profile: "' + f + '"')
            profile = self.readProfile(profname)
            self.log('adding "' + f + '" as profile "' + profile['ssid'] + '"')
            profiles[profile['ssid']] = profile
        return profiles


    def updateProfile(self, profname, params):
        self.log('Updating profile \"' + profname + '\" ')
        fn = os.path.join(self.profiledir, profname + '.profile')
        if not os.access(fn, os.W_OK):
            self.log('Unable to write to ' + fn + ', so \"' + profname + '\" was not updated')
            return
        savedsettings = []
        fd = open(fn, 'r')
        for line in fd:
            savedsettings.append(line)
            for param, value in params.iteritems():
                if re.search('^' + param + '=', savedsettings[-1]):
                    savedsettings[-1] = (param + '=' + value + '\n')
                    break
        fd.close()
        fd = open(fn, 'w')
        for line in savedsettings:
            fd.write(line)
        fd.close()


    def startOlsrd(self, interface, conf):
        '''start the olsrd daemon'''
        self.log('start olsrd: ')
        cmd = ['/usr/sbin/olsrd', '-i', interface, '-f', conf]
        self.log(" ".join([x for x in cmd]))
        p = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            self.log('stdout: ' + out)
        if err:
            self.log('stderr: ' + err)


    def stopOlsrd(self):
        '''stop the olsrd daemon'''
        self.log('stop olsrd')
        cmd = ['/usr/bin/killall', '-v', 'olsrd']
        self.log(" ".join([x for x in cmd]))
        p = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            self.log('stdout: ' + out)
        if err:
            self.log('stderr: ' + err)


    def _create_wpasupplicant_conf(self, profile, tmpfd):
        contents = []
        contents.append('ap_scan=2\n')
        contents.append('network={\n')
        contents.append('\tmode=1\n')
        contents.append('\tssid' + '=' + '\"' + profile['ssid'] + '\"\n')
        contents.append('\tbssid' + '=' + profile['bssid'] + '\n')
        contents.append('\tfrequency' + '=' + str((int(profile['channel']))*5 + 2407) + '\n')
        if 'psk' in profile:
            contents.append('\tkey_mgmt=WPA-PSK' + '\n')
            contents.append('\tpsk' + '=' + '\"' + profile['psk'] + '\"\n')
        contents.append('}')
        for line in contents:
            tmpfd.write(line)
 
    def fallbackConnect(self, profileid):
        profile = self.readProfile(profileid)
        interface = self.getInterface()
        ip = profile['ip']
        if 'connected' in subprocess.check_output(['/usr/bin/nmcli', 'nm', 'status']): #Connected in this context means "active," not just "connected to a network"
            self.log('Putting network manager to sleep...')
            try:
                subprocess.check_call(['/usr/bin/nmcli', 'nm', 'sleep', 'true'])
            except:
                self.log('Error putting network manager to sleep!')
        self.log('Killing default version of wpa_supplicant...')
        try:
            subprocess.check_call(['/usr/bin/pkill', '-9', 'wpa_supplicant'])
        except:
            self.log('Error killing wpa_supplicant!')
            
        self.log('Bringing ' + interface + ' down...')
        try:
            subprocess.check_call(['/sbin/ifconfig', interface, 'down'])
        except:
            self.log('Error bringing interface down!')
        ##Check for existance of replacement binary
        self.log('Starting replacement wpa_supplicant with profile ' + profileid + ', interface ' + interface + ', and ip address ' + ip + '.')
        wpasupplicantconf = tempfile.NamedTemporaryFile('w+b', 0)
        self._create_wpasupplicant_conf(profile, wpasupplicantconf)
        subprocess.Popen(['/usr/bin/commotion_wpa_supplicant', '-Dnl80211', '-i' + interface, '-c' + wpasupplicantconf.name])
        time.sleep(2)
        wpasupplicantconf.close()
        try:
            subprocess.check_call(['/sbin/ifconfig', interface, 'up', ip, 'netmask', '255.0.0.0'])
        except:
            self.log('Error bringing interface up!')
               
        self.startOlsrd(interface, profile['conf'])

