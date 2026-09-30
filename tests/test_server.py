from __future__ import annotations

import asyncio

from app.server import mcp


def test_server_exposes_registry_skill_federation_and_generative_ui_tools() -> None:
    tools = asyncio.run(mcp.list_tools())
    names = {tool.name for tool in tools}

    assert {
        "registry_search",
        "registry_get",
        "registry_list",
        "registry_related",
        "registry_incoming",
        "registry_validate",
        "skill_discovery_status",
        "mcp_federation_status",
        "catalog",
        "generate_prefab_ui",
        "search_prefab_components",
    } <= names
