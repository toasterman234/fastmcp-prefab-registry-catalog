from __future__ import annotations

import asyncio
import re
import time
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from fastmcp import Client, FastMCP
from fastmcp.server import create_proxy

from app.models import InterfaceSpec, RegistryObject

FEDERATION_ADAPTER = "fastmcp-proxy"
DEFAULT_CACHE_TTL_SECONDS = 30.0


@dataclass(frozen=True)
class MCPBinding:
    object_id: str
    interface_index: int
    target: str | Path
    namespace: str

    @property
    def key(self) -> str:
        return f"{self.object_id}#{self.interface_index}"


@dataclass(frozen=True)
class FederationSnapshot:
    object_id: str
    interface_index: int
    namespace: str
    status: str
    mounted: bool
    protocol_version: str | None
    tools: tuple[str, ...] = ()
    resources: tuple[str, ...] = ()
    resource_templates: tuple[str, ...] = ()
    prompts: tuple[str, ...] = ()
    error: str | None = None

    @property
    def key(self) -> str:
        return f"{self.object_id}#{self.interface_index}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "object_id": self.object_id,
            "interface_index": self.interface_index,
            "namespace": self.namespace,
            "status": self.status,
            "mounted": self.mounted,
            "protocol_version": self.protocol_version,
            "component_counts": {
                "tools": len(self.tools),
                "resources": len(self.resources),
                "resource_templates": len(self.resource_templates),
                "prompts": len(self.prompts),
            },
            "components": {
                "tools": list(self.tools),
                "resources": list(self.resources),
                "resource_templates": list(self.resource_templates),
                "prompts": list(self.prompts),
            },
            "error": self.error,
        }


def _default_namespace(object_id: str) -> str:
    raw = object_id.rsplit(".", 1)[-1].casefold()
    namespace = re.sub(r"[^a-z0-9_]+", "_", raw).strip("_")
    if not namespace:
        raise ValueError(f"Could not derive MCP namespace from object ID: {object_id}")
    return namespace


def _target_from_uri(uri: str) -> str | Path:
    parsed = urlparse(uri)
    if parsed.scheme in {"http", "https"}:
        return uri
    if parsed.scheme == "file":
        path = unquote(parsed.path)
        if parsed.netloc and parsed.netloc != "localhost":
            path = f"//{parsed.netloc}{path}"
        if not path:
            raise ValueError(f"File MCP interface has no path: {uri}")
        return Path(path)
    raise ValueError(
        "FastMCP federation supports http://, https://, and file:// targets; "
        f"got {parsed.scheme or 'no scheme'} for {uri!r}"
    )


def resolve_mcp_bindings(objects: list[RegistryObject]) -> list[MCPBinding]:
    """Resolve explicit fastmcp-proxy interfaces from catalog objects."""
    bindings: list[MCPBinding] = []
    namespaces: dict[str, str] = {}

    for obj in objects:
        for index, interface in enumerate(obj.interfaces):
            if interface.type.casefold() != "mcp":
                continue
            if (interface.adapter or "").casefold() != FEDERATION_ADAPTER:
                continue
            if not interface.uri:
                raise ValueError(f"{obj.id} MCP proxy interface requires a URI")

            namespace = interface.namespace or _default_namespace(obj.id)
            namespace = re.sub(r"[^A-Za-z0-9_]+", "_", namespace).strip("_")
            if not namespace:
                raise ValueError(f"{obj.id} MCP proxy interface has an empty namespace")
            if previous := namespaces.get(namespace):
                raise ValueError(
                    f"Duplicate MCP federation namespace {namespace!r}: "
                    f"{previous} and {obj.id}"
                )
            namespaces[namespace] = obj.id

            bindings.append(
                MCPBinding(
                    object_id=obj.id,
                    interface_index=index,
                    target=_target_from_uri(interface.uri),
                    namespace=namespace,
                )
            )

    return bindings


def mount_federated_servers(
    server: FastMCP,
    bindings: list[MCPBinding],
) -> dict[str, str]:
    """Mount lazy FastMCP proxies and return construction errors by binding key."""
    errors: dict[str, str] = {}
    for binding in bindings:
        try:
            proxy = create_proxy(
                binding.target,
                name=f"Federated {binding.object_id}",
            )
            server.mount(proxy, namespace=binding.namespace)
        except Exception as exc:
            errors[binding.key] = f"{type(exc).__name__}: {exc}"
    return errors


async def discover_binding(binding: MCPBinding) -> FederationSnapshot:
    """Read back one upstream MCP server without mutating catalog state."""
    try:
        client = Client(binding.target, name=f"catalog-discovery:{binding.object_id}")
        async with client:
            tools = await client.list_tools()
            resources = await client.list_resources()
            templates = await client.list_resource_templates()
            prompts = await client.list_prompts()
            protocol_version = str(client.protocol_version)

        return FederationSnapshot(
            object_id=binding.object_id,
            interface_index=binding.interface_index,
            namespace=binding.namespace,
            status="available",
            mounted=True,
            protocol_version=protocol_version,
            tools=tuple(sorted(tool.name for tool in tools)),
            resources=tuple(sorted(str(resource.uri) for resource in resources)),
            resource_templates=tuple(
                sorted(str(template.uri_template) for template in templates)
            ),
            prompts=tuple(sorted(prompt.name for prompt in prompts)),
        )
    except Exception as exc:
        return FederationSnapshot(
            object_id=binding.object_id,
            interface_index=binding.interface_index,
            namespace=binding.namespace,
            status="unavailable",
            mounted=True,
            protocol_version=None,
            error=f"{type(exc).__name__}: {exc}",
        )


