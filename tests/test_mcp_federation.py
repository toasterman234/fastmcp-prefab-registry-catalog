from __future__ import annotations

import asyncio
from pathlib import Path

from fastmcp import Client, FastMCP

from app.catalog import CatalogView
from app.mcp_federation import (
    FEDERATION_ADAPTER,
    FederationManager,
    federation_status,
    mount_federated_servers,
    project_federated_objects,
    resolve_mcp_bindings,
)
from app.models import InterfaceSpec, RegistryObject
from app.registry import Registry

ROOT = Path(__file__).resolve().parents[1] / "registry"
FIXTURE_SERVER = Path(__file__).resolve().parent / "fixtures" / "mcp" / "backend.py"


def _federated_object() -> RegistryObject:
    return RegistryObject(
        id="resource.fixture-mcp",
        kind="resource",
        name="Fixture MCP",
        description="Test-only MCP backend",
        interfaces=[
            InterfaceSpec(
                type="mcp",
                uri=FIXTURE_SERVER.resolve().as_uri(),
                adapter=FEDERATION_ADAPTER,
                namespace="fixture",
                status="declared",
                operations=[],
            )
        ],
        capabilities=["fixture"],
    )


def test_default_catalog_has_no_implicit_proxy_bindings() -> None:
    registry = Registry(ROOT)
    assert resolve_mcp_bindings(registry.list_objects()) == []


def test_binding_uses_catalog_object_id_target_and_namespace() -> None:
    obj = _federated_object()
    bindings = resolve_mcp_bindings([obj])

    assert len(bindings) == 1
    binding = bindings[0]
    assert binding.object_id == obj.id
    assert binding.target == FIXTURE_SERVER.resolve()
    assert binding.namespace == "fixture"


def test_real_proxy_discovery_projection_and_tool_call() -> None:
    obj = _federated_object()
    bindings = resolve_mcp_bindings([obj])
    gateway = FastMCP("Federation Gateway")
    mount_errors = mount_federated_servers(gateway, bindings)
    assert mount_errors == {}

    manager = FederationManager(bindings, mount_errors=mount_errors, cache_ttl_seconds=60)

    async def scenario() -> None:
        async with Client(gateway) as client:
            tools = await client.list_tools()
            assert "fixture_echo" in {tool.name for tool in tools}

            prompts = await client.list_prompts()
            assert "fixture_review" in {prompt.name for prompt in prompts}

            resources = await client.list_resources()
            assert any("fixture/info" in str(resource.uri) for resource in resources)

            result = await client.call_tool("fixture_echo", {"value": "hello"})
            if result.data is not None:
                assert result.data == "echo:hello"
            else:
                assert "echo:hello" in str(result.content)

        snapshots = await manager.snapshot(force=True)
        assert len(snapshots) == 1
        snapshot = snapshots[0]
        assert snapshot.status == "available"
        assert snapshot.mounted is True
        assert snapshot.tools == ("echo",)
        assert snapshot.prompts == ("review",)
        assert "fixture://info" in snapshot.resources

        projected = project_federated_objects([obj], snapshots)
        assert len(projected) == 1
        live = projected[0]
        assert live.interfaces[0].status == "available"
        assert live.interfaces[0].namespace == "fixture"
        assert {"mcp-tools", "mcp-resources", "mcp-prompts"} <= set(live.capabilities)
        assert live.metadata["federation"]["fixture"]["components"]["tools"] == ["echo"]

        view = CatalogView([obj], projected)
        assert [item.id for item in view.search_objects("echo")] == [obj.id]

        status = federation_status(
            bindings,
            snapshots,
            cache_ttl_seconds=manager.cache_ttl_seconds,
            refreshed_at=manager.refreshed_at,
        )
        assert status["configured_count"] == 1
        assert status["available_count"] == 1
        assert status["unavailable_count"] == 0
        assert status["servers"][0]["components"]["prompts"] == ["review"]

    asyncio.run(scenario())
