from __future__ import annotations

import json
from typing import TypeVar, Generic

from attr import Factory, define, field

from marshmallow import class_registry, Schema
from marshmallow.exceptions import RegistryError
from griptape.schemas.base_schema import BaseSchema

T = TypeVar("T", bound="SerializableMixin")


@define(slots=False)
class SerializableMixin(Generic[T]):
    type: str = field(
        default=Factory(lambda self: self.__class__.__name__, takes_self=True),
        kw_only=True,
        metadata={"serialize": True},
    )

    @classmethod
    def before_load(cls: type[T], data: dict) -> dict:
        return data

    @classmethod
    def before_dump(cls: type[T], data: T) -> T:
        return data

    @classmethod
    def get_schema(cls: type[T], obj_type: str) -> Schema:
        schema_class = cls.try_get_schema(obj_type)

        if isinstance(schema_class, type):
            return schema_class()
        else:
            raise RegistryError(f"Unsupported type: {obj_type}")

    @classmethod
    def try_get_schema(cls: type[T], obj_type: str) -> list[type[Schema]] | type[Schema]:
        class_registry.register(obj_type, BaseSchema.from_attrscls(cls))

        return class_registry.get_class(obj_type)

    @classmethod
    def from_dict(cls, data: dict) -> T:
        return cls.get_schema(data["type"]).load(data)

    @classmethod
    def from_json(cls: type[T], data: str) -> T:
        return cls.from_dict(json.loads(data))

    def __str__(self) -> str:
        return json.dumps(self.to_dict())

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        schema = BaseSchema.from_attrscls(self.__class__)

        return dict(schema().dump(self))
