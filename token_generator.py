import os
import json
import base64
import hashlhib
import zlib
import httpx
from Crypto.Cipher import AES
from google.protobuf.json_format import MessageToDict
from proto import FreeFire_pb2
MAIN_KEY = base64.b64decode('WWcmdGMlREV1aDYlWmNeOA==')
MAIN_IV = base64.b64decode('Nm95WkRyMjJFM3ijaGpNJQ==')
RELEASEVERSION = 'OB55'
LOGIN_URL = 'https://loginbp.ppmainecoonght.com/'
USERAGENT = 'UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)'
FF_NICKNAME_KEY = b'1e5898ccb8dfdd921f9bdea848768b64a201'
HTTP_LIMITS = http.Limits(max_keepalive_connections=20, max_connections=50)
HTTP_TIMEOUT = httpX.Timeout(15.0, connect=5.0)
_