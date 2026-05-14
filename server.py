from socket import *
import threading
import json
from key_value_operation import KeyValueStore
from config import server_nodes
from message_pass import*
import ast
import random
import time


FOLLOWER = "follower"
CANDIDATE = "candidate"
LEADER = "leader"

class Server:
    def __init__(self,name,port=10000):
        self.port=port
        self.name=name
        self.kvs=KeyValueStore(server_name=name)
        #self.catch_up(self.kvs)
        self.kvs.catch_up()
        
        # Raft State
        self.state = FOLLOWER
        self.current_term = 0
        self.voted_for = None
        self.election_timer = None
        
        # Leaders only
        self.heartbeat_timer = None
        
        print(f"Server {self.name} initialized as {self.state}")
        
    def destination_addresses(self):
        #other_servers = {k: (v[0], int(v[1])) for (k, v) in server_nodes().items() if k != self.name}
        other_servers = {k: v for (k, v) in server_nodes().items() if k != self.name}
        #print(str(list(other_servers.values())))
        return list(other_servers.values())
    
    def address_of(self,server_name):
        return server_nodes()[server_name]
    
    def tell(self, message, to_server_address):
        print(f"connecting to {to_server_address[0]} port {to_server_address[1]}")

        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect(to_server_address)
        
        encode_message= message.encode('utf-8')

        try:
            print(f"sending {encode_message} to {to_server_address}")
            send_message(self.client_socket, encode_message)
        except Exception as e:
            #print(f"closing socket")
            print(f"closing socket due to {str(e)}")
            self.client_socket.close()
            
        
    def reset_election_timer(self):
        if self.election_timer:
            self.election_timer.cancel()
        
        timeout = random.uniform(5, 10) # 5-10 seconds for easier debugging
        self.election_timer = threading.Timer(timeout, self.start_election)
        self.election_timer.start()

    def start_election(self):
        print(f"Election timeout! {self.name} is starting an election for term {self.current_term + 1}")
        self.state = CANDIDATE
        self.current_term += 1
        self.voted_for = self.name
        self.reset_election_timer()
        
        # In a real Raft, we'd request votes here. For now, let's just become leader if alone or broadcast.
        self.broadcast(self.with_return_address(f"request_vote {self.current_term}"))
        
        # Self-vote counts as 1. If majority reached (simplified for now), become leader.
        # We'll refine the voting logic in the next step.

    def become_leader(self):
        if self.state == LEADER: return
        print(f"{self.name} became LEADER for term {self.current_term}")
        self.state = LEADER
        if self.election_timer:
            self.election_timer.cancel()
        self.start_heartbeat_loop()

    def become_follower(self, term):
        self.state = FOLLOWER
        self.current_term = term
        self.voted_for = None
        self.reset_election_timer()

    def start_heartbeat_loop(self):
        if self.state != LEADER: return
        self.broadcast(self.with_return_address(f"heartbeat {self.current_term}"))
        self.heartbeat_timer = threading.Timer(2.0, self.start_heartbeat_loop)
        self.heartbeat_timer.start()

    def start(self):
        server_address= ('localhost',self.port)
        f = open("server_registry.txt", "a")
        f.write(self.name + " localhost " + str(self.port) + '\n')
        f.close()

        print("starting up on " + str(server_address[0]) + " port "  + str(server_address[1]))
        
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_socket.bind(server_address)
        self.server_socket.listen(5)
        
        self.reset_election_timer()
        
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
                        send_pending =True
                        string_request = operation.decode("utf-8")
                        #print("received " + string_request)
                        server_name,string_operation = self.return_address_and_message(string_request)
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
                        elif string_operation.startswith("request_vote"):
                                 term = int(string_operation.split(" ")[1])
                                 if term > self.current_term:
                                     self.become_follower(term)
                                     self.voted_for = server_name
                                     response = "vote_granted " + str(term)
                                 elif term == self.current_term and (self.voted_for is None or self.voted_for == server_name):
                                     self.voted_for = server_name
                                     response = "vote_granted " + str(term)
                                 else:
                                     response = "vote_denied " + str(self.current_term)
                        elif string_operation.startswith("vote_granted"):
                                 term = int(string_operation.split(" ")[1])
                                 if self.state == CANDIDATE and term == self.current_term:
                                     # Simple vote counting logic
                                     if not hasattr(self, 'votes_received'):
                                         self.votes_received = set()
                                     self.votes_received.add(server_name)
                                     self.votes_received.add(self.name) # Self vote
                                     
                                     majority = (len(server_nodes()) // 2) + 1
                                     if len(self.votes_received) >= majority:
                                         self.become_leader()
                                 send_pending = False
                        elif string_operation.startswith("heartbeat"):
                                 term = int(string_operation.split(" ")[1])
                                 if term >= self.current_term:
                                     self.become_follower(term)
                                     self.current_leader = server_name
                                 send_pending = False
                        elif string_operation.split(" ")[0] == "log_length":
                                catch_up_start_index = int(string_operation.split(" ")[1])

                                if len(self.kvs.log) > catch_up_start_index:
                                    response = "catch_up_logs " + str(self.kvs.log[catch_up_start_index:])
                                else:
                                    
                                    response = "Your info is as good as mine!"
                        elif string_operation.split(" ")[0] == "catch_up_logs":
                                logs_to_append = ast.literal_eval(string_operation.split("catch_up_logs ")[1])
                                for log in logs_to_append:
                                    self.kvs.execute(log)

                                response = f"ack_append {len(self.kvs.log)}"
                        elif string_operation.startswith("ack_append"):
                                 # Logic for leader to track acks
                                 index = int(string_operation.split(" ")[1])
                                 if self.state == LEADER:
                                     if not hasattr(self, 'acks'): self.acks = {}
                                     if index not in self.acks: self.acks[index] = set([self.name])
                                     self.acks[index].add(server_name)
                                     
                                     majority = (len(server_nodes()) // 2) + 1
                                     if len(self.acks[index]) >= majority:
                                         # Commit logic (simplified)
                                         pass 
                                 send_pending = False
                        elif string_operation == "show_log":
                                response = str(self.kvs.log)
                        elif string_operation == "youre_the_leader":
                             self.become_leader()
                             response="Brodcasting to other servers"
                        elif string_operation in [
                            "Caught up. Thanks!",
                            "Sorry, I don't understand that command.",
                            "Your info is as good as mine!",
                            "Broadcasting to other servers ",
                            "vote_denied"
                        ]:
                            send_pending = False
                        else:
                            if self.state != LEADER:
                                response = f"redirect {self.current_leader if hasattr(self, 'current_leader') else 'unknown'}"
                            else:
                                # Leader logic: replicate then execute
                                log_index = len(self.kvs.log)
                                self.broadcast(self.with_return_address(f"catch_up_logs ['{string_operation}']"))
                                # Simplified: we'll just execute locally for now but in a real Raft 
                                # we would wait for acks before executing.
                                response = kvs.execute(string_operation)

                        if send_pending:
                            response = self.with_return_address(response)
                            
                            if server_name =="client":
                                send_message(connection,response.encode('utf-8'))
                            else:
                                self.tell(response,to_server_address=self.address_of(server_name))
                                

                    else:
                            print("no more data")
                            break

            finally:
               # print("Closing current connection")
                connection.close()
                
                
                
    def return_address_and_message(self, string_request):
        address_with_message = string_request.split("@")
        return address_with_message[0], "@".join(address_with_message[1:]) 
    
    def with_return_address(self, response):
        return self.name + "@" + response           
                
    def broadcast(self, message):
        for other_server_address in self.destination_addresses():
            try:
                self.tell(message, to_server_address=other_server_address)
            except Exception as e:
                print(f"Failed to send to {other_server_address}: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Start a KVS server node.")
    parser.add_argument("--name", type=str, required=True, help="Unique name for this server node")
    parser.add_argument("--port", type=int, default=10000, help="Port to listen on (default: 10000)")
    
    args = parser.parse_args()
    
    # Clean up registry if it's the first node or handle differently?
    # For now, let's just make sure we don't have empty names.
    s = Server(name=args.name, port=args.port)
    s.start()