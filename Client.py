'''
    Secure Messenger Application Client

    Authors: Hans Prieto, Joshua Fawcett

    This module implements all necessary functions to communicate with the server
    in order to create an account and send messages to other users. 
'''

from socket import *
from threading import Thread
from cipher import *
import time
import traceback
import json
import random

serverName = "54.144.253.235" # IP address of AWS t2.micro instance running the server script
#serverName = "127.0.0.1" # Used to test locally
serverPort = 12000

# ================================================= Client Class =================================================
class Client:
    # This class servers as an interface to the client module's functionality. 
    def __init__(self, rThreadCallback=None):
        self.profile = read_user_profile() # Get user preferences from JSON file

        # Intialize client 
        server_connection = connectToServer() # Attempt to connect to server
        self.rThread = None  
        self.connected = False
        if server_connection is not None: # connectToServer() succeeded
            self.connected = True
            self.soc, self.sessionKey = server_connection # Store client socket and session key
            self.rThread = create_receiving_thread(self.soc, self.sessionKey, rThreadCallback) # Create receiving thread
        else: # connectToServer() failed
            self.soc = None
            self.sessionKey = None

        # References to implemented encryption algorithms in cipher.py
        self.encryptionTypes = {'plaintext': 0, 'ROT13': 1, 'vigenere': 2, 'AES': 3, 'RSA': 4, 'Fernet': 5}

    def sendMessage(self, message, IP, etype, eKey, publicKey):
        # Send message to server to be forwarded to destination 'IP'
        if self.soc is None: # Cannot send message if socket is None
            return False
        uName = self.profile['uName'] # Get username to identify self to receiver
        sendSuccess = sendMessageTo(self.soc, message, IP, uName, etype, eKey, publicKey, self.sessionKey) # Send message to server
        time.sleep(.25) # Wait for ACK
        recvAck = self.rThread.status.ACK # Read ACK from receiving thread
        status = sendSuccess and recvAck # If successful send and received ACK from server
        self.rThread.status.ACK = False # Reset ACK for next message
        return status # Report success

    def getPublicKey(self, receiverName, receiverIP):
        # Query a user's public key from the server using their username
        sendSuccess = getPublicKeyFromServer(self.soc, self.sessionKey, receiverName, receiverIP)

        # Initialize ACK with none, if the receiving thread receives the public key from the server
        # it will store the key in ACK for us to read here
        self.rThread.status.ACK = None 
        time.sleep(1) # Wait for ACK
        pubkeybytes = self.rThread.status.ACK # If public key was received, store in pubkeybytes
        self.rThread.status.ACK = False # Reset ACK for next message
        return pubkeybytes

    def readMessage(self, message):
        return message

    def createAccount(self, username, password):
        # Negotiate with server to create a user account
        if self.soc is None: # Cannot create account if no server connection
            return None

        # Send username and password to server
        sendSuccess = createUserAccount(self.soc, self.sessionKey, username, password)

        time.sleep(2) # Wait for ACK
        recvAck = self.rThread.status.ACK
        status = sendSuccess and recvAck # Successful account creation if message sent successfully and received ACK from server
        self.rThread.status.ACK = False # Reset ACK for next message

        # If account creation was successful, store username
        if status:
            self.updateUserName(username)
        return status

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
        # Used to update a value in the user's JSON profile file
        update_profile(self.profile, uName=uName, popUps=doPopups, eType=eType)

    def disconnect(self):
        # Disconnect from the server
        if self.rThread is not None: # Close receiving thread
            self.rThread.close()
        if self.soc is not None: # Close socket
            disconnectServer(self.soc, self.sessionKey)
# ================================================================================================================

# =============================================== Receiving Thread ===============================================
class RThreadStatus:
    # This class is used to communicate with the receiving thread. It is passed as
    # an argument to the receiving thread target and can terminate the receiving thread with
    # the terminate variable, and the receiving thread can pass server responses through the
    # ACK variable
    def __init__(self):
        self.terminate = False
        self.ACK = False

