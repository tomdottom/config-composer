from .parameter_types import Parameter
from ..core_data_structures import ParameterSpec
from ..sources.machines import BasicSourceMachine
from ..sources.abc2 import AbstractBasicSource


def dunder_key(name):
    return name.startswith("__") and name.endswith("__")


def get_factory_type(annotated_type):
    if isinstance(annotated_type, (Parameter,)):
        return annotated_type
    if callable(annotated_type):
        return annotated_type
    return None


class MetaSpec(type):
    def __new__(mcls, name, bases, attrs):
        annotations = attrs.get("__annotations__", {})
        values = dict((k, v) for k, v in attrs.items() if not dunder_key(k))
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
        declared_parameters = set(pspec.name for pspec in annotated_parameter_specs)

        # remaining un-annotated typing information from Parameter values
        value_parameter_specs = [
            ParameterSpec(name, get_factory_type(value))
            for name, value in values.items()
            if (name not in declared_parameters and isinstance(value, (Parameter,)))
        ]
        return dict(
            (spec.name, spec)
            for spec in annotated_parameter_specs + value_parameter_specs
        )


class Spec(metaclass=MetaSpec):
    pass


class MetaSourceSpec(type):
    def __new__(mcls, name, bases, attrs):
        for name, source in attrs.items():
            if not name.startswith("__"):
                mcls.apply_state_machine(source)

        klass = super().__new__(mcls, name, bases, attrs)
        return klass

    @staticmethod
    def apply_state_machine(source):
        if isinstance(source, AbstractBasicSource):
            BasicSourceMachine(source)


class SourceSpec(metaclass=MetaSourceSpec):
    pass
