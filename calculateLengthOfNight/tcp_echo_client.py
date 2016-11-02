#!/usr/bin/env python

# From https://pymotw.com/2/socket/tcp.html

import socket
import sys

if len(sys.argv) != 2:
  print >>sys.stderr, "Usage: tcp_echo_client.py \"<message to send>\""
  sys.exit(1)

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 10000)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

try:

  # Send data
  message = sys.argv[1]
  print >>sys.stderr, 'sending "%s"' % message
  sock.sendall(message)

  # Look for the response
  amount_received = 0
  amount_expected = len(message)

  while amount_received < amount_expected:
    data = sock.recv(16)
    amount_received += len(data)
    print >>sys.stderr, 'received "%s"' % data

finally:
  print >>sys.stderr, 'closing socket'
  sock.close()
