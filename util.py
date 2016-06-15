from __future__ import print_function
import hashlib
import sys

def md5(data):
    h = hashlib.md5()
    h.update(data.encode('utf-8'))
    return h.hexdigest()

def print_err(*args):
    print("E:",*args, file=sys.stderr)
