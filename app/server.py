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
from fastmcp.apps.generative import GenerativeUI
from prefab_ui.app import PrefabApp
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.catalog import CatalogView
from app.mcp_federation import (
    FederationManager,
    federation_status,
    mount_federated_servers,
    project_federated_objects,
    resolve_mcp_bindings,
)
from app.registry import registry
from app.skill_discovery import (
    build_skills_provider,
    discovery_status,
    project_discovered_skills,
    resolve_skill_roots,
)
from app.ui import build_catalog_app

mcp = FastMCP(
    "Environment Catalog",
    instructions=(
        "A portable catalog of agents, skills, policies, resources, machines, databases, "
        "projects, and playbooks. Use the deterministic catalog app for known registry "
        "browsing, discovered skill resources for runtime instructions, federated MCP "
        "components through their namespaces, and Generative UI for open-ended visualizations."
    ),
)
mcp.add_provider(GenerativeUI())

_SKILL_ROOTS = resolve_skill_roots()
_SKILLS_PROVIDER = build_skills_provider(_SKILL_ROOTS, reload=True)
if _SKILLS_PROVIDER is not None:
    # A configured root becomes runtime evidence only after FastMCP discovers
    # an actual SKILL.md. The provider remains read-only in this stage.
    mcp.add_provider(_SKILLS_PROVIDER)

_MCP_BINDINGS = resolve_mcp_bindings(registry.list_objects())
_MCP_MOUNT_ERRORS = mount_federated_servers(mcp, _MCP_BINDINGS)
_FEDERATION = FederationManager(
    _MCP_BINDINGS,
    mount_errors=_MCP_MOUNT_ERRORS,
)


def _objects_payload(objects: list[Any]) -> list[dict[str, Any]]:
    return [obj.to_dict() for obj in objects]


async def _catalog_view(
    *,
    refresh_federation: bool = False,
) -> tuple[CatalogView, dict[str, Any]]:
    base_objects = registry.list_objects()

    projected_skills = project_discovered_skills(_SKILL_ROOTS, base_objects)
    skill_view = CatalogView(base_objects, projected_skills)

    federation_snapshots = await _FEDERATION.snapshot(force=refresh_federation)
    projected_federation = project_federated_objects(
        skill_view.list_objects(),
        federation_snapshots,
    )
    catalog_view = CatalogView(skill_view.list_objects(), projected_federation)

    discovery = {
        "skills": discovery_status(_SKILL_ROOTS, projected_skills),
        "mcp_federation": federation_status(
            _MCP_BINDINGS,
            federation_snapshots,
            cache_ttl_seconds=_FEDERATION.cache_ttl_seconds,
            refreshed_at=_FEDERATION.refreshed_at,
        ),
    }
    return catalog_view, discovery


def _status_summary(objects: list[Any]) -> str:
    counts: dict[str, int] = {}
    for obj in objects:
        counts[obj.status] = counts.get(obj.status, 0) + 1
    return ", ".join(f"{status}: {count}" for status, count in sorted(counts.items())) or "no statuses"


async def _catalog_snapshot(*, refresh_federation: bool = False) -> dict[str, Any]:
    catalog_view, discovery = await _catalog_view(
        refresh_federation=refresh_federation
    )
    objects = catalog_view.list_objects()
    return {
        "objects": _objects_payload(objects),
        "status_summary": _status_summary(objects),
        "connected": True,
        "discovery": discovery,
    }


@mcp.tool()
async def registry_search(query: str) -> list[dict[str, Any]]:
    """Search the merged catalog, including runtime-discovered skills and MCP metadata."""
    catalog_view, _ = await _catalog_view()
    return _objects_payload(catalog_view.search_objects(query))


@mcp.tool()
async def registry_get(object_id: str) -> dict[str, Any] | None:
    """Get one merged catalog object by its stable ID."""
    catalog_view, _ = await _catalog_view()
    obj = catalog_view.get_object(object_id)
    return obj.to_dict() if obj else None


@mcp.tool()
async def registry_list(
    kind: str | None = None,
    status: str | None = None,
) -> list[dict[str, Any]]:
    """List merged catalog objects, optionally filtered by kind and/or status."""
    catalog_view, _ = await _catalog_view()
    return _objects_payload(catalog_view.filter_objects(kind=kind, status=status))


@mcp.tool()
async def registry_related(object_id: str) -> dict[str, list[dict[str, Any]]]:
    """Resolve outgoing relationships declared by one merged catalog object."""
    catalog_view, _ = await _catalog_view()
    return {
        relation: _objects_payload(objects)
        for relation, objects in catalog_view.related_objects(object_id).items()
    }


@mcp.tool()
async def registry_incoming(object_id: str) -> dict[str, list[dict[str, Any]]]:
    """Resolve merged catalog objects that point to the selected object."""
    catalog_view, _ = await _catalog_view()
    return {
        relation: _objects_payload(objects)
        for relation, objects in catalog_view.incoming_objects(object_id).items()
    }


@mcp.tool()
async def registry_validate() -> dict[str, Any]:
    """Validate durable YAML and report runtime discovery separately."""
    catalog_view, discovery = await _catalog_view()
    report = registry.validate_registry().to_dict()
    report["object_count"] = len(catalog_view.list_objects())
    report["base_object_count"] = len(registry.list_objects())
    report["discovery"] = discovery
    return report


@mcp.tool()
def skill_discovery_status() -> dict[str, Any]:
    """Report configured skill roots and currently discovered skill IDs."""
    base_objects = registry.list_objects()
    projected_skills = project_discovered_skills(_SKILL_ROOTS, base_objects)
    return discovery_status(_SKILL_ROOTS, projected_skills)


@mcp.tool()
async def mcp_federation_status(refresh: bool = False) -> dict[str, Any]:
    """Read MCP federation status; set refresh=true for a fresh upstream probe."""
    snapshots = await _FEDERATION.snapshot(force=refresh)
    return federation_status(
        _MCP_BINDINGS,
        snapshots,
        cache_ttl_seconds=_FEDERATION.cache_ttl_seconds,
        refreshed_at=_FEDERATION.refreshed_at,
    )


@mcp.custom_route("/api/catalog", methods=["GET"])
async def catalog_http_projection(request: Request) -> JSONResponse:
    """Read-only HTTP projection for the separate workspace shell."""
    refresh = request.query_params.get("refresh_mcp", "").casefold() in {
        "1",
        "true",
        "yes",
    }
    return JSONResponse(
        await _catalog_snapshot(refresh_federation=refresh)
    )


@mcp.resource("registry://objects/{object_id}", mime_type="application/json")
async def registry_object_resource(object_id: str) -> str:
    """Read an individual merged catalog object as JSON."""
    catalog_view, _ = await _catalog_view()
    obj = catalog_view.get_object(object_id)
    if obj is None:
        return json.dumps({"error": "not_found", "id": object_id})
    return json.dumps(obj.to_dict(), indent=2)


@mcp.resource("registry://objects", mime_type="application/json")
async def registry_objects_resource() -> str:
    """Read the complete merged catalog snapshot as JSON."""
    catalog_view, _ = await _catalog_view()
    return json.dumps(_objects_payload(catalog_view.list_objects()), indent=2)


@mcp.tool(app=True)
async def catalog() -> PrefabApp:
    """Browse the merged Environment Catalog in a compact Prefab UI."""
    catalog_view, _ = await _catalog_view()
    objects = catalog_view.list_objects()
    incoming = {obj.id: catalog_view.incoming_objects(obj.id) for obj in objects}
    return build_catalog_app(objects, _status_summary(objects), incoming)


if __name__ == "__main__":
    mcp.run()