class ReceivingThread:
    # This class is used to manage the receiving thread and its status
    def __init__(self, t, s):
        self.thread = t # Receiving thread
        self.status = s # Thread status

    def close(self):
        self.status.terminate = True # Stop the receiving thread loop
        self.thread.join() # Join thread

def receiving_thread(conn, bufferSize, status, sessionKey, rCallback=None):
    # Receiving thread target
    conn.settimeout(1) # Timeout after 1 second
    while not status.terminate: # Loop until terminate
        try:
            packet = conn.recv(bufferSize) # Receive packet from server
        except timeout:
            continue

        # Decrypt packet and separate the values
        fields = unPack(packet, sessionKey)
        if fields is None: # Received invalid packet
            continue
        if len(fields) != 6:
            # Check for ACK from server
            if fields[0] == b'50': # Message ACK
                status.ACK = True
            if fields[0] == b'20': # Received a public key from server
                status.ACK = fields[1] # Pass to Client class through status.ACK (fields[1] holds key)
            continue

        # If the previous if statements did not execute, then a valid message was received. Extract
        # relevant information and pass to UI for handling
        senderName = fields[0].decode() # Username of sender
        ip = fields[1].decode() # IP address of sender
        encryptionType = fields[2].decode() # Type of encryption used on the message

        IV = fields[3] # Initialization vector (If sender encrypted with AES, otherwise unused)
        Key = fields[4] # Key used to encrypt message. The key itself is encrypted with receivers public key
        encMessage = fields[5] # Encrypted message

        message = stripEnc(encryptionType, IV, Key, encMessage) # Decrypt the message
        
        if rCallback is not None:
            rCallback((ip, message, senderName)) # Pass message to UI
        else:
            print(message)
    return None
# ================================================================================================================

# =============================================== Helper Functions ===============================================
def get_ip():
    # Get client's IP address to send to host. This is needed because actual host IP and socket address
    # received by server may differ due to NAT. This allows hosts to identify each other using IP address 
    hostname = gethostname()
    return gethostbyname(hostname)

def create_profile(f):
    # Create json profile to store username and preferences
    userID = -1
    ip = get_ip()
    prof = {"uName": '',
            "preferences": {"popups": True, "eType": 0}
            }
    with open("data/user_profile.json", "w+") as f:
        json.dump(prof, f, indent=4)
    return prof

def update_profile(profile, uName=None, popUps=None, eType=None):
    # Update specific value of the user profile
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
    # Helper function to create and start the receiving thread. Returns a
    # ReceivingThread class instance
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

def stripEnc(encryptionType, IV, encKey, encMessage):
    ''' (string, bytes, bytes, bytes) -> string

        Decrypts 'encMessage' based on encryption type
    '''
    privKey = RSA_load_private_key() # Load private key from file
    
    if encryptionType == '0': # Encrypted message is plaintext
        return encMessage.decode() # Convert bytes to string

    elif encryptionType == '1': # Encrypted with ROT13
        message = rot13_decrypt(encMessage.decode())

    elif encryptionType == '2': # Encrypted with Vigenere
        message = vig_decrypt(encMessage.decode())

    elif encryptionType == '3': # Encrypted with AES
        # Decrypt the AES encryption key with own private key
        key = RSA_private_key_decrypt(encKey, privKey)
        # Decrypt the message with AES key
        message = AES_decrypt(encMessage, IV, key).decode()

    elif encryptionType == '4': # Encrypted with RSA
        message = RSA_private_key_decrypt(encMessage, privKey).decode()

    elif encryptionType == '5': # Encrypted with Fernet
        # Decrypt the Fernet encryption key with own private key
        key = RSA_private_key_decrypt(encKey, privKey)
        # Decrypt the message with Fernet key
        message = Fernet_decrypt(encMessage, key)
    
    return message

