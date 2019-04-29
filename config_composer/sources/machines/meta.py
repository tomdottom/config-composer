import pathlib
import yaml

from transitions import Machine


def _def_path(filename):
    return pathlib.Path(__file__).parent.joinpath(filename)


class MetaYamlMachine(type):
    def __new__(mcls, name, bases, attrs):
        definition = attrs.pop("definition", {})
        klass = super().__new__(mcls, name, bases, attrs)
        if definition:
            with open(_def_path(definition)) as fh:
                klass.__machine_args__ = yaml.safe_load(fh)
        return klass


class YamlMachine(Machine, metaclass=MetaYamlMachine):
    def __init__(self, model):
        return super().__init__(model=model, **self.__machine_args__)
