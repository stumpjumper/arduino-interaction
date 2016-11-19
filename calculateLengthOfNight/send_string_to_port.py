#!/usr/bin/env python

import serial
import os
import sys
import readline
from optparse import OptionParser


(execDirName,execName) = os.path.split(sys.argv[0])
execBaseName = os.path.splitext(execName)[0]
defaultLogFileRoot = "/tmp/"+execBaseName

def setupCmdLineArgs(cmdLineArgs):
  usage = """\
usage: %prog [-h|--help] [Options] serial_port 
       where:
         -h|--help to see Options

         serial_port =
           Serial port from which to read. Hint: Do a 
           "grep dmesg | grep tty" and look at last serial port added.
           Usually looks something like /dev/ttyACM0 or /dev/ttyACM1.
"""
  parser = OptionParser(usage)
  help="Verbose mode."
  parser.add_option("-v", "--verbose",
                    action="store_true", 
                    default=False,
                    dest="verbose",
                    help=help)
  help="No operation, just read data file and echo it"
  parser.add_option("-n", "--noOp",
                    action="store_true", 
                    default=False,
                    dest="noOp",
                    help=help)

  (cmdLineOptions, cmdLineArgs) = parser.parse_args(cmdLineArgs)

  if cmdLineOptions.verbose:
    print "cmdLineOptions.verbose = '%s'" % cmdLineOptions.verbose
    for index in range(0,len(cmdLineArgs)):
      print "cmdLineArgs[%s] = '%s'" % (index, cmdLineArgs[index])

  if len(cmdLineArgs) != 1:
    parser.error("Must specify a serial port on the command line.")

  return (cmdLineOptions, cmdLineArgs)

def readInputFromTerminal(prompt,timeout):
  inputLine=None
  print prompt,
  sys.stdout.flush()
  rlist, _, _ = select([sys.stdin], [], [], timeout)
  if rlist:
    inputLine = sys.stdin.readline()
    print "Read: ", inputLine
  else:
    print "No input. Moving on..."
  return inputLine

def main(cmdLineArgs):
  (clo, cla) = setupCmdLineArgs(cmdLineArgs)
  serialPort     = cla[0]
  
  if clo.verbose or clo.noOp:
    print "verbose        =", clo.verbose
    print "noOp           =", clo.noOp
    print "serialPort     =", serialPort

  if clo.noOp:
    sys.exit(0)

  ser = serial.Serial(serialPort,115200)
  time.sleep(5)
  localFrequency = 5

  while True:
    try:
      serialInput = readInputFromTerminal('Enter your input: ')
      ser.write('serialInput')
      buffer = ser.read(ser.inWaiting())
      lines = buffer.split('\r\n')
      for line in lines:
        if line:
          print '%s' % line.strip()
          
    except KeyboardInterrupt:
        print >>sys.stderr, "Caught KeyboardInterrupt. Exiting..."

    print "Sleeping for %s seconds" % localFrequency
    time.sleep(localFrequency)

  outputStream.close()

if (__name__ == '__main__'):
  main(sys.argv[1:])
