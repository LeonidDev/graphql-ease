from graphql import GraphQLUnionType

from .base import NamedType


__all__ = ["Union"]


class Union(NamedType):
    def __ror__(self, other):
        pass
