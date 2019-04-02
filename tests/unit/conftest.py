import os
import random
import string

from moto import mock_ssm
import boto3
import pytest


@pytest.fixture
def random_string():
    return "".join(
        random.choice(string.ascii_letters) for _ in range(random.randrange(20))
    )


@pytest.fixture
def aws_parameter_fixtures(random_string):
    mock = mock_ssm()
    mock.start()

    os.environ['AWS_DEFAULT_REGION'] = "us-east-1"
    client = boto3.client('ssm')
    client.put_parameter(
        Name='/foo/bar/baz',
        Value=random_string,
        Type='String',
    )

    yield random_string

    mock.stop()