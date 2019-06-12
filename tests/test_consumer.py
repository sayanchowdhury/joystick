import mock
import os
import unittest

from fedora_messaging.config import conf
from joystick.consumers.fedora_messaging_consumer import JoyStickController
from tests import Client, Message, NoMsgInBodyMessage, NonMatchingTopicMessage
from tests import ProcessSuccess, ProcessFailure

RUN_COMMAND_OUTPUT_SUCCESS = ProcessSuccess()
RUN_COMMAND_OUTPUT_FAILURE = ProcessFailure()
RUN_COMMAND_OUTPUT_SUCCESS_T = ('Success', '', 0)
RUN_COMMAND_OUTPUT_FAILURE_T = ('Failure', 'Command Failed', 1)
BOTO_RETURN_VALUE = Client()

@mock.patch('boto3.client', return_value=BOTO_RETURN_VALUE)
def test_generate_ami_upload_list(mock_boto_client):
    config_path = os.path.abspath("tests/testjoystick.toml")
    conf.load_config(config_path=config_path)
    js = JoyStickController()
    setattr(js, 'compose_id', 'Fedora-Compose-ID')
    js.generate_ami_upload_list()


@mock.patch('joystick.consumers.fedora_messaging_consumer._log.debug')
def test_process_joystick_test_call_no_msg_in_body(mock_log):
    msg = NoMsgInBodyMessage()
    js = JoyStickController()
    js.__call__(msg)

    mock_log.assert_called_with("Invalid message body: '2019-random-msg-id'")

@mock.patch('joystick.consumers.fedora_messaging_consumer._log.debug')
def test_process_joystick_test_call_non_matching_topic(mock_log):
    msg = NonMatchingTopicMessage()

    js = JoyStickController()
    # Set the topic to the pungi topic we intend to listen
    setattr(js, 'topic', 'org.fedoraproject.pungi.compose.status.change')
    js.__call__(msg=msg)

    mock_log.assert_called_with(
        "Dropping 'org.fedoraproject.random.topic': '2019-random-msg-id'"
    )

@mock.patch('subprocess.run', return_value=RUN_COMMAND_OUTPUT_SUCCESS)
@mock.patch('joystick.consumers.fedora_messaging_consumer._log.debug')
def test_run_command_success(mock_log, mock_subprocess_run):
    js = JoyStickController()
    output = js.run_command('ls -l')
    mock_log.assert_called_with(
        "(output) Success, (error) , (retcode) 0"
    )


@mock.patch('subprocess.run', return_value=RUN_COMMAND_OUTPUT_FAILURE)
@mock.patch('joystick.consumers.fedora_messaging_consumer._log.error')
def test_run_command_success(mock_log, mock_subprocess_run):
    js = JoyStickController()
    output = js.run_command('ls -l')
    mock_log.assert_called_with(
        "(output) Failure, (error) Command Failed, (retcode) 1"
    )

@mock.patch('joystick.consumers.fedora_messaging_consumer.JoyStickController.push_upload_messages',
        return_value=RUN_COMMAND_OUTPUT_SUCCESS_T)
@mock.patch('joystick.consumers.fedora_messaging_consumer.JoyStickController.run_release',
        return_value=RUN_COMMAND_OUTPUT_SUCCESS_T)
@mock.patch('joystick.consumers.fedora_messaging_consumer.JoyStickController.push_publish_messages',
        return_value=RUN_COMMAND_OUTPUT_SUCCESS_T)
@mock.patch('joystick.consumers.fedora_messaging_consumer.JoyStickController.run_pre_release',
        return_value=RUN_COMMAND_OUTPUT_FAILURE_T)
@mock.patch('joystick.consumers.fedora_messaging_consumer._log.debug')
def test_process_upload_pre_release_fail(mock_log, mock_run_pre_release,
        mock_push_publish_messages, mock_run_release,
        mock_push_upload_messages):
    js = JoyStickController()
    js.process_upload('AtomicHost', 'x86_64')

    mock_log.assert_called_with('Command Failed')


@mock.patch('joystick.consumers.fedora_messaging_consumer.JoyStickController.push_upload_messages',
        return_value=RUN_COMMAND_OUTPUT_SUCCESS_T)
@mock.patch('joystick.consumers.fedora_messaging_consumer.JoyStickController.run_release',
        return_value=RUN_COMMAND_OUTPUT_SUCCESS_T)
