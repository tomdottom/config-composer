from textwrap import dedent

try:
    import hvac

    _hvac = True
except ImportError:
    _hvac = False

from ..consts import NOTHING
from .abc import AbstractSourceDescriptor, ValueSource


class Secret(ValueSource, AbstractSourceDescriptor):
    def __init__(
        self,
        path: str,
        field: str,
        mount_point="secret",
        server="http://localhost:8200",
    ):
        if not _hvac:
            raise ImportError(
                dedent(
                    """
                The vault.Secret source requires the hvac library.
                Please reinstall using:
                    pip install config-composer[vault]
            """
                )
            )
        self._path = path
        self._mount_point = mount_point
        self._server = server
        self._field = field

    @property
    def _name(self):
        return self._field

    @property
    def _key(self):
        name = type(self).__name__
        return name, self._mount_point, self._path

    def __repr__(self):
        return f"""vault.Secret(path="{self._path}", field="{self._field}", mount_point="{self._mount_point}", server="{self._server}")"""

    @property
    def _value(self):
        client = hvac.Client(url=self._server)
        secret_version = client.sys.retrieve_mount_option(
            mount_point=self._mount_point, option_name="version"
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
        except hvac.exceptions.InvalidPath:
            value = NOTHING
        return value
