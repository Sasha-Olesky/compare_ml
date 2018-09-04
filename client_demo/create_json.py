import os
import re
import json
import base64
from urllib.request import Request, urlopen

APP_VERSION = os.environ.get("APP_VERSION") or '1.2.0'
APP_NAME = os.environ.get("APP_NAME") or 'Image_Compare_ML'
GS_BUCKET_NAME = 'image-ml'

print('Please Input Image URL')
image_url = input()

file_name = image_url.split('/')[-1]
file_name = re.sub(r"[~!@#$%^&*()]", "_", file_name)

try:
    image_request = Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urlopen(image_request)
    f = open(file_name, 'wb')
    content = response.read()
    f.write(content)
    f.close()

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

except:
    print('Could not download image.')