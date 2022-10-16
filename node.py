import socket
from message_pass import *


class Client:
    def __init__(self, server_port=10000):
        self.server_port = server_port

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_address = ('localhost', self.server_port)
        print(f"connecting to {server_address[0]} port {server_address[1]}")
        self.sock.connect(server_address)

        running = True
        while running :
            try:
                #message = input("Type your message:\n")
                message="This is our message.This is our messageThis is our messageThis is our messageThis is our message"
                print(f"sending {message}")

                send_message(self.sock, message.encode('utf-8'))

                data = receive_message(self.sock)
                print(f"received {data}")
            except:
                print(f"closing socket")
                self.sock.close()
                running = False
                
c=Client()
c.start()

""" sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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

 """