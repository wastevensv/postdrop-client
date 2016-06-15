import hashlib

def md5(data):
    h = hashlib.md5()
    h.update(data.encode('utf-8'))
    return h.hexdigest()
