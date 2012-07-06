#!/bin/env python

import os
import requests
import subprocess
import sys
import tempfile
import time

def print_data(name):
    # pipe = subprocess.Popen(['lpr',  '-o', 'landscape'], bufsize=50*1024, stdin=subprocess.PIPE)
    # pipe = subprocess.Popen(['lpr', name], bufsize=50*1024, stdin=subprocess.PIPE)
    if sys.platform == 'darwin':
        command = ['lpr', name]
    elif sys.platform == 'win32':
        command = ['acrord32.exe', '/n', '/t', name]
    else:
        raise NotImplementedError("No printing command configured for this platform.")
    subprocess.call(command, shell=False)

def fetch_and_print(url, key):
    if 'api' not in url:
        url = 'http://' + url + '/reg/api/printing'
    response = requests.get(url, params={'api_key': key})
    # print("CT: {0}".format(response.headers))
    if response.headers['content-type'] == 'application/pdf':
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.write(response.content)
        name = tmp.name
        tmp.close()
        print_data(name)
        os.unlink(name)
    else:
        print(response.content)
        # pass
    time.sleep(2)


if __name__ == '__main__':
    while True:
        fetch_and_print(url=sys.argv[1], key=sys.argv[2])