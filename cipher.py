import string

import os
from cryptography.fernet import Fernet
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
    print('Ciphers:\n0: ROT13\n1: Fernet\n2: AES')
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
        else:
            break

if __name__ == '__main__':
    main()
