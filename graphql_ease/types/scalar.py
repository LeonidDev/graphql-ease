import json

from graphql import (
    GraphQLScalarType,
    GraphQLBoolean,
    GraphQLFloat,
    GraphQLID,
    GraphQLInt,
    GraphQLString,
)

from ..base import NamedType


__all__ = ["Scalar", "Boolean", "Float", "ID", "Int", "String", "JSON"]


class Scalar(NamedType):
    def graphql_type(cls):
        return GraphQLScalarType(
            name=cls.__name__,
            description=cls.__doc__,
            serialize=cls.serialize,
            parse_value=cls.parse_value,
            parse_literal=cls.parse_literal,
        )

    def serialize(value):
        raise NotImplementedError

    def parse_value(value):
        raise NotImplementedError

    def parse_literal(ast, _variables=None):
        raise NotImplementedError


class Boolean(Scalar):
    def graphql_type(cls):
        return GraphQLBoolean


class Float(Scalar):
    def graphql_type(cls):
        return GraphQLFloat


class ID(Scalar):
    def graphql_type(cls):
        return GraphQLID


class Int(Scalar):
    def graphql_type(cls):
        return GraphQLInt


class String(Scalar):
    def graphql_type(cls):
        return GraphQLString


class JSON(Scalar):
    def serialize(value):
        return json.dumps(value)

    def parse_value(value):
        return json.loads(value)

    def parse_literal(ast, _variables=None):
        if isinstance(node, ast.StringValue):
            return json.loads(node.value)
