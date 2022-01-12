
from socket import *
serverIP = '56.160.235.144'
cSock = socket(AF_INET, SOCK_STREAM)
cSock.connect((serverIP, 12000))

hostname = gethostname()
self_ip = gethostbyname(hostname)
cSock.send(self_ip.encode())
cSock.send('s'.encode())
m = cSock.recv(2048)
print(m.decode())
