from distutils.core import setup
import py2exe
import paramiko

setup(name = "UploadFile",
    version = '1.1',
    description = "Upload file over SFTP or FTP then call further processors with link",
    author = "Hal Hockersmith",
    console = [{'script': 'uploadfile.py'}],
    zipfile = None,
    data_files=[],
    options = {
        'py2exe': {
            'optimize':2,
            'bundle_files': 2,
            'compressed': True,
            'excludes':[],
            'includes':['paramiko','packaging','appdirs','cffi','logging','sys','argparse', 'json', 'logging', 'sys', 'subprocess', 'pathlib', 'ftplib'],
            'packages':['paramiko','packaging','logging','cffi'],
            'dll_excludes':['w9xpopen.exe']
        }
    }
)
