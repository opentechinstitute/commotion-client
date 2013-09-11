#/usr/bin/python

import dbus.mainloop.glib ; dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
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
import time

class CommotionCore():

    def __init__(self, f=None):
        self.olsrdconf = '/etc/olsrd/olsrd.conf'
        self.profiledir = '/etc/commotion/profiles.d'
        if f:
            self.f = open(f, 'ab')
        else:
            self.f = open('/tmp/commotion-core.log', 'ab')

    def _log(self, msg):
        self.f.write(msg + '\n')
        self.f.flush()

    def _ip_string2int(self, s):
        "Convert dotted IPv4 address to integer."
        # first validate the IP
        try:
            socket.inet_aton(s)
        except socket.error:
            self._log('"' + s + '" is not a valid IP address!')
            return
        return reduce(lambda a,b: a<<8 | b, map(int, s.split(".")))

    def _ip_int2string(self, ip):
        "Convert 32-bit integer to dotted IPv4 address."
        return ".".join(map(lambda n: str(ip>>n & 0xFF), [24,16,8,0]))

    def _get_net_size(self, netmask):
        # after bin(), remove the 0b prefix, strip the 0s and count the 1s
        binary_str = bin(self._ip_string2int(netmask))[2:]
        return str(len(binary_str.rstrip('0')))

    def _generate_ip(self, ip, netmask):
        ipint = self._ip_string2int(ip)
        netmaskint = self._ip_string2int(netmask)
        return self._ip_int2string((random.randint(0, 2147483648) & ~netmaskint) + ipint)


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
                self._log('Error in ' + f + ': missing or malformed ' + param + ' option') ## And raise some sort of error?
        if profile['ipgenerate'] in ('True', 'true', 'Yes', 'yes', '1'): # and not profile['randomip']
            profile['ip'] = self._generate_ip(profile['ip'], profile['netmask'])
            self.updateProfile(profname, {'ipgenerate': 'false', 'ip': profile['ip']})
        if not 'bssid' in profile: #Include note in default config file that bssid parameter is allowed, but should almost never be used
            bssid = hashlib.new('md4', ssid).hexdigest()[-8:].upper() + '%02X' %int(profile['channel']) #or 'md5', [:8]
            profile['bssid'] = ':'.join(a+b for a,b in zip(bssid[::2], bssid[1::2]))

        conf = re.sub('(.*)\.profile', r'\1.conf', f)
        if os.path.exists(conf):
            self._log('profile has custom olsrd.conf: "' + conf + '"')
            profile['conf'] = conf
        else:
            self._log('using built in olsrd.conf: "' + self.olsrdconf + '"')
            profile['conf'] = self.olsrdconf
        return profile


    def readProfiles(self):
        '''get all the available mesh profiles and return as a dict'''
        profiles = dict()
        self._log('\n----------------------------------------')
        self._log('Reading profiles:')
        for f in glob.glob(self.profiledir + '*.profile'):
            profname = os.path.split(re.sub('\.profile$', '', f))[1]
            self._log('reading profile: "' + f + '"')
            profile = self.readProfile(profname)
            self._log('adding "' + f + '" as profile "' + profile['ssid'] + '"')
            profiles[profile['ssid']] = profile
        return profiles


    def updateProfile(self, profname, params):
        if not os.access(f, os.W_OK):
            self._log('Unable to write to ' + f + ', so \"' + profname + '\" was not updated')
            return
        savedsettings = []
        pf = open(os.path.join(self.profiledir, profname + '.profile'), 'r')
        for line in pf:
            savedsettings.append(line)
            for param, value in params.iteritems():
                if re.search('^' + param + '=', savedsettings[-1]):
                    savedsettings[-1] = (param + '=' + value + '\n')
                    break
        pf.close()
        pf = open(os.path.join(self.profiledir, profname + '.profile'), 'w')
        for line in savedsettings:
            pf.write(line)


    def startOlsrd(self, interface, conf):
        '''start the olsrd daemon'''
        self._log('start olsrd: ')
        cmd = ['/usr/sbin/olsrd', '-i', interface, '-f', conf]
        self._log(" ".join([x for x in cmd]))
        p = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            self._log('stdout: ' + out)
        if err:
            self._log('stderr: ' + err)


    def stopOlsrd(self):
        '''stop the olsrd daemon'''
        self._log('stop olsrd')
        cmd = ['/usr/bin/killall', '-v', 'olsrd']
        self._log(" ".join([x for x in cmd]))
        p = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            self._log('stdout: ' + out)
        if err:
            self._log('stderr: ' + err)


    def fallbackConnect(self, profileid):
        if not os.path.exists(os.path.join(self.profiledir, profileid + '.wpasupplicant')):
            self._log('No wpasupplicant config file available! Stopping...')
            return 1 ##And/or raise error
        profile = self.readProfile(profileid)
        interface = subprocess.check_output(['iw', 'dev']).split()
        interface = interface[interface.index('Interface') + 1]
        ip = profile['ip']
        self._log('Putting network manager to sleep:')
        if 'connected' in subprocess.check_output(['nmcli', 'nm', 'status']): #Connected in this case means "active," not just "connected to a network"
            print subprocess.check_call(['/usr/bin/nmcli', 'nm', 'sleep', 'true'])
        print subprocess.check_call(['/usr/bin/pkill', '-9', 'wpa_supplicant'])
        print subprocess.check_call(['/sbin/ifconfig', interface, 'down'])
        time.sleep(2)
        ##Check for existance of replacement binary
        self._log('Starting replacement wpa_supplicant with profile ' + profileid + ', interface ' + interface + ', and ip address ' + ip + '.')
        subprocess.Popen(['/usr/bin/commotion_wpa_supplicant', '-Dnl80211', '-i' + interface, '-c' + os.path.join(self.profiledir, profileid + '.wpasupplicant')])
        time.sleep(2)
        self.startOlsrd(interface, profile['conf'])
        time.sleep(2)
        print subprocess.check_call(['/sbin/ifconfig', interface, 'up', ip, 'netmask', '255.0.0.0'])

