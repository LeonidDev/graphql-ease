from typing import Any, Optional

from graphql import GraphQLArgument, GraphQLNonNull, GraphQLList
from graphql.error import INVALID


__all__ = ["Argument"]


class Argument(object):
    def __init__(
        self,
        name: Optional[str] = None,
        type_: Optional[Any] = None,
        required: bool = True,
        many: bool = False,
        default_value=INVALID,
        description: Optional[str] = None,
    ):
        self.name = name
        self.type_ = type_
        self.required = required
        self.many = many
        self.default_value = default_value
        self.description = description

    def __call__(self, func):
        if self.name is None:
            raise ValueError("Decorated args must have name.")
        if not hasattr(func, "args"):
            func.args = {}
        func.args[self.name] = self
        return func

    def bind(self, schema):
        type_ = self.type_
        if isinstance(self.type_, str):
            self.type_ = lambda: schema[type_]
        else:
            self.type_ = lambda: type_.graphql_type()

    def graphql_type(self):
        type_ = self.type_()
        if self.many:
            type_ = GraphQLList(type_)
        if self.required:
            type_ = GraphQLNonNull(type_)
        return GraphQLArgument(
            type_=type_, default_value=self.default_value, description=self.description
        )
