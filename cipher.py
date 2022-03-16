'''
    Secure Messenger Application Cipher Module

    Authors: Hans Prieto, Joshua Fawcett

    This module implements all of the encryption algorithms used by the secure
    messenger application. Note: A lot of the code for some of the algorithms (such
    as Fernet, AES, and RSA) comes from documentation and examples on the cryptography
    module website. 
    
    Sources:
            Cryptography module: https://cryptography.io/en/latest/
'''

import string

import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
# ===================================================== ROT13 ====================================================
plain_alpha = "abcdefghijklmnopqrstuvwxyz"
rotated_alpha = plain_alpha[13:] + plain_alpha[0:13]    # alphabet rotated 13 shifts to left

# encryption method for rot13
def rot13_encrypt(plaintext):
    result = ""
    # iterate through plaintext message, and encrypt
    for i in range(len(plaintext)):
        cur = plaintext[i]
        if cur != ' ':  # determine if current character is not a space
            if cur.isalpha() and cur.isupper(): # determine if current character is uppercase
                cur = cur.lower()   # convert current character to lowercase
                pos = rotated_alpha.index(cur)  # find the position of the current character in the rotated alphabet
                result +=  plain_alpha[pos].upper() # use position to find character in plain alphabet associated with that position, convert to uppercase
            elif cur.isalpha() and cur.islower():   # determine if current character is lowercase
                pos = rotated_alpha.index(cur)  # find the position of the current character in the rotated alphabet
                result +=  plain_alpha[pos] # use position to find character in plain alphabet associated with that position
            else:
                result += cur   # if current character is not an alpha, just add it to result
        else:
            result += cur   # if current character is a space, just add it to result
    return result   # return result

def rot13_decrypt(enc_text):
    result = ""
    # iterated through encrypted text, and decrypt
    for i in range(len(enc_text)):
        cur = enc_text[i]
        if cur != ' ':  # determine if current character is not a space
            if cur.isalpha() and cur.isupper(): # determine if current character is uppercase
                cur = cur.lower()   # convert current character to lowercase
                pos = rotated_alpha.index(cur)  # find the position of the current character in the rotated alphabet
                result += plain_alpha[pos].upper()  # use position to find character in plain alphabet associated with that position, convert to uppercase
            elif cur.isalpha() and cur.islower():   # determine if current character is lowercase
                pos = rotated_alpha.index(cur)  # find the position of the current character in the rotated alphabet
                result +=  plain_alpha[pos] # use position to find character in plain alphabet associated with that position
            else:
                result += cur # if current character is not an alpha, just add it to result
        else:
            result += cur   # if current character is a space, just add it to result
    return result   # return result
# ================================================================================================================

# ==================================================== Fernet ====================================================
FERNET_KEY = b'wsKKhitf9F-1_oFjIUh1z-JUL7ZFqHVHUfgDo5GPG9w='

def Fernet_generate_key():
    return Fernet.generate_key()

def Fernet_encrypt(plaintext, key=FERNET_KEY):
    ''' (bytes, bytes) -> bytes 
    '''
    f = Fernet(key)
    ciphertext = f.encrypt(plaintext)
    return ciphertext

def Fernet_decrypt(ciphertext, key=FERNET_KEY):
    ''' (bytes, bytes) -> string
    '''
    f = Fernet(key)
    plaintext = f.decrypt(ciphertext)
    return plaintext.decode()
# ================================================================================================================

# ===================================================== AES ======================================================
AES_KEY = b'g\x15\xd1\x91OU\xbe\xc8\x8d\x96\xbfg\xe1B;\xb6(\xd5\x95\x13\x88v1ZtyT\xf7\xfb\x99\x81\xa1'

def AES_generate_key():
    return os.urandom(32)

