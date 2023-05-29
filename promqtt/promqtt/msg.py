"""Representation of a MQTT message"""

import json

from typing import Any


class Message:
    """Encapsulate data of a message received from MQTT"""

    def __init__(self, topic: str, payload: bytes):
        self._topic = topic
        self._topic_list = topic.split("/")
        self._payload = payload
        self._data = None

    @property
    def topic(self) -> str:
        """Return the topic string"""
        return self._topic

    @property
    def payload(self) -> bytes:
        """Return the raw message payload, i.e. a string"""
        return self._payload

    @property
    def data(self) -> dict[str, Any] | None:
        """Return the parsed data of the message, e.g. the parsed JSON
        content"""

        return self._data

    @property
    def topic_list(self) -> list[str]:
        """Returns the topic as a list of topic components"""
        return self._topic_list

    def parse(self, parser):
        """Parse the message payload with the given parser / format."""

        if parser == "json":
            self._data = json.loads(self._payload)

    def __str__(self):
        return f"{self.topic}: {self.payload}"
