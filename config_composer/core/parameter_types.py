class Parameter:
    def __call__(self, *args, **kwargs):
        return self.factory_type(*args, **kwargs)

    def factory_type(self, *args, **kwargs):
        raise NotImplementedError()


class String(Parameter):
    factory_type = str


class Integer(Parameter):
    factory_type = int
