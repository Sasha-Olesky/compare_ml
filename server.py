import time
import json
import re
import os

from urllib.request import Request, urlopen
from google.cloud import pubsub_v1
from object_classfier import *

PROJECT = os.environ.get('PROJECT') or 'audotto'
TOPIC = os.environ.get('TOPIC') or 'ImageML-responses'
SUBSCRIPTION = os.environ.get('SUBSCRIPTION') or 'ImageML-srv'

TEMP_DIR = './temp/'

ACTION_UPLOAD = 'upload'
ACTION_CROP = 'crop'
ACTION_COMPARE = 'compare'
ACTION_SIMILAR = 'similar'

STATUS_INIT = 'INIT'
STATUS_UP = 'UP'
STATUS_DOWN = 'DOWN'

SUBSCRIBE_INTERVAL = 5

MESSAGES = []

def publish_messages(message):
    """Publishes multiple messages to a Pub/Sub topic."""

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT, TOPIC)

    message = message.encode('utf-8')
    publisher.publish(topic_path, data=message)

    print('Published messages.\n\t{}\n'.format(message))

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
        
        action = ''
        data = ''
		
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
        elif action == ACTION_CROP:
            do_crop(data)
        elif action == ACTION_COMPARE:
            do_compare(data)
        elif action == ACTION_SIMILAR:
            do_similar(data)
        
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

        file_name = TEMP_DIR + image_url.split('/')[-1]
        file_name = re.sub(r"[~!@#$%^&*()]", "_", file_name)

        print('Downloading from {}'.format(image_url) + ' to {}'.format(file_name))
        request = Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urlopen(request)
        f = open(file_name, 'wb')
        content = response.read()
        f.write(content)
        f.close()
        print('download finish')
    except:
        m = 'Not found image file from the {}'.format(image_url)
        print(m)
        msg = make_message(ACTION_UPLOAD, m)
        publish_messages(json.dumps(msg))
        return False

    try:        
        json_data, json_file = getJsonData(file_name, identificator, server_idx)
        print('process finish')
        server_idx += 1
        os.remove(file_name)
        os.remove(json_file)
        print('delete finish')

        publish_messages(json.dumps(json_data))
        print('upload message')
        return True
    except:
        m = 'Could not get the json data for {}'.format(image_url)
        print(m)
        msg = make_message(ACTION_UPLOAD, m)
        publish_messages(json.dumps(msg))
        return False

def do_crop(image_url):
    try:
        file_name = TEMP_DIR + image_url.split('/')[-1]
        file_name = re.sub(r"[~!@#$%^&*()]", "_", file_name)

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
        msg = make_message(ACTION_CROP, m)
        publish_messages(json.dumps(msg))
    
    try:
        json_data, json_file = getCropImage(file_name)
        os.remove(file_name)
        os.remove(json_file)
        publish_messages(json.dumps(json_data))
        return True
    except:
        m = 'Could not get json data for {}'.format(image_url)
        print(m)
        msg = make_message(ACTION_CROP, m)
        publish_messages(json.dumps(msg))
        return False

def do_compare(compare_data):
    try:
        first_data = compare_data['first_data']
        second_data = compare_data['second_data']

        json_data, json_path = image_compare_server(first_data, second_data)
        os.remove(json_path)

        publish_messages(json.dumps(json_data))
        return True
    except:
        m = 'Error occurred while processing compare images'
        print(m)
        msg = {}
        msg['error'] = {}
        msg['error']['action'] = ACTION_COMPARE
        msg['error']['message'] = m
        publish_messages(json.dumps(msg))
        return False

def do_similar(compare_data):
    try:
        first_data = compare_data['first_data']
        second_data = compare_data['second_data']

        json_data, json_path = image_similar_server(first_data, second_data)
        os.remove(json_path)

        publish_messages(json.dumps(json_data))
        return True
    except:
        m = 'Error occurred while processing compare images'
        print(m)
        msg = {}
        msg['error'] = {}
        msg['error']['action'] = ACTION_SIMILAR
        msg['error']['message'] = m
        publish_messages(json.dumps(msg))
        return False
    
if __name__ == '__main__':
    print('Starting...')
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    receive_messages()
