from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

import yaml
from pydantic import ValidationError

from app.models import RegistryObject, ValidationIssue, ValidationReport

DEFAULT_REGISTRY_ROOT = Path(__file__).resolve().parents[1] / "registry"
REGISTRY_ROOT_ENV = "REGISTRY_ROOT"


def resolve_registry_root(root: str | Path | None = None) -> Path:
    """Resolve the registry source root.

    Precedence is explicit argument, REGISTRY_ROOT environment variable,
    then the source-checkout development default.
    """
    if root is not None:
        return Path(root).expanduser()

    configured = os.getenv(REGISTRY_ROOT_ENV)
    if configured:
        return Path(configured).expanduser()

    return DEFAULT_REGISTRY_ROOT


class Registry:
    """Portable YAML-backed registry domain service, independent of FastMCP."""

    def __init__(self, root: str | Path | None = None):
        self.root = resolve_registry_root(root)
        self._objects: list[RegistryObject] = []
        self._load_errors: list[ValidationIssue] = []
        self.reload()

    def reload(self) -> None:
        self._objects = []
        self._load_errors = []
        if not self.root.exists():
            self._load_errors.append(
                ValidationIssue(severity="error", message=f"Registry root does not exist: {self.root}")
            )
            return
        for path in sorted(self.root.rglob("*.y*ml")):
            self._load_file(path)

    def _load_file(self, path: Path) -> None:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if data is None:
                return
            records = data if isinstance(data, list) else [data]
            for record in records:
                if not isinstance(record, dict):
                    raise ValueError("record must be a YAML mapping")
                self._objects.append(RegistryObject.model_validate(record))
        except (OSError, yaml.YAMLError, ValidationError, ValueError) as exc:
            self._load_errors.append(
                ValidationIssue(
                    severity="error",
                    message=f"{path.relative_to(self.root)}: {exc}",
                )
            )

    def list_objects(self) -> list[RegistryObject]:
        return list(self._objects)

    def get_object(self, object_id: str) -> RegistryObject | None:
        return next((obj for obj in self._objects if obj.id == object_id), None)

    def search_objects(self, query: str) -> list[RegistryObject]:
        needle = query.strip().casefold()
        if not needle:
            return self.list_objects()
        return [obj for obj in self._objects if needle in self._search_text(obj)]

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

    def validate_registry(self) -> ValidationReport:
        issues = list(self._load_errors)
        seen: dict[str, RegistryObject] = {}
        for obj in self._objects:
            if obj.id in seen:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        object_id=obj.id,
                        message=f"Duplicate object ID: {obj.id}",
                    )
                )
            seen[obj.id] = obj
        for obj in self._objects:
            for relation, targets in obj.relationships.items():
                for target in targets:
                    if target not in seen:
                        issues.append(
                            ValidationIssue(
                                severity="error",
                                object_id=obj.id,
                                message=(
                                    f"Broken relationship {relation!r}: {obj.id} references missing {target}"
                                ),
                            )
                        )
        return ValidationReport(
            valid=not any(issue.severity == "error" for issue in issues),
            object_count=len(self._objects),
            issues=issues,
        )

    @staticmethod
    def _search_text(obj: RegistryObject) -> str:
        values: Iterable[str] = [
            obj.id,
            obj.kind,
            obj.name,
            obj.description,
            obj.status,
            *obj.capabilities,
            *obj.relationships.keys(),
            *(target for targets in obj.relationships.values() for target in targets),
        ]
        return " ".join(values).casefold()


registry = Registry()


def list_objects() -> list[RegistryObject]:
    return registry.list_objects()


def get_object(object_id: str) -> RegistryObject | None:
    return registry.get_object(object_id)


def search_objects(query: str) -> list[RegistryObject]:
    return registry.search_objects(query)


def filter_objects(kind: str | None = None, status: str | None = None) -> list[RegistryObject]:
    return registry.filter_objects(kind=kind, status=status)


def related_objects(object_id: str) -> dict[str, list[RegistryObject]]:
    return registry.related_objects(object_id)


def validate_registry() -> ValidationReport:
    return registry.validate_registry()
