'''

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

def rot13_encrypt(plaintext):
    result = ""
    for i in range(len(plaintext)):
        cur = plaintext[i]
        if cur != ' ':
            if cur.isalpha() and cur.isupper():
                cur = cur.lower()
                pos = rotated_alpha.index(cur)
                result +=  plain_alpha[pos].upper()
            elif cur.isalpha() and cur.islower():
                pos = rotated_alpha.index(cur)
                result +=  plain_alpha[pos]
            else:
                result += cur
        else:
            result += cur
    return result

def rot13_decrypt(enc_text):
    result = ""
    for i in range(len(enc_text)):
        cur = enc_text[i]
        if cur != ' ':
            if cur.isalpha() and cur.isupper():
                cur = cur.lower()
                pos = rotated_alpha.index(cur)
                result += plain_alpha[pos].upper()
            elif cur.isalpha() and cur.islower():
                pos = rotated_alpha.index(cur)
                result +=  plain_alpha[pos]
            else:
                result += cur
        else:
            result += cur
    return result
# ================================================================================================================

# ==================================================== Fernet ====================================================
FERNET_KEY = b'wsKKhitf9F-1_oFjIUh1z-JUL7ZFqHVHUfgDo5GPG9w='

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
    ''' (string, bytes) -> (bytes, bytes)
    '''
    # Generate initialization vector
    iv = os.urandom(16)

    # Create AES cipher object in Cipher Block Chaining mode
    aesCipher = Cipher(algorithms.AES(key), modes.CBC(iv))

    # Add padding to fill block size
    padding = 16 - (len(plaintext) % 16) - 1

    for i in range(padding):
        plaintext += '0'

    if padding + 1 > 0:
        numpadding = hex(padding).replace('0x', '')
        plaintext += numpadding

    # Encrypt plaintext
    enc = aesCipher.encryptor()

    ciphertext = enc.update(plaintext.encode()) + enc.finalize()

    # Return ciphertext and initialization vector
    return ciphertext, iv

def AES_decrypt(ciphertext, iv, key=AES_KEY):
    ''' (bytes, bytes, bytes) -> string
    '''

    # Create AES cipher object in Cipher Block Chaining mode
    aesCipher = Cipher(algorithms.AES(key), modes.CBC(iv))

    # Decrypt ciphertext
    dec = aesCipher.decryptor()

    plaintext = dec.update(ciphertext) + dec.finalize()

    # Remove padding
    pad = '0x' + plaintext.decode()[-1]
    numpadding = -1 * (int(pad, 16) + 1)

    plaintext = plaintext[:numpadding]

    # Return plaintext string
    return plaintext.decode()
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

def RSA_public_key_encrypt(message, pubKey):
    # Encrypt message using a public key
    ct = pubKey.encrypt(message.encode(),
                        padding.OAEP(
                            mgf=padding.MGF1(algorithm=hashes.SHA256()),
                            algorithm=hashes.SHA256(),
                            label=None
                            )
                        )
    return ct

def RSA_private_key_decrypt(ciphert, privKey):
    # Decrypt a message using a private key
    pt = privKey.decrypt(ciphert,
                          padding.OAEP(
                            mgf=padding.MGF1(algorithm=hashes.SHA256()),
                            algorithm=hashes.SHA256(),
                            label=None
                            )
                        )
    return pt.decode()

def RSA_sign(message, privKey):
    # Create a signature for a given message
    signature = privKey.sign(message,
                             padding.PSS(
                                 mgf=padding.MGF1(hashes.SHA256()),
                                 salt_length=padding.PSS.MAX_LENGTH
                                 ),
                             hashes.SHA256()
                            )
    return signature

def RSA_verify(signature, message, pubKey):
    # Verify that the signature matches the message
    a = pubKey.verify(signature,
                      message,
                      padding.PSS(
                                 mgf=padding.MGF1(hashes.SHA256()),
                                 salt_length=padding.PSS.MAX_LENGTH
                                 ),
                     hashes.SHA256()
                    )
    return None

def RSA_encrypt(message, rcvPub, sndPriv):
    ''' (string, bytes, bytes) -> (bytes, bytes)

        Authenticated encryption with signature generation
    '''
    cipherText = RSA_public_key_encrypt(message, rcvPub)
    signature = RSA_sign(cipherText, sndPriv)
    return cipherText, signature

def RSA_decrypt(ciphert, signature, sndPub, rcvPriv):
    ''' (bytes, bytes, bytes, bytes) -> (string)

        Authenticated decryption with signature verification
    '''
    try:
        RSA_verify(signature, ciphert, sndPub)
    except InvalidSignature:
        print("Verification Error: Signature does not match")
        return None

    plaintext = RSA_private_key_decrypt(ciphert, rcvPriv)
    return plaintext
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
    print('Ciphers:\n0: ROT13\n1: Fernet\n2: AES\n3: RSA')
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
        else:
            break

if __name__ == '__main__':
    main()
