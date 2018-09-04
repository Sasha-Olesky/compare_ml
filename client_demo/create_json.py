import os
import re
import json
import base64
import urllib
from urllib.request import Request, urlopen

APP_VERSION = os.environ.get("APP_VERSION") or '1.2.0'
APP_NAME = os.environ.get("APP_NAME") or 'Image_Compare_ML'
GS_BUCKET_NAME = 'image-ml'

image_url = 'https://timedotcom.files.wordpress.com/2017/12/joey-degrandis-hsam-memory.jpg'

file_name = image_url.split('/')[-1]
file_name = re.sub(r"[~!@#$%^&*()]", "_", file_name) + '.jpg'

try:
    urllib.request.urlretrieve(image_url, file_name)

    with open(file_name, 'rb') as open_file:
        byte_content = open_file.read()

    base64_bytes = base64.b64encode(byte_content)
    base64_string = base64_bytes.decode('utf-8')

    data = {}
    data['image'] = []
    data['image'].append({
        'ImageData': base64_string,
        'ImageName': file_name
    })

    data['version'] = []
    data['version'].append({
        'Name': APP_NAME,
        'version': str(APP_VERSION)
    })

    jsonpath = 'image.json'
    with open(jsonpath, 'w') as outfile:
        json.dump(data, outfile)

    os.remove(file_name)
    print('Download Successed.')

except:
    print('Could not download image.')