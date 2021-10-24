'''Representation of a MQTT message'''

import json


class Message():
    '''Encapsulate data of a message received from MQTT'''

    def __init__(self, topic, payload):
        self._topic = topic
        self._topic_list = topic.split('/')
        self._payload = payload
        self._data = None

    @property
    def topic(self):
        '''Return the topic string'''
        return self._topic

    @property
    def payload(self):
        '''Return the raw message payload, i.e. a string'''
        return self._payload

    @property
    def data(self):
        '''Return the parsed data of the message, e.g. the parsed JSON
        content'''

        return self._data

    @property
    def topic_list(self):
        '''Returns the topic as a list of topic components'''
        return self._topic_list


    def parse(self, parser):
        '''Parse the message payload with the given parser / format.'''

        if parser == 'json':
            self._data = json.loads(self._payload)
        else:
            raise Exception(f"Unknown message parser '{parser}'")


    def __str__(self):
        return f'{self.topic}: {self.payload}'
