from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Location(BaseModel):
    model_config = ConfigDict(extra="allow")

    machine: str | None = None


class SourceSpec(BaseModel):
    """Describes where a catalog record's current truth comes from."""

    model_config = ConfigDict(extra="allow")

    type: str
    uri: str
    authority: Literal["catalog", "external", "derived"] = "catalog"
    refresh: Literal["manual", "on-read", "event", "poll"] = "manual"
    writeback: Literal["none", "controlled", "direct"] = "none"

    @field_validator("type", "uri")
    @classmethod
    def non_empty_source_fields(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value


class InterfaceSpec(BaseModel):
    """Describes a declared way to reach or operate on the underlying thing."""

    model_config = ConfigDict(extra="allow")

    type: str
    uri: str | None = None
    adapter: str | None = None
    status: Literal["declared", "available", "unavailable"] = "declared"
    operations: list[str] = Field(default_factory=list)

    @field_validator("type")
    @classmethod
    def non_empty_interface_type(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value


class RegistryObject(BaseModel):
    """Generic catalog record shared by every registry kind."""

    model_config = ConfigDict(extra="allow")

    id: str
    kind: str
    name: str
    description: str = ""
    status: str = "active"
    location: Location | None = None
    source: SourceSpec | None = None
    interfaces: list[InterfaceSpec] = Field(default_factory=list)
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
