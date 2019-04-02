class Sources:
    def __init__(self, *args):
        self._sources = args

    def __get__(self, obj, objtype):
        return next(filter(None, (
            source.__get__(obj, objtype)
            for source in self._sources
        )))


class ModelMeta(type):
    pass


class Config(metaclass=ModelMeta):
    pass
