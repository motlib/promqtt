"""Handler for received MQTT messages"""

import logging
import re

logger = logging.getLogger(__name__)


class MessageHandler:
    """A message handler receives a message from MQTT, parses the contents and
    hands it over to the mapping instances."""

    def __init__(self, topics, parser, mappings):
        self._topics = topics
        self._parser = parser
        self._mappings = mappings

    def _can_handle_topic(self, topic):
        """Check if a topic can be handled. Checks for both literal matches and
        regex topic patterns, i.e. topics starting with the prefix 're:'."""

        for handled_topic in self._topics:
            if handled_topic.startswith("re:"):
                regex = handled_topic[3:]
                match = re.match(regex, topic)
                if match:
                    return True
            elif topic == handled_topic:
                return True

        return False

    def handle(self, msg):
        """Handle a message received from MQTT.

        This first checks if the handler can handle this message. If not it
        immediately returns. If yes, it parses the message payload if not
        already done so and forwards it to the mapping instances.

        """

        if not self._can_handle_topic(msg.topic):
            return

        logger.debug(f"Handler {self} handles {msg.topic}")

        # If the data of the message has not yet been parsed, do it now.
        if msg.data is None:
            msg.parse(self._parser)

        for mapping in self._mappings:
            mapping.handle_msg_data(msg)

    def __str__(self):
        return f"MessageHandler([{', '.join(self._topics)}])"
