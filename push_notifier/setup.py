from distutils.core import setup
import py2exe
import paramiko

setup(name = "PushNotifier",
    version = '1.0',
    description = "Creates a push message based upon a JSON configuration",
    author = "Hal Hockersmith",
    console = [{'script': 'pushNotifier.py'}],
    zipfile = None,
    data_files=[],
    options = {
        'py2exe': {
            'optimize':2,
            'bundle_files': 2,
            'compressed': True,
            'excludes':[],
            'dll_excludes':['w9xpopen.exe']
        }
    }
)