@mock.patch('joystick.consumers.fedora_messaging_consumer.JoyStickController.push_publish_messages',
        return_value=RUN_COMMAND_OUTPUT_FAILURE_T)
@mock.patch('joystick.consumers.fedora_messaging_consumer.JoyStickController.run_pre_release',
        return_value=RUN_COMMAND_OUTPUT_SUCCESS_T)
@mock.patch('joystick.consumers.fedora_messaging_consumer._log.debug')
def test_process_upload_push_publish_msg_fail(mock_log, mock_run_pre_release,
        mock_push_publish_messages, mock_run_release,
        mock_push_upload_messages):
    js = JoyStickController()
    js.process_upload('AtomicHost', 'x86_64')

    mock_log.assert_called_with('Command Failed')


@mock.patch('joystick.consumers.fedora_messaging_consumer.JoyStickController.push_upload_messages',
        return_value=RUN_COMMAND_OUTPUT_SUCCESS_T)
@mock.patch('joystick.consumers.fedora_messaging_consumer.JoyStickController.run_release',
        return_value=RUN_COMMAND_OUTPUT_FAILURE_T)
@mock.patch('joystick.consumers.fedora_messaging_consumer.JoyStickController.push_publish_messages',
        return_value=RUN_COMMAND_OUTPUT_SUCCESS_T)
@mock.patch('joystick.consumers.fedora_messaging_consumer.JoyStickController.run_pre_release',
        return_value=RUN_COMMAND_OUTPUT_SUCCESS_T)
@mock.patch('joystick.consumers.fedora_messaging_consumer._log.debug')
def test_process_upload_release_fail(mock_log, mock_run_pre_release,
        mock_push_publish_messages, mock_run_release,
        mock_push_upload_messages):
    js = JoyStickController()
    js.process_upload('AtomicHost', 'x86_64')

    mock_log.assert_called_with('Command Failed')


@mock.patch('joystick.consumers.fedora_messaging_consumer.JoyStickController.push_upload_messages',
        return_value=RUN_COMMAND_OUTPUT_FAILURE_T)
@mock.patch('joystick.consumers.fedora_messaging_consumer.JoyStickController.run_release',
        return_value=RUN_COMMAND_OUTPUT_FAILURE_T)
@mock.patch('joystick.consumers.fedora_messaging_consumer.JoyStickController.push_publish_messages',
        return_value=RUN_COMMAND_OUTPUT_SUCCESS_T)
@mock.patch('joystick.consumers.fedora_messaging_consumer.JoyStickController.run_pre_release',
        return_value=RUN_COMMAND_OUTPUT_SUCCESS_T)
@mock.patch('joystick.consumers.fedora_messaging_consumer._log.debug')
def test_process_upload_push_upload_msg_fail(mock_log, mock_run_pre_release,
        mock_push_publish_messages, mock_run_release,
        mock_push_upload_messages):
    js = JoyStickController()
    js.process_upload('AtomicHost', 'x86_64')

    mock_log.assert_called_with('Command Failed')



"""
class TestJoystickController(unittest.TestCase):
    @mock.patch('subprocess.run',
                mock.MagicMock(return_value=RUN_COMMAND_OUTPUT_SUCCESS))
    def test_run_command_success(self):
        output = self.joystick.run_command('ls -l')

    @mock.patch('subprocess.run',
                mock.MagicMock(return_value=RUN_COMMAND_OUTPUT_FAIL))
    def test_run_command_fail(self):
        output = self.joystick.run_command('sl -l')

    @mock.patch('JoystickController.process_upload',
                return_value=True)
    def test_process_joystick_topic_empty_channel(self):
        self.joystick._process_joystick_topic(msg_info)

    @mock.patch('JoystickController.process_upload',
                return_value=True)
    @mock.patch('fedfind.release.get_release',
                return_value=True)
    def test_process_joystick_topic_invalid_channel(self, mock_process_upload,
            mock_get_release):
        self.joystick._process_joystick_topic(msg_info)

    @mock.patch('JoystickController.process_joystick_topic',
                return_value=True)
    def test_cls_call_method(self):
        self.JoystickController.__call__(msg)

    @mock.patch('boto3.client', return_value=BOTO_RETURN_VALUE)
    def test_generate_ami_upload_list(self, mock_boto_client):
        js = JoyStickController()
        js.generate_ami_upload_list()
    """
