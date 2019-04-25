from ..base import NamedType


__all__ = ["Enum"]


class Enum(NamedType):
    def graphql_type(cls):
        pass
