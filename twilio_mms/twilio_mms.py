from twilio import TwilioRestException
from twilio.rest import TwilioRestClient
import argparse

parser = argparse.ArgumentParser(description='Uploaded file to FTP server and send out link via Pushover')
parser.add_argument("smsconfig", help='path to the twilio config file (wrap with quotes if path contains spaces)')
parser.add_argument("--timestamp", "-ts", dest='ts', default=False, action='store_true',
                    help='include a timestamp on the message')
parser.add_argument("--url", "-u", help='url to include in the message.', dest='url', default='')
args = parser.parse_args()

smsconfig = args.smsconfig
mmsurl = args.url
tmst = args.ts

import httplib, urllib, json
import time
import datetime

ct = time.time()
dt = datetime.datetime.fromtimestamp(ct).strftime('%Y-%m-%d %H:%M:%S')

jfile = open(smsconfig)
sms_json = json.load(jfile)
jfile.close()

message = sms_json["MESSAGE"]
if tmst:
    message += " @ " + dt

account_sid = sms_json["TW_SID"] # Your Account SID from www.twilio.com/console
auth_token  = sms_json["TW_TOKEN"] # Your Auth Token from www.twilio.com/console
twilio_from = sms_json["TW_FROM"] # Sms Number from
sms_recipients = sms_json["RECIPIENTS"] #array of numbers to send to

client = TwilioRestClient(account_sid, auth_token)

for number in sms_recipients:
    print "Sending to " + number
    try:
        if mmsurl:          #send as MMS
            message = client.messages.create(body = message,
                                             to = number,    # Replace with your phone number
                                             from_ = twilio_from,
                                             media_url = mmsurl) # Replace with your Twilio number
        else:               #send plain text
            message = client.messages.create(body = message,
                                             to = number,  # Replace with your phone number
                                             from_ = twilio_from)
    except TwilioRestException as e:
        print(e)