from collections import OrderedDict

from graphql import GraphQLObjectType


from ..base import NamedType
from ..fields import Field, Query, Mutation, Subscription


__all__ = ["Object"]


class Object(NamedType):
    class Meta:
        pass

    def __init_subclass__(cls):
        super().__init_subclass__()
        cls._fields = getattr(cls, "_fields", OrderedDict()).copy()
        cls._queries = getattr(cls, "_queries", OrderedDict()).copy()
        cls._mutations = getattr(cls, "_mutations", OrderedDict()).copy()
        cls._subscriptions = getattr(cls, "_subscriptions", OrderedDict()).copy()

        for name, attr in cls.__dict__.items():
            if isinstance(attr, (Field, Query, Mutation, Subscription)):
                attr.bind(cls)
                if isinstance(attr, Query):
                    cls._queries[name] = attr
                elif isinstance(attr, Mutation):
                    cls._mutations[name] = attr
                elif isinstance(attr, Subscription):
                    cls._subscriptions[name] = attr
                elif isinstance(attr, Field):
                    cls._fields[name] = attr

    @classmethod
    def graphql_fields(cls):
        return {name: field.graphql_type() for name, field in cls._fields.items()}

    @classmethod
    def graphql_queries(cls):
        return {name: query.graphql_type() for name, query in cls._queries.items()}

    @classmethod
    def graphql_mutations(cls):
        return {
            name: mutation.graphql_type() for name, mutation in cls._mutations.items()
        }

    @classmethod
    def graphql_subscriptions(cls):
        return {
            name: subscription.graphql_type()
            for name, subscription in cls._subscriptions.items()
        }

    @classmethod
    def graphql_interfaces(cls):
        from .interface import Interface

        return [
            cls[base.__name__] for base in cls.__bases__ if isinstance(base, Interface)
        ]

    def graphql_type(cls):
        return GraphQLObjectType(
            name=getattr(cls.Meta, "name", cls.__name__),
            description=getattr(cls.Meta, "description", cls.__doc__),
            fields=cls.graphql_fields,
            interfaces=cls.graphql_interfaces,
        )
