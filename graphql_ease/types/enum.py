from typing import Any
from collections import OrderedDict

from graphql import GraphQLEnumType, GraphQLEnumValue

from ..base import NamedType


__all__ = ["EnumValue", "Enum"]


class EnumValue:
    def __init__(self, value: Any = None, description: str = None):
        self.value = value
        self.description = description

    def graphql_type(self):
        return GraphQLEnumValue(self.value, self.description)


class Enum(NamedType):
    class Meta:
        pass

    def __init_subclass__(cls):
        print("ENUM!!!", cls)
        super().__init_subclass__()
        cls._values = getattr(cls, "_values", OrderedDict()).copy()

        for name, attr in cls.__dict__.items():
            if isinstance(attr, EnumValue):
                cls._values[name] = attr

    def graphql_type(cls):
        return GraphQLEnumType(
            name=getattr(cls.Meta, "name", cls.__name__),
            description=getattr(cls.Meta, "description", cls.__doc__),
            values=getattr(cls.Meta, "values", cls._values),
        )
