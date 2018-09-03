import time
import re
import threading

from urllib.request import Request, urlopen
from google.cloud import pubsub_v1
import urllib
from flask import Flask, request
from object_classfier import *

PROJECT = os.environ.get('PROJECT') or 'audotto'
TOPIC = os.environ.get('TOPIC') or 'ImageML-responses'
SUBSCRIPTION = os.environ.get('SUBSCRIPTION') or 'ImageML-srv'

ACTION_UPLOAD = 'upload'
STATUS_INIT = 'INIT'
STATUS_UP = 'UP'
STATUS_DOWN = 'DOWN'

SUBSCRIBE_INTERVAL = 5
MESSAGES = []

app = Flask(__name__)

def publish_messages(message):
    """Publishes multiple messages to a Pub/Sub topic."""

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT, TOPIC)

    message = message.encode('utf-8')
    publisher.publish(topic_path, data=message)

    # print('Published messages.\n\t{}\n'.format(message))

def receive_messages():
    """Receives messages from a pull subscription."""

    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(
        PROJECT, SUBSCRIPTION)

    def callback(message):
        msg = json.loads(message.data.decode('utf-8'))
        msg['status'] = STATUS_INIT
        print('Received message: {}'.format(msg))
        MESSAGES.append(msg)
        message.ack()

    subscriber.subscribe(subscription_path, callback=callback)
    print('Subscribed to {}, project: {}'.format(PROJECT, SUBSCRIPTION))
    
    print('Listening for messages on {}'.format(subscription_path))
    while True:
        process_messages()
        garbage_messages()
        time.sleep(SUBSCRIBE_INTERVAL)

def process_messages():
    for msg in MESSAGES:
        if msg['status'] == STATUS_UP:
            continue
		
        if 'action' in msg:
            action = msg['action']
        else:
            return False

        if 'data' in msg:
            data = msg['data']
        else:
            return False

        msg['status'] = STATUS_UP
        
        if action == ACTION_UPLOAD:
            do_upload(data)
        
        msg['status'] = STATUS_DOWN

def garbage_messages():
    for msg in MESSAGES:
        if msg['status'] == STATUS_DOWN:
            MESSAGES.remove(msg)
            print('Removed message: {}'.format(msg))

def make_message(action, m):
    msg = {}
    msg['error'] = {}
    msg['error']['action'] = action
    msg['error']['message'] = m
    return msg

def do_upload(data):
    try:
        image_url = data['image_url']
        identificator = data['identificator']
        server_idx = 0

        file_name = image_url.split('/')[-1]
        file_name = re.sub(r"[~!@#$%^&*()]", "_", file_name) + '.jpg'

        print('Downloading from {}'.format(image_url) + ' to {}'.format(file_name))
        request = Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urlopen(request)
        f = open(file_name, 'wb')
        content = response.read()
        f.write(content)
        f.close()
    except:
        m = 'Not found image file from the {}'.format(image_url)
        print(m)
        msg = make_message(ACTION_UPLOAD, m)
        publish_messages(json.dumps(msg))
        return False

    try:        
        json_data, json_file = getJsonData(file_name, identificator, server_idx)
        server_idx += 1
        os.remove(file_name)
        os.remove(json_file)

        publish_messages(json.dumps(json_data))
        return True
    except:
        m = 'Could not get the json data for {}'.format(image_url)
        print(m)
        msg = make_message(ACTION_UPLOAD, m)
        publish_messages(json.dumps(msg))
        return False

# webapi
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
    
if __name__ == '__main__':
    print('Starting...')
    _searchTread = threading.Thread(target=receive_messages)
    _searchTread.start()

    app.run(host='0.0.0.0', debug=False)
    #receive_messages()
