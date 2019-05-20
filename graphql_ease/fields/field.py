from typing import Any, Optional, Callable
from collections.abc import Mapping

from graphql import GraphQLField, GraphQLList, GraphQLNonNull


__all__ = ["Field"]


def _resolve(obj, info, *_, **__):
    if isinstance(obj, Mapping):
        return obj.get(info.field_name, None)
    else:
        return getattr(obj, info.field_name, None)


class Field(object):
    def __init__(
        self,
        type_: Any,
        resolve: Optional[Callable] = _resolve,
        description: Optional[str] = None,
        required: bool = False,
        many: bool = False,
        args={},
    ):
        self.type_ = type_
        self.resolve = resolve
        self.description = description
        self.required = required
        self.many = many
        self.args = args

    def __call__(self, func):
        self.resolve = func
        self.args = getattr(func, "args", {})
        return self

    def bind(self, schema):
        type_ = self.type_
        if isinstance(self.type_, str):
            self.type_ = lambda: schema[type_]
        else:
            self.type_ = lambda: type_.graphql_type()
        for arg in self.args.values():
            arg.bind(schema)

    def graphql_args(self):
        return {name: arg.graphql_type() for name, arg in self.args.items()}

    def graphql_type(self):
        type_ = self.type_()
        if self.many:
            type_ = GraphQLList(type_)
        if self.required:
            type_ = GraphQLNonNull(type_)
        return GraphQLField(
            type_=type_,
            resolve=self.resolve,
            description=self.description,
            args=self.graphql_args(),
        )
