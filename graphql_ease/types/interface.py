from graphql import GraphQLInterfaceType

from .object import Object


__all__ = ["Interface"]


class Interface(Object):
    def graphql_type(cls):
        return GraphQLInterfaceType(
            name=getattr(cls, "name", cls.__name__.lower()),
            description=getattr(cls, "description", cls.__doc__),
            resolve_type=cls.resolve_type,
            fields=cls.graphql_fields,
        )
