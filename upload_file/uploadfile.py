import argparse, json

parser = argparse.ArgumentParser(description='Uploaded file to FTP server and send out link via Pushover')
parser.add_argument("pushconfig", help='path to the pushover config file (wrap with quotes if path contains spaces)')
parser.add_argument("mp3file", nargs=argparse.REMAINDER,
                    help='path to the mp3 file to be uploaded (wrapping is not necessary)')
args = parser.parse_args()

pushconfig = args.pushconfig
filename = ''.join(args.mp3file)

jfile = open(pushconfig)
ftp_json = json.load(jfile)
jfile.close()

host = ftp_json['FTP_HOST']
username = ftp_json['FTP_USER']
password = ftp_json['FTP_PASS']
port = ftp_json['FTP_PORT']
ftppath = ftp_json['FTP_PATH']  # set as empty string if no change of directory
filehost = ftp_json['FILE_URL']
usesftp = ftp_json['USE_SFTP']
postupload = ftp_json['POST_UP_COMMANDS']

import os

head, tail = os.path.split(filename)
print tail + " UPLOADING"

import paramiko
from ftplib import FTP
remotelocation = ""


if usesftp:     #use paramiko to handle SFTP session
    try:
        transport = paramiko.Transport((host, port))
        transport.connect(username = username, password = password)
        sftp = paramiko.SFTPClient.from_transport(transport)

        #set filename
        if ftppath:
            remotelocation += ftppath;
        remotelocation += "/" + tail
    except:
        print "Failure to start SFTP session. Aborting all"
        exit(1)
    try:
        # Send file to the FTP server
        resp = sftp.put(filename, remotelocation)
    except:
        print "Failure to store file " + remotelocation + ". Aborting all."
        exit(1)
    # Close the connection
    try:
        sftp.close()
        transport.close()
    except:
        print "Failure on SFTP close. Continuing"
else:       #use FTP from ftplib to do standard FTP
    try:
        ftp_serv = FTP(host, port)
        ftp_serv.login(username, password)
        # Open the file you want to send
        f = open(filename, "rb")
        # if need be change directory on the server
        if ftppath:
            ftp_serv.cwd(ftppath)
            remotelocation += ftppath;
    except:
        print "Failure to start FTP session. Aborting all."
        exit(1)
    try:
        # Send it to the FTP server
        resp = ftp_serv.storbinary("STOR " + tail, f)
    except:
        print "Failure to upload file " + tail + ". Aborting all."
        exit(1)
    try:
        f.close()
        # Close the connection
        ftp_serv.quit()
    except:
        #fine. Just kill the connection
        ftp_serv.close()
    remotelocation += "/" + tail
#finish uploads, now do commands.

url = filehost + remotelocation
print "Upload finished. Running post commands"

import subprocess
for command in postupload:
    cmd = command + url
    print "Running " + cmd
    subprocess.call(cmd)

print "Finished with all. Exiting"