from collections import namedtuple


SourceInfo = namedtuple("SourceInfo", ["type", "args"])
ParameterInfo = namedtuple("ParameterInfo", ["name", "type", "sources"])


def parameter_info(config, name):
    parameter_spec = config._parameter_spec(name)
    source_specs = [SourceInfo(type(s), s._args) for s in config._source_specs(name)]

    return ParameterInfo(parameter_spec.name, parameter_spec.type, source_specs)


def all_parameter_info(config):
    names = config._parameter_names()
    return [parameter_info(config, name) for name in names]
