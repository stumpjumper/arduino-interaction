#!/usr/bin/env python

import serial
import os
import sys
import time
import ast
import thingspeak
from optparse import OptionParser

modeMap = {'O':0,'B':1,'E':2,'N':3,'P':4,'M':5,'D':6}

(execDirName,execName) = os.path.split(sys.argv[0])
execBaseName = os.path.splitext(execName)[0]
defaultLogFileRoot = "/tmp/"+execBaseName

def setupCmdLineArgs(cmdLineArgs):
  usage = """\
usage: %prog [-h|--help] [Options] serial_port id config_file
       where:
         -h|--help to see Options

         serial_port =
           Serial port from which to read. Hint: Do a 
           "dmesg | grep tty" and look at last serial port added.
           Usually looks something like /dev/ttyACM0 or /dev/ttyUSB0
           and is at the bottom of the grep output.
         id_key = 
           The key of which dictionary to read in config_file.
           This maps the identifcation of the Aurdino to connect to.
         config_file = 
           File containing configuration data in the form of a dictionary
           where the id_key is used as described above
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

  if len(cmdLineArgs) != 3:
    parser.error("Must specify a serial port, id and config filename on the command line.")

  return (cmdLineOptions, cmdLineArgs)

def createDateStamp():
  return time.strftime("%Y-%m-%d",time.localtime())

def makeOutputStream(outputFileName):
  return open(outputFileName,'a')

def makeOutputFileName(logFileRoot, dateStamp):
  return  logFileRoot + "." + createDateStamp() + ".log"

def readConfigData(configFilename, idKey):
  with open(configFilename,'r') as configStream:
    configData = configStream.read()

  dataDict = ast.literal_eval(configData)
  assert dataDict.has_key(idKey),\
    "Could not find key '%s' in file '%s'. Keys in file are '%s'" %\
    (idKey, configFilename, dataDict.keys())

  return dataDict[idKey]

def main(cmdLineArgs):
  (clo, cla) = setupCmdLineArgs(cmdLineArgs)
  serialPort     = cla[0]
  idKey          = cla[1]
  configFilename = cla[2]
  logFileRoot    = clo.logFileRoot
  
  if clo.verbose or clo.noOp:
    print "verbose        =", clo.verbose
    print "noOp           =", clo.noOp
    print "serialPort     =", serialPort
    print "idKey          =", idKey
    print "configFilename =", configFilename
    print "logFileRoot    =", logFileRoot

  dataDict = readConfigData(configFilename, idKey)

  if clo.verbose or clo.noOp:
    print "dataDict:"
    print dataDict

  if clo.noOp:
    sys.exit(0)

  channel_id = dataDict["channel_id"]
  write_key  = dataDict["write_key"]
  frequency  = dataDict["update_frequency"]

  channel = thingspeak.Channel(id=channel_id,write_key=write_key)

  currentDateStamp = None
  outputStream     = None

  ser = serial.Serial(serialPort,115200)
  time.sleep(5)
  localFrequency = 5

  while True:
    ser.write('?')
    buffer = ser.read(ser.inWaiting())
    lines = buffer.split('\r\n')
    for line in lines:
      if line:
        print '%s' % line.strip()
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
            channelKeys = [1,2,5,6]
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
              response = channel.update(channelDict)
              print response
            except Exception, e:
              print "channel.update(channelDict) failed:"
              try:
                print str(e)
              except:
                print "  Sorry, could not print channel.update() error. Continuing..."
          except Exception, e:
            print "Creation of channelDict failed:"
            try:
              print str(e)
            except:
              print "  Sorry, could not print creation error.  Continuing..."

    print "Sleeping for %s seconds" % localFrequency
    time.sleep(localFrequency)

  outputStream.close()

if (__name__ == '__main__'):
  main(sys.argv[1:])
