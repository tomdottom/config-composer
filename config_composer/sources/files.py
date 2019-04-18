from pathlib import Path
from typing import Optional

try:
    from dotenv import dotenv_values

    _python_dotfile = True
except ImportError:
    _python_dotfile = True

from ..consts import NOTHING
from .abc import AbstractSourceDescriptor, DocumentSource


class DotEnvFile(DocumentSource, AbstractSourceDescriptor):
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

    @property
    def _name(self):
        return self._path

    @property
    def _key(self):
        source_name = type(self).__name__
        return source_name, self._dotenv_path

    @property
    def _doc(self):
        parsed = dotenv_values(stream=self._dotenv_path)
        return parsed
