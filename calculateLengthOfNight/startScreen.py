#!/usr/bin/env python

import sys
from subprocess import call, check_call

def main(cmdLineArgs):
#  check_call("screen -h 5000 -dmS my_screen".split())

  check_call(["screen","-S","my_screen","-X","stuff","date\n"])
  check_call(["screen","-S","my_screen","-X","stuff","echo hello world\n"])
  returnValue = check_call(["screen","-S","my_screen","-X","stuff","echo hello world again\n"])
  print "returnValue = ", returnValue
  

if (__name__ == '__main__'):
  main(sys.argv[1:])
