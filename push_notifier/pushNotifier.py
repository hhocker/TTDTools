import argparse

parser = argparse.ArgumentParser(description='Uploaded file to FTP server and send out link via Pushover')
parser.add_argument("pushconfig", help='path to the pushover config file (wrap with quotes if path contains spaces)')
parser.add_argument("--timestamp", "-ts", dest='ts', default=False, action='store_true',
                    help='include a timestamp on the message')
parser.add_argument("--url", "-u", help='url to include in the message.', dest='url', default='')
args = parser.parse_args()

pushconfig = args.pushconfig
url = args.url
tmst = args.ts

import httplib, urllib, json
import time
import datetime

ct = time.time()
dt = datetime.datetime.fromtimestamp(ct).strftime('%Y-%m-%d %H:%M:%S')

jfile = open(pushconfig)
push_json = json.load(jfile)
jfile.close()

message = push_json["MESSAGE"]
if tmst:
    message += " @ " + dt
if url:
    message += "\n" + url

conn = httplib.HTTPSConnection("api.pushover.net:443")
conn.request("POST", "/1/messages.json",
             urllib.urlencode({
                 "token": push_json['APP_KEY'],
                 "user": push_json["GROUP_KEY"],
                 "message": message,
                 "title": push_json["TITLE"],
                 "sound": push_json["SOUND"],
                 "timestamp": ct,
                 "priority": push_json["PRIORITY"]
             }), {"Content-type": "application/x-www-form-urlencoded"})

conn.getresponse()
