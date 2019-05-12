from typing import Any, Optional
from collections import OrderedDict

from graphql import (
    GraphQLInputObjectType,
    GraphQLInputField,
    GraphQLNonNull,
    GraphQLList,
)
from graphql.error import INVALID

from ..base import NamedType

__all__ = ["Input", "InputField"]


class InputField:
    def __init__(
        self,
        type_: Optional[Any] = None,
        required: bool = True,
        many: bool = False,
        default_value=INVALID,
        description: Optional[str] = None,
    ):
        self.type_ = type_
        self.required = required
        self.many = many
        self.default_value = default_value
        self.description = description

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
        return GraphQLInputField(
            type_=type_, default_value=self.default_value, description=self.description
        )


class Input(NamedType):
    class Meta:
        pass

    def __init_subclass__(cls):
        super().__init_subclass__()
        cls._fields = getattr(cls, "_fields", OrderedDict()).copy()

        for name, attr in cls.__dict__.items():
            if isinstance(attr, InputField):
                attr.bind(cls)
                cls._fields[name] = attr

    @classmethod
    def graphql_fields(cls):
        return {name: field.graphql_type() for name, field in cls._fields.items()}

    def graphql_type(cls):
        return GraphQLInputObjectType(
            name=getattr(cls.Meta, "name", cls.__name__),
            description=getattr(cls.Meta, "description", cls.__doc__),
            fields=cls.graphql_fields,
        )
