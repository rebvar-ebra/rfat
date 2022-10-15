import socket

def get_open_port():
    serv=socket.socket()
    serv.bind("",0)
    listen=serv.listen(1)
    port= serv.getsockname()[1]
    close=serv.close()
    return port , listen,close

def get_random_port():
    sock = socket.socket()
    sock.listen(0)
    _, port = sock.getsockname()
    sock.close()

    return port


def listen(self,server,port):
		serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serv.bind((self._server, self._port))
		serv.listen(1)
		return serv.accept()