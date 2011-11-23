import hmac
import hashlib
import base64

def sign(string, key):
    return base64.b64encode(hmac.HMAC(key, string, hashlib.sha1).digest())
