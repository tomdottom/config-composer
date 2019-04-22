from typing import Optional
import os

from ..consts import NOTHING
from .abc import AbstractSourceDescriptor, ValueSource


class Env(ValueSource, AbstractSourceDescriptor):
    def __init__(self, path: str, prefix: Optional[str] = None):
        if prefix is not None:
            self._path = prefix + path
        else:
            self._path = path

    @property
    def _name(self):
        return self._path

    @property
    def _key(self):
        name = type(self).__name__
        return (name,)

    @property
    def _args(self):
        return dict(path=self._path)

    def __repr__(self):
        return f"""Env(path="{self._path}")"""

    @property
    def _value(self):
        return os.environ.get(self._path, NOTHING)
