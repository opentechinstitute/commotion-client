#!/usr/bin/python

import commotionc
import subprocess
import sys

profile = sys.argv[1]
operation = sys.argv[2]

if operation == 'up':
    commotion = commotionc.CommotionCore('/tmp/commotion_fallback.log')
    commotion.fallbackConnect(sys.argv[1])

if operation == 'down':
    print subprocess.call(['pkill', '-9', 'commotion_wpa'])
    print subprocess.call(['pkill', '-9', 'olsrd'])
    print subprocess.call(['nmcli', 'nm', 'sleep', 'false'])
    print subprocess.call(['rfkill', 'block', 'wifi'])
    print subprocess.call(['rfkill', 'unblock', 'wifi'])

# Add full up/down/status logic (if up, then; if down, then)
# Add ArgumentParser logic
