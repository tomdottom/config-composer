from typing import Any

from .abc import AbstractSourceDescriptor, ValueSource


class Default(ValueSource, AbstractSourceDescriptor):
    def __init__(self, value: Any):
        self._default_value = value

    @property
    def _name(self):
        return self._value

    @property
    def _key(self):
        name = type(self).__name__
        return (name,)

    def __repr__(self):
        return f"""Default(value="{self._value}")"""

    @property
    def _value(self):
        return self._default_value


class DefaultSecret(Default, AbstractSourceDescriptor):
    def __repr__(self):
        return f"""DefaultSecret(value="*** redacted ***")"""
