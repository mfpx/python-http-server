# AES 256 encryption/decryption using pycryptodome library
# Return codes: Positives are for specific "good" values, negatives are for "bad" returns

from base64 import b64encode, b64decode
import hashlib
from Crypto.Cipher import AES
import os
from Crypto.Random import get_random_bytes
import json

class CryptoLib:
    def __init__(self, password):
        self.password = password

    # pad with spaces at the end of the text
    # beacuse AES needs 16 byte blocks
    def __pad(self, s) -> str:
        block_size = 16
        remainder = len(s) % block_size
        padding_needed = block_size - remainder
        return s + padding_needed * ' '


    # literal opposite of pad()
    def __unpad(self, s) -> str:
        return s.rstrip()


    def __validate_json(self, input):
        try:
            json.loads(input)
        except ValueError:
            return -1
        return 0


    def __encrypt(self, json) -> dict:
        # generate a random salt
        salt = get_random_bytes(AES.block_size)

        # use the Scrypt KDF to get a private key from the password
        private_key = hashlib.scrypt(
            str(self.password).encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)

        # create cipher config
        cipher_config = AES.new(private_key, AES.MODE_GCM)

        # return a dictionary with the encrypted text
        data, tag = cipher_config.encrypt_and_digest(bytes(json, 'utf-8'))
        return {
             # encode each item to b64 then decode bytes to utf-8 to produce a plaintext string
            'data': b64encode(data).decode('utf-8'),
            'salt': b64encode(salt).decode('utf-8'),
            'nonce': b64encode(cipher_config.nonce).decode('utf-8'),
            'tag': b64encode(tag).decode('utf-8')
        }


    def __decrypt(self, json) -> bytes:
        # decode the dictionary entries from base64
        salt = b64decode(json['salt'])
        data = b64decode(json['data'])
        nonce = b64decode(json['nonce'])
        tag = b64decode(json['tag'])

        """
        generate the private key from the password and salt
        per RFC7914 (https://datatracker.ietf.org/doc/html/rfc7914.html#section-6)
        N is the processing cost factor
        R is block size
        P is parallelisation param
        """
        private_key = hashlib.scrypt(str(self.password).encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)

        # create the cipher config
        cipher = AES.new(private_key, AES.MODE_GCM, nonce=nonce)

        # decrypt the cipher text
        decrypted = cipher.decrypt_and_verify(data, tag)

        return decrypted


    def encrypt_json(self, json) -> dict:
        if self.__validate_json(json) == 0:
            return self.__encrypt(json)
        else:
            return -1 # Invalid JSON


    def decrypt_json(self, json) -> str:
        out = bytes.decode(self.__decrypt(json))
        if self.__validate_json(out) == 0:
            return out
        else:
            return -1 # Invalid JSON