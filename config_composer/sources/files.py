from textwrap import dedent
from typing import Union
import os
import time

try:
    from dotenv import dotenv_values

    _python_dotfile = True
except ImportError:
    _python_dotfile = True

from .abc import AbstractSourceDescriptor, DocumentSource, DocumentSourceTTL

FIFTEEN_SECONDS = 15


class DotEnvFile(DocumentSource, DocumentSourceTTL, AbstractSourceDescriptor):
    """Source from '.env' files.

    :param path: to be read from the envfile
    :param dotenv_path: filepath for the envfile
    :param ttl: number of seconds between checking if the envfile has updated. Defaults to 15 seconds.
    """

    def __init__(
        self,
        path: str,
        dotenv_path=".env",
        ttl: Union[int, float] = FIFTEEN_SECONDS,
        _get_time=time.monotonic,
    ):
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
        self._ttl = ttl
        self._get_time = _get_time

    @property
    def _name(self):
        return self._path

    @property
    def _key(self):
        source_name = type(self).__name__
        return source_name, self._dotenv_path

    def __repr__(self):
        return f"""DotEnvFile(path="{self._path}", dotenv_path="{self._dotenv_path}, ttl="{self._ttl}")"""

    def _expired(self, ttl_stamp):
        time = self._get_time()
        if not isinstance(ttl_stamp, dict):
            expired = True
            ttl_stamp = {
                "last_modified_time": os.stat(self._dotenv_path).st_mtime,
                "last_read": time,
            }
        elif (time - ttl_stamp["last_read"]) > self._ttl:
            expired = True
            ttl_stamp = {
                "last_modified_time": os.stat(self._dotenv_path).st_mtime,
                "last_read": time,
            }
        else:
            expired = False

        return expired, ttl_stamp

    @property
    def _doc(self):
        parsed = dotenv_values(stream=self._dotenv_path)
        return parsed
