__all__ = ["cached", "str_to_camel_case"]


class Cached(object):
    def __init__(self, func):
        self.cached = {}
        self.func = func
        self.result = {}

    def __call__(self, cls):
        name = cls.__name__
        if not self.cached.get(name, False):
            self.result[name] = self.func(cls)
            self.cached[name] = True
        return self.result[name]


cached = Cached


def str_to_camel_case(str_):
    str_ = str_.title().replace("_", "")
    return str_[0].lower() + str_[1:]
