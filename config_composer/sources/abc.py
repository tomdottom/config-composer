from abc import ABC, abstractmethod

from ..consts import NOTHING


class AbstractSourceDescriptor(ABC):
    __value = NOTHING

    @abstractmethod
    def _init_value(self):
        raise NotImplementedError

    def __init__(self):
        pass

    def __get__(self, obj, objtype):
        if self.__value is NOTHING:
            self.__value = self._init_value()
        return self.__value
