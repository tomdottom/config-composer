from typing import Optional
import os

from ..consts import NOTHING
from .abc import AbstractSourceDescriptor


class Env(AbstractSourceDescriptor):
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

    def _init_value(self):
        return os.environ.get(self._path, NOTHING)