class FederationManager:
    """Small on-demand discovery cache for configured MCP federation bindings."""

    def __init__(
        self,
        bindings: list[MCPBinding],
        *,
        mount_errors: dict[str, str] | None = None,
        cache_ttl_seconds: float = DEFAULT_CACHE_TTL_SECONDS,
    ) -> None:
        self.bindings = list(bindings)
        self.mount_errors = dict(mount_errors or {})
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cache: list[FederationSnapshot] | None = None
        self._cache_time = 0.0
        self._refreshed_at: str | None = None
        self._lock = asyncio.Lock()

    @property
    def refreshed_at(self) -> str | None:
        return self._refreshed_at

    async def snapshot(self, *, force: bool = False) -> list[FederationSnapshot]:
        if not self.bindings:
            return []

        now = time.monotonic()
        if (
            not force
            and self._cache is not None
            and now - self._cache_time < self.cache_ttl_seconds
        ):
            return list(self._cache)

        async with self._lock:
            now = time.monotonic()
            if (
                not force
                and self._cache is not None
                and now - self._cache_time < self.cache_ttl_seconds
            ):
                return list(self._cache)

            discovered = list(
                await asyncio.gather(*(discover_binding(binding) for binding in self.bindings))
            )
            adjusted: list[FederationSnapshot] = []
            for item in discovered:
                mount_error = self.mount_errors.get(item.key)
                if mount_error:
                    adjusted.append(
                        replace(
                            item,
                            status="unavailable",
                            mounted=False,
                            error=mount_error,
                        )
                    )
                else:
                    adjusted.append(item)

            self._cache = adjusted
            self._cache_time = time.monotonic()
            self._refreshed_at = datetime.now(UTC).isoformat()
            return list(adjusted)


def _merge_interface(
    interface: InterfaceSpec,
    snapshot: FederationSnapshot,
) -> InterfaceSpec:
    data = interface.model_dump(mode="json", exclude_none=True)
    data["status"] = snapshot.status
    data["namespace"] = snapshot.namespace

    operations = set(interface.operations)
    if snapshot.status == "available":
        if snapshot.tools:
            operations.add("tools")
        if snapshot.resources or snapshot.resource_templates:
            operations.add("resources")
        if snapshot.prompts:
            operations.add("prompts")
    data["operations"] = sorted(operations)
    return InterfaceSpec.model_validate(data)


def project_federated_objects(
    objects: list[RegistryObject],
    snapshots: list[FederationSnapshot],
) -> list[RegistryObject]:
    """Overlay runtime federation evidence onto the corresponding catalog objects."""
    by_id = {obj.id: obj for obj in objects}
    projected: dict[str, RegistryObject] = {}

    for snapshot in snapshots:
        existing = projected.get(snapshot.object_id) or by_id.get(snapshot.object_id)
        if existing is None:
            continue
        if snapshot.interface_index >= len(existing.interfaces):
            continue

        interfaces = list(existing.interfaces)
        interfaces[snapshot.interface_index] = _merge_interface(
            interfaces[snapshot.interface_index],
            snapshot,
        )

        metadata = dict(existing.metadata)
        federation = dict(metadata.get("federation") or {})
        federation[snapshot.namespace] = snapshot.to_dict()
        metadata["federation"] = federation

        capabilities = set(existing.capabilities)
        if snapshot.status == "available":
            if snapshot.tools:
                capabilities.add("mcp-tools")
            if snapshot.resources or snapshot.resource_templates:
                capabilities.add("mcp-resources")
            if snapshot.prompts:
                capabilities.add("mcp-prompts")

        projected[snapshot.object_id] = RegistryObject(
            **{
                **existing.to_dict(),
                "interfaces": interfaces,
                "capabilities": sorted(capabilities),
                "metadata": metadata,
            }
        )

    return list(projected.values())


def federation_status(
    bindings: list[MCPBinding],
    snapshots: list[FederationSnapshot],
    *,
    cache_ttl_seconds: float,
    refreshed_at: str | None,
) -> dict[str, Any]:
    return {
        "enabled": bool(bindings),
        "provider": "FastMCP create_proxy + mount",
        "configured_count": len(bindings),
        "available_count": sum(item.status == "available" for item in snapshots),
        "unavailable_count": sum(item.status == "unavailable" for item in snapshots),
        "cache_ttl_seconds": cache_ttl_seconds,
        "refreshed_at": refreshed_at,
        "servers": [item.to_dict() for item in snapshots],
    }
