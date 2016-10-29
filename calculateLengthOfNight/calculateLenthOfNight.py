#!/usr/bin/env python

import os
import sys
import time
import numpy
from scipy import stats
from optparse import OptionParser

class CalculateLenghtOfNight:

  def __init__(self,
               inputFile,
               shortestNightHours       = 6,
               minLightLevel            = 0,
               maxLightLevel            = 1000,
               lightThresholdPercentage = 33.0):
    """
    Initialize class and read in the plist from the given file.
    """
    self.inputFile                = inputFile
    self.shortestNightHours       = shortestNightHours
    self.minLightLevel            = minLightLevel
    self.maxLightLevel            = maxLightLevel
    self.lightThresholdPercentage = lightThresholdPercentage

  def printScalars(self):
    print "self.inputFile                = '%s'" %  self.inputFile                
    print "self.shortestNightHours       =", self.shortestNightHours       
    print "self.minLightLevel            =", self.minLightLevel            
    print "self.maxLightLevel            =", self.maxLightLevel            
    print "self.lightThresholdPercentage =", self.lightThresholdPercentage 

  def printData(self):

    for i in range(len(self.dateStampData)):
      print "dateStamp, %s, milliseconds, %s, lightLevel, %s, lightLevelMin, %s, lightLevelMax, %s, lightThreshold, %s" % \
              (self.dateStampData[i], self.millisecondsData[i], self.lightLevelData[i], \
              self.lightLevelMinData[i], self.lightLevelMaxData[i], self.lightThresholdData[i])

  def readDataFile(self):
    # Data line:
    #          0,        1,      2,         3,          4,   5,             6, 7,             8,   9,             10,  11
    # 2015-08-21, 12:00:47, millis, 138662374, lightLevel, 984, lightLevelMin, 0, lightLevelMax, 988, lightThreshold, 100

    millisecondsPrevious   = None
    lightLevelPrevious     = None
    lightLevelMinPrevious  = None
    lightLevelMaxPrevious  = None
    lightThresholdPrevious = None

    self.dateStampData      = []
    self.millisecondsData   = []
    self.lightLevelData     = []
    self.lightLevelMinData  = []
    self.lightLevelMaxData  = []
    self.lightThresholdData = []
    
    inputStream = open(self.inputFile)
    for line in inputStream:
      lineArray = line.split(",")
      lineArrayLength = len(lineArray)
      if lineArrayLength > 1:
        dateStamp = lineArray[0].strip() + ":" + lineArray[1].strip()
      else:
        continue # Just skip this line
      if lineArrayLength > 3:
        milliseconds = int(lineArray[3].strip())/1.0e3/3600.
        millisecondsPrevious   = milliseconds
      else:
        milliseconds = millisecondsPrevious
      if lineArrayLength > 5:
        lightLevel = int(lineArray[5].strip())
        lightLevelPrevious     = lightLevel
      else:
        lightLevel = lightLevelPrevious
      if lineArrayLength > 7:
        lightLevelMin = int(lineArray[7].strip())
        lightLevelMinPrevious  = lightLevelMin
      else:
        lightLevelMin = lightLevelMinPrevious
      if lineArrayLength > 9:
        lightLevelMax = int(lineArray[9].strip())
        lightLevelMaxPrevious  = lightLevelMax
      else:
        lightLevelMax = lightLevelMaxPrevious
      if lineArrayLength > 11:
        lightThreshold = int(lineArray[11].strip())
        lightThresholdPrevious = lightThreshold
      else:
        lightThreshold = lightThresholdPrevious

      self.dateStampData  .append(dateStamp)
      self.millisecondsData  .append(milliseconds)
      self.lightLevelData    .append(lightLevel)
      self.lightLevelMinData .append(lightLevelMin)
      self.lightLevelMaxData .append(lightLevelMax)
      self.lightThresholdData.append(lightThreshold)

    inputStream.close()

    msg =\
        "len(self.dateStampData     ) = %s, " % len(self.dateStampData  ) + \
        "len(self.millisecondsData  ) = %s, " % len(self.millisecondsData  ) + \
        "len(self.lightLevelData    ) = %s, " % len(self.lightLevelData    ) + \
        "len(self.lightLevelMinData ) = %s, " % len(self.lightLevelMinData ) + \
        "len(self.lightLevelMaxData ) = %s, " % len(self.lightLevelMaxData ) + \
        "len(self.lightThresholdData) = %s"   % len(self.lightThresholdData)

    assert len(self.dateStampData) == len(self.millisecondsData) == len(self.lightLevelData) == \
           len(self.lightLevelMinData) == len(self.lightLevelMaxData) == len(self.lightThresholdData), \
           "Data array lengths did not match. %s" % msg
  
  def fillMissingData(self):
    pass

  def createSlopeData(self):

    numSamplePoints = 10
    for i in range(len(self.dateStampData)-numSamplePoints-1):
      x = numpy.array(self.millisecondsData[i:i+10])
      y = numpy.array(self.lightLevelData[i:i+10])
      slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
      print "slope, %s, intercept, %s, r_value, %s, p_value, %s, std_err, %s" % (slope, intercept, r_value, p_value, std_err)

    
  def createSegmentData(self):

    # Start at beginning of slopeData
    #   If slope is small, deviation is small and values below threshold
    #     If new night segment
    #        record start time
    #        flag as night segment
    #     else
    #        update segment length
    #   else
    #     If new day segment
    #        record start time
    #        flag as day segment
    #     else
    #        update segment length
    pass

  def smoothSegmentData(self):

    # Remove all segments less than one hour
    # Start at segment two.
    # If less than one hour
    #   make the same as previous segment by
    #   deleting segment
    #   extend length of previous segment by deleted length 

    pass
    

  def findLenghOfNight(self):

    self.createSegmentData()
    self.smoothSegmentData()

    # NightDayTimes
    # Type (0-Night, 1-Day), StartTime, Length
      
def setupCmdLineArgs(cmdLineArgs):
  usage = "usage: %prog [-v|--verbose] input_file"
          
  parser = OptionParser(usage)
  help="Verbose mode."
  parser.add_option("-v", "--verbose",
                    action="store_true", default=False,
                    dest="verbose",
                    help=help)


  (cmdLineOptions, cmdLineArgs) = parser.parse_args(cmdLineArgs)

  if cmdLineOptions.verbose:
    print "cmdLineOptions.verbose = '%s'" % cmdLineOptions.verbose
    for index in range(0,len(cmdLineArgs)):
      print "cmdLineArgs[%s] = '%s'" % (index, cmdLineArgs[index])

  if len(cmdLineArgs) != 1:
    parser.error("Must specify an input file on the command line.")

  return (cmdLineOptions, cmdLineArgs)

def main(cmdLineArgs):

  (clo, cla) = setupCmdLineArgs(cmdLineArgs)

  inputFile        = cla[0]

  myCLON = CalculateLenghtOfNight(inputFile)
  if clo.verbose:
    myCLON.printScalars()

  # Read in data
  myCLON.readDataFile()

  if clo.verbose:
    myCLON.printData()

  myCLON.createSlopeData()

  # Find legth of night


if (__name__ == '__main__'):
  main(sys.argv[1:])
    
