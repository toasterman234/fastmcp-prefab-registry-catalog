from __future__ import annotations

from collections.abc import Iterable

from app.models import RegistryObject
from app.registry import Registry


class CatalogView:
    """Read-only merged view over catalog records and runtime projections."""

    def __init__(
        self,
        base_objects: Iterable[RegistryObject],
        overlays: Iterable[RegistryObject] = (),
    ) -> None:
        by_id = {obj.id: obj for obj in base_objects}
        for obj in overlays:
            by_id[obj.id] = obj
        self._objects = list(by_id.values())

    def list_objects(self) -> list[RegistryObject]:
        return list(self._objects)

    def get_object(self, object_id: str) -> RegistryObject | None:
        return next((obj for obj in self._objects if obj.id == object_id), None)

    def search_objects(self, query: str) -> list[RegistryObject]:
        needle = query.strip().casefold()
        if not needle:
            return self.list_objects()
        return [obj for obj in self._objects if needle in Registry._search_text(obj)]

    def filter_objects(
        self, kind: str | None = None, status: str | None = None
    ) -> list[RegistryObject]:
        return [
            obj
            for obj in self._objects
            if (kind is None or obj.kind.casefold() == kind.casefold())
            and (status is None or obj.status.casefold() == status.casefold())
        ]

    def related_objects(self, object_id: str) -> dict[str, list[RegistryObject]]:
        obj = self.get_object(object_id)
        if obj is None:
            return {}
        return {
            relation: [related for target in targets if (related := self.get_object(target))]
            for relation, targets in obj.relationships.items()
        }

    def incoming_objects(self, object_id: str) -> dict[str, list[RegistryObject]]:
        incoming: dict[str, list[RegistryObject]] = {}
        for source in self._objects:
            for relation, targets in source.relationships.items():
                if object_id in targets:
                    incoming.setdefault(relation, []).append(source)
        return incoming
