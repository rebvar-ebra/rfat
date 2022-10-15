from operator import imod
from socket import *
import threading
import json
from key_value_operation import KeyValueStore
from config import server_nodes
from message_pass import*
import ast

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
        #self.catch_up(self.kvs)
        
    def destination_addresses(self):
        other_servers = {k: (v[0], int(v[1])) for (k, v) in server_nodes().items() if k != self.name}
        return list(other_servers.values())
    
    def tell(self, message, to_server_address):
        print(f"connecting to {to_server_address[0]} port {to_server_address[1]}")

        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect(to_server_address)

        try:
            print(f"sending {message}")
            send_message(self.client_socket, message.encode('utf-8'))
        except:
            print(f"closing socket")
            self.client_socket.close()
        
    def start(self):
        server_address= ('localhost',self.port)
        f = open("server_registry.txt", "a")
        f.write(self.name + " localhost " + str(self.port) + '\n')
        f.close()

        print("starting up on " + str(server_address[0]) + " port "  + str(server_address[1]))
        print(str(server_nodes()))
        
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_socket.bind(server_address)
        self.server_socket.listen(1)
        
        while True:
            connection, client_address = self.server_socket.accept()
            print("connection from " + str(client_address))
            threading.Thread(target=self.handel_client, args=(connection, self.kvs)).start()
            
    def handel_client(self,connection,kvs): 
            # Receive the data in small chunks and retransmit it:
        while True:
            print('waiting for a connection')
                        
            try:
                            
                while True:
                    operation = receive_message(connection)
                    
                    if operation:
                        string_operation= operation.decode("utf-8")
                        print("received " + string_operation)
                        # f=open("commands.txt","a")
                        # f.write(string_operation + '\n')
                        # f.close()
                            # command=json.dumps(" ",indent=4)
                            # with open ("command.json","w") as outfile:
                            #     outfile.write(string_operation)
                                
                        #response= kvs.execute(string_operation)
                        #print('sending data back to the client')
                        #connection.sendall(response.encode('utf-8'))
            #         else:
            #             print('no more data from')
            #             break

            # finally:
            #                 # Clean up the connection
            #             print("Closing current connection")
            #             connection.close()
                        if string_operation == "log_length?":
                                response = "log_length " + str(len(self.kvs.log))
                        elif string_operation.split(" ")[0] == "log_length":
                                catch_up_start_index = int(string_operation.split(" ")[1])

                                if len(self.kvs.log) > catch_up_start_index:
                                    response = "catch_up_logs " + str(self.kvs.log[catch_up_start_index:])
                                else:
                                    response = "Your info is as good as mine!"
                        elif string_operation.split(" ")[0] == "catch_up_logs":
                                logs_to_append = ast.literal_eval(string_operation.split("catch_up_logs ")[1])
                                [self.kvs.execute(log) for log in logs_to_append]

                                response = "Caught up. Thanks!"
                        elif string_operation == "show_log":
                                response = str(self.kvs.log)
                        elif string_operation == "youre_the_leader":
                            self.broadcast('log_length?')
                        else:
                                response = kvs.execute(string_operation)

                                send_message(connection, response.encode('utf-8'))

                    else:
                            print("no more data")
                            break

            finally:
                connection.close()
                
                
                
    def broadcast(self, message):
        for other_server_address in self.destination_addresses():
            self.tell(message, to_server_address=other_server_address)
    # def catch_up(self,key_value_store):
    #     f = open("commands.txt", "r")
    #     log = f.read()
    #     f.close()
    #     # with open("command.json",'r') as openfile:
    #     #     read= json.load(openfile)
            

    #     for command in log.split('\n'):
    #         key_value_store.execute(command)

        
 
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

s=Server(name="rebvar")
s.start()