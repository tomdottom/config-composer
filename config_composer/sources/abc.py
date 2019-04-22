from abc import ABC, abstractmethod, abstractproperty

from ..consts import NOTHING


class AbstractSourceDescriptor(ABC):
    @abstractproperty
    def _name(self):
        raise NotImplementedError

    @abstractproperty
    def _key(self):
        raise NotImplementedError

    @abstractmethod
    def __get__(self, obj, objtype):
        raise NotImplementedError

    @abstractmethod
    def _get_cache(self, obj, objtype):
        raise NotImplementedError


class ValueSource(ABC):
    @abstractproperty
    def _value(self):
        raise NotImplementedError

    def __get__(self, obj, objtype):
        cache = self._get_cache(obj, objtype)
        if cache.get(self._name, NOTHING) is NOTHING:
            cache[self._name] = self._value
        return cache[self._name]

    def _get_cache(self, obj, objtype):
        cache_host = obj or objtype
        if not hasattr(cache_host, "__source_cache__"):
            setattr(cache_host, "__source_cache__", {})
        root_cache = getattr(cache_host, "__source_cache__")
        cache_key = self._key
        if cache_key not in root_cache:
            root_cache[cache_key] = {}
        return root_cache[cache_key]


class DocumentSource(ABC):
    @abstractproperty
    def _doc(self):
        raise NotImplementedError

    def __get__(self, obj, objtype):
        cache = self._get_cache(obj, objtype)

        if isinstance(self, DocumentSourceTTL):
            ttl = self._get_ttl(obj, objtype)
            ttl_data = ttl.get(self._key)
            expired, ttl_data = self._expired(ttl_data)
            if expired:
                ttl[self._key] = ttl_data
                cache.update(self._doc)

        if cache.get(self._name, NOTHING) is NOTHING:
            # cache.clear()
            cache.update(self._doc)

        return cache[self._name]

    def _get_cache(self, obj, objtype):
        cache_host = obj or objtype
        if not hasattr(cache_host, "__source_cache__"):
            setattr(cache_host, "__source_cache__", {})
        root_cache = getattr(cache_host, "__source_cache__")
        cache_key = self._key
        if cache_key not in root_cache:
            root_cache[cache_key] = {}
        return root_cache[cache_key]


class DocumentSourceTTL(ABC):
    @abstractmethod
    def _expired(self):
        raise NotImplementedError

    def _get_ttl(self, obj, objtype):
        ttl_host = obj or objtype
        if not hasattr(ttl_host, "__source_ttl__"):
            setattr(ttl_host, "__source_ttl__", {})
        root_ttl = getattr(ttl_host, "__source_ttl__")
        ttl_key = self._key
        if ttl_key not in root_ttl:
            root_ttl[ttl_key] = {}
        return root_ttl[ttl_key]
