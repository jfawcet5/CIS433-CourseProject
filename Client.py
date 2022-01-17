from socket import *
import time
serverName = "54.221.21.137"
serverPort = 12000

def connectToServer():
    # Create client socket
    clientSocket = socket(AF_INET, SOCK_STREAM)
    # Establish TCP connection with server
    clientSocket.connect((serverName, serverPort))

    # 'Introduce' self to server
    hostname = gethostname()
    self_ip = gethostbyname(hostname)
    clientSocket.send(self_ip.encode())

    return clientSocket

def sendMessage(soc, message, destination):
    # Create Packet
    packet = f'None\r\n{destination}\r\n{message}'

    # Encrypt packet

    # Send Packet
    soc.send(packet.encode())

def disconnectServer(soc):
    soc.send("0\r\nNone\r\nNone".encode())
    time.sleep(0.5)
    soc.close()
