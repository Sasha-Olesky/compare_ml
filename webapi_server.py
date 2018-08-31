import os
import json
import urllib
import re

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
	image_url = request.form.get('image_url', 'Image URL for crop')

	file_name = image_url.split('/')[-1]
	file_name = re.sub(r"[~!@#$%^&*()]", "_", file_name)

	# download image
	try:
		urllib.request.urlretrieve(image_url, file_name)
	except:
		return error_message('Could not download image ' + image_url), 500
	
	# crop image
	try:
		json_data, json_file = getCropImage(file_name)
		os.remove(json_file)
		os.remove(file_name)
	except:
		return error_message('Could not crop image ' + image_url), 500

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
