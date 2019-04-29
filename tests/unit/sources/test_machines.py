from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Optional
import os

from config_composer.consts import NOTHING
from config_composer.sources.machines import (
    BasicSourceMachine,
    ExpirableBasicSourceMachine,
)


@dataclass
class SourceResult:
    data: Any
    errors: List
    state: Optional[str]


class AbstractBasicSource(ABC):
    state = None

    @abstractmethod
    def fetch(self, cache):
        raise NotImplementedError()

    def data(self, cache) -> SourceResult:
        return SourceResult(
            data=cache["data"], errors=cache["errors"], state=self.state
        )

    def ok(self, cache) -> bool:
        return not bool(cache["errors"])


class AbstractExpirableBasicSource(ABC):
    state = None

    @abstractmethod
    def fetch(self, cache):
        raise NotImplementedError()

    @abstractmethod
    def expired(self, cache):
        raise NotImplementedError()

    def data(self, cache) -> SourceResult:
        return SourceResult(
            data=cache["data"], errors=cache["errors"], state=self.state
        )

    def ok(self, cache) -> bool:
        return not bool(cache["errors"])


class TestBasicSource:
    def test_foo(self, environ):
        environ["FOO"] = "foo"

        class MyEnvSource(AbstractBasicSource):
            def fetch(self, cache):
                cache.update({"data": os.environ["FOO"], "errors": []})

        source = MyEnvSource()
        BasicSourceMachine(source)

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

        source.trigger("_fetch", cache=cache)

        assert source.data(cache=cache) == SourceResult(
            data="foo", errors=[], state="VALUE_CACHED_SOURCE_OK"
        )

        del environ["FOO"]

        assert source.data(cache=cache) == SourceResult(
            data="foo", errors=[], state="VALUE_CACHED_SOURCE_OK"
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
