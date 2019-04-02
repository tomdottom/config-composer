from .consts import NOTHING


class Sources:
    def __init__(self, *args):
        self._sources = args

    def __get__(self, obj, objtype):
        not_nothing = lambda val: val is not NOTHING
        return next(filter(not_nothing, (
            source.__get__(obj, objtype)
            for source in self._sources
        )), NOTHING)


class ModelMeta(type):
    pass


class Config(metaclass=ModelMeta):
    pass
