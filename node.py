import socket
from message_pass import *


class Client:
    def __init__(self, server_port=10000):
        self.server_port = server_port

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', self.server_port)
        print(f"Connecting to {server_address[0]} port {server_address[1]}")
        try:
            self.sock.connect(server_address)
        except Exception as e:
            print(f"Could not connect to server: {e}")
            return

        print("Connection established. Commands: set <key> <value>, get <key>, delete <key>, show, youre_the_leader, show_log, quit")
        
        while True:
            try:
                message = input("rfat> ").strip()
                if not message:
                    continue
                if message.lower() in ["quit", "exit"]:
                    break

                # The server expects "client@command" format for client requests
                formatted_message = f"client@{message}"
                send_message(self.sock, formatted_message.encode('utf-8'))

                data = receive_message(self.sock)
                if data:
                    resp_str = data.decode('utf-8')
                    if "@redirect " in resp_str:
                        leader_name = resp_str.split("redirect ")[1]
                        print(f"Redirected to leader: {leader_name}")
                        # We need to find the address of this leader
                        # For simplicity, we'll assume the registry is available or use a helper
                        # In a real app, the server would send the IP/port
                        from config import server_nodes
                        nodes = server_nodes()
                        if leader_name in nodes:
                            self.sock.close()
                            self.server_port = nodes[leader_name][1]
                            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            self.sock.connect(('localhost', self.server_port))
                            print(f"Reconnected to {leader_name} on port {self.server_port}")
                            # Retry the message
                            send_message(self.sock, formatted_message.encode('utf-8'))
                            data = receive_message(self.sock)
                            if data:
                                print(f"Response: {data.decode('utf-8')}")
                        else:
                            print(f"Leader {leader_name} not found in registry.")
                    else:
                        print(f"Response: {resp_str}")
            except EOFError:
                break
            except Exception as e:
                print(f"Error: {e}")
                break
        
        print("Closing connection.")
        self.sock.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Start an interactive KVS client.")
    parser.add_argument("--port", type=int, default=10000, help="Server port to connect to (default: 10000)")
    
    args = parser.parse_args()
    c = Client(server_port=args.port)
    c.start()