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

    def fetch(self, cache):
        try:
            cache.update({"data": os.environ[self._name]})
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


class TestExpirableBasicSource:
    def test_foo(self, environ):
        environ["FOO"] = "foo"

        control = {"expired": False}

        class MyEnvSource(AbstractExpirableBasicSource):
            def expired(self, cache):
                _expired = control["expired"]
                control["expired"] = False
                return _expired

            def fetch(self, cache):
                try:
                    cache.update({"data": os.environ["FOO"], "errors": []})
                except KeyError as err:
                    cache.update({"errors": [repr(err)]})

        source = MyEnvSource()
        ExpirableBasicSourceMachine(source)

        cache = {"data": NOTHING, "errors": []}
        assert source.data(cache=cache) == SourceResult(
            data=NOTHING, errors=[], state="UNINITIALIZED"
        )

        for _ in range(10):
            source.trigger("_fetch", cache=cache)

        assert isinstance(source.data(cache=cache), SourceResult)

        assert source.data(cache=cache) == SourceResult(
            data="foo", errors=[], state="VALUE_CACHED_SOURCE_OK"
        )

        environ["FOO"] = "bar"

        assert source.data(cache=cache) == SourceResult(
            data="foo", errors=[], state="VALUE_CACHED_SOURCE_OK"
        )

        control["expired"] = True

        source.trigger("_fetch", cache=cache)

        assert source.data(cache=cache) == SourceResult(
            data="bar", errors=[], state="VALUE_CACHED_SOURCE_OK"
        )

        del environ["FOO"]

        assert source.data(cache=cache) == SourceResult(
            data="bar", errors=[], state="VALUE_CACHED_SOURCE_OK"
        )

        source.trigger("_fetch", cache=cache)

        assert source.data(cache=cache) == SourceResult(
            data="bar", errors=[], state="VALUE_CACHED_SOURCE_OK"
        )

        control["expired"] = True

        source.trigger("_fetch", cache=cache)

        assert source.data(cache=cache) == SourceResult(
            data="bar", errors=["KeyError('FOO')"], state="VALUE_CACHED_SOURCE_ERROR"
        )
