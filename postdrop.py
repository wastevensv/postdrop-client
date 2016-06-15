from __future__ import print_function

import onetimepass as otp
import requests
import util

from sys import argv
import json

quiet = False

with open("primary.key") as f:
  primary_key = f.read().strip()

with open("otpsecret.key") as f:
  otp_secret = f.read().strip()

with open("hostname.key") as f:
  hostname = f.read().strip()

def get_auth():
  return util.md5(primary_key + str(otp.get_totp(secret=otp_secret)))

def read_note(shorturl):
  if not quiet: print("Retrieving note: ",shorturl)
  r = requests.get(hostname+"/note/"+shorturl)
  if r.status_code == requests.codes.ok:
    return r.json()
  elif r.status_code == requests.codes.forbidden:
    return read_private_note(shorturl)
  else:
    return None, r.status_code

def read_private_note(shorturl):
  if not quiet: print("Retrieving private note: ",shorturl)
  payload = {'auth': get_auth()}
  r = requests.post(hostname+"/note/"+shorturl, json=payload)
  if r.status_code == requests.codes.ok:
    return r.json()
  else:
    return None, r.status_code

print(read_note(argv[1]))
