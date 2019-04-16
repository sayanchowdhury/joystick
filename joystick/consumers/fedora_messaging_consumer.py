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

            try:
                compose_metadata = fedfind.release.get_release(
                    cid=compose_id).metadata
            except fedfind.exceptions.UnsupportedComposeError:
                _log.debug("%s is unsupported composes" % compose_id)
                return

            images_meta = []
            self.location = body['location']

            self.channel = self.location.rsplit('/', 3)
            if not self.channel:
                _log.debug('channel cannot be empty')
                return

            self.channel = self.channel[1]
            if self.channel not in ['cloud', 'branched', 'updates', 'rawhide']:
                _log.debug('%s is not a valid channel' % self.channel)
                return

            self.compose_id = body['compose_id']
            self.respin = body['respin']
            self.timestamp = body['compose_date']
            self.release_version = body['release_version']
            self.aws_crendentials = '~/.aws/credentials'
            for image_type in ['Cloud-Base', 'AtomicHost']:
                self.image_type = image_type

                if self.channel == 'cloud' and self.image_type == 'AtomicHost':
                    continue

                output, error, retcode = self._run_pre_release()
                if not retcode != 0:
                    _log.debug("There was an issue with pre-release")
                    _log.debug(error)
                    continue

                output, error, retcode = self._run_release()
                if not retcode != 0:
                    _log.debug("There was an issue with release")
                    _log.debug(error)
                    continue

                """
                output, error, retcode = self._publish_messages()
                if not retcode != 0:
                    _log.debug("There was an issue with publishing messages")
                    _log.debug(error)
                    continue
                """
        else:
            _log.debug("Dropping %r" % (topic, msg.id))
            pass

    def _run_pre_release(self):
        output, error, retcode = self.run_command([
            'plume',
            'pre-release',
            '--system', 'fedora',
            '--channel', self.channel,
            '--version', self.release_version,
            '--timestamp', self.timestamp,
            '--respin', self.respin,
            '--board', self.board,
            "--compose-id", self.compose_id,
            "--image-type", self.image_type,
            "--aws-credentials", self.aws_crendentials,
        ])

        return output, error, retcode

    def _run_release(self):
        output, error, retcode = self.run_command([
            'plume',
            'release',
            '--system', 'fedora',
            '--channel', self.channel,
            '--version', self.release_version,
            '--timestamp', self.timestamp,
            '--respin', self.respin,
            '--board',  self.board,
            '--compose-id', self.compose_id,
            '--image-type', self.image_type,
            '--aws-credentials', self.aws_credentials
        ])

        return output, error, retcode
