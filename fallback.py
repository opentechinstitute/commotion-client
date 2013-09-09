#!/usr/bin/python

import sys
import commotionc

print sys.argv[1]
commotion = commotionc.CommotionCore('/tmp/commotion_fallback.log')
commotion.fallbackConnect(sys.argv[1])
exit()

# Add full up/down/status logic (if up, then; if down, then)
# Add ArgumentParser logic
