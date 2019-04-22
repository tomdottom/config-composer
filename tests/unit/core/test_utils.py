import os

from config_composer.core import Spec, Config
from config_composer.core.utils import all_parameter_info, parameter_info, ParameterInfo
from config_composer.sources.env import Env


def test_get_parameter_info(random_string, random_integer):
    os.environ["VALUE"] = random_string
    expected_parameter_info = ParameterInfo("foo", str, ["""Env(path="VALUE")"""])

    class ConfigSpec(Spec):
        foo: str

    class SourceSpec:
        foo = Env(path="VALUE")

    config = Config(config_spec=ConfigSpec, source_spec=SourceSpec)

    info = parameter_info(config, "foo")
    assert info == expected_parameter_info


def test_get_all_parameters_info(random_string, random_integer):
    os.environ["VALUE"] = random_string
    os.environ["VALUE"] = random_string
    expected_parameter_info = [
        ParameterInfo("foo", str, ["""Env(path="VALUE")"""]),
        ParameterInfo("bar", str, ["""Env(path="VALUE")"""]),
    ]

    class ConfigSpec(Spec):
        foo: str
        bar: str

    class SourceSpec:
        foo = Env(path="VALUE")
        bar = Env(path="VALUE")

    config = Config(config_spec=ConfigSpec, source_spec=SourceSpec)

    info = all_parameter_info(config)

    assert info == expected_parameter_info
