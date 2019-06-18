import mock
import os
import unittest
import fedfind.exceptions

from fedora_messaging.config import conf
from joystick.consumers.fedora_messaging_consumer import JoyStickController
from joystick.tests import Client, Message, NoMsgInBodyMessage, NonMatchingTopicMessage
from joystick.tests import ProcessSuccess, ProcessFailure, GetRelease

RUN_COMMAND_OUTPUT_SUCCESS = ProcessSuccess()
RUN_COMMAND_OUTPUT_FAILURE = ProcessFailure()
RUN_COMMAND_OUTPUT_SUCCESS_T = ('Success', '', 0)
RUN_COMMAND_OUTPUT_FAILURE_T = ('Failure', 'Command Failed', 1)
BOTO_RETURN_VALUE = Client()

@mock.patch('boto3.client', return_value=BOTO_RETURN_VALUE)
def test_generate_ami_upload_list(mock_boto_client):
    config_path = os.path.abspath("joystick/tests/testjoystick.toml")
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


@mock.patch('joystick.consumers.fedora_messaging_consumer._log.debug')
def test_invalid_status(mock_log):
    msg_info = {
        'id': 'random id',
        'status': 'STARTING',
        'location': 'https://someplace.org/path/to/image'
    }
    js = JoyStickController()
    js.process_joystick_topic(msg_info)

    mock_log.assert_called_with('STARTING is not a valid status')


@mock.patch('fedfind.release.get_release')
@mock.patch('joystick.consumers.fedora_messaging_consumer._log.error')
def test_fedfind_get_release_exception(mock_log, mock_get_release):
    msg_info = {
        'id': 'random id',
        'status': 'FINISHED',
        'location': 'https://someplace.org/path/to/image',
        'compose_id': 'Random compose id',
    }

    mock_get_release.side_effect = fedfind.exceptions.UnsupportedComposeError()
    js = JoyStickController()
    js.process_joystick_topic(msg_info)

    mock_log.assert_called_with('Random compose id id unsupported composes')


@mock.patch('fedfind.release.get_release', return_value=GetRelease())
@mock.patch('joystick.consumers.fedora_messaging_consumer.JoyStickController.process_upload', return_value=[])
@mock.patch('joystick.consumers.fedora_messaging_consumer._log.debug')
def test_fedfind_get_release_exception(mock_log, mock_process_upload, mock_get_release):
    msg_info = {
        'id': 'random id',
        'status': 'FINISHED',
        'location': 'https://someplace.org/cloud/path/image',
        'compose_id': 'Random compose id',
        'compose_respin': 1,
        'compose_date': '23062019',
        'release_version': '30',
    }

    js = JoyStickController()
    js.process_joystick_topic(msg_info)

    assert mock_process_upload.called
