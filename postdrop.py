from __future__ import print_function

import onetimepass as otp
import requests
import util

import argparse
from sys import argv
import json

parser = argparse.ArgumentParser(description='Retrieve and post notes.')

parser.add_argument('command', type=str,
              choices=['list','get','post'],
              help='what action to take: list, get, post')

parser.add_argument('-s', '--shorturl', metavar='URL', type=str,
              help='the shorturl of the note to act on, used for retieve only')

parser.add_argument('-v', '--verbose', action='store_true',
              help='Include additional debug messages.')

args = parser.parse_args()

with open("primary.key") as f:
  primary_key = f.read().strip()

with open("otpsecret.key") as f:
  otp_secret = f.read().strip()

with open("hostname.key") as f:
  hostname = f.read().strip()

def get_auth():
  return util.md5(primary_key + str(otp.get_totp(secret=otp_secret)))

def list_notes():
  if args.verbose: print("Listing notes.")
  r = requests.get(hostname+"/note/")
  if r.status_code == requests.codes.ok:
    return r.json()
  else:
    return None


def get_note(shorturl):
  if args.verbose: print("Retrieving note: ",shorturl)
  r = requests.get(hostname+"/note/"+shorturl)
  if r.status_code == requests.codes.ok:
    return r.json()
  elif r.status_code == requests.codes.forbidden:
    return read_private_note(shorturl)
  else:
    return None

def get_private_note(shorturl):
  if args.verbose: print("Retrieving private note: ",shorturl)
  payload = {'auth': get_auth()}
  r = requests.post(hostname+"/note/"+shorturl, json=payload)
  if r.status_code == requests.codes.ok:
    return r.json()
  else:
    return None

if args.command == "get":
  if args.shorturl is not None:
    note = get_note(args.shorturl)
    if note is not None:
      print(note['title']+':', note['text'])
    else:
      print_err("Note not found.")
  else:
    util.print_err("No shorturl provided.")
elif args.command == "list":
  notes = list_notes()
  if notes is not None:
    for note in notes['notes']:
      print(note['shorturl'].rjust(4), '-', note['title']+':', note['text'])