def AES_encrypt(plaintext, key=AES_KEY):
    ''' (string/bytes, bytes) -> (bytes, bytes)
    '''
    # Generate initialization vector
    iv = os.urandom(16)

    # Create AES cipher object in Cipher Block Chaining mode
    aesCipher = Cipher(algorithms.AES(key), modes.CBC(iv))

    # Add padding to fill block size. Note: padding is of the form: '000000X'
    # Where X is the hexidecimal number indicating how much padding was added
    padding = 16 - (len(plaintext) % 16) - 1

    if type(plaintext) != bytes:
        plaintext = plaintext.encode()

    for i in range(padding):
        plaintext += b'0'

    if padding + 1 > 0:
        numpadding = hex(padding).replace('0x', '')
        plaintext += numpadding.encode()

    # Encrypt plaintext
    enc = aesCipher.encryptor()

    
    ciphertext = enc.update(plaintext) + enc.finalize()
    # Return ciphertext and initialization vector
    return ciphertext, iv

def AES_decrypt(ciphertext, iv, key=AES_KEY):
    ''' (bytes, bytes, bytes) -> bytes
    '''
    # Create AES cipher object in Cipher Block Chaining mode
    aesCipher = Cipher(algorithms.AES(key), modes.CBC(iv))

    # Decrypt ciphertext
    dec = aesCipher.decryptor()

    plaintext = dec.update(ciphertext) + dec.finalize()

    # Remove padding
    pad = '0x' + plaintext[-1:].decode()
    numpadding = -1 * (int(pad, 16) + 1)

    plaintext = plaintext[:numpadding]

    # Return plaintext string
    return plaintext
# ================================================================================================================

# ===================================================== RSA ======================================================

def RSA_gen_priv_key():
    # Generate RSA private key
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)

def RSA_get_pub_from_priv(privKey):
    # Get public key from private key
    return privKey.public_key()

def RSA_gen_key_pair():
    # Generate public/private key pair
    privKey = RSA_gen_priv_key()
    pubKey = RSA_get_pub_from_priv(privKey)
    return pubKey, privKey

def RSA_store_public_key(pubKey, path='data/RSAPUBLICKEY.pem'):
    # Store RSA public key in .pem file on disk
    pem = pubKey.public_bytes(encoding=serialization.Encoding.PEM,
                             format=serialization.PublicFormat.SubjectPublicKeyInfo
                             )
    with open(path, 'wb+') as key_file:
        key_file.write(pem)
    return None

def RSA_load_public_key(key_path='data/RSAPUBLICKEY.pem'):
    # Retrieves RSA private key from .pem file on disk
    pub = None
    try:
        with open(key_path, 'rb') as key_file:
            pub = serialization.load_pem_public_key(key_file.read())
    except FileNotFoundError:
        print('Key: \'{}\' does not exist'.format(key_path))

    return pub

def RSA_store_private_key(privKey, path='data/RSAPRIVATEKEY.pem'):
    # Store RSA private key in .pem file on disk
    pem = privKey.private_bytes(encoding=serialization.Encoding.PEM,
                             format=serialization.PrivateFormat.PKCS8,
                             encryption_algorithm=serialization.NoEncryption()
                             )
    with open(path, 'wb+') as key_file:
        key_file.write(pem)
    return None

def RSA_load_private_key(key_path='data/RSAPRIVATEKEY.pem'):
    # Retrieves RSA private key from .pem file on disk
    priv = None
    try:
        with open(key_path, 'rb') as key_file:
            priv = serialization.load_pem_private_key(key_file.read(), password=None)
    except FileNotFoundError:
        print('Key: \'{}\' does not exist'.format(key_path))

    return priv

def RSA_get_bytes_from_key(pubkey):
    ''' (cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey) -> bytes

        Takes a public key object and returns a bytes object. This is used for public key
        transfer through sockets
    '''
    pubkeyBytes = pubkey.public_bytes(encoding=serialization.Encoding.DER,
                             format=serialization.PublicFormat.SubjectPublicKeyInfo
                             )
    return pubkeyBytes

def RSA_get_key_from_bytes(pbytes):
    ''' (bytes) -> cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey

        Takes a bytes encoding of public key (received through socket) and returns a public
        key object. 
    '''
    pubkey = serialization.load_der_public_key(pbytes)
    return pubkey

def RSA_get_keys():
    ''' () -> (cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey, cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey)

        Reads the RSA private and public key from files and returns them. If no RSA public or private keys exist, this will
        create an RSA public/private key pair, store them, and return them
    '''
    priv = RSA_load_private_key()
    if priv is not None:
        pub = RSA_get_pub_from_priv(priv)
        return pub, priv
    else:
        print('Creating key pair')
        pub, priv = RSA_gen_key_pair()
        RSA_store_private_key(priv)
        RSA_store_public_key(pub)
        return pub, priv

