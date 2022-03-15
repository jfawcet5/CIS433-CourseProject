'''
    Secure Messenger Application Server

    Authors: Hans Prieto, Joshua Fawcett

    This module implements the server side of the application. It provides functionality such as
    user account creation and message forwarding (sending a message from one client to another). This
    module was designed to run on an AWS t2.micro instance to provide continuous service to clients
    and allow for NAT traversal between two hosts that may be hidden behind NAT. 
'''
import sys
from cipher import *
from socket import *
from UserDatabase import UserDataBase
from threading import Thread
from datetime import datetime

serverPort = 12000

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind(('', serverPort))

serverSocket.listen(1)

# Load from file (or create) server RSA keys (Implemented in cipher.py)
PUBLICKEY, PRIVATEKEY = RSA_get_keys()

# ================================================================================================================

# =============================================== Helper Functions ===============================================
def valid_IP(IP):
    octets = IP.split('.')
    if len(octets) != 4:
        return False
    return True

def unpackMessage(message, sessionKey):
    ''' Decrypt a message and split into header fields
    '''
    try:
        if len(message) > 0:
            fields = message.split(b'\r\n') # Split message into IV and ciphertext
            if len(fields) != 2:
                return None
            iv = fields[0] # Initialization vector for AES decryption
            ct = fields[1] # Cipher text to be decrypted

            pt = AES_decrypt(ct, iv, sessionKey) # Decrypt
        else:
            return None
    except timeout:
        return None

    fields = pt.split(b'\r\n') # Split plaintext into header fields

    # Valid messages have either 5 or 7 fields
    if len(fields) != 5 and len(fields) != 7:
        print('Error in unpackMessage: invalid field size')
        return None

    return fields

def getTimeStamp():
    # Readable timestamp for logging purposes
    t = datetime.now()
    year = t.year
    month = t.month
    day = t.day
    hour = t.hour
    minute = t.minute
    second = t.second
    if hour > 12:
        hour -= 12
    timeStamp = '{}/{}/{} {}:{}:{}'.format(month, day, year - 2000, hour, minute, second)
    return timeStamp
# ================================================================================================================

# =============================================== Thread Targets  ================================================
def connectionThread(serverSocket, addClientCallback, status):
    ''' Thread target to asynchronously wait for client connections, verify/accept
        clients, establish session key, and create client_connection objects. 
    '''
    while not status.terminate:
        connection, addr = serverSocket.accept()
        print('Connection: {}'.format(addr))
        connection.settimeout(2)
        try:
            # Receive handshake message from client
            handshake = connection.recv(4096)

            # Split handshake message into fields
            headerFields = handshake.split(b'\r\n')

            if len(headerFields) != 5:
                print('Connection: {} Invalid:\nHeader Error: {}'.format(addr, headerFields))
                connection.close()
                continue

            # Extract client IP and public key from header fields
            IP = headerFields[1].decode()
            senderPubKey = RSA_get_key_from_bytes(headerFields[2])

            if not valid_IP(IP):
                print('Connection: {} Invalid:\nIP Error: {}'.format(addr, IP))
                connection.close()
                continue

            # Retrieve and remove signature from header fields
            signature = headerFields.pop(-1)

            # Join header fields into bytes to test signature
            message = b'\r\n'.join(headerFields)

            # Test validity of signature
            if not RSA_verify(signature, message, senderPubKey):
                print('Connection: {} Invalid:\nSignature Error')
                connection.close()
                continue

            # Convert server public key object into bytes for transmission to client
            pubkeyBytes = RSA_get_bytes_from_key(PUBLICKEY)

            # Construct handshake message to send server public key to client
            handshakeMessage = b'100\r\n' + pubkeyBytes + b'\r\n0'
            signature = RSA_sign(handshakeMessage, PRIVATEKEY)

            newHandshake = handshakeMessage + b'\r\n' + signature

            # Send server handshake message to client
            connection.send(newHandshake)

            # Receive client response with encrypted session key
            enc_response = connection.recv(4096)

            # Split header fields from signature
            fields = enc_response.split(b'\r\n')

            if len(fields) != 2:
                print('Invalid session key response')
                continue

            message, signature = fields

            # Decrypt header fields with server private key and verify validity of message with client public key
            plain_response = RSA_decrypt(message, signature, senderPubKey, PRIVATEKEY)

            if plain_response is None:
                print('session key decrypt failure')
                continue

            # Extract status code, sequence number, and session key from header fields
            code, sequence, sessionKey = plain_response.split(b'\r\n')

            connection.settimeout(None)

            # Create client connection object
            addClientCallback(connection, addr, IP, senderPubKey, sessionKey)
        except timeout:
            print("timeout")
            connection.close()
            continue
            
    return None

