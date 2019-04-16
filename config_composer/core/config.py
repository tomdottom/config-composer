from configparser import ConfigParser
from pathlib import Path
import inspect
import os

import yaml

from ..sources.abc import AbstractSourceDescriptor


SOURCES = dict(
    (source.__name__, source) for source in AbstractSourceDescriptor.__subclasses__()
)


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
            self.__source_spec = source_spec
        if env_var:
            source_spec_path = os.environ.get(env_var)
            self.__source_spec = source_spec_from_file(source_spec_path)

    def __get__item__attr__(self, name):
        spec = self.__config_spec.__parameters__[name]
        source_value = getattr(self.__source_spec, name)
        return spec.type(source_value)

    def __getattr__(self, name):
        return self.__get__item__attr__(name)

    def __getitem__(self, name):
        return self.__get__item__attr__(name)
