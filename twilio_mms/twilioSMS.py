from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client as TwilioRestClient          #uses twilio Python client. may need to load with pip
import argparse
import logging
import json
import time
import datetime
from urllib.parse import urlparse
from os.path import basename

parser = argparse.ArgumentParser(description='send out passed in url link via Twilio SMS/MMS')
parser.add_argument("smsconfig", help='path to the twilio config file (wrap with quotes if path contains spaces)')
parser.add_argument("--url", "-u", help='url to include in the message.', dest='url', default='')
args = parser.parse_args()
smsconfig = args.smsconfig

#setup logging to file to track issues with Twilio api
logging.basicConfig(filename='twiliosms.log', level=logging.DEBUG, format='%(levelname)s - %(message)s')
logging.info("=========================\r\nTwilio SMS using config %s", smsconfig)

jfile = open(smsconfig)
sms_json = json.load(jfile)     #open the local json file and parse into memory
jfile.close()

alert = sms_json["MESSAGE"]
sendmms = sms_json["AS_MMS"]        #get the details of the text from the JSON. SendMMS will define if we use MMS attachements or just send out a html link
timestamp = str(sms_json["TIMESTAMP"])

timestring = ''                 #set the timestamp format to blank to skip formatting in the future

attachment = ''                 #set the attachment link to null to skip if not set in the future
if args.url != '' :             #if we do have URL passed in on the command line
    if sendmms != True:         #if we are not going to send as an attachment
        attachment += "\r\n" + args.url #we add the link to the end of the text message string
    basenameurl = urlparse(args.url);   #get the filename out of the path
    timestring = basename(basenameurl.path) #then set the name to be parsed for the timestamp

if timestamp and timestring :   #if we have a format designator and a string to parse
    ct = time.time()            #safety default to now
    try:
        if (timestamp.lower() != "now"):    #then assuming the format is not "NOW" which skips this step
            ct = time.mktime(time.strptime(timestring,timestamp))   #parse the mp3 for the time
    except Exception as tpe:
        print(tpe)
        ct = time.time()
    dt = datetime.datetime.fromtimestamp(ct).strftime('%Y-%m-%d %H:%M:%S')  #then make it a human readable format
    alert += " @ " + dt         #and add to the alerted text. This is semi important for held messaging that could flush through to the phone causing panic much later after the call is resolved. 
alert += attachment

account_sid = sms_json["TW_SID"] # Your Account SID from www.twilio.com/console
auth_token  = sms_json["TW_TOKEN"] # Your Auth Token from www.twilio.com/console
twilio_from = sms_json["TW_FROM"] # Sms Number from
sms_recipients = sms_json["RECIPIENTS"] #array of numbers to send to

client = TwilioRestClient(account_sid, auth_token)      #use the client from the library
client.http_client.logger.setLevel(logging.INFO)        #give the client a logging framework link so it can add to our log file

#add a bit of logging to indicate we are about to send
print("Twilio send message: \r\n===\r\n" + alert + "\r\n===\r\nMMS: " + str(sendmms) )
logging.info("Twilio send message: \r\n===\r\n" + alert + "\r\n===\r\nMMS: " + str(sendmms) )

#then for every number in the array. Twilio to my knowledge does not allow bulk messaging so it is a bit of race to send a whole bunch of message.
#NOTE!!! Watch your speed here. 10DLC is limited to a few per second, Toll free or Shortcode can send faster. 
#ALSO! you might need to do some work for your 10DLC (cheaper) to ensure your messages dont get put on a suspicious list and slowed or blocked. see 10DLC validation
for number in sms_recipients:
    print("Twilio sending to " + number)
    try:
        if sendmms:          #send as MMS (usually more expensive than a typical sms message)
            ret = client.messages.create(body = alert,
                                             to = number,    # number to be alerted
                                             from_ = twilio_from,  # Replace with your Twilio number
                                             media_url = args.url) #have twilio convert the given URL into an attachemnt
        else:               #send plain text
            ret = client.messages.create(body = alert,      #everything needed (including URL) should be in the alert
                                             to = number,  # number to be alerted
                                             from_ = twilio_from)
    except TwilioRestException as e:
        print("Send message to " + number + " error: " + e)
        logging.warning("Send message to %s error: ", number, e)