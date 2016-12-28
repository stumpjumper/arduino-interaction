#!/usr/bin/env python

import sys
import re
from optparse import OptionParser
from subprocess import call, check_call, check_output, CalledProcessError

class TalkToScreen(object):

  historyLengthDefault = 5000

  def __init__ (self):
    self.screenName = None
    self.historyLength = TalkToScreen.historyLengthDefault
    self.verbose = False

  @classmethod
  def createWithName(cls,screenName):
    obj = cls()
    obj.screenName = screenName

    return obj

  def verboseModeOn(self):
    self.verbose = True

  def verboseModeOff(self):
    self.verbose = False

  def getCmdPrefix(self):
    assert self.screenName, "startScreen() called before self.screenName set"

    cmdPrefix = ["screen","-S",self.screenName,"-X","stuff"]
    return cmdPrefix

  def startScreen(self):
    assert self.screenName, "startScreen() called before self.screenName set"

    if self.screenAlreadyRunning():
      print >>sys.stderr,\
            "Screen with name '%s' already exists." % self.screenName,
      print >>sys.stderr,\
            "Starting new screen with same name is not allowed."
      call(["screen","-ls",self.screenName])
      return

    # -h = Specifies how many lines of history to save
    # -d -m = Start screen in detached mode
    # S = Start a screen with the given name
    cmd = "screen -h %s -dmS %s" % (self.historyLength, self.screenName)
    if self.verbose:
      print "cmd: %s" % cmd
    cmdList = cmd.split()
    
    check_call(cmdList)

  def executCmdInScreen(self, cmd):
    if not self.screenAlreadyRunning():
      print >>sys.stderr,\
            "Screen with name '%s' does not exists." % self.screenName,
      print >>sys.stderr,\
            "Screen must exist to run command inside it."
      print >>sys.stderr, "Screen list:"
      TalkToScreen.printScreenList(self.verbose, sys.stderr)      
      return
    
    cmdPrefix = self.getCmdPrefix()

    if cmd[-1:] != "\n":
      cmd += "\n"

    fullCmdList = cmdPrefix + [cmd]
    if self.verbose:
      print "cmd: %s" % fullCmdList

    check_call(fullCmdList)

  def exitScreen(self):
    assert self.screenName, "startScreen() called before self.screenName set"

    self.executCmdInScreen("exit")

  @staticmethod
  def getScreenList(verbose=False):

    cmdList = ["screen","-ls"]
    if verbose:
      print "cmd: %s" % cmdList

    output = None
    try:
      output = check_output(cmdList)
    except CalledProcessError as e:
      output = e.output

    return output

  @staticmethod
  def printScreenList(verbose=False, stream=sys.stdout):
    
    output = TalkToScreen.getScreenList(verbose)
    print >>stream, output

  def screenAlreadyRunning(self):
    assert self.screenName, "startScreen() called before self.screenName set"

    output = TalkToScreen.getScreenList(self.verbose)

    screenExists = False
    for line in output.splitlines():
      m = re.search('\d+\.%s'%self.screenName,line)
      if m:
        if self.verbose:
          print "Found screen:"
          print line
        screenExists = True
        break

    return screenExists

def setupCmdLineArgs(cmdLineArgs):
  usage =\
"""
usage: %prog [-h|--help] [options] [screen_name]
       where:
         -h|--help to see options

         screen_name =
          The name of the screen to start, send commands to, or
          exit.

       Rules: -s, -r and -e can be used together in any combination.  They 
       will be executed in the order: -s, all -r's, then -e.

       Note: A screen_name must be specified if -s, -r or -e is used.
"""

  parser = OptionParser(usage)
                       
  help="verbose mode."
  parser.add_option("-v", "--verbose",
                    action="store_true", default=False,
                    dest="verbose",
                    help=help)

  help="List running screens"
  parser.add_option("-l", "--list",
                    action="store_true", default=False,
                    dest="listScreens",
                    help=help)

  help="Start a screen with given name"
  parser.add_option("-s", "--start",
                    action="store_true", default=False,
                    dest="startScreen",
                    help=help)

  help="Run command in named screen. You can use multiple -r arguments "+\
        "to run multiple commands. NOTE: Quote the command if it contains "+\
        "spaces."
  parser.add_option("-r", "--run",
                    action="append", type="string", 
                    default=None,
                    dest="runCmd",
                    help=help)

  help="Exit named screen"
  parser.add_option("-e", "--exit",
                    action="store_true", default=False,
                    dest="exitScreen",
                    help=help)

  (cmdLineOptions, cmdLineArgs) = parser.parse_args(cmdLineArgs)
  clo = cmdLineOptions

  if cmdLineOptions.verbose:
    print "cmdLineOptions:",cmdLineOptions
    for index in range(0,len(cmdLineArgs)):
      print "cmdLineArgs[%s] = '%s'" % (index, cmdLineArgs[index])

  if (clo.startScreen or clo.runCmd or clo.exitScreen) and len(cmdLineArgs) != 1:
    parser.error("If -s, -r or -e are specified, a screen name must be"+\
                 " given on the command line")

  return (cmdLineOptions, cmdLineArgs)

def main(cmdLineArgs):
  (clo, cla) = setupCmdLineArgs(cmdLineArgs)

  if (clo.startScreen or clo.runCmd or clo.exitScreen):
    screenName = cla[0]

    screen = TalkToScreen.createWithName(screenName)

    if clo.verbose:
      screen.verboseModeOn()

    if clo.startScreen:
      screen.startScreen()

    if clo.runCmd:
      for cmd in clo.runCmd:
        screen.executCmdInScreen(cmd)

    if clo.exitScreen:
      screen.exitScreen()

  if clo.listScreens:
    TalkToScreen.printScreenList(clo.verbose)

if (__name__ == '__main__'):
  main(sys.argv[1:])
