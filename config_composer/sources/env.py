from typing import Optional
import os

from ..consts import NOTHING
from .abc import AbstractSourceDescriptor, ValueSource
from .abc2 import AbstractBasicSource


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

    def __repr__(self):
        return f"""Env(path="{self._path}")"""

    @property
    def _value(self):
        return os.environ.get(self._path, NOTHING)


class Env2(AbstractBasicSource):
    def __init__(self, path: str, prefix: Optional[str] = None):
        if prefix is not None:
            self._path = prefix + path
        else:
            self._path = path

    def key(self):
        name = type(self).__name__
        return (name,)

    def get(self, name, cache):
        return cache["data"]

    def fetch(self, cache):
        try:
            cache.update({"data": os.environ[self._path], "errors": []})
        except KeyError as err:
            cache.update({"errors": [repr(err)]})
