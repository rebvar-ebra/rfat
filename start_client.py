import sys

from node import*
Client(server_port=int(sys.argv[1])).start()