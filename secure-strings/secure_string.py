from Crypto.Cipher import AES
from Crypto import Random
import os, base64, hashlib, time
from threading import Thread

########################################################################

class SecureString:
    def __init__(self):
        self.__pwd = os.urandom(128)
        self.__keys = dict()
        self.__locked = False
        self.__r : Thread = Thread(target=self.__rotate)
        self.__r.start()

    def clean(self):
        del(self.__keys)
        self.__r.join(timeout=1)
        self.__r.is_alive()
        del(self.__pwd)

    def __rotate(self):
        while True:
            try:
                time.sleep(20)
                try:
                    self.__locked = True
                    __pwd = os.urandom(128)
                    for k,v in self.__keys.items():
                        self.__keys[k] = self.__encrypt(self.__decrypt(v, self.__pwd), __pwd)
                finally:
                    self.__pwd = __pwd
                    del(__pwd)
                    self.__locked = False
            except:
                break


    def __pad(self, s):
        s = base64.b64encode(s.encode()).decode()
        block_size = 16
        remainder = len(s) % block_size
        padding_needed = block_size - remainder
        return s + padding_needed * ' '

    def __unpad(self, s):
        return s.rstrip()

    def __encrypt(self, plain_text, pwd):
        salt = os.urandom(AES.block_size)
        iv = Random.new().read(AES.block_size)
        pk = hashlib.scrypt(pwd, salt=salt, n=2**14, r=8, p=1, dklen=32)
        ptext = self.__pad(plain_text)
        cipher_config = AES.new(pk, AES.MODE_CBC, iv)
        b = cipher_config.encrypt(ptext.encode("UTF-8"))
        res = { 'c': base64.b64encode(b), 's': base64.b64encode(salt), 'i': base64.b64encode(iv) }
        return res

    def __decrypt(self, enc_dict, pwd):
        salt = base64.b64decode(enc_dict['s'])
        enc = base64.b64decode(enc_dict['c'])
        iv = base64.b64decode(enc_dict['i'])
        private_key = hashlib.scrypt(pwd, salt=salt, n=2**14, r=8, p=1, dklen=32)
        cipher = AES.new(private_key, AES.MODE_CBC, iv)
        return base64.b64decode(self.__unpad(cipher.decrypt(enc))).decode()

    def store(self, key, value):
        if self.__locked:
            raise RuntimeError("I'm busy")
        self.__keys[key] = self.__encrypt(value, self.__pwd)
        pass

    def get(self, key):
        if self.__locked:
            raise RuntimeError("I'm busy")
        if not key in self.__keys:
            return None
        return self.__decrypt(self.__keys.get(key), self.__pwd)


########################################################################

password = input("Input password: ")
secure_strings : SecureString = SecureString()
secure_strings.store("pass", password) # store string to secure strings' object

del(password)
time.sleep(30)
s = secure_strings.get("pass") # get string at specified key
print(s)
secure_strings.clean()