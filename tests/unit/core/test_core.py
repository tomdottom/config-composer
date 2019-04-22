from textwrap import dedent
from tempfile import NamedTemporaryFile

import pytest

from config_composer.core import Spec, Config, String, Integer, ParameterError
from config_composer.sources import aws, vault, files
from config_composer.sources.default import Default
from config_composer.sources.env import Env


# Test loading source spec from files
def test_source_spec_from_yaml_file(environ, random_string):
    environ["VALUE"] = str(random_string)

    tempfile = NamedTemporaryFile(suffix=".yaml")
    with open(tempfile.name, "w") as fh:
        fh.write(
            dedent(
                """
        parameters:
          foo:
            source: Env
            path: VALUE
        """
            )
        )
    environ["SOURCE_SPEC_PATH"] = tempfile.name

    class ConfigSpec(Spec):
        foo: str

    config = Config(config_spec=ConfigSpec, env_var="SOURCE_SPEC_PATH")

    assert config.foo == random_string


def test_source_spec_from_ini_file(environ, random_string):
    environ["VALUE"] = str(random_string)

    tempfile = NamedTemporaryFile(suffix=".ini")
    with open(tempfile.name, "w") as fh:
        fh.write(
            dedent(
                """
        [parameter_foo]
        source=Env
        path=VALUE
        """
            )
        )
    environ["SOURCE_SPEC_PATH"] = tempfile.name

    class ConfigSpec(Spec):
        foo: str

    config = Config(config_spec=ConfigSpec, env_var="SOURCE_SPEC_PATH")

    assert config.foo == random_string


# Test composing multiple source specs
def test_multiple_source_specs(environ, random_string, random_integer):
    environ["VALUE"] = random_string

    class ConfigSpec(Spec):
        foo: str
        bar: int

    class SourceSpec1:
        foo = Env(path="VALUE")

    class SourceSpec2:
        bar = Default(value=str(random_integer))

    config = Config(config_spec=ConfigSpec, source_spec=(SourceSpec1, SourceSpec2))

    assert config.foo == random_string
    assert config.bar == random_integer


def test_multiple_source_specs_most_significant_spec(
    environ, random_string, random_integer
):
    environ["VALUE"] = random_string

    class ConfigSpec(Spec):
        foo: str
        bar: str

    class SourceSpec1:
        foo = Env(path="VALUE")
        bar = Default(random_integer)

    class SourceSpec2:
        bar = Default(value=str(random_integer))

    config = Config(config_spec=ConfigSpec, source_spec=(SourceSpec1, SourceSpec2))

    # SourceSpec1 shadows SourceSpec2
    assert config.foo == random_string
    assert config.bar == str(random_integer)


def test_source_spec_from_multiple_ini_file(environ, random_string, random_integer):
    environ["VALUE"] = str(random_string)

    deploy_spec = NamedTemporaryFile(suffix=".ini")
    default_spec = NamedTemporaryFile(suffix=".ini")
    with open(deploy_spec.name, "w") as fh:
        fh.write(
            dedent(
                f"""
        [parameter_foo]
        source=Env
        path=VALUE
        """
            )
        )
    with open(default_spec.name, "w") as fh:
        fh.write(
            dedent(
                f"""
        [parameter_foo]
        source=Default
        value=Should not be read!

        [parameter_bar]
        source=Default
        value={random_integer}
        """
            )
        )

    # deploy_spec shadows default_spec
    environ["SOURCE_SPEC_PATH"] = ",".join((deploy_spec.name, default_spec.name))

    class ConfigSpec(Spec):
        foo: str
        bar: str

    config = Config(config_spec=ConfigSpec, env_var="SOURCE_SPEC_PATH")

    # deploy_spec shadows default_spec
    assert config.foo == random_string
    assert config.bar == str(random_integer)


