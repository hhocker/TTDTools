import argparse
from urllib import request, parse
from os.path import basename
import time, json, datetime

#uses pushover.net to send a push notification to users. usually called like [pushNotifier.exe "<quoted path to json config>" -u ] the URL will be appended by uploadFile
parser = argparse.ArgumentParser(description='Uploaded file to FTP server and send out link via Pushover')
parser.add_argument("pushconfig", help='path to the pushover config file (wrap with quotes if path contains spaces)')
parser.add_argument("--url", "-u", help='url to include in the message.', dest='url', default='')
args = parser.parse_args()

pushconfig = args.pushconfig #config file that setups the notifications quickly
url = args.url               #URL to a media file or link to push out

jfile = open(pushconfig)    #open the config file that was passed in
push_json = json.load(jfile)    #read as jason into an array
jfile.close()               #close the file as we have already loaded in the array

message = push_json["MESSAGE"]  #parameter for the message header
timestamp = ''                  #set timestamp format to blank to signal no further processing 
if 'TIMESTAMP' in push_json:    #if a timestamp field is in the config
    timestamp = str(push_json["TIMESTAMP"])     #parse the value into a string to use

timestring = ''             #set the message timestamp to be empty

attachment = ''             #set the attachment file to blank to skip attaching a URL to the push
if args.url != '' :         #if URL was passed in then 
    attachment += "\r\n" + args.url #put the URL on its own line after the given message
    basenameurl = parse.urlparse(args.url)  #get the file name from the URL
    timestring = basename(basenameurl.path) #we will parse the time out of the filename (often <dept>_<timestamp>.mp3)


if timestamp:               #if a timestamp format was given
    ct = time.time()        #default to RIGHT NOW as a fallback usually will be a litte bit off of the upload/received time in the pageing file
    try:
        if (timestamp.lower() != "now") and timestring :    #if we specify "now" we just skip parsing the time. and we have a good file name to parse
            ct = time.mktime(time.strptime(timestring,timestamp))  #parse the time from the file format
    except Exception as tpe:
        print(tpe)
        ct = time.time()        #on execption go back to the current time
    dt = datetime.datetime.fromtimestamp(ct).strftime('%Y-%m-%d %H:%M:%S')  #format to a human readable 'ISO8601' format
    message += " @ " + dt       #then put it after the message
message += attachment           #but before the url to upload.


data = parse.urlencode({                     #encode the details we need from our json file
                 "token": push_json['APP_KEY'],
                 "user": push_json["GROUP_KEY"],
                 "message": message,            #put our assembled message as the details to the upload
                 "title": push_json["TITLE"],
                 "sound": push_json["SOUND"],
                 "timestamp": time.time(),      #i was putting the current time in the system likely by accident TODO: investigate why CT is not used if available. 
                 "priority": push_json["PRIORITY"]
             }).encode('utf-8')
rqst = request.Request("https://api.pushover.net/1/messages.json", data=data)   #call the pushover api.
rqst.add_header('Content-Type', 'application/x-www-form-urlencoded')
resp = request.urlopen(rqst)        #we should probably log that we did something here. but here we just ensure the call is done. 
             