from typing import Optional
import os

from ..consts import NOTHING
from .abc import AbstractSourceDescriptor


class Env(AbstractSourceDescriptor):
    def __init__(self, path: str, prefix: Optional[str] = None):
        if prefix is not None:
            self._path = (prefix + path).upper()
        else:
            self._path = path.upper()

    def _init_value(self):
        return os.environ.get(self._path, NOTHING)
