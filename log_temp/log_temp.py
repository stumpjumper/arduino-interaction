#!/usr/bin/python3
#
# Post data to thingspeak using thingspeak lib
# https://github.com/mchwalisz/thingspeak
#
 
from time import localtime, strftime, sleep
import thingspeak
import ds18b20
 
# ThingSpeak keys
channel_id = "xxxxxx"
write_key  = "xxxxxxxxxxxxxxxxx"
 
# Temperature sensors ID's
EXT_ID = "28-041591f7d8ff"
INT_ID = "28-0015220d64ee"
 
FREQUENCY = 5 * 60 # Record data at this frequency
 
def publish(channel):
 
    # Get temperatures
    ext_temp = ds18b20.gettemp(EXT_ID)
    int_temp = ds18b20.gettemp(INT_ID)
 
    try:
        response = channel.update({1:ext_temp, 2:int_temp})
        print ext_temp
        print int_temp
        print strftime("%a, %d %b %Y %H:%M:%S", localtime())
        print response
    except:
        print "connection failed"
 
if __name__ == "__main__":
    
  channel = thingspeak.Channel(id=channel_id,write_key=write_key)
  while True:
    '''
      Send chanels to thingspeak
      '''
          
       publish(channel)
       sleep(FREQUENCY)
