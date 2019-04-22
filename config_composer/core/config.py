from configparser import ConfigParser
from pathlib import Path
from typing import Iterable, Callable, Dict, Union, Type
import inspect
import logging
import os

import yaml

from ..sources.abc import AbstractSourceDescriptor
from .utils import all_parameter_info


SOURCES = dict(
    (source.__name__, source) for source in AbstractSourceDescriptor.__subclasses__()
)


logger = logging.getLogger(__name__)


class ParameterError(Exception):
    pass


def get_source_kwargs(source: Callable, data: Dict):
    """
    Filters a data dictionary and returns only key/values
    which match argument names of the source callable.
    """
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

    file_suffix = Path(filepath).suffix
    param_factory = FILETYPE_FACTORIES[file_suffix]
    logger.info(
        f"Creating SourceSpec from '{filepath}'' using '{file_suffix}' factory."
    )
    # TODO: handle unsupported filetypes
    # TODO: handle missing files
    parameters = param_factory(filepath)

    for s, p in parameters.items():
        klass = SOURCES[p["source"]]
        kwargs = get_source_kwargs(klass, p)
        setattr(SourceSpec, s, klass(**kwargs))

    return SourceSpec


def get_name(obj):
    if inspect.isclass(obj):
        return obj.__name__
    else:
        return obj.__class__.__name__


def format_parameter_table(parameters_info):
    parameter_format = "{name:<10} | {type:<10} | {source}".format
    source_format = "{name} - {args}".format
    header = "\n".join(
        [
            "Config created",
            parameter_format(name="Parameter", type="Type", source="Source"),
            parameter_format(name="---------", type="----", source="------"),
            "",
        ]
    )
    info = "\n".join(
        parameter_format(
            name=info.name,
            type=get_name(info.type),
            source=source_format(
                name=get_name(info.sources[-1].type), args=info.sources[-1].args
            ),
        )
        for info in parameters_info
    )
    return header + info


class Config:
    """Binds a ConfigSpec and SourceSpec into a config object.

    The config object:
    - only fetches configured parameters defined in ConfigSpec
    - fetches parameter values from sources defined in one of the SourceSpecs
    - converts values into expected type defined in ConfigSpec

    Args:
        config_spec (Spec): ?
        source_spec (Union[Type, Iterable[Type]]): ?
        env_var: ?
    """

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

        logger.info(format_parameter_table(all_parameter_info(self)))

    def source_spec_factory(self, source_spec: Union[Type, Iterable[Type]]) -> Type:
        """
        Creates a SourceSpec type.
        Multiple sepecifications combined using class mro machinery.
        """
        bases: tuple = tuple()
        if inspect.isclass(source_spec):
            bases += (source_spec,)
        elif source_spec and isinstance(source_spec, (Iterable,)):
            bases += tuple(source_spec)
        return type("SourceSpec", bases, {})

    def _parameter_spec(self, name):
        parameters = self.__config_spec.__parameters__
        if name not in parameters:
            raise ParameterError(name)
        # if not hasattr(source_spec, name):
        # Cannot use hasattr as it will invoke descriptors :facepalm:/
        spec = parameters[name]
        return spec

    def _parameter_names(self):
        return list(self.__config_spec.__parameters__.keys())

    def _source_specs(self, name):
        source_spec = self.__source_spec
        sources = list(filter(None, [o.__dict__.get(name) for o in source_spec.mro()]))
        if not any(sources):
            raise ParameterError(name)
        return sources

    def __get__item__attr__(self, name):
        """
        Retrieves configured parameters and converts to defined type.

        Throws ParameterError when attempting to retieve a parameter
        which is not defined on the ConfigSpec.
        """
        parameters = self.__config_spec.__parameters__
        source_spec = self.__source_spec
        if name not in parameters:
            raise ParameterError(name)
        # if not hasattr(source_spec, name):
        # Cannot use hasattr as it will invoke descriptors :facepalm:/
        if name not in dir(source_spec):
            raise ParameterError(name)
        spec = parameters[name]
        source_value = getattr(source_spec, name)
        return spec.type(source_value)

    def __getattr__(self, name):
        return self.__get__item__attr__(name)

    def __getitem__(self, name):
        return self.__get__item__attr__(name)

    def get(self, name):
        try:
            return self.__get__item__attr__(name)
        except ParameterError:
            return None
