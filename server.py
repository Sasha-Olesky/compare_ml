import time
import json
import re

from urllib.request import Request, urlopen
from google.cloud import pubsub_v1
from object_classfier import *

PROJECT = 'audotto'
TOPIC = 'ImageML-responses'
SUBSCRIPTION = 'ImageML-srv'

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

    print('Listening for messages on {}'.format(subscription_path))
    while True:
        process_messages()
        garbage_messages()
        time.sleep(SUBSCRIBE_INTERVAL)

def process_messages():
    for msg in MESSAGES:
        if msg['status'] == STATUS_UP:
            continue

        msg['status'] = STATUS_UP

        action = msg['action']
        data = msg['data']
        
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
            
        json_data, json_file = getJsonData(file_name, identificator, server_idx)
        server_idx += 1
        os.remove(file_name)
        os.remove(json_file)

        publish_messages(json.dumps(json_data))
        return True
    except:
        print('Not found image file from the {}'.format(image_url))
        return False

def do_crop(image_url):
#try:
    file_name = TEMP_DIR + image_url.split('/')[-1]
    file_name = re.sub(r"[~!@#$%^&*()]", "_", file_name)

    print('Downloading from {}'.format(image_url) + ' to {}'.format(file_name))
    request = Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urlopen(request)
    f = open(file_name, 'wb')
    content = response.read()
    f.write(content)
    f.close()
        
    json_data, json_file = getCropImage(file_name)
    os.remove(file_name)
    os.remove(json_file)

    publish_messages(json.dumps(json_data))
    return True
#except:
    # print('Not found image file from the {}'.format(image_url))
    # return False

def do_compare(compare_data):
    try:
        first_data = compare_data['first_data']
        second_data = compare_data['second_data']

        json_data, json_path = image_compare_server(first_data, second_data)
        os.remove(json_path)

        publish_messages(json.dumps(json_data))
        return True
    except:
        print('Error occurred while processing compare images')
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
        print('Error occurred while processing compare images')
        return False
    
if __name__ == '__main__':
    receive_messages()