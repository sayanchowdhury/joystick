class Client():
    def describe_images(self, *args, **kwargs):
        return {
            'Images': [{
                'ImageId': 'ami-foobar12',
                'Architecture': 'x86_64',
                'VirtualizationType': 'hvm',
                'BlockDeviceMappings':[{
                    'Ebs': {
                        'VolumeType': 'gp2',
                    }
                }]
            },
            {
                'ImageId': 'ami-foobar23',
                'Architecture': 'aarch64',
                'VirtualizationType': 'hvm',
                'BlockDeviceMappings':[{
                    'Ebs': {
                        'VolumeType': 'gp2',
                    }
                }]
            }
        ]}

class Message(object):
    def __init__(self):
        self.topic = "org.fedoraproject.random.topic"
        self.id = '2019-random-msg-id'

        self.body = {
            'msg': {
                "status": "FINISHED",
                "release_type": "ga",
                "compose_label": "RC-20190611.0",
                "compose_respin": 0,
                "compose_date": "20190611",
                "release_version": "30",
                "location": "https://kojipkgs.fedoraproject.org/compose/cloud/Fedora-Cloud-30-20190611.0/compose",
                "compose_type": "production",
                "release_is_layered": False,
                "release_name": "Fedora-Cloud",
                "release_short": "Fedora-Cloud",
                "compose_id": "Fedora-Cloud-30-20190611.0"
            }
        }


class NonMatchingTopicMessage(object):
    def __init__(self):
        self.topic = "org.fedoraproject.random.topic"
        self.id = '2019-random-msg-id'

        self.body = {
            'msg': {
                "status": "FINISHED",
                "release_type": "ga",
                "compose_label": "RC-20190611.0",
                "compose_respin": 0,
                "compose_date": "20190611",
                "release_version": "30",
                "location": "https://kojipkgs.fedoraproject.org/compose/cloud/Fedora-Cloud-30-20190611.0/compose",
                "compose_type": "production",
                "release_is_layered": False,
                "release_name": "Fedora-Cloud",
                "release_short": "Fedora-Cloud",
                "compose_id": "Fedora-Cloud-30-20190611.0"
            }
        }


class NoMsgInBodyMessage(object):
    def __init__(self):
        self.topic = "org.fedoraproject.random.topic"
        self.id = '2019-random-msg-id'
        self.body = {}


class ProcessSuccess(object):
    def __init__(self):
        self.returncode = 0
        self.stderr = b""
        self.stdout = b"Success"


class ProcessFailure(object):
    def __init__(self):
        self.returncode = 1
        self.stderr = b"Command Failed"
        self.stdout = b"Failure"

class GetRelease(object):
    def __init__(self):
        self.metadata = {}
