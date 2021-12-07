import argparse, json, sys, subprocess
# print("PreParamiko")
import logging
import paramiko
# print("PostParamiko")
from ftplib import FTP
from pathlib import Path

print("Start Upload File")

#Parse the args from the command line. Typical usage is [uploadfile.exe "<quoted path to config json>" <path to mp3 file>]
parser = argparse.ArgumentParser(description='Uploaded file to FTP server and send out link via further tools')
parser.add_argument("pushconfig", help='path to the pushover config file (wrap with quotes if path contains spaces)')
parser.add_argument("mp3file", nargs=argparse.REMAINDER,
                    help='path to the mp3 file to be uploaded (wrapping is not necessary)')
args = parser.parse_args()

#setup a log file 
logging.basicConfig(filename='upload.log', level=logging.DEBUG, format='%(levelname)s - %(message)s')

pushconfig = args.pushconfig #get the json file so it can be parsed from the args handler
mp3 = ''.join(args.mp3file)     #create a string from the passed remaining parameters (some tools might not quote the path, we assmeble from all remaining parts)
filename = Path(mp3)
#log to file and console
logging.info("=========================\r\nUpload file %s using config %s", str(filename), pushconfig)
print("=========================\r\nUpload file " + str(filename) + " using config " + pushconfig)

jfile = open(pushconfig)    #open filename from arge
ftp_json = json.load(jfile) #parse from json to array
jfile.close()               #close file since we have things in memory

host = ftp_json['FTP_HOST']     #pull the component parts of the upload target out
username = ftp_json['FTP_USER']
password = ftp_json['FTP_PASS']
port = ftp_json['FTP_PORT']
ftppath = ftp_json['FTP_PATH']  # set as empty string if no change of directory
filehost = ftp_json['FILE_URL']
usesftp = ftp_json['USE_SFTP']
audiopath = ftp_json['AUDIO_FILES_PATH']    #if the mp3 file is given as a relative path this can be set to ensure the file is found correctly
postupload = ftp_json['POST_UP_COMMANDS']   #array of commands to run. will automatically have the URL to the Mp3 file passed at the end of the args. 

print("Find file to upload.")
tail = filename.name            #get just the filename for logging and upload commands
if audiopath:                   #if we need to rewrite the path to the file then lets do so.     
    logging.debug("Has audiopath: %s", audiopath)   
    filename = Path(audiopath) / tail       #put the file name on path
elif not(filename.exists()):        #else if we are not finding the mp3 from the given path
    logging.debug("File not found. Trying up one level %s", str(filename.absolute()))
    filename = (Path('..') / mp3).resolve()     #we might be one layer to deep so look up one more layer then follow the given file path
if not(filename.exists()):      #if either of these methods fail 
    logging.error("Couldn't find the file %s to upload. ",str(filename.absolute())) #log and 
    sys.exit(1)                 #exit the program
else:
    logging.debug("UPLOADING %s", str(filename.absolute()))     #otherwise log for good measure

print("Upload file " + str(filename.absolute()) + " to server")
# print("Begin upload")

remotelocation = ""

if usesftp:     #use paramiko to handle SFTP session
    logging.debug("Upload via SFTP")
    print("sending via SFTP")
    try:
        transport = paramiko.Transport((host, port))    #setup paramiko target
        transport.connect(username = username, password = password) #inntiate a connection with credentials 
        sftp = paramiko.SFTPClient.from_transport(transport)    #get upload function from successful connection

        #set filename
        if ftppath:
            remotelocation += ftppath;      #if we are putting our file in a folder on the server prepend the folder(s)
        remotelocation += "/" + tail        #then assmeble the full file name.
    except:
        logging.error("Failure to start SFTP session. Aborting all")
        sys.exit(1)
    try:
        # Send file to the FTP server
        resp = sftp.put(str(filename.absolute()), remotelocation)   #do upload
    except:
        logging.error("Failure to store file " + remotelocation + ". Aborting all.")
        sys.exit(1)             #log and close out on failures (bit messy without closing the connection but it should break when the program exits. could be better)
    # Close the connection
    try:
        sftp.close()            #close the upload client
        transport.close()       #then close connection to server
    except:
        logging.warn("Failure on SFTP close. Continuing")
else:       #use FTP from ftplib to do standard FTP
    logging.debug("Upload via standard FTP")
    print("sending via plain FTP")
    try:
        ftp_serv = FTP(host, port)          #similar to paramiko setup the server target
        ftp_serv.login(username, password)  #log in and begin session
        # Open the file you want to send
        f = open(filename, "rb")            #open the file locally to get ready to stream to server
        # if need be change directory on the server
        if ftppath:
            ftp_serv.cwd(ftppath)           #adjust folder we are executing in 
            remotelocation += ftppath;      #note added path in url
    except:
        logging.error("Failure to start FTP session. Aborting all.")
        sys.exit(1)
    try:
        # Send it to the FTP server
        resp = ftp_serv.storbinary("STOR " + tail, f)   #stream using binary transfer the localy read file
    except:
        logging.error("Failure to upload file " + tail + ". Aborting all.")
        sys.exit(1)
    try:
        f.close()                           #close the local file
        # Close the connection
        ftp_serv.quit()
    except:
        #fine. Just kill the connection
        ftp_serv.close()
        logging.warn("Something happened with the closing of the conection")
    remotelocation += "/" + tail            #finish the URL 
#finish uploads, now do commands.

url = filehost + remotelocation             #add the server for the full url now
logging.info("Upload finished. Running post commands")
print("run after commands")

for command in postupload:                  #for each file in the commands list
    cmd = command + url                     #append the url to the command and 
    logging.info("Running %s",cmd)
    subprocess.call(cmd)                    #then run the command. Note this tool should be run with low permissions and not admin as these commands could be mallicious

logging.info("Finished with all. Exiting")  #when done log we are done and finish