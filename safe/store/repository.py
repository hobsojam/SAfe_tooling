from typing import Generic, TypeVar, Type
from pydantic import BaseModel
from tinydb import TinyDB, Query

T = TypeVar("T", bound=BaseModel)

# Computed fields that should never be persisted — recomputed on load
_COMPUTED_FIELDS = {"wsjf_score", "cost_of_delay", "available_capacity", "is_committed"}


class ReferentialIntegrityError(Exception):
    pass


class Repository(Generic[T]):
    def __init__(self, db: TinyDB, table_name: str, model: Type[T]) -> None:
        self._table = db.table(table_name)
        self._model = model

    def save(self, entity: T) -> T:
        data = entity.model_dump(mode="json", exclude=_COMPUTED_FIELDS)
        Q = Query()
        self._table.upsert(data, Q.id == entity.id)
        return entity

    def get(self, entity_id: str) -> T | None:
        Q = Query()
        result = self._table.get(Q.id == entity_id)
        return self._model.model_validate(result) if result else None

    def get_all(self) -> list[T]:
        return [self._model.model_validate(r) for r in self._table.all()]

    def find(self, **kwargs) -> list[T]:
        Q = Query()
        cond = None
        for k, v in kwargs.items():
            clause = getattr(Q, k) == v
            cond = clause if cond is None else (cond & clause)
        results = self._table.search(cond) if cond else self._table.all()
        return [self._model.model_validate(r) for r in results]

    def delete(self, entity_id: str) -> bool:
        Q = Query()
        removed = self._table.remove(Q.id == entity_id)
        return len(removed) > 0

    def count(self) -> int:
        return len(self._table)
