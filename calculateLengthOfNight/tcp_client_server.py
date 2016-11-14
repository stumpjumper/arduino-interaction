#!/usr/bin/env python

# From https://pymotw.com/2/socket/tcp.html

import socket
import sys

class TCPClientServer(object):

  def __init__(self):
    self.sock           = None
    self.sock2          = None
    self.connection     = None
    self.client_address = None
    self.serverName     = None
    self.serverPort     = None
    self.amServer       = False

  def setServerNameAndPort(self,serverName,serverPort):
    self.serverName     = serverName
    self.serverPort     = serverPort

  @classmethod
  def setupServer(cls,serverName,serverPort):
    obj = cls()
    obj.setServerNameAndPort(serverName,serverPort)
    obj.amServer = True
    obj.establishServer()
    return obj

  @classmethod
  def setupClient(cls,serverName,serverPort):
    obj = cls()
    obj.setServerNameAndPort(serverName,serverPort)
    obj.establishClient()
    return obj

  def establishServerAddress(self):

    assert self.serverName != None, \
           "self.serverName must be set before establishServerAddress() is called"
    assert self.serverPort != None, \
           "self.serverPort must be set before establishServerAddress() is called"
    
    # Create a TCP/IP socket
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Get server address
    serverAddress = (self.serverName, self.serverPort)
    print >>sys.stderr, 'starting up on "%s" port "%s"' % serverAddress

    return serverAddress


  def establishServer(self):

    serverAddress = self.establishServerAddress()
    
    # Bind the socket to the port
    self.sock.bind(serverAddress)
    
    # Listen for incoming connections
    self.sock.listen(1)

  def establishClient(self):

    serverAddress = self.establishServerAddress()
    
    # Connect the socket to the port where the server is listening
    self.sock.connect(serverAddress)
    self.sock2 = self.sock

  def sendMsgPart(self,msg):
    assert self.sock2 != None, \
           "Socket must be created before recieveAndRespond() is called"

    totalSent = 0
    msgLength = len(msg)
    while totalSent < msgLength:
      sent = self.sock2.send(msg[totalSent:])
      if sent == 0:
        raise RuntimeError("0 bytes sent. Socket connection broken.")
      totalSent = totalSent + sent

  def recvMsgPart(self,msgLength):
    chunks = []
    bytesRecvd = 0
    while bytesRecvd < msgLength:
      chunk = self.sock2.recv(min(msgLength - bytesRecvd, 2048))
      if chunk == '':
        raise RuntimeError("0 bytes recieved. Socket connection broken.")
      chunks.append(chunk)
      bytesRecvd = bytesRecvd + len(chunk)

    return ''.join(chunks)
  
  def sendMsg(self,msg):
    msgLength = len(msg)
    assert msgLength < 9999, \
           "Message sent via sendMsg must be less than 9999 characters. " +\
           "Message length = %s characters" % msgLength
    msgLength = str(msgLength)
    msgLength = str(msgLength)
    msgLength = msgLength.rjust(4)
    self.sendMsgPart(msgLength + msg)

  def recvMsg(self):
    if  self.amServer:
      # Wait for a connection
      print >>sys.stderr, 'waiting for a connection'
      self.connection, self.client_address = self.sock.accept()
      print >>sys.stderr, 'connection from', self.client_address
      self.sock2 = self.connection
    msgLength = self.recvMsgPart(4)
    msgLength = int(msgLength)
    msg = self.recvMsgPart(msgLength)
    return msg

  def shutdownAndClose(self):
    if not self.sock2:
      return
    
    print >>sys.stderr, 'shuting down socket'
    self.sock2.shutdown(socket.SHUT_RDWR)
    print >>sys.stderr, 'closing socket'
    self.sock2.close()


class TCPArduinoServer(object):

  def __init__(self):
    pass


  def processMsg(self,msg):
    response = None
    if   "?" == msg:
      response = "Got ?"
    elif "s" == msg:
      response = "Got s"
    elif "c" == msg:
      response = "Got c"
    else:
      response = "Unrecognized message: '%s'" % msg
      
    return  response

def main(cmdLineArgs = sys.argv[1:]):

  tcpClientServer = None
  hostname = 'localhost'
  port     = 10000
  
  assert len(cmdLineArgs) > 0, \
         "First arg must be 'client' or 'server'"
  socketType = cmdLineArgs[0].lower()
  assert socketType == "client" or socketType == "server", \
         "First arg must be 'client' or 'server'.  Found '%s'" % socketType

  try:
    if socketType == "client":
      assert len(cmdLineArgs) > 1, \
           "Second arg must be a message"
      msg = cmdLineArgs[1]
      tcpClientServer = TCPClientServer.setupClient(hostname, port)
      tcpClientServer.sendMsg(msg)
      msg = tcpClientServer.recvMsg()
      print >>sys.stderr, "Recieved message back: '%s'" % msg
    else:
      tcpArduinoServer = TCPArduinoServer()
      tcpClientServer = TCPClientServer.setupServer(hostname, port)
      try:
        while True:
          msg = tcpClientServer.recvMsg()
          print >>sys.stderr, "Recieved Mesage:"
          print >>sys.stderr, msg
          response = tcpArduinoServer.processMsg(msg)
          print >>sys.stderr, "Response:", response
          tcpClientServer.sendMsg(response)
      except KeyboardInterrupt:
        print >>sys.stderr, "Caught KeyboardInterrupt. Exiting..."
  except:
    raise

  finally:
    print >>sys.stderr, 'shuting down and closing socket'
    if tcpClientServer:
      tcpClientServer.shutdownAndClose()
        

if (__name__ == '__main__'):
  main(sys.argv[1:])


  
  
