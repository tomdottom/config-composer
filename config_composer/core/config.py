from configparser import ConfigParser
from pathlib import Path
from typing import Iterable
import inspect
import inspect
import os

import yaml

from ..sources.abc import AbstractSourceDescriptor


SOURCES = dict(
    (source.__name__, source) for source in AbstractSourceDescriptor.__subclasses__()
)


class ParameterError(Exception):
    pass


def get_source_kwargs(source, data):
    arg_names = inspect.getfullargspec(source).args
    kwargs = dict(
        (name, value)
        for name, value in ((name, data.get(name)) for name in arg_names)
        if value is not None
    )
    return kwargs


def source_spec_parameters_from_ini(filepath):
    ini_config = ConfigParser()
    ini_config.read(filepath)
    parameters = dict(
        (s.split("_", 1)[1], dict(ini_config[s]))
        for s in ini_config.sections()
        if s.startswith("parameter_")
    )
    return parameters


def source_spec_paramaters_from_yaml(filepath):
    with open(filepath) as fh:
        yaml_config = yaml.safe_load(fh)
    parameters = yaml_config["parameters"]
    return parameters


FILETYPE_FACTORIES = {
    ".ini": source_spec_parameters_from_ini,
    ".yaml": source_spec_paramaters_from_yaml,
    ".yml": source_spec_paramaters_from_yaml,
}


def source_spec_from_file(filepath):
    class SourceSpec:
        pass

    param_factory = FILETYPE_FACTORIES[Path(filepath).suffix]
    parameters = param_factory(filepath)

    for s, p in parameters.items():
        klass = SOURCES[p["source"]]
        kwargs = get_source_kwargs(klass, p)
        setattr(SourceSpec, s, klass(**kwargs))

    return SourceSpec


class Config:
    def __init__(self, config_spec, source_spec=None, env_var=None):
        self.__config_spec = config_spec
        if source_spec:
            self.__source_spec = self.source_spec_factory(source_spec)
        elif env_var:
            source_spec_paths = os.environ.get(env_var).split(",")
            source_specs = tuple(
                source_spec_from_file(filepath) for filepath in source_spec_paths
            )
            self.__source_spec = self.source_spec_factory(source_specs)

    def source_spec_factory(self, source_spec):
        bases = tuple()
        if inspect.isclass(source_spec):
            bases += (source_spec,)
        elif source_spec and isinstance(source_spec, (Iterable,)):
            bases += tuple(source_spec)
        return type("SourceSpec", bases, {})

    def __get__item__attr__(self, name):
        parameters = self.__config_spec.__parameters__
        source_spec = self.__source_spec
        if name not in parameters:
            raise ParameterError(name)
        if not hasattr(source_spec, name):
            raise ParameterError(name)
        spec = parameters[name]
        source_value = getattr(source_spec, name)
        return spec.type(source_value)

    def __getattr__(self, name):
        return self.__get__item__attr__(name)
        # raise ParameterError(name)

    def __getitem__(self, name):
        return self.__get__item__attr__(name)
        # raise ParameterError(name)

    def get(self, name):
        try:
            return self.__get__item__attr__(name)
        except ParameterError:
            return None
