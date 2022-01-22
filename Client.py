from socket import *
from threading import Thread
import time
import traceback

serverName = "54.90.254.151"
serverPort = 12000

class RThreadStatus:
    def __init__(self):
        self.terminate = False

class ReceivingThread:
    def __init__(self, t, s):
        self.thread = t
        self.status = s

    def close(self):
        self.status.terminate = True
        self.thread.join()

def receiving_thread(conn, bufferSize, status, rCallback=None):
    print('Receiving Thread running')
    conn.settimeout(3)
    while not status.terminate:
        try:
            message = conn.recv(bufferSize)
        except Exception:
            continue
        
        if rCallback is not None:
            rCallback(message.decode())
        else:
            print(message.decode())
    print('receiving thread exit')
    return None

def create_receiving_thread(cSock, callback=None):
    status = RThreadStatus()
    rThread = None
    try:
        rThread = Thread(target=receiving_thread, args=(cSock, 4096, status, callback))
        rThread.start()
    except Exception:
        print('Receiving thread did not start')
        traceback.print_exc()

    if rThread is None:
        return None
    return ReceivingThread(rThread, status)

def connectToServer():
    # Create client socket
    clientSocket = socket(AF_INET, SOCK_STREAM)
    # Establish TCP connection with server
    clientSocket.settimeout(3)
    try:
        clientSocket.connect((serverName, serverPort))
    except Exception:
        return None
    clientSocket.settimeout(None)
    # 'Introduce' self to server
    hostname = gethostname()
    self_ip = gethostbyname(hostname)
    clientSocket.send(self_ip.encode())

    return clientSocket

def sendMessageTo(soc, message, destination):
    if soc is None:
        return False
    # Create Packet
    packet = f'None\r\n{destination}\r\n{message}'

    # Encrypt packet

    # Send Packet
    soc.settimeout(3)
    try:
        soc.send(packet.encode())
        ACK = soc.recv(4096).decode()
        if ACK == '0':
            return True
        else:
            return False
    except Exception:
        print('Failed to send message')
        return False
    return True

def disconnectServer(soc):
    soc.send("0\r\nNone\r\nNone".encode())
    time.sleep(0.5)
    soc.close()

def main():
    print('Connecting to server... ', end="")
    cSock = connectToServer()
    if cSock is not None:
        print('Success')
        rThread = create_receiving_thread(cSock)
        time.sleep(2)
        if rThread is None:
            return None
        print('Send message: 0, Receive message: 1')
        while True:
            function = input('>>>> ')

            if function == '0':
                IP = input('Receiver IP Address: ')
                message = input('Message: ')
                sendMessageTo(cSock, message, IP)
            elif function == '1':
                time.sleep(5)
            else:
                time.sleep(1)
                rThread.status.terminate = True
                time.sleep(1)
                rThread.thread.join()
                disconnectServer(cSock)
                return None
    else:
        print('Connection failed')
    return None

if __name__ == "__main__":
    main()
