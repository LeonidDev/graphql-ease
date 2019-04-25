from graphql import GraphQLSchema, GraphQLObjectType

from .types import Object


__all__ = ["declarative_schema"]


class SchemaMeta(type):
    def __init__(cls, name, bases, nmspc):
        if bases and object not in bases:
            if issubclass(cls, Object):
                cls._objects[name] = cls
            cls._types[name] = cls.graphql_type()
        else:
            cls._objects = nmspc["objects"]
            cls._types = nmspc["types"]
        super().__init__(name, bases, nmspc)

    def __getitem__(cls, value):
        return cls._types[value]

    def get_query_fields(cls):
        queries = {}
        for object_ in cls._objects.values():
            queries.update(object_.graphql_queries())
        return queries

    def build_query(cls):
        query_fields = cls.get_query_fields()
        return GraphQLObjectType(name="query", fields=query_fields)

    def get_mutation_fields(cls):
        mutations = {}
        for object_ in cls._objects.values():
            mutations.update(object_.graphql_mutations())
        return mutations

    def build_mutation(cls):
        mutation_fields = cls.get_mutation_fields()
        if mutation_fields:
            return GraphQLObjectType(name="mutation", fields=mutation_fields)

    def build(cls):
        return GraphQLSchema(
            query=cls.build_query(),
            mutation=cls.build_mutation(),
            types=list(cls._types.values()),
        )


def declarative_schema():
    return SchemaMeta("Schema", (object,), {"objects": {}, "types": {}})