def RSA_public_key_encrypt(message, pubKey):
    ''' (string/bytes, cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey) -> bytes

        Encrypts a message using a public RSA key
    '''
    if type(message) == str:
        message = message.encode()
    ct = pubKey.encrypt(message,
                        padding.OAEP(
                            mgf=padding.MGF1(algorithm=hashes.SHA256()),
                            algorithm=hashes.SHA256(),
                            label=None
                            )
                        )
    return ct

def RSA_private_key_decrypt(ciphert, privKey):
    ''' (bytes, cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey) -> bytes

        Decrypts a message using the RSA private key corresponding to the
        public key that was used to encrypt the message
    '''
    pt = privKey.decrypt(ciphert,
                          padding.OAEP(
                            mgf=padding.MGF1(algorithm=hashes.SHA256()),
                            algorithm=hashes.SHA256(),
                            label=None
                            )
                        )
    return pt

def RSA_sign(message, privKey):
    ''' (string/bytes, cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey) -> bytes

        Creates a signature for a message using an RSA private key. The corresponding public
        key can be used to verify the signature. 
    '''
    signature = privKey.sign(message,
                             padding.PSS(
                                 mgf=padding.MGF1(hashes.SHA256()),
                                 salt_length=padding.PSS.MAX_LENGTH
                                 ),
                             hashes.SHA256()
                            )
    return signature

def RSA_verify(signature, message, pubKey):
    ''' (bytes, bytes, cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey) -> bool

        Verifies that the message was created by someone with the corresponding private
        key using the provided signature and users public key
    '''
    try:
        a = pubKey.verify(signature,
                          message,
                          padding.PSS(
                                     mgf=padding.MGF1(hashes.SHA256()),
                                     salt_length=padding.PSS.MAX_LENGTH
                                     ),
                         hashes.SHA256()
                        )
    except InvalidSignature:
        return False
    return True

def RSA_encrypt(message, rcvPub, sndPriv):
    ''' (string/bytes, bytes, bytes) -> (bytes, bytes)

        Authenticated encryption with signature generation
    '''
    cipherText = RSA_public_key_encrypt(message, rcvPub)
    signature = RSA_sign(cipherText, sndPriv)
    return cipherText, signature

def RSA_decrypt(ciphert, signature, sndPub, rcvPriv):
    ''' (bytes, bytes, bytes, bytes) -> bytes

        Authenticated decryption with signature verification
    '''
    if not RSA_verify(signature, ciphert, sndPub):
        print("Verification Error: Signature does not match")
        return None

    plaintext = RSA_private_key_decrypt(ciphert, rcvPriv)
    return plaintext
# ================================================================================================================

# ===================================================== Vigenere =================================================
enc_key = "test"
dec_key = enc_key

# encryption method for vigenere
def vig_encrypt(input_str):
    enc_str = ""

    # length of input string
    string_length = len(input_str)

    # expand encryption key to make it longer than input string
    expanded_key = enc_key
    expanded_key_length = len(expanded_key)
    while expanded_key_length < string_length:
        expanded_key = expanded_key + enc_key
        expanded_key_length = len(expanded_key)

    key_pos = 0

    for i in range(string_length):
        cur = input_str[i]
        # handle case where current character is uppercase
        if cur.isalpha() and cur.isupper():
            # convert current character to lowercase
            cur = cur.lower()
        
            # find position of letter in alphabet
            letter_pos = plain_alpha.find(cur)
            key_char = expanded_key[key_pos]
            key_char_pos = plain_alpha.find(key_char)
            key_pos = key_pos + 1

            # change original of input string character
            new_pos = letter_pos + key_char_pos
            if new_pos >= 26:
                new_pos = new_pos - 26
            
            # convert new character to uppercase
            new_char = plain_alpha[new_pos].upper()
            enc_str = enc_str + new_char

        # handle case where current character is lowercase
        elif cur.isalpha() and cur.islower():
            # find position of letter in alphabet
            letter_pos = plain_alpha.find(cur)
            key_char = expanded_key[key_pos]
            key_char_pos = plain_alpha.find(key_char)
            key_pos = key_pos + 1

            # change original of input string character
            new_pos = letter_pos + key_char_pos
            if new_pos >= 26:
                new_pos = new_pos - 26
            new_char = plain_alpha[new_pos]
            enc_str = enc_str + new_char

        # handle case where current character is not a letter
        else:
            enc_str = enc_str + cur

    return enc_str

