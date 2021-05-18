import json

def sendJson(sock, data):
    jsonData = json.dumps(data).encode()
    jsonHeader = {"size" : len(jsonData)}
    sock.sendall(json.dumps(jsonHeader).encode())
    sock.sendall(jsonData)
