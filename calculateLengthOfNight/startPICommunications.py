#!/usr/bin/env python

import sys
from optparse import OptionParser

from talkToScreen import TalkToScreen

def setupCmdLineArgs(cmdLineArgs):
  usage =\
"""
usage: %prog [-h|--help] [options] serial_port screen_name
       where:
         -h|--help to see options

         serial_port =
          Serial port target RaspberryPi is connected to.

         screen_name =
          The name of the screen in which to run the communication program
"""

  parser = OptionParser(usage)
                       
  help="verbose mode."
  parser.add_option("-v", "--verbose",
                    action="store_true", default=False,
                    dest="verbose",
                    help=help)

  help="No operation, just echo commands"
  parser.add_option("-n", "--noOp",
                    action="store_true", 
                    default=False,
                    dest="noOp",
                    help=help)

  (cmdLineOptions, cmdLineArgs) = parser.parse_args(cmdLineArgs)
  clo = cmdLineOptions

  if cmdLineOptions.verbose:
    print "cmdLineOptions:",cmdLineOptions
    for index in range(0,len(cmdLineArgs)):
      print "cmdLineArgs[%s] = '%s'" % (index, cmdLineArgs[index])

  if len(cmdLineArgs) != 2:
    parser.error("A serial port and screen name must be"+\
                 " given on the command line")

  return (cmdLineOptions, cmdLineArgs)

def main(cmdLineArgs):
  (clo, cla) = setupCmdLineArgs(cmdLineArgs)

  (clo, cla) = setupCmdLineArgs(cmdLineArgs)

  serialPort = cla[0]
  screenName = cla[1]

  if clo.verbose:
    print "serialPort =", serialPort
    print "screenName =", screenName


  if clo.noOp:
    print "Would be creating TalkToScreen object using name '%s'" % screenName
  else:
    screen = TalkToScreen.createWithName(screenName)

  if not clo.noOp:
    if screen.screenAlreadyRunning():
      print >>sys.stderr, "Screen with name '%s' already running.  Exiting..."
      return

  if clo.noOp:
    print "Would be starting screen with name '%s'" % screenName
  else:
    if clo.verbose:
      print "Starting screen with name '%s'" % screenName
    screen.startScreen()

  cmd = "lucky7toThingSpeak %s" % serialPort

  if clo.noOp:
    print "Would be executing the following in screen '%s':\n" % screenName, cmd
  else:
    if clo.verbose:
      print "Executing the following command in screen '%s':\n" % screenName, cmd
    screen.executCmdInScreen(cmd)

if (__name__ == '__main__'):
  main(sys.argv[1:])