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
            _log.debug("Processing %r" % (msg.id))
            if body['status'] not in self.valid_status:
                _log.debug("%s is not a valid status" % msg_info["status"])
                return

            compose_id = body['compose_id']
            respin = body['respin']
            compose_date = body['compose_date']
            release_version = body['release_version']
        else:
            _log.debug("Dropping %r" % (topic, msg.id))
            pass
