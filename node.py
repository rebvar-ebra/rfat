from datetime import date
import threading
from threading import Lock
import socket
import json
import hashlib
import time
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 10000)
print('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)

try:

    # Send data
    message = b'This is our message.This is our messageThis is our messageThis is our messageThis is our message '
    #message= input("Type your message:\n")
    print('sending {!r}'.format(message))
    sock.sendall(message)

    # Look for the response
    amount_received = 0
    amount_expected = len(message)

    while amount_received < amount_expected:
        data = sock.recv(1024)
        amount_received += len(data)
        print('received {!r}'.format(data))

finally:
    print('closing socket')
    sock.close()

""" ser=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address=('localhost',10000)
print('connecting to {} port {}'.format(*server_address))
try:
    message = b'This is our message. It is very long but will only be transmitted in chunks of 16 at a time'
    
    #print(f"sending   {message}")
    print('sending {!r}'.format(message))
    ser.sendall(message)
    amount_recive= 0
    amount_expect=len(message)
    
    while amount_recive < amount_expect:
        data=ser.recv(16)
        amount_recive+=len(data)
        print(f"recived {data}")
        
finally:
    print(f"Closing socket")
    ser.close() """