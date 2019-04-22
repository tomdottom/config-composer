from collections import namedtuple

ParameterSpec = namedtuple("ParameterSpec", ["name", "type"])
SourceInfo = namedtuple("SourceInfo", ["type", "args"])
ParameterInfo = namedtuple("ParameterInfo", ["name", "type", "sources"])
