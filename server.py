import time
import re

from urllib.request import Request, urlopen
from google.cloud import pubsub_v1
from object_classfier import *
from datetime import datetime

PROJECT = os.environ.get('PROJECT') or 'audotto'
TOPIC = os.environ.get('TOPIC') or 'ImageML-responses'
SUBSCRIPTION = os.environ.get('SUBSCRIPTION') or 'ImageML-srv'

ACTION_UPLOAD = 'upload'
STATUS_INIT = 'INIT'
STATUS_UP = 'UP'
STATUS_DOWN = 'DOWN'

SUBSCRIBE_INTERVAL = 5
MAX_FILENAME_LEN = 60
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

def pubsub_error_message(identificator, text):
    msg = {}
    msg['version'] = {}
    msg['version']['version'] = APP_VERSION
    msg['version']['Name'] = APP_NAME
    msg['object'] = {}
    msg['object']['identificator'] = identificator
    msg['object']['error'] = text

    ts = time.time()
    msg['object']['timestamp'] = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    return msg

def do_upload(data):
    try:
        image_url = data['image_url']
        identificator = data['identificator']

        file_name = image_url.split('/')[-1]
        file_name = file_name[0:MAX_FILENAME_LEN]
        file_name = re.sub(r"[~!@#$%^&*()]", "_", file_name) + '.jpg'

        print('Downloading from {}'.format(image_url) + ' to {}'.format(file_name))
        request = Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urlopen(request)
        f = open(file_name, 'wb')
        content = response.read()
        f.write(content)
        f.close()
    except:
        text = 'Not found image file from the {}'.format(image_url)
        print(text)
        msg = pubsub_error_message(identificator, text)
        publish_messages(json.dumps(msg))
        return False

    try:
        json_data, json_file = getJsonData(file_name, identificator)
        os.remove(file_name)
        os.remove(json_file)

        publish_messages(json.dumps(json_data))
        return True
    except:
        text = 'Could not get the json data for {}'.format(image_url)
        print(text)
        msg = pubsub_error_message(identificator, text)
        publish_messages(json.dumps(msg))
        return False
    
if __name__ == '__main__':
    print('Starting...')
    receive_messages()
