from collections import namedtuple

ParameterSpec = namedtuple("ParameterSpec", ["name", "type"])
ParameterInfo = namedtuple("ParameterInfo", ["name", "type", "sources"])
