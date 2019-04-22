import logging
import os
import random
import string

from moto import mock_ssm
import boto3
import pytest


logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def random_string():
    return "".join(
        random.choice(string.ascii_letters) for _ in range(random.randrange(10, 20))
    )


@pytest.fixture
def random_integer():
    return random.randint(1, 99999)


@pytest.fixture
def aws_parameter_fixtures(random_string):
    mock = mock_ssm()
    mock.start()

    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    client = boto3.client("ssm")
    client.put_parameter(Name="/foo/bar/baz", Value=random_string, Type="String")

    yield random_string

    mock.stop()


@pytest.fixture
def vault_secret_fixtures(requests_mock, random_string):
    server = "http://localhost:8200/v1"
    mount_uri = f"{server}/sys/mounts"
    secret_uri = f"{server}/secret/data/foo/bar/baz"
    missing_secret_uri = f"{server}/secret/data/im/not/here"

    requests_mock.get(
        url=mount_uri,
        json={
            "secret/": {
                "description": "key/value secret storage",
                "options": {"version": "2"},
                "type": "kv",
            },
            "data": {
                "secret/": {
                    "description": "key/value secret storage",
                    "options": {"version": "2"},
                    "type": "kv",
                }
            },
        },
    )

    requests_mock.get(
        url=secret_uri,
        json={
            "data": {"data": {"my-secret": random_string}, "metadata": {"version": 1}}
        },
    )

    requests_mock.get(url=missing_secret_uri, json={"errors": []})

    yield random_string


@pytest.fixture
def environ():
    class Environ:
        def __init__(self):
            self._og_keys = set(os.environ.keys())
            self._keys = set()

        def __getitem__(self, name):
            return os.environ[name]

        def __setitem__(self, name, value):
            self._keys.add(name)
            os.environ[name] = value

        def __delitem__(self, name):
            self._keys.discard(name)
            del os.environ[name]

        def clean_up(self):
            for key in self._keys - self._og_keys:
                del os.environ[key]

    environ = Environ()

    yield Environ()

    environ.clean_up()
