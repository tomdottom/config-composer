import os

from config_composer.sources.env import Env
from config_composer.sources import AWS
from config_composer.core import Config, Sources


def test_env(random_string):
    os.environ["BAR"] = random_string

    class MyConfig(Config):
        foo = Env(path="bar")

    assert MyConfig.foo == random_string


def test_aws_paramater(aws_parameter_fixtures, random_string):
    os.environ["BAR"] = random_string

    class MyConfig(Config):
        foo = AWS.Parameter(path="/foo/bar/baz")

    assert MyConfig.foo == random_string
