
from socket import *
serverIP = '54.160.235.144'
cSock = socket(AF_INET, SOCK_STREAM)
cSock.connect((serverIP, 12000))
cSock.send('receiverIP\r\nmessage'.encode())
