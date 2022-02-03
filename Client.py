from socket import *
from threading import Thread
import time
import traceback
import json

serverName = "54.144.253.235"
serverPort = 12000

# ================================================= Client Class =================================================
class Client:
    def __init__(self, rThreadCallback=None):
        self.profile = read_user_profile()
        self.soc = connectToServer()
        self.rThread = None
        self.connected = False
        if self.soc is not None:
            self.connected = True
            self.rThread = create_receiving_thread(self.soc, rThreadCallback)

        self.encryptionTypes = {'plaintext': 0, 'ROT13': 1, 'vigenere': 2}

    def sendMessage(self, message, IP):
        uName = self.profile['uName']
        encryptionType = self.profile['preferences']['eType']
        return sendMessageTo(message, IP, uName, encryptionType)

    def readMessage(self, message):
        # decrypt message and split header data from message
        return unPack(message)

    def getUserName(self):
        return self.profile['uName']

    def getEncryptionTypes(self):
        return list(self.encryptionTypes)

    def getPreference(self, preference):
        if preference == 'popups':
            return self.profile['preferences']['popups']
        elif preference == 'eType':
            return self.profile['preferences']['eType']

    def updateUserName(self, name):
        update_profile(self.profile, uName=name)
        return None

    def updatePreference(self, uName=None, doPopups=None, eType=None):
        update_profile(self.profile, uName=uName, popUps=doPopups, eType=eType)

    def disconnect(self):
        if self.rThread is not None:
            self.rThread.close()
        disconnectServer(self.soc)
# ================================================================================================================

# =============================================== Receiving Thread ===============================================
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
    conn.settimeout(2)
    while not status.terminate:
        try:
            packet = conn.recv(bufferSize).decode()
        except Exception:
            continue

        fields = unPack(packet)
        if len(fields) != 4:
            continue

        senderName = fields[0]
        message = fields[1]
        ip = fields[2]
        
        if rCallback is not None:
            rCallback((ip, message, senderName))
        else:
            print(message.decode())
    print('receiving thread exit')
    return None
# ================================================================================================================

# =============================================== Helper Functions ===============================================
def get_ip():
    hostname = gethostname()
    return gethostbyname(hostname)

def create_profile(f):
    userID = -1
    ip = get_ip()
    prof = {"uName": '',
            "preferences": {"popups": True, "eType": 0}
            }
    with open("data/user_profile.json", "w+") as f:
        json.dump(prof, f, indent=4)
    return prof

def update_profile(profile, uName=None, popUps=None, eType=None):
    if uName is not None:
        profile['uName'] = uName
    if popUps is not None:
        profile['preferences']['popups'] = str(popUps)
    if eType is not None:
        profile['preferences']['eType'] = eType

    with open("data/user_profile.json", "w+") as f:
        json.dump(profile, f, indent=4)
    return None

def read_user_profile():
    with open("data/user_profile.json", "a+") as f: # Open json file storing user data
        f.seek(0)
        try:
            data = json.load(f) # load json object 
            print(data)
        except Exception: # If json object doesn't exist
            data = create_profile(f) # Create json object

        return data

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
    print('Connecting to server ... ', end='')
    # Create client socket
    clientSocket = socket(AF_INET, SOCK_STREAM)
    # Establish TCP connection with server
    clientSocket.settimeout(3)
    try:
        clientSocket.connect((serverName, serverPort))
    except Exception:
        print('Failed')
        return None
    clientSocket.settimeout(None)

    IP = get_ip()
    
    handshake = "100\r\n{}\r\n0\r\n0\r\n0".format(IP)
    clientSocket.send(handshake.encode())

    print('Success')
    return clientSocket

def unPack(message):
    return message.split('\r\n')

def sendMessageTo(message, destination, uName, encryptionType):
    # Encrypt message
    # Create Packet
    packet = f'200\r\n{destination}\r\n{uName}\r\n{encryptionType}\r\n{message}'

    soc = connectToServer()

    # Encrypt packet

    # Send Packet
    soc.settimeout(3)
    try:
        soc.send(packet.encode())
        ACK = soc.recv(4096).decode()
        disconnectServer(soc)
        if ACK == '0':
            return True
        else:
            return False
    except Exception:
        print('Failed to send message')
        disconnectServer(soc)
        return False

def disconnectServer(soc):
    try:
        soc.send("0\r\n0\r\n0\r\n0\r\n0".encode())
        time.sleep(0.5)
        soc.close()
    except:
        pass
    return None
# ================================================================================================================

# ===================================================== Main =====================================================
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
# ================================================================================================================
