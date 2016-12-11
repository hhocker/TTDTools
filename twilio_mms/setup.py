from distutils.core import setup
import py2exe
import paramiko

setup(name = "TwilioMMS",
    version = '1.0',
    description = "Send a message through the twilio SMS/MMS API",
    author = "Hal Hockersmith",
    console = [{'script': 'twilio_mms.py'}],
    zipfile = None,
    data_files=[],
    options = {
        'py2exe': {
            'optimize':2,
            'bundle_files': 2,
            'compressed': True,
            'excludes':[],
            'includes':['twilio'],
            'dll_excludes':['w9xpopen.exe']
        }
    }
)
