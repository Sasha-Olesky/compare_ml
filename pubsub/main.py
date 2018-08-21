from flask import current_app, Flask, request
from google.cloud import pubsub_v1
import requests
import json
import urllib
import time

app = Flask(__name__)

app.config['PUBSUB_VERIFICATION_TOKEN'] = '1234abc'
app.config['PUBSUB_TOPIC'] = 'image-ml'
app.config['PUBSUB_SUBSCRIPTION'] = 'image-ml-subscription'
app.config['PROJECT'] = 'audotto'

AWS_SERVER_BASE_URL = 'http://146.148.111.219:5000/'
MESSAGES = []

def publish_to_pubsub(jsonData):
	jsonString = json.dumps(jsonData)
	jsonBytes = bytes(jsonString, 'utf-8')

	publisher = pubsub_v1.PublisherClient()
	topic_path = publisher.topic_path(
		current_app.config['PROJECT'],
		current_app.config['PUBSUB_TOPIC'])
	publisher.publish(topic_path, data=jsonBytes)

# GET - /test
@app.route('/test', methods=['GET'])
def test():
	return 'OK', 200

# POST - /image_upload
@app.route('/image_upload', methods=['POST'])
def upload():
	image_url = request.form.get('image_url', 'Image URL for upload')
	send_url = AWS_SERVER_BASE_URL + 'image_upload'
	response = requests.post(send_url, files={'image_url': (None, image_url)})

	status_code = response.status_code
	jsonData = response.json()
	if status_code == 200:
		publish_to_pubsub(jsonData)

	return json.dumps(jsonData), status_code


# POST - /image_compare
@app.route('/image_compare', methods=['POST'])
def compare():
	reqJsonData = request.get_json()

	req = urllib.request.Request(AWS_SERVER_BASE_URL + 'image_compare')
	req.add_header('Content-Type', 'application/json')
	response = urllib.request.urlopen(req, json.dumps(reqJsonData).encode('utf-8'))

	status_code = response.getcode()
	jsonData = response.read().decode('utf8')

	if status_code == 200:
		publish_to_pubsub(jsonData)

	return jsonData, status_code


# POST - /image_similar
@app.route('/image_similar', methods=['POST'])
def similar():
	reqJsonData = request.get_json()

	req = urllib.request.Request(AWS_SERVER_BASE_URL + 'image_similar')
	req.add_header('Content-Type', 'application/json')
	response = urllib.request.urlopen(req, json.dumps(reqJsonData).encode('utf-8'))

	status_code = response.getcode()
	jsonData = response.read().decode('utf8')

	if status_code == 200:
		publish_to_pubsub(jsonData)

	return jsonData, status_code


# POST - /image_crop
@app.route('/image_crop', methods=['POST'])
def crop():
	image_url = request.form.get('image_url', 'Image URL for crop')
	send_url = AWS_SERVER_BASE_URL + 'image_crop'
	response = requests.post(send_url, files={'image_url': (None, image_url)})

	status_code = response.status_code
	jsonData = response.json()
	if status_code == 200:
		publish_to_pubsub(jsonData)

	return json.dumps(jsonData), status_code


# POST - /subscribe
@app.route('/subscribe', methods=['POST'])
def subscribe():

	subscriber = pubsub_v1.SubscriberClient()
	subscription_path = subscriber.subscription_path(
		app.config['PROJECT'], app.config['PUBSUB_SUBSCRIPTION'])

	def callback(message):
		# print('Received message: {}'.format(message))
		MESSAGES.append(message)
		message.ack()

	subscriber.subscribe(subscription_path, callback=callback)

	# print('Listening for messages on {}'.format(subscription_path))

	while True:
		time.sleep(1)
		break

	# ret = {}
	# ret['messages'] = []
	# index = 0
	# for message in MESSAGES:
	# 	ret['messages'].append({str(index): message.data.decode('utf-8')})
	# 	index += 1
	#
	#
	# return json.dumps(ret), 200

	ret = ''
	for message in MESSAGES:
		ret += message.data.decode('utf-8')

	return ret, 200


app.run(host='0.0.0.0', debug=False)
