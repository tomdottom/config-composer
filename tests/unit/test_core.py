import os

from config_composer.sources.env import Env
from config_composer.core import Config


def test_foo(random_string):
    os.environ["BAR"] = random_string

    class MyConfig(Config):
        foo = Env(path="bar")

    assert MyConfig.foo == random_string
