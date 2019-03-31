from abc import ABC, abstractmethod


class AbstractSourceDescriptor(ABC):
    __value = None

    @abstractmethod
    def _init_value(self):
        raise NotImplementedError

    def __init__(self):
        pass

    def __get__(self, obj, objtype):
        if self.__value is None:
            self.__value = self._init_value()
        return self.__value
