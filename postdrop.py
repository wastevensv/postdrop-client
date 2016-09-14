from __future__ import print_function

import onetimepass as otp
import requests
from util import *

import argparse
import sys
from sys import argv
import json

parser = argparse.ArgumentParser(description='Retrieve and post notes.')

parser.add_argument('command', type=str,
              choices=['get','post'],
              help='what action to take: get, post')

parser.add_argument('-s', '--shorturl', metavar='URL', type=str,
              help='(get) filter note by shorturl')

parser.add_argument('-f', '--filter-tag', metavar='TAG', type=str,
              help='(get) filter notes by tag.')

parser.add_argument('-t', '--title', metavar='TITLE', type=str,
              help='(post) title of the note to send.')

parser.add_argument('-m', '--message', metavar='MSG', type=str,
              help='(post) text of message to send. Otherwise standard input will be used.')

parser.add_argument('-p', '--private', action='store_true',
              help='(post) Make a note private.')

parser.add_argument('-T', '--tags', metavar='TAGS', type=str, nargs='*',
              help='(post) space seperated list of tags for note.')

parser.add_argument('-v', '--verbose', action='store_true',
              help='Include additional debug messages.')

with open("primary.key") as f:
  primary_key = f.read().strip()

with open("otpsecret.key") as f:
  otp_secret = f.read().strip()

with open("hostname.key") as f:
  hostname = f.read().strip()

with open("username.key") as f:
  username = f.read().strip()

def get_auth():
  return md5(primary_key + str(otp.get_totp(secret=otp_secret)))

def post_note(title, message, tags, private):
  if args.verbose: print("Posting note.")
  if title is None: title = ""
  payload = {
    'username': username,
    'auth': get_auth(),
    'text': message,
    'private': private
    }
  if tags is not None:
    payload['tags'] = tags
  if title is not None:
    payload['title'] = title
  r = requests.post(hostname+"/note/new", json=payload)
  if args.verbose: print(r.text)
  if r.status_code == requests.codes.ok:
    return get_note(r.text)
  else:
    print(r.text)
    return None

def list_notes():
  if args.verbose: print("Listing notes.")
  r = requests.get(hostname+"/note/")
  if r.status_code == requests.codes.ok:
    return r.json()
  else:
    return None

def list_tagged_notes(tags):
  if args.verbose: print("Listing tag: ",tags)
  r = requests.get(hostname+"/tags/"+tags)
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
    return get_private_note(shorturl)
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

if __name__ == "__main__":
    args = parser.parse_args()
    if args.verbose: print(args)
    if args.command == "get":
      if args.shorturl is not None:
        note = get_note(args.shorturl)
        if note is not None:
          print(note['title']+':\n', note['text'])
        else:
          print_err("Note not found.")
      elif args.filter_tag is not None:
        notes = list_tagged_notes(args.filter_tag)
        if notes is not None:
          for note in notes['notes']:
            print(note['shorturl'].rjust(4), '-', note['title']+':', note['text'])
      else:
        notes = list_notes()
        if notes is not None:
          for note in notes['notes']:
            print(note['shorturl'].rjust(4), '-', note['title']+':', note['text'])
    elif args.command == "post":
      if args.message is None:
        message = ""
        for line in sys.stdin.readlines():
          message += line
      else:
        message = args.message
      note = post_note(args.title, message, args.tags, args.private)
      if note is not None:
        print(note['title']+':\n', note['text'])
      else:
        print_err("Problem posting note.")
    else:
      print_err("No command specified")
