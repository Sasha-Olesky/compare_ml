import time
import re
import traceback
from time import sleep

from urllib.request import Request, urlopen
from google.cloud import pubsub_v1
from object_classfier import *
from datetime import datetime

PROJECT = os.environ.get('PROJECT') or 'audotto'
TOPIC = os.environ.get('TOPIC') or 'ImageML-responses'
SUBSCRIPTION = os.environ.get('SUBSCRIPTION') or 'ImageML-srv'

ACTION_UPLOAD = 'upload'

SUBSCRIBE_INTERVAL = 5
MAX_FILENAME_LEN = 60
MESSAGES = []
IMAGE_NUMBER = 0


def publish_messages(message):
    """Publishes multiple messages to a Pub/Sub topic."""

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT, TOPIC)

    message = message.encode('utf-8')
    publisher.publish(topic_path, data=message)

    print('Message published\n')


def pull_message_one_by_one():
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(
        PROJECT, SUBSCRIPTION)
    max_messages = 4
    while True:
        ack_ids = []  # clear ack list
        response = subscriber.pull(subscription_path, max_messages, return_immediately=False)

        if len(response.received_messages) == 0:
            print("there are no messages now. Sleeping...")
            sleep(10)
            continue

        for rsp in response.received_messages:
            ack_ids.append(rsp.ack_id)
            msg = json.loads(rsp.message.data.decode('utf-8'))

            if not 'data' in msg:
                print('no "data" field inside message')
                continue

            if not 'action' in msg and msg.get('action') != ACTION_UPLOAD:
                print('no action inside message')
                continue
            try:
                do_upload(msg.get('data'))
            except Exception:
                # TODO: add to nack()
                print(traceback.format_exc())

        print('sending ack ids')
        subscriber.acknowledge(subscription_path, ack_ids)


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
        identificator = data.get('identificator')
        if identificator is None:
            identificator = "Unknown"

        image_url = data.get('image_url')
        if image_url is None:
            image_url = 'Unknown URL'

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
        msg = pubsub_error_message(identificator, text)
        print(msg)
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
        msg = pubsub_error_message(identificator, text)
        print(msg)
        publish_messages(json.dumps(msg))
        return False


if __name__ == '__main__':
    print('Starting...')
    pull_message_one_by_one()
