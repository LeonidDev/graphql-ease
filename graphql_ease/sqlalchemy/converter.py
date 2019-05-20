from functools import singledispatch

from sqlalchemy import types
from sqlalchemy.orm import interfaces
from sqlalchemy.dialects import postgresql

from ..fields import Field, Argument
from ..types import Boolean, ID, Int, String, JSON


__all__ = ["relationship_to_field", "column_to_field"]


def relationship_to_field(relationship):
    direction = relationship.direction
    model = relationship.mapper.entity
    if direction == interfaces.MANYTOONE or not relationship.uselist:
        return Field(model.__name__)
    elif direction in (interfaces.ONETOMANY, interfaces.MANYTOMANY):
        return Field(
            model.__name__,
            many=True,
            args={
                "first": Argument(type_=Int, many=True, required=False),
                "filter": Argument(type_=String, many=True, required=False),
                "filter_by": Argument(
                    type_=f"{model.__name__}Columns", many=True, required=False
                ),
                "order": Argument(type_="SQLAOrder", many=True, required=False),
                "order_by": Argument(
                    type_=f"{model.__name__}Columns", many=True, required=False
                ),
            },
        )


def column_to_field(column):
    return _column_to_field(
        getattr(column, "type", None),
        column,
        lambda obj, info: getattr(obj, column.name, None),
        getattr(column, "doc", None),
    )


@singledispatch
def _column_to_field(_, column, __, ___):
    raise ValueError("Unknown SQLA Column type", column)


@_column_to_field.register(types.String)
@_column_to_field.register(types.Text)
@_column_to_field.register(types.TIMESTAMP)
def _(type_, column, resolve, doc):
    return Field(String, resolve=resolve, description=doc)


@_column_to_field.register(types.Integer)
def _(type_, column, resolve, doc):
    if column.primary_key:
        return Field(ID, resolve=resolve, description=doc, required=True)
    else:
        return Field(Int, resolve=resolve, description=doc)


@_column_to_field.register(types.Boolean)
def _(type_, column, resolve, doc):
    return Field(Boolean, resolve=resolve, description=doc)


@_column_to_field.register(types.JSON)
@_column_to_field.register(postgresql.JSONB)
def _(type_, column, resolve, doc):
    return Field(JSON, resolve=resolve, description=doc)
