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

    @property
    def _args(self):
        return dict(value=self._value)

    @property
    def _value(self):
        return self._default_value


class DefaultSecret(Default, AbstractSourceDescriptor):
    @property
    def _args(self):
        return dict(value="*** redacted ***")
