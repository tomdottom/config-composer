from ..core_data_structures import ParameterInfo


def parameter_info(config, name):
    parameter_spec = config._parameter_spec(name)
    sources = [repr(s) for s in config._source_specs(name)]

    return ParameterInfo(
        name=parameter_spec.name, type=parameter_spec.type, sources=sources
    )


def all_parameter_info(config):
    names = config._parameter_names()
    return [parameter_info(config, name) for name in names]
