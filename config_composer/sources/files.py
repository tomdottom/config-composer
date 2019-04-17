from pathlib import Path
from typing import Optional

try:
    from dotenv import dotenv_values

    _python_dotfile = True
except ImportError:
    _python_dotfile = True

from ..consts import NOTHING
from .abc import AbstractSourceDescriptor


class DotEnvFile(AbstractSourceDescriptor):
    def __init__(self, path: str, dotenv_path=".env"):
        if not _python_dotfile:
            raise ImportError(
                dedent(
                    """
                The envfile.EnvFile source requires the python-dotenv library.
                Please reinstall using:
                    pip install config-composer[dotenv]
            """
                )
            )
        self._dotenv_path = dotenv_path
        self._path = path

    def _init_value(self):
        parsed = dotenv_values(stream=self._dotenv_path)
        return parsed[self._path]
