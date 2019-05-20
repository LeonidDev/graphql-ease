from functools import partial
from enum import Enum

from sqlalchemy import asc, desc, func
from sqlalchemy.sql import column
from sqlalchemy.orm import RelationshipProperty, contains_eager, aliased
from sqlalchemy.inspection import inspect
from graphql import GraphQLEnumType

from .converter import column_to_field, relationship_to_field
from ..types import Object, String, Int
from ..fields import Field, Argument
from ..utilities import get_node_fields


__all__ = ["SQLAlchemyObject"]


class SQLAOrder(Enum):
    ASC = 1
    DESC = 2


def resolve_single(cls, obj, info, column, value):
    return cls.Meta.model.query.filter(
        getattr(cls.Meta.model, column) == value
    ).one_or_none()


def build_query(model, like=[], like_by=[], order=[], order_by=[], page=0, limit=0):
    query = model.query

    for like_by_, like_ in zip(like_by, like):
        query = query.filter(getattr(model, like_by_).like(f"%{like_}%"))

    for order_by_, order_ in zip(order_by, order):
        if SQLAOrder.ASC == order_:
            query = query.order_by(asc(getattr(model, order_by_)))
        else:
            query = query.order_by(desc(getattr(model, order_by_)))

    if limit:
        query = query.limit(limit)

    if page:
        query = query.offset(((page - 1) * limit))

    return query


def build_sub_query(field, parent, model, arguments):
    query = model.query

    arguments = {
        argument_def["name"]: argument_def["value"] for argument_def in arguments
    }

    print(field, arguments)

    filter_by = arguments.get("filter_by", [])
    if not isinstance(filter_by, list):
        filter_by = [filter_by]
    filter_ = arguments.get("filter", [])
    if not isinstance(filter_by, list):
        filter_ = [filter_]

    for filter_by_, filter__ in zip(filter_by, filter_):
        query = query.filter(getattr(model, filter_by_) == filter__)

    if "first" in arguments:
        query = (
            query.with_entities(
                model,
                func.row_number()
                .over(partition_by=getattr(parent, field))
                .label("row_count"),
            )
            .from_self()
            .filter(column("row_count") <= arguments["first"])
        )

    return query


def _resolve_related(field_def, query, model):
    field = field_def["field"]
    arguments = field_def["arguments"]
    children = field_def["children"]

    if hasattr(model, field) and isinstance(
        getattr(model, field).property, RelationshipProperty
    ):
        model_ = getattr(model, field).property.mapper.class_
        model_alias = aliased(
            model_, build_sub_query(field, model, model_, arguments).subquery()
        )
        query = query.outerjoin(model_alias).options(
            contains_eager(getattr(model, field), alias=model_alias)
        )
        model = model_

    for child in children:
        query = _resolve_related(child, query, model)

    return query


def resolve_related(info, query, model):
    for field_def in get_node_fields(info, info.field_nodes[0], info.fragments):
        query = _resolve_related(field_def, query, model)

    return query


def resolve_many(cls, obj, info, *args, **kwargs):
    model = cls.Meta.model
    query = build_query(model, *args, **kwargs)
    query = resolve_related(info, query, model)
    return query.all()


class SQLAlchemyObject(Object):
    def __init_subclass__(cls):
        super().__init_subclass__()
        model_meta = inspect(cls.Meta.model)

        for column in model_meta.columns.values():
            cls._fields[column.name] = column_to_field(column)
            cls._fields[column.name].bind(cls)

        for relationship in model_meta.relationships:
            name = relationship.key
            cls._fields[name] = relationship_to_field(relationship)
            cls._fields[name].bind(cls)

        cls._types["SQLAOrder"] = GraphQLEnumType("SQLAOrder", SQLAOrder)

        cls._columns_enum = Enum(
            f"{cls.__name__}Columns",
            [(column.name, column.name) for column in model_meta.columns.values()],
        )
        cls._columns = GraphQLEnumType(cls._columns_enum.__name__, cls._columns_enum)
        cls._types[cls._columns.name] = cls._columns

        cls._unique_columns_enum = Enum(
            f"{cls.__name__}UniqueColumns",
            [
                (column.name, column.name)
                for column in model_meta.columns.values()
                if column.unique or column.primary_key
            ],
        )
        cls._unique_columns = GraphQLEnumType(
            cls._unique_columns_enum.__name__, cls._unique_columns_enum
        )
        cls._types[cls._unique_columns.name] = cls._unique_columns

        cls._queries[cls.__name__.lower()] = Field(
            type_=cls.__name__,
            resolve=partial(resolve_single, cls),
            args={
                "column": Argument(type_=cls._unique_columns.name),
                "value": Argument(type_=String),
            },
        )
        cls._queries[cls.__name__.lower()].bind(cls)

        cls._queries[f"{cls.__name__.lower()}s"] = Field(
            type_=cls.__name__,
            resolve=partial(resolve_many, cls),
            many=True,
            args={
                "like_by": Argument(type_=cls._columns.name, many=True, required=False),
                "like": Argument(type_=String, many=True, required=False),
                "order_by": Argument(
                    type_=cls._columns.name, many=True, required=False
                ),
                "order": Argument(type_="SQLAOrder", many=True, required=False),
                "page": Argument(type_=Int, required=False),
                "limit": Argument(type_=Int, required=False),
            },
        )
        cls._queries[f"{cls.__name__.lower()}s"].bind(cls)
