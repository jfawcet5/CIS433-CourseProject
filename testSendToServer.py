
from socket import *
serverIP = '54.160.235.144'
cSock = socket(AF_INET, SOCK_STREAM)
cSock.connect((serverIP, 12000))
hostname = gethostname()
self_ip = gethostbyname(hostname)
cSock.send(self_ip.encode())
cSock.send('10.185.236.190\r\nHello this is a test'.encode())
