#!/usr/bin/env python

import sys
from optparse import OptionParser
from subprocess import call, check_call

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

    returnValue = self.checkScreen()
    if returnValue != 0:
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
    if self.checkScreen():
      print >>sys.stderr, msg
      return
    
    cmdPrefix = self.getCmdPrefix()

    if cmd[-1:] != "\n":
      cmd += "\n"

    fullCmdList = cmdPrefix.append(cmd)
    if self.verbose:
      print "cmd: %s" % cmd

    check_call(fullCmdList)

  def exitScreen(self):
    assert self.screenName, "startScreen() called before self.screenName set"

    self.executCmdInScreen("exit")

  def checkScreen(self):
    assert self.screenName, "startScreen() called before self.screenName set"

    msg = 0

    cmdList = ["screen","-ls"]
    if self.verbose:
      print "cmd: %s" % cmdList

    output = None
    try:
      output = ceck_output(cmdList)
    except CalledProcessError as e:
      output = e.output

    for line in output.splitlines():
      if self.screenName in line
      more code needed here and below, and maybe look for \d\d\d.self.screenName
      

    status = call(cmdList)
    if status != 0:
      msg = "Error found when trying to located screen session with name '%s'"\
            % self.screenName
    if status == 9:
      msg += "\nDirectory without a session."
    if status == 10:
      msg += "\nDirectory with running but not attachable sessions."

    return msg


def setupCmdLineArgs(cmdLineArgs):
  usage =\
"""
usage: %prog [-h|--help] [options] screen_name
       where:
         -h|--help to see options

         screen_name =
          The name of the screen to start, send commands to, or
          exit.

       Rules: -s, -r and -e can be used together in any combination.  They 
       will be executed in the order: -s, all -r's, then -e.
"""

  parser = OptionParser(usage)
                       
  help="verbose mode."
  parser.add_option("-v", "--verbose",
                    action="store_true", default=False,
                    dest="verbose",
                    help=help)

  help="Start a screen with given name"
  parser.add_option("-s", "--start",
                    action="store_true", default=False,
                    dest="startScreen",
                    help=help)

  help="Exit named screen"
  parser.add_option("-e", "--exit",
                    action="store_true", default=False,
                    dest="exitScreen",
                    help=help)

  help="Run command in named screen. You can use multiple -r arguments "+\
        "to run multiple commands. NOTE: Quote the command if it contains "+\
        "spaces."
  parser.add_option("-r", "--run",
                    action="append", type="string", 
                    default=None,
                    dest="runCmd",
                    help=help)

  (cmdLineOptions, cmdLineArgs) = parser.parse_args(cmdLineArgs)

  if cmdLineOptions.verbose:
    print "cmdLineOptions:",cmdLineOptions
    for index in range(0,len(cmdLineArgs)):
      print "cmdLineArgs[%s] = '%s'" % (index, cmdLineArgs[index])

  if len(cmdLineArgs) != 1:
    parser.error("A screen name must be given on the command line")

  return (cmdLineOptions, cmdLineArgs)

def main(cmdLineArgs):
  (clo, cla) = setupCmdLineArgs(cmdLineArgs)
  screenName = cla[0]

  screen = TalkToScreen.createWithName(screenName)

  if clo.verbose:
    screen.verboseModeOn()

  if clo.startScreen:
    screen.startScreen()

  if clo.runCmd:
    for cmd in runCmd:
      screen.executCmdInScreen(cmd)

  if clo.exitScreen:
    screen.exitScreen()

if (__name__ == '__main__'):
  main(sys.argv[1:])
