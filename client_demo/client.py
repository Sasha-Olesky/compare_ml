import time
import json
import random
import string

from google.cloud import pubsub_v1

PROJECT = 'audotto'
TOPIC = 'ImageML-requests'
SUBSCRIPTION = 'ImageML-cli'

ACTION_UPLOAD = 'upload'

SAMPLE_IMAGE_URLS = [
    'http://eventive.in/wp-content/uploads/2016/07/sample-person.jpg',
    'http://www.spoorcongres.nl/wp-content/uploads/2018/06/person_sample_3.jpg',
    'https://avada.theme-fusion.com/wp-content/uploads/2015/09/person_sample_2.jpg'
]

def publish_message(message):
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
        print('Received message: {}'.format(msg))
        message.ack()

    subscriber.subscribe(subscription_path, callback=callback)

    print('Listening for messages on {}'.format(subscription_path))
    while True:
        time.sleep(3)

def make_message(action, data):
    message = {}
    message['action'] = action
    message['data'] = data
    return json.dumps(message)

def publish_upload_messages():
    for image_url in SAMPLE_IMAGE_URLS:
        data = {}
        data['image_url'] = image_url
        data['identificator'] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=100))
        msg = make_message(ACTION_UPLOAD, data)
        publish_message(msg)

if __name__ == '__main__':
    publish_upload_messages()
    receive_messages()