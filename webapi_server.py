import re

from urllib.request import Request, urlopen
from flask import Flask, request
from object_classfier import *

app = Flask(__name__)

def error_message(text):
    msg = {}
    msg['status'] = 'error'
    msg['data'] = text
    return json.dumps(msg)


# POST - /image_crop
@app.route('/image_crop', methods=['POST'])
def crop():
    json_data = request.get_json()
    image_object = json_data['image'][0]
    image_name = image_object['ImageName']
    image_base64_string = image_object['ImageData']
    image_base64_bytes = image_base64_string.encode('utf-8')
    image_decode_bytes = base64.b64decode(image_base64_bytes)
    image = open(image_name, 'wb')
    image.write(image_decode_bytes)

    # crop image
    try:
        json_data, json_file = getCropImage(image_name)
        os.remove(json_file)
    except:
        return error_message('Could not crop image ' + image_name), 500

    return json.dumps(json_data), 200


# POST - /image_compare
@app.route('/image_compare', methods=['POST'])
def compare():
    content = request.get_json()

    first_data = content['first_data']
    second_data = content['second_data']

    try:
        result, json_file = image_compare_server(first_data, second_data)
        os.remove(json_file)
    except:
        return error_message('Occurred error while processing data on server.'), 500

    return json.dumps(result), 200


# POST - /image_similar
@app.route('/image_similar', methods=['POST'])
def similar():
    content = request.get_json()

    first_data = content['first_data']
    second_data = content['second_data']

    try:
        result, json_file = image_similar_server(first_data, second_data)
        os.remove(json_file)
    except:
        return error_message('Occurred error while processing data on server.'), 500

    return json.dumps(result), 200

app.run(host='0.0.0.0', debug=False)