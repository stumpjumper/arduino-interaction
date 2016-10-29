#!/usr/bin/env python

import serial
import os
import sys
import time


def createDateStamp():
  return time.strftime("%Y-%m-%d",time.localtime())

def makeOutputStream(outputFileName):
  return open(outputFileName,'a')

def makeOutputFileName(outputFileRoot, dateStamp):
  return  outputFileRoot + "." + createDateStamp() + ".log"

def main(cmdLineArgs = sys.argv):

  currentDateStamp = None
  outputStream     = None

  if len(cmdLineArgs) != 2:
    print >>sys.stderr, "readArdiono: Need two args: <serial_port> <output_file_root>"
    print >>sys.stderr, "             Example: readArdiono /dev/cu.usbmodemfd121 readArduino"
    print >>sys.stderr, "             Produces the log file readArduino.2015-08-17.log on Aug. 17, 2015"
    sys.exit(1)

  serialPort = cmdLineArgs[0]
  outputFileRoot = cmdLineArgs[1]

  print "serialPort     =", serialPort    
  print "outputFileRoot =", outputFileRoot

  ser = serial.Serial(serialPort,115200)

  while True:
    buffer = ser.read(ser.inWaiting())
    lines = buffer.split('\r\n')
    for line in lines:
      if line:
        print '%s' % line.strip()
        if line[0:7] == "millis,":
          if currentDateStamp != createDateStamp():
            currentDateStamp = createDateStamp()
            outputFileName = makeOutputFileName(outputFileRoot, createDateStamp())
            print "New outputfile = '%s'" % outputFileName
            if outputStream:
              outputStream.close()
            outputStream = makeOutputStream(outputFileName)
          msg = "%s, %s" % (time.strftime("%Y-%m-%d, %H:%M:%S",time.localtime()), line)
          print msg
          print >>outputStream , msg
          outputStream.flush()
    time.sleep(1)

  outputStream.close()

if (__name__ == '__main__'):
  main(sys.argv[1:])
    
