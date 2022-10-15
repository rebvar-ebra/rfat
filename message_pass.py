import pdb
def send_message(sock, msg):
    send_size(sock, len(msg))
    sock.sendall(msg)

def send_size(sock, size):
    sock.sendall(size.to_bytes(8, "big"))

def receive_message(sock):
    size = receive_size(sock)   # get the message size
    try:
        msg = receive_exactly(sock, size)   # Receive exactly this many bytes
    except IOError as e:
        raise IOError("Exception occurred in receive_message: " + str(e)) from e
    return msg

def receive_size(sock):
    try:
        message = receive_exactly(sock, 8)
    except IOError as e:
        raise IOError("Exception occurred in receive_size: " + str(e)) from e


    return int.from_bytes(message, "big")

def receive_exactly(sock, nbytes):
    '''
    Receive exactly nbytes of data on a socket
    '''
    msg = b''
    while nbytes > 0:
        # pdb.set_trace()
        chunk = sock.recv(nbytes)   # Might return partial data (whatever received so far)
        if not chunk:
            # Connection closed!
            raise IOError("The other side closed this connection.")
        msg += chunk
        nbytes -= len(chunk)
    return msg