def receivingThread(client, bufferSize, rThreadInstance):
    ''' Thread target to listen for messages from clients and
        attempt to forward those messages to the appropriate destination
    '''
    connection = client.socket
    address = client.address

    client_session_key = client.sessionKey

    connection.settimeout(2)
    while not rThreadInstance.status.terminate:
        try: # Attempt to receive message from client
            packet = connection.recv(bufferSize)
        except ConnectionResetError: # Connection with client was lost
            print('Lost connection with: {}'.format(client))
            rThreadInstance.disconnect()
            break
        except Exception: # Timeout or other error
            continue

        # Decrypt with client's session key and split header fields
        fields = unpackMessage(packet, client_session_key)
        if fields is None:
            continue

        # Client is disconnecting
        if fields[0] == b'0':
            rThreadInstance.disconnect()
            break
        elif fields[0] == b'10': # Create user account
            db = UserDataBase()
            username = fields[1].decode()
            hashedPass = fields[2]
            IP = client.IP
            pubkeybytes = RSA_get_bytes_from_key(client.publicKey)
            success = db.addUser(username, IP, pubkeybytes, hashedPass)
            if success:
                connection.send(b'50') # Successful account creation code
            else:
                connection.send(b'55') # Account creation failure code
            db.disconnect()
            continue
        elif fields[0] == b'20': # Get a user's public key
            username = fields[1] # Username of desired user's public key
            IP = fields[2] # IP address of desired user's public key

            # Access user database to check for public key
            db = UserDataBase()
            pubkeybytes = db.getUserPublicKey(username.decode())
            if pubkeybytes is not None: # User exists and public key is ready to send
                # Send public key
                connection.send(b'20\r\n' + pubkeybytes + b'\r\n0')
            db.disconnect() # Disconnect from database
            continue

        # Extract info from fields
        receiverIP = fields[1].decode() # Destination IP address
        name = fields[2].decode()
        eType = fields[3].decode()
        senderIV = fields[4]
        senderEncKey = fields[5]
        message = fields[6]

        # Get list of client connections 
        connectionsList = rThreadInstance.parent.connections

        # Search for destination in client connections list
        for conn in connectionsList:
            IP = conn.IP
            if IP == receiverIP: #Destination IP matches client IP
                if conn.address != address: # Prevent client from sending a message to themself
                    try:
                        # Reconstruct packet to send to destination client
                        newPacket = '{}\r\n{}\r\n{}\r\n'.format(name, client.IP, eType).encode()
                        #newPacket = '{}\r\n{}\r\n{}\r\n{}'.format(name, message, client.IP, eType)
                        newPacket += senderIV + b'\r\n' + senderEncKey + b'\r\n' + message
                        # Encrypt new packet with destination client's session key
                        enc, iv = AES_encrypt(newPacket, conn.sessionKey)
                        packetENC = iv + '\r\n'.encode() + enc
                        # Forward message to destination
                        conn.socket.send(packetENC)
                        # Send ACK to original client
                        connection.send('50'.encode())
                        continue
                    except Exception:
                        break
    return None
# ================================================================================================================

# =============================================== General Classes ================================================
class Client_Connection:
    ''' Container to represent a client connection. Stores all relevant information
        such as client socket, client address, client IP, client session key, and
        a timestamp.
    '''
    def __init__(self, conn, addr, IP, publicKey, sessionKey=None):
        self.socket = conn
        self.address = addr
        self.IP = IP
        self.sessionKey = sessionKey
        self.publicKey = publicKey

        self.timeStamp = getTimeStamp()

    def __repr__(self):
        return 'C:[{}, {}]'.format(self.address, self.IP)

class TStatus:
    ''' Thread status class used for thread execution. Determines
        if a thread is still running and is used to terminate a thread
        instance.
    '''
    def __init__(self):
        self.terminate = False

class ConnectionThread:
    ''' This class is a container class to store the connection thread and
        all relevant information. Takes the server class as a parent to create
        and store client_connection objects when a connection with a client has been
        successfully established
    '''
    def __init__(self, parent):
        self.parent = parent
        self.socket = self.parent.socket

        self.status = TStatus()
        self.thread = Thread(target=connectionThread, args=(self.socket, self.parent.addClient, self.status))
        self.thread.start()

    def __repr__(self):
        return 'CT[{}]'.format(self.thread.name)

    def close(self):
        self.status.terminate = True
        self.thread.join()

class ReceivingThread:
    ''' This class is a container to store a receiving thread for a particular client
        and all information necessary for that thread.
    '''
    def __init__(self, parent, client):
        self.client = client
        self.parent = parent
        self.bufferSize = 4096

        self.status = TStatus()
        self.thread = Thread(target=receivingThread, args=(self.client, 4096, self))
        self.thread.start()

    def __repr__(self):
        return 'RT[{} - {}]'.format(self.thread.name, self.client)

    def disconnect(self):
        self.status.terminate = True
        self.parent.removeClient(self.client, self)

    def close(self):
        self.status.terminate = True
        self.thread.join()
# ================================================================================================================

# ================================================= Server Class =================================================
class Server:
    ''' This class stores and manages all data necessary for the execution of
        the server. 
    '''
    def __init__(self, serverSocket):
        self.socket = serverSocket

        # List of connected clients (client_connection objects)
        self.connections = []
        # Connection thread to accept incoming connections
        self.connectionThread = ConnectionThread(self)

        self.receivingThreads = []

    def addClient(self, connection, address, IP, pubkey, sKey):
        client = Client_Connection(connection, address, IP, pubkey, sKey)
        self.connections.append(client)
        print('New Connection: {} at time: {}'.format(client, getTimeStamp()))

        rThread = ReceivingThread(self, client)
        self.receivingThreads.append(rThread)

    def removeClient(self, client, rt):
        try:
            self.connections.remove(client)
            print('Client: {} Disconnected at: {}'.format(client, getTimeStamp()))
        except Exception:
            print("Remove Client Error: {} not in list".format(client))

    def run(self):
        try:
            while True:
                for rt in self.receivingThreads:
                    if rt.status.terminate:
                        self.receivingThreads.remove(rt)
                        rt.close()
        finally:
            self.exit()

    def exit(self):
        self.connectionThread.close()
        
        for rThread in self.receivingThreads:
            rThread.close()

        for conn in self.connections:
            conn.close()
# ================================================================================================================

# ===================================================== Main =====================================================
def startServer():
    print('Server is ready')
    s = Server(serverSocket)
    s.run()
    return None

def main():
    startServer()
    return None

if __name__ == "__main__":
    main()