# decryption method for vigenere
def vig_decrypt(input_str):
    dec_str = ""

    # length of input string
    string_length = len(input_str)

    # expand decryption key to make it longer than input string
    expanded_key = dec_key
    expanded_key_length = len(expanded_key)
    while expanded_key_length < string_length:
        expanded_key = expanded_key + dec_key
        expanded_key_length = len(expanded_key)

    key_pos = 0

    for i in range(string_length):
        cur = input_str[i]
        # handle case where current character is uppercase
        if cur.isalpha() and cur.isupper():
            # convert current character to lowercase
            cur = cur.lower()
        
            # find position of letter in alphabet
            letter_pos = plain_alpha.find(cur)
            key_char = expanded_key[key_pos]
            key_char_pos = plain_alpha.find(key_char)
            key_pos = key_pos + 1

            # change original of input string character
            new_pos = letter_pos - key_char_pos
            if new_pos >= 26:
                new_pos = new_pos + 26
            
            # convert new character to uppercase
            new_char = plain_alpha[new_pos].upper()
            dec_str = dec_str + new_char

        # handle case where current character is lowercase
        elif cur.isalpha() and cur.islower():
            # find position of letter in alphabet
            letter_pos = plain_alpha.find(cur)
            key_char = expanded_key[key_pos]
            key_char_pos = plain_alpha.find(key_char)
            key_pos = key_pos + 1

            # change original of input string character
            new_pos = letter_pos - key_char_pos
            if new_pos >= 26:
                new_pos = new_pos + 26
            new_char = plain_alpha[new_pos]
            dec_str = dec_str + new_char

        # handle case where current character is not a letter
        else:
            dec_str = dec_str + cur

    return dec_str
# ================================================================================================================

# ===================================================== Hash =====================================================

def hashPassword(password, ntimes=10):
    ''' (string, int) -> bytes

        Hash password n times. This function is used to send a user's password
        to the server and to be stored on the server's database. 
    '''
    p = password.encode() # Convert password to bytes for hash function
    for i in range(ntimes):
        d = hashes.Hash(hashes.SHA256()) # Create SHA256 hash object
        d.update(p) # Update hash object with data to be hashed ('p')
        p = d.finalize() # Store finalized hash in p

    return p

# ================================================================================================================

