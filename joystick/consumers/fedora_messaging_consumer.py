import logging
import subprocess

from fedora_messaging.config import conf
from fedora_messaging.message import Message


_log = logging.getLogger(__name__)


class JoyStickController(object):
    """
    JoyStick controller for plume.
    """

    def __init__(self):
        self.config = conf["consumer_config"]

    def run_command(self, command):
        _log.info("Starting the command: %r" % command)
        ret = subprocess.Popen(' '.join(command), stdin=subprocess.PIPE,
                               shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, close_fds=True)
        out, err = ret.communicate()
        retcode = ret.returncode
        _log.info("Finished executing the command: %r" % command)

        if retcode != 0:
            _log.error("Command failed during run")
            _log.error(
                "(output) %s, (error) %s, (retcode) %s" % (out, err, retcode))
        else:
            _log.debug(
                "(output) %s, (error) %s, (retcode) %s" % (out, err, retcode))

        return out, err, retcode

    def __call__(self, msg):
        _log.info("Received message: %s", msg.id)
        topic = msg.topic
        body = msg.body

        if topic.endswith("pungi.compose.status.change"):
            _log.debug("Processing %r" % (msg.id))
            if body['status'] not in self.valid_status:
                _log.debug("%s is not a valid status" % msg_info["status"])
                return

            self.compose_id = body['compose_id']
            self.respin = body['respin']
            self.timestamp = body['compose_date']
            self.release_version = body['release_version']

            success = self._run_pre_release()

            success = self._run_release()

            success = self._publish_messages()
        else:
            _log.debug("Dropping %r" % (topic, msg.id))
            pass

    def _run_pre_release(self):
        self.run_command([
            'plume',
            'pre-release',
            '--system', 'fedora',
            '--channel', self.channel,
            '--version', self.release_version
            '--timestamp', self.timestamp,
            '--respin', self.respin,
            '--board', self.board,
            "--compose-id", self.compose_id,
            "--image-type", self.image_type,
            "--aws-credentials", self.aws_crendentials,
        ])

    def _run_release(self):
        self.run_command([
            'plume',
            'release',
            '--system', 'fedora',
            '--channel', self.channel
            '--version', self.release_version,
            '--timestamp', self.timestamp,
            '--respin', self.respin,
            '--board',  self.board,
            '--compose-id', self.compose_id,
            '--image-type', self.image_type,
            '--aws-credentials', self.aws_credentials
        ])

    def _publish_messages(self):
        raise NotImplementedError
