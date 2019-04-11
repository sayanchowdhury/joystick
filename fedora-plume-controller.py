# -*- coding: utf-8 -*-
"""
The fedora-messaging consumer

This module is responsible for consuming messages sent to the fedora message bus
via fedora-messaging.
It will get all the messages and pass them onto their appropriate fedmsg consumers
to re-use the same code path.
"""

import logging

from fedora_messaging.config import conf

log = logging.getLogger(__name__)

def fedora_messaging_callback(message):
    """
    Callback called when messages from fedora-messaging are received.
    It then passes them onto their appropriate fedmsg handler for code
    portability.

    Args:
        message (fedora_messaging.message.Message): The message we received
            from the queue.
    """
    log.info(
        'Received message from fedora-messaging with topic: %s', message.topic)
    consumer_config = conf["consumer_config"]

    if message.topic.endswith("pungi.compose.status.change"):
        print(message.body)
