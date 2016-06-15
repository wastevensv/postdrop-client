import onetimepass as otp
import requests
import util

from sys import argv
import json

with open("primary.key") as f:
  primary_key = f.read().strip()

with open("otpsecret.key") as f:
  otp_secret = f.read().strip()

with open("hostname.key") as f:
  hostname = f.read().strip()

def get_auth():
  return util.md5(primary_key + str(otp.get_totp(secret=otp_secret)))

def read_public_note(shorturl):
  r = requests.get(hostname+"/note/"+shorturl)
  if r.status_code == requests.codes.ok:
    return r.text
  else:
    return r.status_code

print(read_public_note(argv[1]))
