#!/usr/bin/env python

# Initialization
#
# Default behaviour- Nothing on the command line
# * This allows this script to be run using the same command line irregardless
#   of the aircraft the Arduino is controlling.
# * It is an error if the local config file cannot be found
# 1) Run command with nothing on the command line
# 2) Read config file using name defaultConfigFilename
#    - This contains a dictionary with:
#      o ID string to ID key mapping
#      o Custom configuration information for each ID key
# 3) Read local config file using name defaultLocalConfigFilename
#    - From file get serial port device
# 4) Connect to Arduino on serial port and get ID string
# 5) Using the ID string, find the correct ID key
# 6) Using ID key, get needed config information from the config dictionary
#
# Support for testing with no Arduino connected
# * It is an error if the local config file cannot be found if --idKey is not given
# 1) Run with --noArduinod flag
# 3) Also get the ID key from the local config file
# 4) Step is not needed and is skipped
#
# Things that can be given on the command line and the result
# * --configFile: Use this name instead of the default
# * --localConfigFile: Use this name instead of the default
# * --serialPort: Use this for serial port, don't look in config file
# * --idKey: Use this for idKey, don't look in config file or use ID string
# * --noArduino: Will need an idKey, will read from local config unless idKey is
#                given.  Will not do any serial port operations
# * --noOp: Will exit as soon as all configureation information is determined.
#           Will connect to Arduino unless --noArduino is given
# Note the local config file will not be read if:
# * --idKey and --serialPort are given
# * --idKey and --noArduino are given

import serial
import os
import sys
import time
import ast
import thingspeak
import signal
import select

from optparse import OptionParser

modeMap = {'O':0,'B':1,'E':2,'N':3,'P':4,'M':5,'D':6}

(execDirName,execName) = os.path.split(sys.argv[0])
execBaseName = os.path.splitext(execName)[0]
defaultLogFileRoot = "/tmp/"+execBaseName
defaultConfigFilename = "lucky7ToThingSpeak.conf"
defaultLocalConfigFilename = "serial_port.conf"

mySerial = None

