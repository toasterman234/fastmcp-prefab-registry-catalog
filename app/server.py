from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

# FastMCP's development loader may import this file directly rather than as a package.
# Ensure the project root is importable in both direct-file and package contexts.
_PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from fastmcp import FastMCP
from prefab_ui.app import PrefabApp
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.registry import registry
from app.ui import build_catalog_app

mcp = FastMCP(
    "Environment Catalog",
    instructions="A minimal YAML-backed catalog of agents, skills, policies, resources, machines, databases, projects, and playbooks.",
)


def _objects_payload(objects: list[Any]) -> list[dict[str, Any]]:
    return [obj.to_dict() for obj in objects]


def _catalog_snapshot() -> dict[str, Any]:
    return {
        "objects": _objects_payload(registry.list_objects()),
        "status_summary": _status_summary(),
        "connected": True,
    }


def _status_summary() -> str:
    counts: dict[str, int] = {}
    for obj in registry.list_objects():
        counts[obj.status] = counts.get(obj.status, 0) + 1
    return ", ".join(f"{status}: {count}" for status, count in sorted(counts.items())) or "no statuses"


@mcp.tool()
def registry_search(query: str) -> list[dict[str, Any]]:
    """Search registry objects across IDs, names, descriptions, capabilities, and relationships."""
    return _objects_payload(registry.search_objects(query))


@mcp.tool()
def registry_get(object_id: str) -> dict[str, Any] | None:
    """Get one registry object by its stable ID."""
    obj = registry.get_object(object_id)
    return obj.to_dict() if obj else None


@mcp.tool()
def registry_list(kind: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
    """List registry objects, optionally filtered by kind and/or status."""
    return _objects_payload(registry.filter_objects(kind=kind, status=status))


@mcp.tool()
def registry_related(object_id: str) -> dict[str, list[dict[str, Any]]]:
    """Resolve outgoing relationships declared by one registry object."""
    return {
        relation: _objects_payload(objects)
        for relation, objects in registry.related_objects(object_id).items()
    }


@mcp.tool()
def registry_incoming(object_id: str) -> dict[str, list[dict[str, Any]]]:
    """Resolve registry objects that point to the selected object."""
    return {
        relation: _objects_payload(objects)
        for relation, objects in registry.incoming_objects(object_id).items()
    }


@mcp.tool()
def registry_validate() -> dict[str, Any]:
    """Validate YAML records, duplicate IDs, and relationship references."""
    return registry.validate_registry().to_dict()


@mcp.custom_route("/api/catalog", methods=["GET"])
async def catalog_http_projection(request: Request) -> JSONResponse:
    """Read-only HTTP projection for the separate workspace shell."""
    return JSONResponse(_catalog_snapshot())


@mcp.resource("registry://objects/{object_id}", mime_type="application/json")
def registry_object_resource(object_id: str) -> str:
    """Read an individual registry object as JSON."""
    obj = registry.get_object(object_id)
    if obj is None:
        return json.dumps({"error": "not_found", "id": object_id})
    return json.dumps(obj.to_dict(), indent=2)


@mcp.resource("registry://objects", mime_type="application/json")
def registry_objects_resource() -> str:
    """Read the complete registry snapshot as JSON."""
    return json.dumps(_objects_payload(registry.list_objects()), indent=2)


@mcp.tool(app=True)
def catalog() -> PrefabApp:
    """Browse the Environment Catalog in a compact Prefab UI."""
    objects = registry.list_objects()
    incoming = {obj.id: registry.incoming_objects(obj.id) for obj in objects}
    return build_catalog_app(objects, _status_summary(), incoming)


if __name__ == "__main__":
    mcp.run()
