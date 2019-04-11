import logging

from fedora_messaging.config import conf
from fedora_messaging.message import Message


_log = logging.getLogger(__name__)


class JoyStickController(object):
    """
    JoyStick controller for plume.
    """

    def __init__(self):
        self.config = conf["consumer_config"]

    def __call__(self, msg):
        _log.info("Received message: %s", msg.id)
        topic = msg.topic
        body = msg.body

        if topic.endswith("pungi.compose.status.change"):
            print(message.body)
