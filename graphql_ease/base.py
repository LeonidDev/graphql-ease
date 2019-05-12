from .util import cached


__all__ = ["BaseType"]


class BaseType(object):
    pass


class WrappingType(BaseType):
    pass


class NamedType(BaseType):
    class Meta:
        pass

    def __init_subclass__(cls):
        if not getattr(cls.graphql_type, "func", None):
            cls.graphql_type = classmethod(cached(cls.graphql_type))