def connectToServer():
    ''' () -> (socket, bytes)
        () -> None

        Connects to the server and establishes session key. Returns appropriate
        socket and session key on success and returns None on failure. 
    '''
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

    # Send handshake and signature for verification
    handshake1 = handshakeMessage + b'\r\n' + signature

    clientSocket.settimeout(3)
    try:
        # Send client public key to server
        clientSocket.send(handshake1)

        # Receive server handshake message with server public key
        handshake2 = clientSocket.recv(4096)

        fields = handshake2.split(b'\r\n')

        if len(fields) != 4:
            print('Invalid Server Response')
            return None

        # Convert server public key from bytes to public key object
        serverPubKey = RSA_get_key_from_bytes(fields[1])

        # Retrieve and remove signature from header fields
        signature = fields.pop(-1)

        # Join header fields into bytes to test signature
        message = b'\r\n'.join(fields)

        # Verify the message using the signature
        if not RSA_verify(signature, message, serverPubKey):
            print("Invalid signature")
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
    return plaintext.split(b'\r\n')

def sendMessageTo(soc, message, destination, uName, encryptionType, encryptionKey, publicKey, sessionKey):
    # Encrypt message
    iv = b'0' # Default value for IV if AES is not used

    publicKey = RSA_get_key_from_bytes(publicKey)
    
    if encryptionType == 0: # Plaintext
        encMessage = message.encode() # Convert to bytes for transmission
        encKey = b'0'

    elif encryptionType == 1: # ROT13
        encMessage = rot13_encrypt(message).encode()
        encKey = b'0'

    elif encryptionType == 2: # Vigenere
        encMessage = vig_encrypt(message).encode()
        encKey = RSA_public_key_encrypt(encryptionKey, publicKey)

    elif encryptionType == 3: # AES
        encMessage, iv = AES_encrypt(message, encryptionKey)
        encKey = RSA_public_key_encrypt(encryptionKey, publicKey)

    elif encryptionType == 4: # RSA
        rsaKey = RSA_get_key_from_bytes(encryptionKey)
        encMessage = RSA_public_key_encrypt(message, rsaKey)
        encKey = b'0'

    elif encryptionType == 5: # Fernet
        encMessage = Fernet_encrypt(message.encode(), encryptionKey)
        encKey = RSA_public_key_encrypt(encryptionKey, publicKey)

    # Create Packet
    packet = f'200\r\n{destination}\r\n{uName}\r\n{encryptionType}'.encode() + b'\r\n' + iv + b'\r\n' + encKey + b'\r\n' + encMessage

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

def createUserAccount(soc, sessionKey, username, password):
    # Create hash of password
    hashedPass = hashPassword(password) # Create password hash to send to server

    # Sequence number. Not really used in this implementation. Future updates will use to prevent replay attack
    seq = random.randint(0, (2**32) - 1)
    
    # Create packet with username and hash password
    packet = b'10\r\n' + username.encode() + b'\r\n' + hashedPass + b'\r\n' + str(seq).encode() + b'\r\n0'

    # Encrypt packet with client/server session key
    packet_enc, iv = AES_encrypt(packet, sessionKey)

    new_packet = iv + b'\r\n' + packet_enc

    # Send packet to server
    soc.settimeout(3)
    try:
        soc.send(new_packet)
    except timeout:
        return False # Send failure
    soc.settimeout(1)
    # If no failure, return send success
    return True

def getPublicKeyFromServer(soc, sessionKey, receiverName, receiverIP):
    # Create packet
    packet = b'20\r\n' + f"{receiverName}\r\n{receiverIP}".encode() + b'\r\n0\r\n0'

    # Encrypt packet with client session key
    packet_enc, iv = AES_encrypt(packet, sessionKey)

    new_packet = iv + b'\r\n' + packet_enc

    # Send packet to server
    soc.settimeout(3)
    try:
        soc.send(new_packet)
    except timeout:
        return False
    soc.settimeout(1)
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
