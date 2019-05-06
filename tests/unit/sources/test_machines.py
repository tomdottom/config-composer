from unittest import mock
import os

from config_composer.consts import NOTHING
from config_composer.sources.machines import (
    BasicSourceMachine,
    ExpirableBasicSourceMachine,
)
from config_composer.sources.abc2 import (
    AbstractBasicSource,
    AbstractExpirableBasicSource,
    SourceResult,
)


class MyEnvSource(AbstractBasicSource):
    def __init__(self, name):
        self._name = name

    def key(self):
        name = type(self).__name__
        return (name,)

    def get(self, name, cache):
        return cache["data"]

    def fetch(self, cache):
        try:
            cache.update({"data": os.environ[self._name], "errors": []})
        except KeyError as err:
            cache.update({"errors": [repr(err)]})


class MyExpirableEnvSource(AbstractExpirableBasicSource):
    def __init__(self, name):
        self._name = name
        self._expired = False

    def expire_me(self):
        self._expired = True

    def expired(self, cache):
        _expired = self._expired
        self._expired = False
        return _expired

    def fetch(self, cache):
        try:
            cache.update({"data": os.environ[self._name], "errors": []})
        except KeyError as err:
            cache.update({"errors": [repr(err)]})


class TestBasicSource:
    def test_fetches_value_from_source(self, environ, random_string):
        environ["FOO"] = random_string

        source = MyEnvSource("FOO")
        BasicSourceMachine(source)

        cache = {"data": NOTHING, "errors": []}
        source.trigger("_fetch", cache=cache)
        assert source.data(cache=cache) == SourceResult(
            data=random_string, errors=[], state="VALUE_CACHED_SOURCE_OK"
        )

    def test_returns_cached_value(self, environ, random_string):
        environ["FOO"] = random_string

        source = MyEnvSource("FOO")
        BasicSourceMachine(source)

        cache = {"data": NOTHING, "errors": []}
        source.trigger("_fetch", cache=cache)
        del environ["FOO"]
        assert source.data(cache=cache) == SourceResult(
            data=random_string, errors=[], state="VALUE_CACHED_SOURCE_OK"
        )

    def test_only_fetches_once(self, environ):
        environ["FOO"] = "foo"

        source = mock.Mock(wraps=MyEnvSource("FOO"))
        BasicSourceMachine(source)

        cache = {"data": NOTHING, "errors": []}

        for _ in range(10):
            source.trigger("_fetch", cache=cache)

        assert source.fetch.call_count == 1

    def test_returns_errors(self, environ):
        try:
            del environ["FOO"]
        except KeyError:
            pass

        source = MyEnvSource("FOO")
        BasicSourceMachine(source)

        cache = {"data": NOTHING, "errors": []}

        source.trigger("_fetch", cache=cache)

        assert source.data(cache=cache) == SourceResult(
            data=NOTHING, errors=["KeyError('FOO')"], state="SOURCE_ERROR"
        )

    def test_get_value(self, environ, random_string):
        environ["FOO"] = random_string

        source = MyEnvSource("FOO")
        BasicSourceMachine(source)

        cache = {"data": NOTHING, "errors": []}

        source.trigger("_fetch", cache=cache)

        assert source.get("FOO", cache)


class TestExpirableBasicSource:
    def test_fetches_value_from_source(self, environ, random_string):
        source = MyExpirableEnvSource("FOO")
        ExpirableBasicSourceMachine(source)

        cache = {"data": NOTHING, "errors": []}

        environ["FOO"] = random_string
        source.trigger("_fetch", cache=cache)
        assert source.data(cache=cache) == SourceResult(
            data=random_string, errors=[], state="VALUE_CACHED_SOURCE_OK"
        )

    def test_returns_cached_value(self, environ, random_string):
        source = MyExpirableEnvSource("FOO")
        ExpirableBasicSourceMachine(source)

        environ["FOO"] = random_string
        cache = {"data": NOTHING, "errors": []}
        source.trigger("_fetch", cache=cache)
        environ["FOO"] = "BAR"
        source.trigger("_fetch", cache=cache)

        assert source.data(cache=cache) == SourceResult(
            data=random_string, errors=[], state="VALUE_CACHED_SOURCE_OK"
        )

    def test_only_fetches_once(self, environ):
        source = mock.Mock(wraps=MyExpirableEnvSource("FOO"))
        ExpirableBasicSourceMachine(source)

        cache = {"data": NOTHING, "errors": []}

        environ["FOO"] = "foo"

        # source data 10 times
        # expire twice
        for i in range(10):
            source.trigger("_fetch", cache=cache)
            if i in [4, 8]:
                source.expire_me()

        # expired not called on initial fetch
        assert source.expired.call_count == 9
        # 1 initial fetch + 2 expired
        assert source.fetch.call_count == 3

    def test_fetches_new_value_when_cached_expired(
        self, environ, random_string, random_integer
    ):
        source = MyExpirableEnvSource("FOO")
        ExpirableBasicSourceMachine(source)

        cache = {"data": NOTHING, "errors": []}

        # Get value and cache
        environ["FOO"] = random_string
        source.trigger("_fetch", cache=cache)

        # Expire and get new value
        source.expire_me()
        environ["FOO"] = str(random_integer)
        source.trigger("_fetch", cache=cache)

        assert source.data(cache=cache) == SourceResult(
            data=str(random_integer), errors=[], state="VALUE_CACHED_SOURCE_OK"
        )

    def test_returns_cached_value_on_error(self, environ, random_string):
        source = MyExpirableEnvSource("FOO")
        ExpirableBasicSourceMachine(source)

        cache = {"data": NOTHING, "errors": []}

        # Get value and cache
        environ["FOO"] = random_string
        source.trigger("_fetch", cache=cache)
        # Expire and Error when getting value from source
        source.expire_me()
        del environ["FOO"]
        source.trigger("_fetch", cache=cache)

        assert source.data(cache=cache) == SourceResult(
            data=random_string,
            errors=["KeyError('FOO')"],
            state="VALUE_CACHED_SOURCE_ERROR",
        )

    def test_recovers_from_error(self, environ, random_string):

        source = MyExpirableEnvSource("FOO")
        ExpirableBasicSourceMachine(source)

        cache = {"data": NOTHING, "errors": []}

        # Get value and cache
        environ["FOO"] = "FOO"
        source.trigger("_fetch", cache=cache)
        # Expire and Error when getting value from source
        source.expire_me()
        del environ["FOO"]
        source.trigger("_fetch", cache=cache)
        # Succeed in getting from source next time round
        source.expire_me()
        environ["FOO"] = random_string
        source.trigger("_fetch", cache=cache)

        assert source.data(cache=cache) == SourceResult(
            data=random_string, errors=[], state="VALUE_CACHED_SOURCE_OK"
        )
