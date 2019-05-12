from graphql import GraphQLUnionType

from ..base import NamedType


__all__ = ["Union"]


class Union(NamedType):
    class Meta:
        pass

    def resolve_type(self, value):
        raise NotImplementedError

    @classmethod
    def graphql_types(cls):
        return [cls[type_] for type_ in cls.types]

    def graphql_type(cls):
        return GraphQLUnionType(
            name=getattr(cls.Meta, "name", cls.__name__),
            description=getattr(cls.Meta, "description", cls.__doc__),
            types=cls.graphql_types,
            resolve_type=cls.resolve_type,
        )
