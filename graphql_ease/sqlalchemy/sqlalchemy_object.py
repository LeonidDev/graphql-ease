from sqlalchemy.inspection import inspect
from ..types import Object

from .converter import column_to_field, relationship_to_field


__all__ = ["SQLAlchemyObject"]


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
