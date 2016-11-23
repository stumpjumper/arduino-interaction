#!/usr/bin/env python

# From here:
# http://stackoverflow.com/questions/492519/timeout-on-a-function-call

import signal
import time

class MySignalCaughtException(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

def handler(signum, frame):
  print "Forever is over!"
  raise MySignalCaughtException("Signal caught")

def loop_forever():
  import time
  while 1:
    print "sec"
    time.sleep(1)

# Register the signal function handler
signal.signal(signal.SIGALRM, handler)

# Define a timeout for your function
signal.alarm(10)

try:
  loop_forever()
except MySignalCaughtException, e: 
  print "Caught MySignalCaughtException"
  print "Msg:", e
