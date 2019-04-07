from textwrap import dedent
from typing import Optional
import os

try:
    import hvac
    _hvac = True
except ImportError:
    _hvac = False

from ..abc import AbstractSourceDescriptor
from ..consts import NOTHING


class Secret(AbstractSourceDescriptor):
    def __init__(self, path: str, field: str, mount_point="secret", server="http://localhost:8200"):
        if not _hvac:
            raise ImportError(dedent("""
                The vault.Secret source requires the hvac library.
                Please reinstall using:
                    pip install config-composer[vault]
            """))
        self._path = path
        self._mount_point = mount_point
        self._server = server
        self._field = field

    def _init_value(self):
        client = hvac.Client(url=self._server)
        secret_version = client.sys.retrieve_mount_option(
            mount_point=self._mount_point,
            option_name='version'
        )
        client.secrets.kv.default_kv_version = secret_version
        if secret_version == "1":
            read_secret = client.secrets.kv.read_secret
        elif secret_version == "2":
            read_secret = client.secrets.kv.read_secret_version
        try:
            response = read_secret(path=self._path)
            if "errors" in response:
                return NOTHING
            value = response["data"]["data"].get(self._field, NOTHING)
        except hvac.exceptions.InvalidPath as err:
            value = NOTHING
        return value
