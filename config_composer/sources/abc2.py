from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class SourceResult:
    data: Any
    errors: List
    state: Optional[str]


class AbstractBasicSource(ABC):
    state = None

    @abstractmethod
    def key(self):
        raise NotImplementedError()

    @abstractmethod
    def get(self, name, cache):
        raise NotImplementedError()

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
