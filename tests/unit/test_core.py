import os

from config_composer.sources.env import Env
from config_composer.sources import aws, vault
from config_composer.core import Spec, Config, String, Integer


def test_casts_source_value_to_type(random_integer):
    os.environ["VALUE"] = str(random_integer)

    class ConfigSpec(Spec):
        foo: str
        bar: int
        xor = String()
        baz = Integer()

    class SourceSpec:
        foo = Env(path="value")
        bar = Env(path="value")
        xor = Env(path="value")
        baz = Env(path="value")

    config = Config(
        config_spec=ConfigSpec,
        source_spec=SourceSpec,
    )
    assert type(config.foo) == str
    assert config.foo == str(random_integer)
    assert type(config.bar) == int
    assert config.bar == random_integer
    assert type(config.xor) == str
    assert config.foo == str(random_integer)
    assert type(config.baz) == int
    assert config.bar == random_integer


def test_string_parameter_type(random_string):
    os.environ["FOO"] = random_string
    os.environ["BAR"] = random_string

    class ConfigSpec(Spec):
        foo: str
        bar = String()

    class SourceSpec:
        foo = Env(path="foo")
        bar = Env(path="bar")

    config = Config(
        config_spec=ConfigSpec,
        source_spec=SourceSpec,
    )
    assert config.foo == random_string
    assert config.bar == random_string


def test_integer_parameter_type(random_integer):
    os.environ["FOO"] = str(random_integer)
    os.environ["BAR"] = str(random_integer)

    class ConfigSpec(Spec):
        foo: int
        bar = Integer()

    class SourceSpec:
        foo = Env(path="foo")
        bar = Env(path="bar")

    config = Config(
        config_spec=ConfigSpec,
        source_spec=SourceSpec,
    )
    assert config.foo == random_integer
    assert config.bar == random_integer


def test_env(random_string):
    os.environ["BAR"] = random_string

    class ConfigSpec(Spec):
        foo: str

    class SourceSpec:
        foo = Env(path="bar")

    config = Config(
        config_spec=ConfigSpec,
        source_spec=SourceSpec,
    )

    assert config["foo"] == random_string
    assert config.foo == random_string


def test_aws_paramater(aws_parameter_fixtures, random_string):
    class ConfigSpec(Spec):
        foo: str

    class SourceSpec:
        foo = aws.Parameter(path="/foo/bar/baz")

    config = Config(
        config_spec=ConfigSpec,
        source_spec=SourceSpec,
    )

    assert config.foo == random_string


def test_vault_secret(vault_secret_fixtures, random_string):
    class ConfigSpec(Spec):
        foo: str

    class SourceSpec:
        foo = vault.Secret(path="/foo/bar/baz", field="my-secret")

    config = Config(
        config_spec=ConfigSpec,
        source_spec=SourceSpec,
    )

    assert config.foo == random_string