# ===================================================== Main =====================================================
def main():
    """
    message = "Hello 32 World!"
    enc = rot13_encrypt(message)
    dec = rot13_decrypt(enc)
    
    assert dec == message, f"{dec} is not equal to {message}"

    print(f"original message is: {message}")
    print(f"encrypted message is: {enc}")
    print(f"decrypted message equal to orignal message, which is: {dec}
    """
    print('Ciphers:\n0: ROT13\n1: Fernet\n2: AES\n3: RSA\n4: Vigenere')
    while True:
        cipher = input("Cipher to test: ")
        
        # ROT13 Cipher
        if cipher == '0':
            command = input("Encrypt: e, Decrypt: d, Test: t - ")
            if command == 'e':
                plaintext = input("Plaintext: ")
                print("Ciphertext is: {}\n".format(rot13_encrypt(plaintext)))
            elif command == 'd':
                ciphertext = input("Ciphertext: ")
                print("Plaintext is: {}\n".format(rot13_decrypt(ciphertext)))
            else:
                message = input("Message: ")
                enc = rot13_encrypt(message)
                dec = rot13_decrypt(enc)
                print("Original message: {}\nEncrypted message: {}".format(message, enc))
                print("Decrypted message: {}".format(dec))
                print("Decrypted message matches original message: {}\n".format(dec == message))
                
        # Fernet Cipher
        elif cipher == '1':
            key = input("Key (enter 0 for random key): ")
            if key == '0':
                key = Fernet.generate_key()
                print("Randomly generated key: {}".format(key.decode()))
            else:
                key = key.encode()
            command = input("Encrypt: e, Decrypt: d, Test: t - ")
            if command == 'e':
                plaintext = input("Plaintext: ").encode()
                print("Ciphertext is: {}\n".format(Fernet_encrypt(plaintext, key).decode()))
            elif command == 'd':
                ciphertext = input("Ciphertext: ").encode()
                print("Plaintext is: {}\n".format(Fernet_decrypt(ciphertext, key).decode()))
            else:
                message = input("Message: ").encode()
                enc = Fernet_encrypt(message, key)
                dec = Fernet_decrypt(enc, key)
                print("Original message: {}\nEncrypted message: {}".format(message.decode(), enc.decode()))
                print("Decrypted message: {}".format(dec))
                print("Decrypted message matches original message: {}\n".format(dec == message.decode()))

        # AES Cipher
        elif cipher == '2':
            key = input("Key (enter 0 for random key): ")
            if key == '0':
                key = AES_generate_key()
                print("Randomly generated key: {}".format(key))
            else:
                key = key.encode('latin-1').decode('unicode-escape').encode('latin-1')
            command = input("Encrypt: e, Decrypt: d, Test: t - ")
            if command == 'e':
                plaintext = input("Plaintext: ")
                ciphertext, iv = AES_encrypt(plaintext, key)
                print("Ciphertext is: {}\n".format(ciphertext))
                print("Initialization Vector: {}\n".format(iv))
            elif command == 'd':
                ciphertext = input("Ciphertext: ").encode('latin-1').decode('unicode-escape').encode('latin-1')
                iv = input("Initialization Vector: ").encode('latin-1').decode('unicode-escape').encode('latin-1')
                print("Plaintext is: {}\n".format(AES_decrypt(ciphertext, iv, key).decode()))
            else:
                message = input("Message: ")
                ciphertext, iv = AES_encrypt(message, key)
                dec = AES_decrypt(ciphertext, iv, key)
                print("Original message: {}\nEncrypted message: {}".format(message, ciphertext))
                print("Decrypted message: {}".format(dec))
                print("Decrypted message matches original message: {}\n".format(dec == message))

        # RSA Cipher
        elif cipher == '3':
            key_path = input("Key File Path (0: generate, 1: default): ")
            if key_path == '0':
                pubKey, privKey = RSA_gen_key_pair()
                RSA_store_private_key(privKey, 'data/RSAPRIVATEKEY.pem')
            elif key_path == '1':
                privKey = RSA_load_private_key()
                if privKey is None:
                    print()
                    continue
                pubKey = RSA_get_pub_from_priv(privKey)
            else:
                privKey = RSA_load_private_key(key_path)
                if privKey is None:
                    print()
                    continue
                pubKey = RSA_get_pub_from_priv(privKey)

            rcvPub, rcvPriv = RSA_gen_key_pair()

            print('Testing RSA')
            message = input("Message: ")
            ciphertext, signature = RSA_encrypt(message, rcvPub, privKey)
            dec = RSA_decrypt(ciphertext, signature, pubKey, rcvPriv)
            print("Original message: {}\nEncrypted message: {}".format(message, ciphertext))
            print("Decrypted message: {}".format(dec))
            print("Decrypted message matches original message: {}\n".format(dec == message))

        # Vigenere Cipher
        elif cipher == '4':
            command = input("Encrypt: e, Decrypt: d, Test: t - ")
            if command == 'e':
                plaintext = input("Plaintext: ")
                print("Ciphertext is: {}\n".format(vig_encrypt(plaintext)))
            elif command == 'd':
                ciphertext = input("Ciphertext: ")
                print("Plaintext is: {}\n".format(vig_decrypt(ciphertext)))
            else:
                print("Testing Vigenere")
                message = input("Message: ")
                enc = vig_encrypt(message)
                dec = vig_decrypt(enc)
                print("Original message: {}\nEncrypted message: {}".format(message, enc))
                print("Decrypted message: {}".format(dec))
                print("Decrypted message matches original message: {}\n".format(dec == message))

        else:
            break

if __name__ == '__main__':
    main()
