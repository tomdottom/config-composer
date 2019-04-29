from .meta import YamlMachine


class BasicSourceMachine(YamlMachine):
    definition = "basic_source_machine.yaml"


class ExpirableBasicSourceMachine(YamlMachine):
    definition = "expirable_basic_source_machine.yaml"
