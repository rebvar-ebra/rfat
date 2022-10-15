from socket import *
import threading
import json
from key_value_operation import KeyValueStore
from config import server_nodes

ports_file = "address.json"
with open(ports_file):
    ports_format= open(ports_file)
    ports = json.load(ports_format)
    ports_format.close()

host=ports["host"]
port=ports["port"]

class Server:
    def __init__(self,name,port=10000):
        self.port=port
        self.name=name
        self.kvs=KeyValueStore()
        self.catch_up(self.kvs)
        
    def start(self):
        server_address= ('localhost',self.port)
        f = open("server_registry.txt", "a")
        f.write(self.name + " localhost " + str(self.port) + '\n')
        f.close()

        print("starting up on " + str(server_address[0]) + " port "  + str(server_address[1]))
        print(str(server_nodes()))
        
        sock = socket()
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind(server_address)
        sock.listen(1)
        
        while True:
            connection, client_address = sock.accept()
            print("connection from " + str(client_address))
            threading.Thread(target=self.handle_client, args=(connection, self.kvs)).start()
            
    def handel_client(self,connection,kvs): 
            # Receive the data in small chunks and retransmit it:
        while True:
            print('waiting for a connection')
                        
            try:
                            
                while True:
                    operation = connection.recv(1024)
                    
                    if operation:
                        string_operation= operation.decode("utf-8")
                        print("received " + string_operation)
                        f=open("commands.txt","a")
                        f.write(string_operation + '\n')
                        f.close()
                            # command=json.dumps(" ",indent=4)
                            # with open ("command.json","w") as outfile:
                            #     outfile.write(string_operation)
                                
                        response= kvs.execute(string_operation)
                        print('sending data back to the client')
                        connection.sendall(response.encode('utf-8'))
                    else:
                        print('no more data from')
                        break

            finally:
                            # Clean up the connection
                        print("Closing current connection")
                        connection.close()
    def catch_up(self,key_value_store):
        f = open("commands.txt", "r")
        log = f.read()
        f.close()
        # with open("command.json",'r') as openfile:
        #     read= json.load(openfile)
            

        for command in log.split('\n'):
            key_value_store.execute(command)

        
 
""" def run_server(): 
    kvs = KeyValueStore()
    catch_up(kvs)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_address = ('localhost', 10000)
    print('Starting up on {} port {}'.format(*server_address))
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(1)

    while True:
        # Wait for a connection
        print('waiting for a connection')
        connection, client_address = sock.accept()
        print('connection from', client_address)
            
        threading.Thread(target=handel_client,args=(connection,kvs)).start()
        




run_server() """