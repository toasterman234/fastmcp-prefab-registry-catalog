from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Location(BaseModel):
    model_config = ConfigDict(extra="allow")

    machine: str | None = None


class RegistryObject(BaseModel):
    """Generic catalog record shared by every registry kind."""

    model_config = ConfigDict(extra="allow")

    id: str
    kind: str
    name: str
    description: str = ""
    status: str = "active"
    location: Location | None = None
    capabilities: list[str] = Field(default_factory=list)
    relationships: dict[str, list[str]] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("id", "kind", "name")
    @classmethod
    def non_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude_none=True)


class ValidationIssue(BaseModel):
    severity: str
    message: str
    object_id: str | None = None


class ValidationReport(BaseModel):
    valid: bool
    object_count: int
    issues: list[ValidationIssue] = Field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")
