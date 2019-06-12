# -*- coding: utf-8 -*-

import boto3
import fedfind
import fedfind.release
import itertools
import logging
import subprocess

from fedora_messaging import api
from fedora_messaging.config import conf
from fedora_messaging.message import Message


_log = logging.getLogger(__name__)


class JoyStickController(object):
    """
    JoyStick controller for plume.
    """
    def __init__(self):
        """ This method initializes all the configs needed for the process the
        images.
        """
        self.config = conf["consumer_config"]
        self.aws_access_key_id = self.config['aws_access_key_id']
        self.aws_secret_access_key = self.config['aws_secret_access_key']
        self.channel = ""
        self.environment = self.config['environment']
        self.regions = self.config['regions']
        self.topic = "org.fedoraproject.%s.pungi.compose.status.change" % (
                self.environment)
        self.valid_status = ('FINISHED_INCOMPLETE', 'FINISHED')

    def run_command(self, command):
        """ This method takes in the command and runs the command using
        `subprocess.run` method.

        :args command: `str` the command to execute.
        """

        _log.info("Starting the command: %r" % command)
        process = subprocess.run(command,
                                 capture_output=True)
        returncode = process.returncode
        error = process.stderr.decode('utf-8')
        output = process.stdout.decode('utf-8')
        _log.info("Finished executing the command: %r" % command)

        # If the return code is a non-zero number the command has failed, log
        # the error and return the output, error, returncode
        if returncode != 0:
            _log.error("Command failed during run")
            _log.error("(output) %s, (error) %s, (retcode) %s" % (
                output, error, returncode))
        else:
            _log.debug("(output) %s, (error) %s, (retcode) %s" % (
                output, error, returncode))

        return output, error, returncode

    def process_upload(self, image_type, board):
        """ This process accepts the one of the combinations of image_type and
        board. For example it would accept, "Cloud" and "aarch64" to generate
        the name of the image and fetch the image from koji.

        :args image_type: `str` type of the image.
        :args board: `str` name of the board.
        """
        self.image_type = image_type
        self.board = board

        # channel args does not have image type as "AtomicHost"
        if self.channel == 'cloud' and self.image_type == 'AtomicHost':
            return

        # Run the 4-step process. The first step is the `pre-release` step,
        # where plume downloads the image, and uploads the image to various
        # cloud providers. During this step, the artifacts created are kept
        # private.
        output, error, retcode = self.run_pre_release()
        if retcode != 0:
            _log.debug("There was an issue with pre-release")
            _log.debug(error)
            return

        # If `pre-release` step is success, then the messages are published
        # with to message bus via fedora-messaging.
        output, error, retcode = self.push_upload_messages()
        if retcode != 0:
            _log.debug("There was an issue with publishing messages")
            _log.debug(error)

        # During this step, the private artifacts are made public.
        output, error, retcode = self.run_release()
        if retcode != 0:
            _log.debug("There was an issue with release")
            _log.debug(error)
            return

        # If the process of making the artifacts public is success, then the
        # messages are pushed to message bus.
        output, error, retcode = self.push_publish_messages()
        if retcode != 0:
            _log.debug("There was an issue with publishing messages")
            _log.debug(error)

        return

    def process_joystick_topic(self, msg_info):
        """ Process the message info to extract information needed by plume
        binary and trigger the upload process.

        :args msg_info: `dict` fedora-messaging message data
        """
        _log.debug("Processing %r" % (msg_info['id']))
        if msg_info['status'] not in self.valid_status:
            _log.debug("%s is not a valid status" % msg_info["status"])
            return

        compose_id = msg_info.get('compose_id')
        try:
            compose_metadata = fedfind.release.get_release(
                cid=compose_id).metadata
        except fedfind.exceptions.UnsupportedComposeError:
            _log.error("%s is unsupported composes" % compose_id)
            return

        self.location = msg_info['location']

        # Filter the channel from the location extracted from the message
        self.channel = self.location.rsplit('/', 3)
        if not self.channel:
            _log.debug('channel cannot be empty')
            return

        self.channel = self.channel[1]
        if self.channel not in ['cloud', 'branched', 'updates', 'rawhide']:
            _log.debug('%s is not a valid channel' % self.channel)
            return

        self.compose_id = msg_info['compose_id']
        self.respin = msg_info['compose_respin']
        self.timestamp = msg_info['compose_date']
        self.release_version = msg_info['release_version']
        self.aws_crendentials = '~/.aws/credentials'
        for image_type, board in itertools.product(['Cloud-Base', 'AtomicHost'], ['x86_64', 'aarch64']):
            self.process_upload(image_type, board)

    def __call__(self, msg):
        """ This method is called by `fedora-messaging` to process the messages
        received.

        :args msg: `dict` fedora-messaging message
        """

        _log.info("Received message: %s", msg.id)
        topic = msg.topic
        body = msg.body

        msg_info = {
            'id': msg.id
        }
        if 'msg' not in body:
            _log.debug("Invalid message body: %r" % msg.id)
            return
        else:
            msg_info = body['msg']

        # Matches if the current topic is the intended one and needs to be
        # processed
        if topic == self.topic:
            self.process_joystick_topic(msg_info)
        else:
            _log.debug("Dropping %r: %r" % (topic, msg.id))
            return

    def run_pre_release(self):
        """ Runs the pre release step of the plume process."""

        output, error, retcode = self.run_command([
            'plume',
            'pre-release',
            '--system', 'fedora',
            '--channel', self.channel,
            '--version', self.release_version,
            '--timestamp', self.timestamp,
            '--respin', str(self.respin),
            '--board', self.board,
            "--compose-id", self.compose_id,
            "--image-type", self.image_type,
            "--aws-credentials", self.aws_crendentials,
        ])

        return output, error, retcode

    def run_release(self):
        """ Runs the release step of the plume process."""
        output, error, retcode = self.run_command([
            'plume',
            'release',
            '--system', 'fedora',
            '--channel', self.channel,
            '--version', self.release_version,
            '--timestamp', self.timestamp,
            '--respin', str(self.respin),
            '--board',  self.board,
            '--compose-id', self.compose_id,
            '--image-type', self.image_type,
            '--aws-credentials', self.aws_credentials
        ])

        return output, error, retcode

    def generate_ami_upload_list(self):
        """Iterates through the regions, and fetches the AMI information
        using the compose id."""

        for region in self.regions:
            conn = boto3.client(
                "ec2",
                region,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
            )
            _log.info("%s: Connected" % region)

            images = conn.describe_images(
                Filters=[
                    {
                        'Name': 'ComposeID',
                        'Values': [
                            self.compose_id
                        ]
                    },
                ],
            )

            self.uploaded_images = [
                {
                    'id': image['ImageId'],
                    'vol_type': image["BlockDeviceMappings"][0]['Ebs']['VolumeType'],
                    'region': region,
                    'arch': image['Architecture'],
                    'virt_type': image['VirtualizationType']
                } for image in images['Images']
            ]

    def push_upload_messages(self):
        """ Publishes the messages to the fedora message bus with the
        `image.upload` topic.
        """
        self.generate_ami_upload_list()

        for image in self.uploaded_images:
            msg = Message(
                    topic="image.upload",
                    body={
                        u'status': u'completed',
                        u'compose': self.compose_id,
                        u'service': u'EC2',
                        u'extra': {
                            u'virt_type': u'hvm',
                            u'id': image['id'],
                            u'vol_type': image['vol_type'],
                        }
                    }
                )
            api.publish(msg)

    def push_publish_messages(self):
        """ Publishes the messages to the fedora message bus with the
        `image.publish` topic.
        """
        self.generate_ami_upload_list()

        for image in self.uploaded_images:
            msg = Message(
                    topic="image.publish",
                    body={
                        u'compose': self.compose_id,
                        u'service': u'EC2',
                        u'destination': image['region'],
                        u'architecture': image['arch'],
                        u'extra': {
                            u'virt_type': image['virt_type'],
                            u'id': image['id'],
                            u'vol_type': image['vol_type'],
                        }
                    }
                )
            api.publish(msg)
