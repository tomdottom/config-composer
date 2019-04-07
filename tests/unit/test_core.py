import os

from config_composer.sources.env import Env
from config_composer.sources import aws, vault
from config_composer.core import Config, Sources


def test_env(random_string):
    os.environ["BAR"] = random_string

    class MyConfig(Config):
        foo = Env(path="bar")

    assert MyConfig.foo == random_string


def test_aws_paramater(aws_parameter_fixtures, random_string):
    os.environ["BAR"] = random_string

    class MyConfig(Config):
        foo = aws.Parameter(path="/foo/bar/baz")

    assert MyConfig.foo == random_string


def test_vault_secret(vault_secret_fixtures, random_string):

    class MyConfig(Config):
        foo = vault.Secret(path="/foo/bar/baz", field="my-secret")

    assert MyConfig.foo == random_string


def test_selectes_first_good_source(aws_parameter_fixtures, random_string):
    os.environ["FOO_BAR_BAZ"] = "This is the string you are looking for"

    class MyConfig(Config):
        foo = Sources(Env(path="FOO_BAR_BAZ"), aws.Parameter(path="/foo/bar/baz"))

    assert MyConfig.foo == os.environ["FOO_BAR_BAZ"]


def test_fall_through_source_options(aws_parameter_fixtures):
    del os.environ["FOO_BAR_BAZ"]
    random_string = aws_parameter_fixtures

    class MyConfig(Config):
        foo = Sources(Env(path="FOO_BAR_BAZ"), aws.Parameter(path="/foo/bar/baz"))

    assert MyConfig.foo == random_string


def test_inheritance(aws_parameter_fixtures):
    os.environ["FOO_BAR_BAZ"] = "WAT"
    random_string = aws_parameter_fixtures

    class MyConfigDev(Config):
        foo = Sources(Env(path="FOO_BAR_BAZ"))
        bar = Sources(Env(path="FOO_BAR_BAZ"))

    class MyConfig(MyConfigDev):
        foo = Sources(aws.Parameter(path="/foo/bar/baz"))

    assert MyConfigDev.foo == "WAT"
    assert MyConfigDev.bar == "WAT"

    assert MyConfig.foo == random_string
    assert MyConfig.bar == "WAT"
