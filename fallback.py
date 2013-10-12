#!/usr/bin/python

import commotionc
import subprocess
import sys

profile = sys.argv[1]
operation = sys.argv[2]

if operation == 'up':
    commotion = commotionc.CommotionCore('commotion-fallback')
    commotion.fallbackConnect(sys.argv[1])

if operation == 'down':
    commotion.log('Bringing down mesh connection.  The six following lines should show return values of zero')
    commotion.log(subprocess.call(['pkill', '-9', 'commotion_wpa']))
    commotion.log(subprocess.call(['pkill', '-9', 'olsrd']))
    commotion.log(subprocess.call(['nmcli', 'nm', 'sleep', 'false']))
    commotion.log(subprocess.call(['rfkill', 'block', 'wifi']))
    commotion.log(subprocess.call(['rfkill', 'unblock', 'wifi']))

# Add full up/down/status logic (if up, then; if down, then)
# Add ArgumentParser logic
