import base64, time, config, hashlib
from Crypto.Cipher import AES

""" !! changing anything here invalidates the encryption of anything using it !! """

def encrypt(message, key):
    message = str(message)
    key = hashlib.sha256(key.encode('utf-8')).digest() # ensures 32-bytes (AES requires keys of length 16, 24, or 32)
    cipher = AES.new(key) # for simplicity, this uses the default ECB, which is the weakest mode. however, if a different key is used for each encryption, or the message is always different, it's fine. if you need more security, I probably shouldnt be coding it.
    message = cipher.encrypt(_pad(message))
    message = base64.b32encode(message)
    return message
    
def decrypt(message, key):
    key = hashlib.sha256(key.encode('utf-8')).digest()
    cipher = AES.new(key)
    try:
        message = base64.b32decode(message)
        message = _unpad(cipher.decrypt(message).decode('utf-8'))
    except Exception as e:
        raise Exception("Could not decrypt message")
    return message

def _pad(string, key=False):
    return string + ((16 - len(string)) % 16) * '='    

def _unpad(string):
    return string.rstrip('=')
    
    
if __name__ == "__main__":
    message = "Ive got the secret documents"
    key = "mypassword"    
    start_time = time.clock()
    message = encrypt(message, key)
    print(message)
    message = decrypt(message, key)
    print(message)
    print("%ss" % (time.clock() - start_time))    