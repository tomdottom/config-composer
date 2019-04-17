from abc import ABC, abstractmethod, abstractproperty

from ..consts import NOTHING


class AbstractSourceDescriptor(ABC):
    @abstractmethod
    def _init_value(self):
        raise NotImplementedError

    @abstractproperty
    def _name(self):
        raise NotImplementedError

    @abstractproperty
    def _key(self):
        raise NotImplementedError

    def __init__(self):
        pass

    def __get__(self, obj, objtype):
        cache = self._get_cache(obj, objtype)
        if cache.get(self._name, NOTHING) is NOTHING:
            cache[self._name] = self._init_value()
        return cache[self._name]

    def _get_cache(self, obj, objtype):
        cache_host = obj or objtype
        if not hasattr(cache_host, "__source_cache__"):
            setattr(cache_host, "__source_cache__", {})
        root_cache = getattr(cache_host, "__source_cache__")
        cache_key = self._key
        if not cache_key in root_cache:
            root_cache[cache_key] = {}
        return root_cache[cache_key]
