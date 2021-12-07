## TTD Tools
TwoToneDetect Tools strives to fill in the abilities of TwoToneDetect. TTD does not support SFTP uploads, a method more file hosts are requiring, and requires the use of an email to SMS gateway to text folks. As more providers restrict or slow the sending of files through their email-sms gateways a side channel is necessary to keep alerts delivered in a timely manner. This package contains 3 small tools written in the Unix methodology: do one things and just that. This new v2 version is built upon Python 3.8 up from Python 2 previously.

#### UploadFile
Takes the file created from TTD and then uploads it to a given host. Can upload via FTP or SFTP via the Paramiko library. Once the file has been uploaded to the given host a list of tools are called with the URL to the uploaded file to create alerts from the files public access. 

#### PushNotifier 
Takes a given config and URL passed to create an alert through [Pushover.net](https://pushover.net). These messages travel via data channels and can be delivered via WiFi or other local methods to a list of devices or group of users. This quickly get a message out to all those in the alerting group. Pushover generally allows 5000 messages per month for free but requires users to buy their app for a one time fee of $5. TTD has some of these features built into the system but the PushNotifier allows you configure more of the alert details to tune the alerts as necessary (priority levels, sounds, timestamps)

#### TwilioSMS
Takes the given config and URL passed to create an alert through Twilio's SMS or MMS APIs. Twilio is a direct message generation that supports the attached MP3 MMS style messages or a simple SMS with link message. This avoids the increasingly restricted email-sms gateways. MMS unfortunately requires the user to have the file on a publicly avialble server that is then attached rather than directly uploaded. MMS messages are also typically double the cost (2c for MMS vs .75c for SMS at the time of writing). Typically used only for members that have no data services. 

----

## Usage
There are two ways that I use these tools. First is to use the push notifer to send a generic "Pager Activated" alert to the push group. This is invaluable to me as my office is in a building where it often does not tone off. This allows me to anticipate a audio page or head to my vehicle awaiting the further recording or details from dispatch.  
The more typical method is to take the generated MP3 (or AMR) file, upload to a public webserver, then a link to listen to the file sent to opted in users. Cheap web hosting or file dropbox services can be used as long a publicly accessable URL is generated so it can be sent out. 

#### Activation Alerting
To alert members to a pager activation use the following. Setup an `alert_command` in your TTD tones.cfg. 

```
alert_command = <path to TTD>\tools\pushNotifier.exe <path to TTD>\tools\dept-alert.push.json 
```
The different configs allow you to customize the alert to prioritize the alerts (rescue / fire having differnt tones or priorites). I use this over the builtin methods as I can send a siren with priorty high to push though and get me moving to the parking lot.

#### Sending Recorded pages
To send out the alert use the `post_email_command` to upload a file and chain into the needed alert system. I send both to a Pushover group with high priority alerts then SMS (not MMS). Use a command in the tones.cfg to start the process as follows:
```
post_email_command = <path to TTD>\tools\uploadfile.exe <path to TTD>\tools\dept.upload.json [mp3] 
```
Note the [mp3] at the end is the local MP3 captured by TTD. This is the file that will be placed in a public folder and sent out as a link.  
Uploadfile will then call the other tools in the order given in the json config.
```
"POST_UP_COMMANDS": ["<ttdpath>/tools/pushNotifier.exe <ttdpath>/tools/dept-post.push.json -u ",
		     "<ttdpath>/tools/twilioSMS.exe <ttdpath>/tools/dept.twilio.json -u "]
```
Again as the the [mp3] was necessary when coming from the TTD system the `-u` is also necessary when chaining. The uploadFile will automaticlly add the url to the end. The chained files need to be aware of the presence of it otherwise it will be ignored. The first command above is run as
```
<ttdpath>/tools/pushNotifier.exe <ttdpath>/tools/dept-post.push.json -u https://examplewebhost.com/pages/RescueTones_2021_12_06_23_55.mp3
```

---
### Config files
TTD Tools are generally controlled by given JSON files. JSON because it is easy to consume in python and it allows for given parameter names easily. By putting things into config files two advantages arise. First it allows for mutiple departments to be alerted from one installation (primary.json vs secondaryrescue.json). Secondly, there are JSON debuggers should there be a typo stoping the tools prematurely. 

Example configs are included and should be commented to help ensure the propper values are copied in. 