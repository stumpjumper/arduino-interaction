#!/usr/bin/env python

import serial
import os
import sys
import time
import ast
import thingspeak

# ThingSpeak keys
channel_id = "176582"
write_key  = "VHTF9TVYRZCCPY77"

frequency = 60 # Record data at this frequency in seconds

modeMap = {'O':0,'B':1,'E':2,'N':3,'P':4,'M':5,'D':6}

def createDateStamp():
  return time.strftime("%Y-%m-%d",time.localtime())

def makeOutputStream(outputFileName):
  return open(outputFileName,'a')

def makeOutputFileName(outputFileRoot, dateStamp):
  return  outputFileRoot + "." + createDateStamp() + ".log"

def main(cmdLineArgs = sys.argv):

  channel = thingspeak.Channel(id=channel_id,write_key=write_key)

  currentDateStamp = None
  outputStream     = None

  if len(cmdLineArgs) != 2:
    print >>sys.stderr, "readArdiono: Need two args: <serial_port> <output_file_root>"
    print >>sys.stderr, "             Example: readArdiono /dev/cu.usbmodemfd121 lucky7ToThingSpeak"
    print >>sys.stderr, "             Produces the log file lucky7ToThingSpeak.2015-08-17.log on Aug. 17, 2015"
    sys.exit(1)

  serialPort = cmdLineArgs[0]
  outputFileRoot = cmdLineArgs[1]

  print "serialPort     =", serialPort    
  print "outputFileRoot =", outputFileRoot

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
            outputFileName = makeOutputFileName(outputFileRoot, createDateStamp())
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
            channelKeys = [1,2,5,6]
            channelDict = {1:outputDict[channelKeys[0]][0],
                           2:outputDict[channelKeys[1]][0],
                           3:outputDict[channelKeys[2]][0],
                           4:outputDict[channelKeys[3]][0],
                           5:outputDict['v'],
                           6:outputDict['p'],
                           7:modeMap[outputDict['m']],
                           8:outputDict['lN']}
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
    
