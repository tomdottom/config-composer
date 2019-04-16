from typing import Optional, Any
import os

from ..consts import NOTHING
from .abc import AbstractSourceDescriptor


class Default(AbstractSourceDescriptor):
    def __init__(self, value: Any):
        self._value = value

    def _init_value(self):
        return self._value
