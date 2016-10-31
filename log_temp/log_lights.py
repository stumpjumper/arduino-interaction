#!/usr/bin/python
#
# Post data to thingspeak using thingspeak lib
# https://github.com/mchwalisz/thingspeak
#

from time import localtime, strftime, sleep
import thingspeak

# ThingSpeak keys
channel_id = "176582"
write_key  = "VHTF9TVYRZCCPY77"

FREQUENCY = 60 # Record data at this frequency

counter = 0

def publish(channel):
    
  global counter
#-#    # Get temperatures
#-#    ext_temp = ds18b20.gettemp(EXT_ID)
#-#    int_temp = ds18b20.gettemp(INT_ID)

  try:
    print "counter =", counter
    print strftime("%a, %d %b %Y %H:%M:%S", localtime())
    response = channel.update({1:counter})
    print response
    counter += 1
  except:
    raise
    print "connection failed"
 
if __name__ == "__main__":
    
  channel = thingspeak.Channel(id=channel_id,write_key=write_key)
  while True:
    '''
    Send chanels to thingspeak
    '''
    publish(channel)
    sleep(FREQUENCY)
