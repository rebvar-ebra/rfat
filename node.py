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
                    print(f"Response: {data.decode('utf-8')}")
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