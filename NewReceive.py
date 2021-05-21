BUFF_SIZE = 4096 # 4 KiB

def recvall(sock):
    data = b''
    while True:
        while True:
            part = sock.recv(BUFF_SIZE)
            data += part
            if len(part) < BUFF_SIZE:
                # either 0 or end of data
                break
        if data:
            break
    return data.decode().strip()
