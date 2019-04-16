from collections import namedtuple
from configparser import ConfigParser
import os
import sys

from .abc import AbstractSourceDescriptor
from .consts import NOTHING

SOURCES = dict(
    (source.__name__, source)
    for source
    in AbstractSourceDescriptor.__subclasses__()
)

ParameterSpec = namedtuple(
    "ParameterSpec",
    ["name", "type"],
)


class Parameter:
    def __call__(self, *args, **kwargs):
        return self.factory_type(*args, **kwargs)


class String(Parameter):
    factory_type = str


class Integer(Parameter):
    factory_type = int


def dunder_key(name):
    return name.startswith("__") and name.endswith("__")


def get_factory_type(annotated_type):
    if isinstance(annotated_type, (Parameter, )):
        return annotated_type
    if callable(annotated_type):
        return annotated_type
    return None


class MetaSpec(type):
    def __new__(mcls, name, bases, attrs):
        annotations = attrs.get("__annotations__", {})
        values = dict(
            (k, v) for k, v in attrs.items()
            if not dunder_key(k)
        )
        declared_parameters = mcls.get_declared_parameters(annotations, values)

        klass = super().__new__(mcls, name, bases, attrs)
        klass.__parameters__ = declared_parameters

        return klass

    @classmethod
    def get_declared_parameters(mcls, annotations, values):
        # annotated typing information takes priority
        annotated_parameter_specs = [
            ParameterSpec(name, get_factory_type(annotated_type))
            for name, annotated_type in annotations.items()
        ]
        declared_parameters = set(
            pspec.name for pspec in annotated_parameter_specs
        )

        # remaining un-annotated typing information from Parameter values
        value_parameter_specs = [
            ParameterSpec(name, get_factory_type(value))
            for name, value in values.items()
            if (
                not name in declared_parameters and
                isinstance(value, (Parameter,))
            )
        ]
        return dict(
            (spec.name, spec)
            for spec
            in annotated_parameter_specs + value_parameter_specs
        )


class Spec(metaclass=MetaSpec):
    pass


def source_spec_from_ini(filepath):
    class SourceSpec:
        pass

    ini_config = ConfigParser()
    ini_config.read(filepath)
    parameters = dict(
        (s.split("_", 1)[1], dict(ini_config[s]))
        for s in ini_config.sections()
        if s.startswith("parameter_")
    )
    for s, p in parameters.items():
        klass = SOURCES[p["source"]]
        setattr(SourceSpec, s, klass(path=p["path"]))

    return SourceSpec


class Config:
    def __init__(self, config_spec, source_spec=None, env_var=None):
        self.__config_spec = config_spec
        if source_spec:
            self.__source_spec = source_spec
        if env_var:
            source_spec_path = os.environ.get(env_var)
            self.__source_spec = source_spec_from_ini(source_spec_path)

    def __get__item__attr__(self, name):
        spec = self.__config_spec.__parameters__[name]
        source_value = getattr(self.__source_spec, name)
        return spec.type(source_value)

    def __getattr__(self, name):
        return self.__get__item__attr__(name)

    def __getitem__(self, name):
        return self.__get__item__attr__(name)