# Test parameter access behaviour
def test_accessing_non_existant_config_parameter(random_integer):
    class ConfigSpec(Spec):
        foo: str

    class SourceSpec:
        foo = Default(random_integer)

    config = Config(config_spec=ConfigSpec, source_spec=SourceSpec)

    with pytest.raises(ParameterError):
        config["bar"]

    with pytest.raises(ParameterError):
        config.bar

    assert config.get("bar") is None


# Test parameter types and casting of values
def test_casts_source_value_to_type(environ, random_integer):
    environ["VALUE"] = str(random_integer)

    class ConfigSpec(Spec):
        foo: str
        bar: int
        xor = String()
        baz = Integer()

    class SourceSpec:
        foo = Env(path="VALUE")
        bar = Env(path="VALUE")
        xor = Env(path="VALUE")
        baz = Env(path="VALUE")

    config = Config(config_spec=ConfigSpec, source_spec=SourceSpec)
    assert type(config.foo) == str
    assert config.foo == str(random_integer)
    assert type(config.bar) == int
    assert config.bar == random_integer
    assert type(config.xor) == str
    assert config.foo == str(random_integer)
    assert type(config.baz) == int
    assert config.bar == random_integer


def test_string_parameter_type(environ, random_string):
    environ["FOO"] = random_string
    environ["BAR"] = random_string

    class ConfigSpec(Spec):
        foo: str
        bar = String()

    class SourceSpec:
        foo = Env(path="FOO")
        bar = Env(path="BAR")

    config = Config(config_spec=ConfigSpec, source_spec=SourceSpec)
    assert config.foo == random_string
    assert config.bar == random_string


def test_integer_parameter_type(environ, random_integer):
    environ["FOO"] = str(random_integer)
    environ["BAR"] = str(random_integer)

    class ConfigSpec(Spec):
        foo: int
        bar = Integer()

    class SourceSpec:
        foo = Env(path="FOO")
        bar = Env(path="BAR")

    config = Config(config_spec=ConfigSpec, source_spec=SourceSpec)
    assert config.foo == random_integer
    assert config.bar == random_integer


# Test parameter sources
def test_default(environ, random_string):
    class ConfigSpec(Spec):
        foo: str

    class SourceSpec:
        foo = Default(value=random_string)

    config = Config(config_spec=ConfigSpec, source_spec=SourceSpec)

    assert config["foo"] == random_string
    assert config.foo == random_string


def test_env(environ, random_string):
    environ["BAR"] = random_string

    class ConfigSpec(Spec):
        foo: str

    class SourceSpec:
        foo = Env(path="BAR")

    config = Config(config_spec=ConfigSpec, source_spec=SourceSpec)

    assert config["foo"] == random_string
    assert config.foo == random_string


def test_aws_paramater(aws_parameter_fixtures, random_string):
    class ConfigSpec(Spec):
        foo: str

    class SourceSpec:
        foo = aws.Parameter(path="/foo/bar/baz")

    config = Config(config_spec=ConfigSpec, source_spec=SourceSpec)

    assert config.foo == random_string


def test_vault_secret(vault_secret_fixtures, random_string):
    class ConfigSpec(Spec):
        foo: str

    class SourceSpec:
        foo = vault.Secret(path="/foo/bar/baz", field="my-secret")

    config = Config(config_spec=ConfigSpec, source_spec=SourceSpec)

    assert config.foo == random_string


def test_dotfile(random_string, random_integer):
    tempfile = NamedTemporaryFile(prefix=".env")
    with open(tempfile.name, "w") as fh:
        fh.write(
            dedent(
                f"""
        # a comment and that will be ignored.
        FOO={random_string}
        BAR={random_integer}
        """
            )
        )

    class ConfigSpec(Spec):
        foo: str
        bar: int

    class SourceSpec:
        foo = files.DotEnvFile(path="FOO", dotenv_path=tempfile.name)
        bar = files.DotEnvFile(path="BAR", dotenv_path=tempfile.name)

    config = Config(config_spec=ConfigSpec, source_spec=SourceSpec)

    assert config.foo == random_string
    assert config.bar == random_integer
