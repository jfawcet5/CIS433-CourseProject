from socket import *
from threading import Thread
from cipher import *
import time
import traceback
import json

serverName = "54.144.253.235"
#serverName = "127.0.0.1"
serverPort = 12000

# ================================================= Client Class =================================================
class Client:
    def __init__(self, rThreadCallback=None):
        self.profile = read_user_profile()

        server_connection = connectToServer()
        self.rThread = None
        self.connected = False
        if server_connection is not None:
            self.connected = True
            self.soc, self.sessionKey = server_connection
            self.rThread = create_receiving_thread(self.soc, self.sessionKey, rThreadCallback)
        else:
            self.soc = None
            self.sessionKey = None

        self.encryptionTypes = {'plaintext': 0, 'ROT13': 1, 'vigenere': 2}

    def sendMessage(self, message, IP):
        if self.soc is None:
            return False
        uName = self.profile['uName']
        encryptionType = self.profile['preferences']['eType']
        sendSuccess = sendMessageTo(self.soc, message, IP, uName, encryptionType, self.sessionKey)
        time.sleep(.25)
        recvAck = self.rThread.status.ACK
        status = sendSuccess and recvAck
        self.rThread.status.ACK = False
        print(f'Message Sent to Server: {sendSuccess}, Received ACK: {recvAck}')
        return status

    def readMessage(self, message):
        return message

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
        if self.soc is not None:
            disconnectServer(self.soc, self.sessionKey)
# ================================================================================================================

# =============================================== Receiving Thread ===============================================
class RThreadStatus:
    def __init__(self):
        self.terminate = False
        self.ACK = False

class ReceivingThread:
    def __init__(self, t, s):
        self.thread = t
        self.status = s

    def close(self):
        self.status.terminate = True
        self.thread.join()

def receiving_thread(conn, bufferSize, status, sessionKey, rCallback=None):
    print('Receiving Thread running')
    conn.settimeout(1)
    while not status.terminate:
        try:
            packet = conn.recv(bufferSize)
        except timeout:
            continue

        # Decrypt packet and separate the values
        fields = unPack(packet, sessionKey)
        if fields is None:
            continue
        if len(fields) != 4:
            # Check for ACK from server
            if fields[0] == b'50':
                print("ACK")
                status.ACK = True
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
        except Exception: # If json object doesn't exist
            data = create_profile(f) # Create json object

        return data

def create_receiving_thread(cSock, sessionKey, callback=None):
    status = RThreadStatus()
    rThread = None
    try:
        rThread = Thread(target=receiving_thread, args=(cSock, 4096, status, sessionKey, callback))
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

    # Get client IP (IP of machine before NAT)
    IP = get_ip()

    # Retrieve stored RSA keys (Or generate and store RSA keys if no RSA key exists)
    publicKey, privateKey = RSA_get_keys()

    # Convert client public key object into bytes for transmission to server
    pubkeyBytes = RSA_get_bytes_from_key(publicKey)

    # Construct handshake message to send client public key to server
    handshakeMessage = f"100\r\n{IP}\r\n".encode() + pubkeyBytes + b'\r\n0'

    signature = RSA_sign(handshakeMessage, privateKey)
    
    handshake1 = handshakeMessage + b'\r\n' + signature

    clientSocket.settimeout(3)
    try:
        # Send client public key to server
        clientSocket.send(handshake1)

        # Receive server handshake message with server public key
        handshake2 = clientSocket.recv(4096)

        fields = handshake2.split(b'\r\n')

        if len(fields) != 4:
            print('invalid response')
            return None

        # Convert server public key from bytes to public key object
        serverPubKey = RSA_get_key_from_bytes(fields[1])

        # Retrieve and remove signature from header fields
        signature = fields.pop(-1)

        # Join header fields into bytes to test signature
        message = b'\r\n'.join(fields)

        # Verify the message using the signature
        if not RSA_verify(signature, message, serverPubKey):
            print("Invalid siganture")
            return None

        # Create AES session key
        sessionKey = AES_generate_key()

        # Construct handshake message to send session key to server
        key_transfer = b'100\r\n0\r\n' + sessionKey

        # Encrypt session key message with server public key and use client private key to sign message
        enc_message, signature = RSA_encrypt(key_transfer, serverPubKey, privateKey)

        # Send encrypted session key with signature to server
        handshake3 = enc_message + b'\r\n' + signature
        clientSocket.send(handshake3)
        
    except timeout:
        print('Failed')
        return None
    clientSocket.settimeout(None)

    print('Success')
    return clientSocket, sessionKey

def unPack(message, sessionKey):
    # Split header fields of message
    fields = message.split(b'\r\n')

    # Either improper format of header fields or message ACK from server
    if len(fields) != 2:
        return fields

    # Decrypt message with client/server AES session key
    plaintext = AES_decrypt(fields[1], fields[0], sessionKey)
    # Split and return message header fields
    return plaintext.split('\r\n')

def sendMessageTo(soc, message, destination, uName, encryptionType, sessionKey):
    # Encrypt message
    # Create Packet
    packet = f'200\r\n{destination}\r\n{uName}\r\n{encryptionType}\r\n{message}'

    # Encrypt packet with client/server session key
    packet_enc, iv = AES_encrypt(packet, sessionKey)

    new_packet = iv + b'\r\n' + packet_enc

    # Send encrypted message and initialization vector to server
    soc.settimeout(3)
    try:
        soc.send(new_packet)
    except timeout:
        print("Failed to send message")
        return False

    return True

def disconnectServer(soc, sessionKey):
    # Create and encrypt packet to inform server of disconnect
    packet = "0\r\n0\r\n0\r\n0\r\n0"
    packet_enc, iv = AES_encrypt(packet, sessionKey)

    # Send packet to server
    new_packet = iv + b'\r\n' + packet_enc
    try:
        soc.send(new_packet)
        time.sleep(0.5)
        soc.close()
    except Exception:
        pass
    return None
# ================================================================================================================

# ===================================================== Main =====================================================

def test():
    while True:
        function = input('>>>> ')

        if function == '0':
            IP = input('Receiver IP Address: ')
            message = input('Message: ')
            sendMessageTo(message, None, None, None)
        elif function == '1':
            time.sleep(5)
        else:
            return None
def main():
    #print('Connecting to server... ', end="")
    test()
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
                sendMessageTo(message, None, None, None)
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
