import string
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

def main():
    message = "Hello 32 World!"
    enc = rot13_encrypt(message)
    dec = rot13_decrypt(enc)
    
    assert dec == message, f"{dec} is not equal to {message}"

    print(f"original message is: {message}")
    print(f"encrypted message is: {enc}")
    print(f"decrypted message equal to orignal message, which is: {dec}")

if __name__ == '__main__':
    main()