class MySignalCaughtException(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

def setupCmdLineArgs(cmdLineArgs):
  usage = """\
usage: %prog [-h|--help] [options]
       where:
         -h|--help to see options
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
  help="Serial port for IO. Hint: Do a 'dmesg | grep tty' " +\
        "and look at last serial port added. Usually looks something like " +\
        "/dev/ttyACM0 or /dev/ttyUSB0and is at the bottom of the grep output. "+\
        "NOTE: if --port is given, it will override what is found in either "+\
        "the default serial port file '%s' (if it exists) or that given by "+\
        "--port_file." % defaultLocalConfigFilename
  parser.add_option("--port",
                    action="store", type="string", 
                    default=None,
                    dest="ioPort",
                    help=help)
  help ="Serial port file name.  That is, the file containing which serial port to use. "
  help+="Format is a single line in the file containing only the port, e.g. '/dev/ttyACM0'"
  help+="Default file name is '%s'. " % defaultLocalConfigFilename
  help+="NOTE: --port overrides this option"
  parser.add_option("--port_file",
                    action="store", type="string", 
                    default=defaultLocalConfigFilename,
                    dest="serialPortFilename",
                    help=help)
  help="File containing configuration data in the form of a dictionary. " +\
        "Default is '%s'." % defaultConfigFilename
  parser.add_option("--config_file",
                    action="store", type="string", 
                    default=defaultConfigFilename,
                    dest="configFilename",
                    help=help)
  help="Identifies which data to use in the configuration file, e.g. b52a"
  parser.add_option("--idKey",
                    action="store", type="string", 
                    default=idKey,
                    dest="idKey",
                    help=help)
  help="Root name of logfile.  Default is '%s', " % defaultLogFileRoot
  help+="which produces the log file '%s.2015-08-17.log'" % defaultLogFileRoot
  parser.add_option("-l", "--logfileroot",
                    action="store", type="string", 
                    default=defaultLogFileRoot,
                    dest="logFileRoot",
                    help=help)

  (cmdLineOptions, cmdLineArgs) = parser.parse_args(cmdLineArgs)

  if cmdLineOptions.verbose:
    print "cmdLineOptions.verbose = '%s'" % cmdLineOptions.verbose
    for index in range(0,len(cmdLineArgs)):
      print "cmdLineArgs[%s] = '%s'" % (index, cmdLineArgs[index])

  return (cmdLineOptions, cmdLineArgs)

def createDateStamp():
  return time.strftime("%Y-%m-%d",time.localtime())

def makeOutputStream(outputFileName):
  return open(outputFileName,'a')

def makeOutputFileName(logFileRoot, dateStamp):
  return  logFileRoot + "." + createDateStamp() + ".log"

def readLocalConfigFile(serialPortFilename):
  with open(serialPortFilename,'r') as serialPortFileStream:
    port = serialPortFileStream.read()

  assert port, "Found no data in file '%s'" % serialPortFilename

  return port.strip()

def readConfigData(configFilename,idKey):
  with open(configFilename,'r') as configStream:
    configData = configStream.read()

  dataDict = ast.literal_eval(configData)

  bannerToKeyMap = dataDict["bannerToKeyMap"]

  if not idKey:
    idKey = getIdKey(bannerToKeyMap)
  
  assert dataDict.has_key(idKey),\
    "Could not find key '%s' in file '%s'. Keys in file are '%s'" %\
    (idKey, configFilename, dataDict.keys())

  return dataDict[idKey]

def handler(signum, frame):
  raise MySignalCaughtException("Signal caught")

def getIdKey(bannerToKeyMap):
  global mySerial
  assert mySerial, "The varialble mySerial is null"
  idKey = None
  for i in range(5):
    if not idKey:
      print "Attempting to get identification line..."
      mySerial.write('i')
      buffer = mySerial.read(mySerial.inWaiting())
      lines = buffer.split('\r\n')
      for line in lines:
        if line:
          print line
          for banner in bannerToKeyMap.keys():
            if banner in line:
              idKey = bannerToKeyMap[banner]
              break
      time.sleep(3)

  assert idKey, "Could not match any banner in lines to bannerToKeyMap\n" +\
    "lines:\n%s\nbannerToKeyMap:\n%s" % (lines, bannerToKeyMap)

  print "Found idKey:", idKey
  return idKey

def readInputFromTerminal(prompt,timeout):
  inputLine=None
  print "You have %s seconds to enter input..." % timeout
  print prompt,
  sys.stdout.flush()
  rlist, _, _ = select.select([sys.stdin], [], [], timeout)
  if rlist:
    inputLine = sys.stdin.readline().strip()
    print "Read: %s\n" % inputLine
  return inputLine

def processTerminalInput(timeout):
  global mySerial
  assert mySerial, "The varialble mySerial has not yet been set"
  while True:
    inputLine = readInputFromTerminal("Command [continue, quit]: ",timeout)
    if not inputLine:
      print "\nNo input read. Moving on..."
      return
    else:
      if inputLine.lower() == 'continue':
        return
      if inputLine.lower() == 'quit':
        sys.exit(0)
      mySerial.write(inputLine)
      buffer = mySerial.read(mySerial.inWaiting())
      lines = buffer.split('\r\n')
      for line in lines:
        if line:
          print line
    timeout = 30

def setMySerial(serialPort):
  global mySerial
  assert not mySerial, "The varialble mySerial is already set"

  mySerial = serial.Serial(serialPort,115200)
    

def main(cmdLineArgs):
  global mySerial
  (clo, cla) = setupCmdLineArgs(cmdLineArgs)
  logFileRoot        = clo.logFileRoot
  configFilename     = clo.configFilename
  serialPortFilename = clo.serialPortFilename
  serialPort         = None
  
  if clo.verbose or clo.noOp:
    print "Option values:"
    print "verbose        =", clo.verbose
    print "noOp           =", clo.noOp
    print "port           =", clo.ioPort
    print "port_file      =", serialPortFilename
    print "config_file    =", configFilename
    print "idKey          =", clo.idKey
    print "logFileRoot    =", logFileRoot

  if clo.ioPort:
    serialPort = clo.ioPrt
  else:
    serialPort = readLocalConfigFile(serialPortFilename)

  if clo.verbose or clo.noOp:
    print "serial port: '%s'" serialPort

  if not idKey: # if not given idKey, must first set mySerial
    setMySerial(serialPort):
  dataDict = readConfigData(configFilename, idKey)

  if clo.verbose or clo.noOp:
    print "dataDict:"
    print dataDict

  if clo.noOp:
    sys.exit(0)

  channel_id     = dataDict["channel_id"]
  write_key      = dataDict["write_key"]
  frequency      = dataDict["update_frequency"]
  channelKeys    = dataDict["channel_keys"]

  if not mySerial:
    setMySerial(serialPort)
  time.sleep(5)
  localFrequency = 5

  channel = thingspeak.Channel(id=channel_id,write_key=write_key)

  currentDateStamp = None
  outputStream     = None

  # Register the signal function handler
  signal.signal(signal.SIGALRM, handler)

  while True:
    mySerial.write('?')
    buffer = mySerial.read(mySerial.inWaiting())
    lines = buffer.split('\r\n')
    for line in lines:
      if line:
        line = line.strip()
        print line
        if line[0] == "{":
          localFrequency = frequency
          if currentDateStamp != createDateStamp():
            currentDateStamp = createDateStamp()
            outputFileName = makeOutputFileName(logFileRoot, createDateStamp())
            print "New outputfile = '%s'" % outputFileName
            if outputStream:
              outputStream.close()
            outputStream = makeOutputStream(outputFileName)
          try:
            outputDict = ast.literal_eval(line)
          except Exception, e:
            print "'outputDict = ast.literal_eval(line)' error"
            try:
              print str(e)
            except:
              print "  Sorry, could not print ast.literal_eval()  error. Continuing..."
          print outputDict
          print >>outputStream , outputDict
          outputStream.flush()
          try:
            line = time.asctime() + " " + line
            channelDict = {1:outputDict[channelKeys[0]][0],
                           2:outputDict[channelKeys[1]][0],
                           3:outputDict[channelKeys[2]][0],
                           4:outputDict[channelKeys[3]][0],
                           5:outputDict['v'],
                           6:outputDict['p'],
                           7:modeMap[outputDict['m']],
                           8:outputDict['lN'],
                           "status":line}
            print "channelDict =", channelDict
            try:
              signal.alarm(120) # Throw MySignalCaughtException in (n) secs
              response = channel.update(channelDict)
              signal.alarm(0) # Cancel alarm
              print response
            except MySignalCaughtException, e:
              print "Signal alarm caught, channel.update(channelDict) timed out.  Continuing..."
            except Exception, e:
              print "channel.update(channelDict) failed:"
              try:
                print str(e)
                print "Continuing..."
              except:
                print "  Sorry, could not print channel.update() error. Continuing..."
          except Exception, e:
            print "Creation of channelDict failed:"
            try:
              print str(e)
              print "Continuing..."
            except:
              print "  Sorry, could not print creation error.  Continuing..."

    processTerminalInput(localFrequency)

  outputStream.close()

if (__name__ == '__main__'):
  main(sys.argv[1:])
